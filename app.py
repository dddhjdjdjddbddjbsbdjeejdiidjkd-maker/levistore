import os
import re
import sys
import json
import shutil
import signal
import asyncio
import logging
import subprocess
import importlib.util
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, Bot
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
from telegram.error import BadRequest

# إعداد التسجيل للمتابعة
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# التوكن الخاص ببوتك الرئيسي
TOKEN = "8303737313:AAHKGQOmrFG3q5hHyL5dhOW4duHS7hxYxes"

# مجلدات وقواعد البيانات
USER_BOTS_DIR = "hosted_bots"
DB_FILE = "bots_db.json"
MAX_BOTS = 5

os.makedirs(USER_BOTS_DIR, exist_ok=True)

# قاموس لتخزين العمليات الشغالة في الذاكرة { "user_id_slot": process_object }
running_processes = {}
# قاموس لتتبع التوكنات المستضافة للحد من التعارض { token: "user_id_slot" }
active_tokens = {}

# --- إدارة قاعدة البيانات المحلية ---
def load_db():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_db(data):
    try:
        with open(DB_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logging.error(f"خطأ في حفظ قاعدة البيانات: {e}")

# --- تثبيت المكتبات بطريقة غير متزامنة لتفادي تجميد البوت الرئيسي ---
async def install_missing_libraries_async(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

        imports = re.findall(r'^(?:from|import)\s+([a-zA-Z0-9_]+)', content, re.MULTILINE)
        
        lib_map = {
            'bs4': 'beautifulsoup4',
            'telegram': 'python-telegram-bot',
            'cv2': 'opencv-python',
            'PIL': 'Pillow',
            'fitz': 'PyMuPDF',
            'requests': 'requests',
            'aiohttp': 'aiohttp',
            'telebot': 'pyTelegramBotAPI'
        }

        for lib in set(imports):
            package_name = lib_map.get(lib, lib)
            if importlib.util.find_spec(lib) is None:
                proc = await asyncio.create_subprocess_exec(
                    sys.executable, "-m", "pip", "install", package_name,
                    stdout=asyncio.subprocess.DEVNULL,
                    stderr=asyncio.subprocess.DEVNULL
                )
                await proc.wait()
    except Exception as e:
        logging.error(f"خطأ أثناء تثبيت المكتبات: {e}")

# --- إيقاف العملية والموارد بشكل آمن ---
async def kill_process_safely(proc_key):
    if proc_key in running_processes:
        proc = running_processes[proc_key]
        try:
            os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
            await asyncio.sleep(0.5)
            if proc.poll() is None:
                os.killpg(os.getpgid(proc.pid), signal.SIGKILL)
        except Exception:
            try:
                proc.kill()
            except Exception:
                pass
        del running_processes[proc_key]

    tokens_to_remove = [tok for tok, key in active_tokens.items() if key == proc_key]
    for tok in tokens_to_remove:
        del active_tokens[tok]

# --- دالة استخلاص توكن ومعلومات البوت ---
async def get_hosted_bot_info(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        match = re.search(r'\d{8,10}:[A-Za-z0-9_-]{35}', content)
        if match:
            extracted_token = match.group(0)
            temp_bot = Bot(token=extracted_token)
            me = await temp_bot.get_me()
            return me.first_name, f"@{me.username}", extracted_token
    except Exception:
        pass
    return "غير معروف", "غير محدد", None

# --- تشغيل وإدارة البوت المستضاف ---
async def start_hosted_bot(user_id: int, slot: int) -> bool:
    proc_key = f"{user_id}_{slot}"
    user_folder = os.path.abspath(os.path.join(USER_BOTS_DIR, str(user_id), f"bot_{slot}"))
    file_path = os.path.join(user_folder, "main.py")
    log_path = os.path.join(user_folder, "log.txt")

    if not os.path.exists(file_path):
        return False

    await kill_process_safely(proc_key)
    await install_missing_libraries_async(file_path)

    _, _, token = await get_hosted_bot_info(file_path)
    if token:
        active_tokens[token] = proc_key

    # تهيئة بيئة التشغيل لمنع التخزين المؤقت وضمان استقرار السجلات
    env = os.environ.copy()
    env["PYTHONUNBUFFERED"] = "1"

    log_file = open(log_path, "a", encoding="utf-8")
    proc = subprocess.Popen(
        [sys.executable, file_path],
        cwd=user_folder,
        stdout=log_file,
        stderr=log_file,
        start_new_session=True,
        env=env
    )
    running_processes[proc_key] = proc

    # تحديث الحالة في قاعدة البيانات
    db = load_db()
    u_str, s_str = str(user_id), str(slot)
    if u_str not in db:
        db[u_str] = {}
    db[u_str][s_str] = {"running": True, "token": token}
    save_db(db)

    logging.info(f"تم تشغيل البوت بنجاح: {proc_key}")
    return True

async def stop_hosted_bot(user_id: int, slot: int):
    proc_key = f"{user_id}_{slot}"
    await kill_process_safely(proc_key)

    db = load_db()
    u_str, s_str = str(user_id), str(slot)
    if u_str in db and s_str in db[u_str]:
        db[u_str][s_str]["running"] = False
        save_db(db)

# --- نظام المراقبة الدائم (Auto-Restart Monitor Loop) ---
async def bot_monitor_loop():
    while True:
        await asyncio.sleep(10)
        db = load_db()
        for user_id_str, slots in db.items():
            for slot_str, info in slots.items():
                if info.get("running", False):
                    proc_key = f"{user_id_str}_{slot_str}"
                    proc = running_processes.get(proc_key)
                    
                    # إذا توقف البوت أو تعطل لأي سبب، أعد تشغيله فوراً
                    if proc is None or proc.poll() is not None:
                        logging.warning(f"البوت {proc_key} متوقف! جاري إعادة التشغيل تلقائياً...")
                        await start_hosted_bot(int(user_id_str), int(slot_str))

# --- الواجهات والتفاعلات ---
def main_menu_keyboard():
    keyboard = [
        [
            InlineKeyboardButton("🚀 رفع بوت", callback_data="upload_bot"),
            InlineKeyboardButton("⚙️ التحكم في البوتات", callback_data="manage_bots")
        ],
        [
            InlineKeyboardButton("📊 بوتاتك", callback_data="my_bots")
        ],
        [
            InlineKeyboardButton("👨‍💻 الدعم الفني", callback_data="support")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

WELCOME_TEXT = (
    "<b>𝗪𝗘𝗟𝗖𝗢𝗠𝗘 𝗧𝗢 𝗟𝗘𝗩𝗜 𝗠𝗢𝗗</b>\n"
    "الـمـطـور لـيـفـاي ⠉⃝ 🇪🇬 ⸙ꠋꠋꠋꠋꠋꠋꠋꠋꠋꠋꠋ 」\n\n"
    "مرحباً بك في منصة استضافة وتشغيل البوتات 24/7 (نظام الحماية والاستقرار الفائق).\n"
    "قم برفع ملف البوت الخاص بك وسيعمل بتصميمه وكوده الأصلي دون أي توقف:"
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(WELCOME_TEXT, reply_markup=main_menu_keyboard(), parse_mode="HTML")

async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    document = update.message.document

    if not document.file_name.endswith('.py'):
        await update.message.reply_text("⚠️ يرجى إرسال ملف بصيغة Python فقط (<code>.py</code>).", parse_mode="HTML")
        return

    target_slot = context.user_data.get('target_slot')

    if not target_slot:
        for slot in range(1, MAX_BOTS + 1):
            bot_path = os.path.join(USER_BOTS_DIR, str(user_id), f"bot_{slot}", "main.py")
            if not os.path.exists(bot_path):
                target_slot = slot
                break

    if not target_slot:
        await update.message.reply_text(
            "⚠️ <b>وصلت للحد الأقصى المسموح (5/5 بوتات)!</b>\n"
            "يرجى الانتقال للوحة التحكم واختيار بوت للتعويض عليه أو إزالته أولاً.",
            parse_mode="HTML"
        )
        return

    user_folder = os.path.abspath(os.path.join(USER_BOTS_DIR, str(user_id), f"bot_{target_slot}"))
    os.makedirs(user_folder, exist_ok=True)
    
    file_path = os.path.join(user_folder, "main.py")
    file = await context.bot.get_file(document.file_id)
    await file.download_to_drive(file_path)

    context.user_data.pop('target_slot', None)

    _, _, token = await get_hosted_bot_info(file_path)
    proc_key = f"{user_id}_{target_slot}"

    if token and token in active_tokens and active_tokens[token] != proc_key:
        await update.message.reply_text(
            "⚠️ <b>عذراً، هذا التوكن يعمل بالفعل على خانة أخرى أو حساب آخر!</b>",
            parse_mode="HTML"
        )
        return

    # تشغيل البوت عبر النظام المطور
    await start_hosted_bot(user_id, target_slot)

    keyboard = [
        [InlineKeyboardButton("📊 عرض بوتاتك", callback_data="my_bots")],
        [InlineKeyboardButton("⚙️ الانتقال للتحكم", callback_data=f"manage_slot_{target_slot}")],
        [InlineKeyboardButton("🔙 القائمة الرئيسية", callback_data="main_menu")]
    ]
    await update.message.reply_text(
        f"✅ <b>تم رفع وتشغيل (البوت رقم {target_slot}) بنجاح!</b>\n"
        "البوت يعمل الآن ومحمياً بنظام الحماية ضد التوقف 24/7.",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="HTML"
    )

async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    
    try:
        await query.answer()
    except BadRequest:
        pass

    user_id = update.effective_user.id

    if query.data == "upload_bot":
        keyboard = []
        for slot in range(1, MAX_BOTS + 1):
            bot_file = os.path.join(USER_BOTS_DIR, str(user_id), f"bot_{slot}", "main.py")
            status_icon = "📁 (مستعمل)" if os.path.exists(bot_file) else "➕ (فارغ)"
            keyboard.append([InlineKeyboardButton(f"🤖 بوت رقم {slot} {status_icon}", callback_data=f"select_upload_{slot}")])
        keyboard.append([InlineKeyboardButton("🔙 العودة للقائمة الرئيسية", callback_data="main_menu")])

        text = (
            "📤 <b>رفع بوت جديد (اختر الخانة المناسبة):</b>\n\n"
            "يمكنك استضافة حتى 5 بوتات مختلفة تشغلها بوقت واحد.\n"
            "اختر رقم البوت الذي تريد رفعه أو استبداله:"
        )

    elif query.data.startswith("select_upload_"):
        slot = int(query.data.split("_")[2])
        context.user_data['target_slot'] = slot
        text = (
            f"📤 <b>رفع الملف للبوت رقم {slot}:</b>\n\n"
            f"قم بإرسال ملف البوت (<code>.py</code>) مباشرة في الشات وسأقوم بتشغيله وحمايته في الخانة ({slot})."
        )
        keyboard = [[InlineKeyboardButton("🔙 العودة لاختيار خانة", callback_data="upload_bot")]]

    elif query.data == "my_bots":
        uploaded_count = 0
        details_text = ""
        db = load_db()

        for slot in range(1, MAX_BOTS + 1):
            user_file = os.path.join(USER_BOTS_DIR, str(user_id), f"bot_{slot}", "main.py")
            has_file = os.path.exists(user_file)
            
            if has_file:
                uploaded_count += 1
                proc_key = f"{user_id}_{slot}"
                is_running = proc_key in running_processes and running_processes[proc_key].poll() is None
                status = "🟢 شغال (24/7 محمي)" if is_running else "🔴 متوقف"
                bot_name, bot_username, _ = await get_hosted_bot_info(user_file)
                details_text += (
                    f"🤖 <b>بوت {slot}:</b> {bot_name} ({bot_username})\n"
                    f"⚡ <b>الحالة:</b> {status}\n"
                    "----------------------------------\n"
                )
            else:
                details_text += f"🤖 <b>بوت {slot}:</b> ⚪ فارغ\n----------------------------------\n"

        text = (
            f"📊 <b>قائمة وإحصائيات بوتاتك:</b>\n\n"
            f"🔢 <b>عدد البوتات المرفوعة:</b> {uploaded_count}/{MAX_BOTS}\n"
            "━━━━━━━━━━━━━━━━━━\n"
            f"{details_text}"
        )
        keyboard = [
            [InlineKeyboardButton("⚙️ إعدادات والتحكم بالبوتات", callback_data="manage_bots")],
            [InlineKeyboardButton("🚀 رفع بوت جديد", callback_data="upload_bot")],
            [InlineKeyboardButton("🔙 العودة للقائمة الرئيسية", callback_data="main_menu")]
        ]

    elif query.data == "manage_bots":
        text = "⚙️ <b>لوحة التحكم الاحترافية بالبوتات:</b>\n\nاختر البوت الذي تريد التحكم به:"
        keyboard = []
        for slot in range(1, MAX_BOTS + 1):
            user_file = os.path.join(USER_BOTS_DIR, str(user_id), f"bot_{slot}", "main.py")
            has_file = os.path.exists(user_file)
            proc_key = f"{user_id}_{slot}"
            is_running = proc_key in running_processes and running_processes[proc_key].poll() is None
            
            status_text = "🟢 شغال" if is_running else ("🔴 متوقف" if has_file else "⚪ فارغ")
            keyboard.append([InlineKeyboardButton(f"🤖 بوت رقم {slot} [{status_text}]", callback_data=f"manage_slot_{slot}")])

        keyboard.append([InlineKeyboardButton("🔙 العودة للقائمة الرئيسية", callback_data="main_menu")])

    elif query.data.startswith("manage_slot_"):
        slot = int(query.data.split("_")[2])
        user_folder = os.path.abspath(os.path.join(USER_BOTS_DIR, str(user_id), f"bot_{slot}"))
        user_file = os.path.join(user_folder, "main.py")
        has_file = os.path.exists(user_file)
        
        proc_key = f"{user_id}_{slot}"
        is_running = proc_key in running_processes and running_processes[proc_key].poll() is None
        status = "🟢 شغال الآن (24/7)" if is_running else ("🔴 متوقف" if has_file else "⚪ لا يوجد بوت مرفوع")

        bot_name, bot_username = ("غير معروف", "غير محدد")
        if has_file:
            bot_name, bot_username, _ = await get_hosted_bot_info(user_file)

        text = (
            f"⚙️ <b>لوحة التحكم - البوت رقم {slot}:</b>\n\n"
            f"🤖 <b>اسم البوت:</b> {bot_name}\n"
            f"🆔 <b>يوزر البوت:</b> {bot_username}\n"
            f"📊 <b>حالة البوت:</b> {status}\n"
            f"📁 <b>الملف:</b> <code>main.py</code>\n\n"
            "اختر الإجراء المطلوب من الأزرار أدناه:"
        )

        keyboard = []
        if is_running:
            keyboard.append([InlineKeyboardButton("🛑 إيقاف البوت", callback_data=f"stop_bot_{slot}")])
        elif has_file:
            keyboard.append([InlineKeyboardButton("▶️ تشغيل البوت", callback_data=f"run_bot_{slot}")])

        if has_file:
            keyboard.append([
                InlineKeyboardButton("✏️ تعديل / رفع كود جديد", callback_data=f"select_upload_{slot}"),
                InlineKeyboardButton("🔄 إعادة ضبط / حذف", callback_data=f"reset_bot_{slot}")
            ])
        else:
            keyboard.append([InlineKeyboardButton("🚀 رفع بوت جديد", callback_data=f"select_upload_{slot}")])

        keyboard.append([InlineKeyboardButton("🔙 قائمة التحكم بالبوتات", callback_data="manage_bots")])

    elif query.data.startswith("stop_bot_"):
        slot = int(query.data.split("_")[2])
        await stop_hosted_bot(user_id, slot)
        text = f"🛑 <b>تم إيقاف البوت رقم {slot} وتفريغ الذاكرة بنجاح!</b>"
        keyboard = [[InlineKeyboardButton("⚙️ العودة للوحة التحكم", callback_data=f"manage_slot_{slot}")]]

    elif query.data.startswith("run_bot_"):
        slot = int(query.data.split("_")[2])
        success = await start_hosted_bot(user_id, slot)
        if success:
            text = f"🚀 <b>تم تشغيل البوت رقم {slot} بنجاح!</b>"
        else:
            text = f"⚠️ لم تقم برفع أي ملف للبوت رقم {slot} سابقاً."
        keyboard = [[InlineKeyboardButton("⚙️ العودة للوحة التحكم", callback_data=f"manage_slot_{slot}")]]

    elif query.data.startswith("reset_bot_"):
        slot = int(query.data.split("_")[2])
        await stop_hosted_bot(user_id, slot)

        user_folder = os.path.abspath(os.path.join(USER_BOTS_DIR, str(user_id), f"bot_{slot}"))
        if os.path.exists(user_folder):
            shutil.rmtree(user_folder)

        text = f"🔄 <b>تمت إعادة ضبط البوت رقم {slot} وحذف الملفات المرفوعة بنجاح!</b>"
        keyboard = [
            [InlineKeyboardButton("🚀 رفع بوت جديد", callback_data=f"select_upload_{slot}")],
            [InlineKeyboardButton("🔙 القائمة الرئيسية", callback_data="main_menu")]
        ]

    elif query.data == "support":
        text = (
            "👨‍💻 <b>الدعم الفني:</b>\n\n"
            "لأي استفسار أو مشكلة، يمكنك التواصل مع المطور مباشرة عبر اليوزر:\n"
            "@v1_ew"
        )
        keyboard = [
            [InlineKeyboardButton("💬 مراسلة الدعم الفني", url="https://t.me/v1_ew")],
            [InlineKeyboardButton("🔙 العودة للقائمة الرئيسية", callback_data="main_menu")]
        ]

    elif query.data == "main_menu":
        await query.edit_message_text(WELCOME_TEXT, reply_markup=main_menu_keyboard(), parse_mode="HTML")
        return

    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="HTML")

# --- تهيئة الاستعادة والبدء عند تشغيل السيرفر ---
async def post_init(app: Application):
    # تشغيل حلقة المراقبة في الخلفية
    asyncio.create_task(bot_monitor_loop())
    
    # استعادة تشغيل جميع البوتات التي كانت تعمل قبل إعادة تشغيل السيرفر
    db = load_db()
    for user_id_str, slots in db.items():
        for slot_str, info in slots.items():
            if info.get("running", False):
                await start_hosted_bot(int(user_id_str), int(slot_str))

def main():
    app = Application.builder().token(TOKEN).post_init(post_init).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_click))
    app.add_handler(MessageHandler(filters.Document.ALL, handle_document))

    print("⚡ بوت الاستضافة القوي يعمل الآن مع دعم المراقبة التلقائية 24/7...")
    app.run_polling()

if __name__ == "__main__":
    main()