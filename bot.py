import os
import json
import subprocess
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton


API_TOKEN ="8782381961:AAHIhHGlQbBuRMMWSLbZxo5XzvojJQp9oO8"
bot = telebot.TeleBot(API_TOKEN)

# بيئة تخزين الملفات المستضافة وملف الحفظ
hosted_bots = {}
DATA_FILE = "hosted_bots.json"

# بيانات التوقيع والدعم الفني
DEV_SIGNATURE = "الـمـطـور لـيـفـاي ⠉⃝ 🇪🇬 ⸙ꠋꠋꠋꠋꠋꠋꠋꠋꠋꠋꠋ 」"
SUPPORT_USERNAME = "v1_ew"
SUPPORT_URL = f"https://t.me/{SUPPORT_USERNAME}"

def save_bots_to_file():
    """حفظ بيانات ملفات الأكواد والمستخدمين في ملف JSON"""
    data_to_save = {}
    for bot_id, info in hosted_bots.items():
        data_to_save[bot_id] = {
            "filename": info["filename"],
            "name": info["name"],
            "id": info["id"],
            "owner_id": info.get("owner_id")
        }
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data_to_save, f, ensure_ascii=False, indent=4)

def load_bots_from_file():
    """استعادة وإعادة تشغيل البوتات المحفوظة عند إعادة تشغيل السيرفر"""
    if not os.path.exists(DATA_FILE):
        return
    
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            saved_data = json.load(f)
            
        for bot_id, info in saved_data.items():
            filename = info["filename"]
            if os.path.exists(filename):
                proc = subprocess.Popen(["python3", filename])
                hosted_bots[bot_id] = {
                    "process": proc,
                    "filename": filename,
                    "name": info["name"],
                    "id": info["id"],
                    "owner_id": info.get("owner_id")
                }
    except Exception as e:
        print(f"خطأ أثناء استعادة الملفات: {e}")

def get_main_keyboard():
    markup = InlineKeyboardMarkup()
    markup.row_width = 2
    
    btn_add = InlineKeyboardButton("📤 رفع ملف", callback_data="add_bot")
    btn_manage = InlineKeyboardButton("⚙️ البوتات الشغالة", callback_data="manage_bots")
    btn_stats = InlineKeyboardButton("📊 إحصائيات السيرفر", callback_data="stats")
    btn_info = InlineKeyboardButton("ℹ️ عن الاستضافة", callback_data="info")
    btn_support = InlineKeyboardButton("💬 الدعم الفني المباشر", url=SUPPORT_URL)
    
    markup.add(btn_add, btn_manage)
    markup.add(btn_stats, btn_info)
    markup.add(btn_support)
    return markup

@bot.message_handler(commands=['start'])
def start_command(message):
    welcome_text = (
        f"<b>𝗪𝗘𝗟𝗖𝗢𝗠𝗘 𝗧𝗢 𝗟𝗘𝗩𝗜 𝗠𝗢𝗗</b>\n"
        f"<code>{DEV_SIGNATURE}</code>\n\n"
        f"مرحباً بك في منصة استضافة وتشغيل البوتات 24/7.\n"
        f"قم برفع ملف البوت الخاص بك وسيعمل بتصميمه وكوده الأصلي دون أي تعديل أو تدخل:"
    )
    bot.send_message(
        message.chat.id,
        welcome_text,
        parse_mode="HTML",
        reply_markup=get_main_keyboard()
    )

@bot.callback_query_handler(func=lambda call: True)
def handle_callbacks(call):
    chat_id = call.message.chat.id
    data = call.data

    # --- القائمة الرئيسية ---
    if data == "main_menu":
        welcome_text = (
            f"<b>𝗪𝗘𝗟𝗖𝗢𝗠𝗘 𝗧𝗢 𝗟𝗘𝗩𝗜 𝗠𝗢𝗗</b>\n"
            f"<code>{DEV_SIGNATURE}</code>\n\n"
            f"اللوحة الرئيسية للتحكم في الاستضافة:"
        )
        bot.edit_message_text(
            chat_id=chat_id,
            message_id=call.message.message_id,
            text=welcome_text,
            parse_mode="HTML",
            reply_markup=get_main_keyboard()
        )

    # --- طلب رفع ملف ---
    elif data == "add_bot":
        msg = bot.send_message(
            chat_id, 
            "<b>أرسل ملف الكود بصيغة (<code>.py</code>) الآن ليتم استضافته وتشغيله 24/7:</b>",
            parse_mode="HTML"
        )
        bot.register_next_step_handler(msg, process_add_file)

    # --- عرض البوتات الشغالة الخاصة بالمسخدم فقط ---
    elif data == "manage_bots":
        user_bots = {k: v for k, v in hosted_bots.items() if v.get("owner_id") == chat_id}

        if not user_bots:
            markup = InlineKeyboardMarkup()
            markup.add(InlineKeyboardButton("🔙 العودة للقائمة الرئيسية", callback_data="main_menu"))
            bot.edit_message_text(
                chat_id=chat_id,
                message_id=call.message.message_id,
                text="⚠️ <b>لا توجد لديك بوتات مستضافة حالياً.</b>",
                parse_mode="HTML",
                reply_markup=markup
            )
        else:
            markup = InlineKeyboardMarkup()
            for bot_id, info in user_bots.items():
                btn_text = f"🤖 {info['name']}"
                markup.add(InlineKeyboardButton(btn_text, callback_data=f"bot_menu_{bot_id}"))
            
            markup.add(InlineKeyboardButton("🔙 العودة للقائمة الرئيسية", callback_data="main_menu"))
            bot.edit_message_text(
                chat_id=chat_id,
                message_id=call.message.message_id,
                text="<b>📌 البوتات الخاصة بك والمستضافة حالياً:</b>",
                parse_mode="HTML",
                reply_markup=markup
            )

    # --- لوحة التحكم الخاصة ببوت معين ---
    elif data.startswith("bot_menu_"):
        bot_id = data.split("bot_menu_")[1]
        target_info = hosted_bots.get(bot_id)

        if not target_info or target_info.get("owner_id") != chat_id:
            bot.answer_callback_query(call.id, "❌ البوت غير موجود أو لا تملك صلاحية عليه.")
            return

        status_str = "🟢 شغال" if target_info["process"].poll() is None else "🔴 متوقف"
        
        text = (
            f"<b>🎮 لوحة تحكم البوت:</b>\n\n"
            f"• <b>اسم الملف:</b> <code>{target_info['name']}</code>\n"
            f"• <b>المعرف ID:</b> <code>{target_info['id']}</code>\n"
            f"• <b>الحالة:</b> {status_str}\n\n"
            f"<code>{DEV_SIGNATURE}</code>"
        )

        markup = InlineKeyboardMarkup()
        markup.row_width = 2
        markup.add(
            InlineKeyboardButton("🔄 إعادة تشغيل", callback_data=f"restart_{bot_id}"),
            InlineKeyboardButton("🛑 إيقاف البوت", callback_data=f"stop_{bot_id}")
        )
        markup.add(
            InlineKeyboardButton("🗑 مسح البوت نهائياً", callback_data=f"delete_{bot_id}")
        )
        markup.add(
            InlineKeyboardButton("🔙 العودة لقائمة البوتات", callback_data="manage_bots")
        )

        bot.edit_message_text(
            chat_id=chat_id,
            message_id=call.message.message_id,
            text=text,
            parse_mode="HTML",
            reply_markup=markup
        )

    # --- إيقاف بوت ---
    elif data.startswith("stop_"):
        bot_id = data.split("stop_")[1]
        info = hosted_bots.get(bot_id)

        if info and info.get("owner_id") == chat_id:
            if info["process"].poll() is None:
                info["process"].terminate()
                bot.answer_callback_query(call.id, "✅ تم إيقاف تشغيل البوت!")
            else:
                bot.answer_callback_query(call.id, "⚠️ البوت متوقف بالفعل.")
            handle_callbacks(type('obj', (object,), {'message': call.message, 'data': f"bot_menu_{bot_id}", 'id': call.id}))

    # --- إعادة تشغيل بوت ---
    elif data.startswith("restart_"):
        bot_id = data.split("restart_")[1]
        info = hosted_bots.get(bot_id)

        if info and info.get("owner_id") == chat_id:
            if info["process"].poll() is None:
                info["process"].terminate()
            
            proc = subprocess.Popen(["python3", info["filename"]])
            info["process"] = proc
            bot.answer_callback_query(call.id, "🔄 تم إعادة تشغيل البوت بنجاح!")
            handle_callbacks(type('obj', (object,), {'message': call.message, 'data': f"bot_menu_{bot_id}", 'id': call.id}))

    # --- مسح البوت نهائياً ---
    elif data.startswith("delete_"):
        bot_id = data.split("delete_")[1]
        info = hosted_bots.get(bot_id)

        if info and info.get("owner_id") == chat_id:
            if info["process"].poll() is None:
                info["process"].terminate()

            if os.path.exists(info["filename"]):
                os.remove(info["filename"])

            del hosted_bots[bot_id]
            save_bots_to_file()
            bot.answer_callback_query(call.id, "🗑 تم مسح البوت وملفاته بالكامل!")
            handle_callbacks(type('obj', (object,), {'message': call.message, 'data': "manage_bots", 'id': call.id}))

    # --- إحصائيات النظام ---
    elif data == "stats":
        user_active = sum(1 for b in hosted_bots.values() if b.get("owner_id") == chat_id and b["process"].poll() is None)
        user_total = sum(1 for b in hosted_bots.values() if b.get("owner_id") == chat_id)
        
        stats_text = (
            f"<b>📊 إحصائيات الاستضافة الخاصة بك:</b>\n\n"
            f"• إجمالي بوتاتك المستضافة: <b>{user_total}</b>\n"
            f"• بوتاتك النشطة حالياً: <b>{user_active}</b> 🟢\n"
            f"• بوتاتك المتوقفة: <b>{user_total - user_active}</b> 🔴\n\n"
            f"<code>{DEV_SIGNATURE}</code>"
        )
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("🔙 العودة للقائمة الرئيسية", callback_data="main_menu"))
        bot.edit_message_text(
            chat_id=chat_id,
            message_id=call.message.message_id,
            text=stats_text,
            parse_mode="HTML",
            reply_markup=markup
        )

    # --- معلومات الاستضافة ---
    elif data == "info":
        info_text = (
            f"<b>ℹ️ معلومات الاستضافة (LEVI MOD):</b>\n\n"
            f"• يتم تشغيل ملف الكود الخاص بك بشكل مستقل تماماً 24/7 ودون أي تعديل على تصميمه أو وظائفه.\n"
            f"• خصوصية كاملة: لا يظهر بوتك أو ملفاتك لأي مستخدم آخر.\n"
            f"• تحكم كامل (إعادة تشغيل / إيقاف / حذف) من اللوحة الخاصة بك في أي وقت.\n\n"
            f"<code>{DEV_SIGNATURE}</code>"
        )
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("💬 الدعم الفني", url=SUPPORT_URL))
        markup.add(InlineKeyboardButton("🔙 العودة", callback_data="main_menu"))
        bot.edit_message_text(
            chat_id=chat_id,
            message_id=call.message.message_id,
            text=info_text,
            parse_mode="HTML",
            reply_markup=markup
        )

def process_add_file(message):
    chat_id = message.chat.id

    if not message.document or not message.document.file_name.endswith('.py'):
        bot.send_message(
            chat_id,
            "❌ <b>عذراً، يجب إرسال ملف بايثون يحتوي على الامتداد (<code>.py</code>) فقط!</b>",
            parse_mode="HTML",
            reply_markup=get_main_keyboard()
        )
        return

    try:
        doc = message.document
        file_info = bot.get_file(doc.file_id)
        downloaded_file = bot.download_file(file_info.file_path)

        bot_id = doc.file_id[:10]
        safe_filename = f"user_{chat_id}_bot_{bot_id}_{doc.file_name}"

        with open(safe_filename, 'wb') as new_file:
            new_file.write(downloaded_file)

        proc = subprocess.Popen(["python3", safe_filename])

        hosted_bots[bot_id] = {
            "process": proc,
            "filename": safe_filename,
            "name": doc.file_name,
            "id": bot_id,
            "owner_id": chat_id
        }

        save_bots_to_file()

        bot.send_message(
            chat_id,
            f"✅ <b>تم استضافة وتفعيل البوت بنجاح!</b>\n\n"
            f"• <b>اسم الملف:</b> <code>{doc.file_name}</code>\n"
            f"• <b>الحالة:</b> يعمل الآن 24/7 بتصميمه الأصلي ⚡\n\n"
            f"<code>{DEV_SIGNATURE}</code>",
            parse_mode="HTML",
            reply_markup=get_main_keyboard()
        )

    except Exception as e:
        bot.send_message(
            chat_id,
            f"❌ <b>فشل تشغيل ملف الكود!</b>\n<code>الخطأ: {str(e)}</code>",
            parse_mode="HTML",
            reply_markup=get_main_keyboard()
        )

if __name__ == "__main__":
    print("جاري استعادة البوتات المحفوظة...")
    load_bots_from_file()
    print("LEVI MOD Hosting Server is fully active...")
    bot.infinity_polling()
