from datetime import datetime
import os
import shutil
import subprocess
import sys
import threading
import time
import zipfile
from flask import Flask, jsonify, render_template_string, request

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 64 * 1024 * 1024  # 64MB Max Upload

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BOTS_DIR = os.path.join(BASE_DIR, 'bots_storage')
LOGS_DIR = os.path.join(BASE_DIR, 'logs_storage')
os.makedirs(BOTS_DIR, exist_ok=True)
os.makedirs(LOGS_DIR, exist_ok=True)

running_processes = {}
installing_deps = {}

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ar" dir="rtl" class="dark">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>LEVI CLOUD | Cyber Core v5.0</title>
    
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">
    <link href="https://fonts.googleapis.com/css2?family=Tajawal:wght@400;600;800;900&family=JetBrains+Mono:wght@400;600;800&display=swap" rel="stylesheet">
    
    <script>
        tailwind.config = {
            darkMode: 'class',
            theme: {
                extend: {
                    colors: {
                        cyber: {
                            bg: '#030712',
                            card: 'rgba(15, 23, 42, 0.75)',
                            border: 'rgba(255, 255, 255, 0.08)',
                            neonCyan: '#00f2fe',
                            neonPurple: '#a855f7',
                            neonGreen: '#10b981',
                            neonAmber: '#f59e0b',
                            neonRed: '#ef4444'
                        }
                    },
                    fontFamily: {
                        sans: ['Tajawal', 'sans-serif'],
                        mono: ['JetBrains Mono', 'monospace']
                    }
                }
            }
        }
    </script>
    
    <style>
        body {
            background-color: #030712;
            background-image: 
                radial-gradient(at 0% 0%, rgba(0, 242, 254, 0.1) 0px, transparent 50%),
                radial-gradient(at 100% 100%, rgba(168, 85, 247, 0.1) 0px, transparent 50%);
            background-attachment: fixed;
            -webkit-tap-highlight-color: transparent;
        }
        
        .glass-card {
            background: rgba(15, 23, 42, 0.7);
            backdrop-filter: blur(20px);
            -webkit-backdrop-filter: blur(20px);
            border: 1px solid rgba(255, 255, 255, 0.08);
        }
        
        .cyber-glow-cyan { box-shadow: 0 0 25px rgba(0, 242, 254, 0.25); }
        .cyber-glow-green { box-shadow: 0 0 25px rgba(16, 185, 129, 0.25); }
        
        ::-webkit-scrollbar { width: 4px; height: 4px; }
        ::-webkit-scrollbar-track { background: #030712; }
        ::-webkit-scrollbar-thumb { background: #1e293b; border-radius: 10px; }
    </style>
</head>
<body class="text-slate-100 font-sans min-h-screen pb-24 md:pb-8 select-none">

    <!-- Top Header -->
    <header class="sticky top-0 z-40 glass-card border-b border-slate-800/80 px-4 py-3.5 mb-6">
        <div class="max-w-6xl mx-auto flex items-center justify-between">
            <div class="flex items-center gap-3">
                <div class="w-10 h-10 rounded-2xl bg-gradient-to-tr from-cyan-500 via-indigo-500 to-purple-600 p-0.5 cyber-glow-cyan">
                    <div class="w-full h-full bg-slate-950 rounded-[14px] flex items-center justify-center">
                        <i class="fa-solid fa-server text-cyan-400 text-lg"></i>
                    </div>
                </div>
                <div>
                    <div class="flex items-center gap-2">
                        <h1 class="text-lg font-black tracking-wider bg-clip-text text-transparent bg-gradient-to-r from-cyan-400 via-indigo-300 to-purple-400">LEVI CORE</h1>
                        <span class="text-[10px] px-2 py-0.5 rounded-md font-mono bg-cyan-500/10 text-cyan-400 border border-cyan-500/20 font-bold">v5.0 Pro</span>
                    </div>
                    <p class="text-[11px] text-slate-400">سيرفر الاستضافة المستقل لجميع البوتات والمكتبات</p>
                </div>
            </div>

            <div class="flex items-center gap-2">
                <div class="flex items-center gap-2 px-3 py-1.5 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-xs font-bold">
                    <span class="w-2 h-2 rounded-full bg-emerald-400 animate-ping"></span>
                    <span class="hidden sm:inline">السيرفر</span> نشط 24/7
                </div>
            </div>
        </div>
    </header>

    <!-- Main Container -->
    <main class="max-w-6xl mx-auto px-4 space-y-6">

        <!-- Metrics Cards -->
        <div class="grid grid-cols-2 md:grid-cols-4 gap-3">
            <div class="glass-card p-4 rounded-2xl">
                <div class="flex items-center justify-between mb-2">
                    <span class="text-xs font-medium text-slate-400">البوتات النشطة</span>
                    <i class="fa-solid fa-bolt text-emerald-400 text-sm"></i>
                </div>
                <div class="flex items-baseline gap-2">
                    <span id="statActiveBots" class="text-2xl font-black font-mono text-emerald-400">0</span>
                    <span class="text-[10px] text-slate-500">من أصل <span id="statTotalBots" class="font-mono">0</span></span>
                </div>
            </div>

            <div class="glass-card p-4 rounded-2xl">
                <div class="flex items-center justify-between mb-2">
                    <span class="text-xs font-medium text-slate-400">دعم المكتبات</span>
                    <i class="fa-solid fa-cubes text-cyan-400 text-sm"></i>
                </div>
                <div class="flex items-baseline gap-2">
                    <span class="text-sm font-bold font-mono text-cyan-400">requirements.txt</span>
                </div>
            </div>

            <div class="glass-card p-4 rounded-2xl">
                <div class="flex items-center justify-between mb-2">
                    <span class="text-xs font-medium text-slate-400">المحرك الأساسي</span>
                    <i class="fa-brands fa-python text-purple-400 text-sm"></i>
                </div>
                <div class="flex items-baseline gap-2">
                    <span class="text-sm font-bold font-mono text-purple-400">Python 3.11+</span>
                </div>
            </div>

            <div class="glass-card p-4 rounded-2xl">
                <div class="flex items-center justify-between mb-2">
                    <span class="text-xs font-medium text-slate-400">مدة التشغيل</span>
                    <i class="fa-solid fa-stopwatch text-amber-400 text-sm"></i>
                </div>
                <div class="flex items-baseline gap-2">
                    <span id="statUptime" class="text-sm font-bold font-mono text-amber-400">00:00:00</span>
                </div>
            </div>
        </div>

        <!-- Upload Dropzone -->
        <section class="glass-card p-5 rounded-3xl space-y-4">
            <div class="flex items-center gap-2">
                <i class="fa-solid fa-cloud-arrow-up text-cyan-400"></i>
                <h2 class="text-sm font-bold text-slate-200">رفع بوت جديد (.py أو أرشيف .zip)</h2>
            </div>
            
            <form id="uploadForm" class="space-y-3">
                <label for="botFile" class="flex flex-col items-center justify-center w-full h-32 border-2 border-dashed border-slate-700 hover:border-cyan-500/50 rounded-2xl cursor-pointer bg-slate-950/40 transition-all">
                    <div class="flex flex-col items-center justify-center pt-5 pb-6">
                        <i class="fa-solid fa-file-arrow-up text-3xl text-slate-400 mb-2"></i>
                        <p id="fileNameDisplay" class="text-xs text-slate-300 font-medium px-2 text-center">
                            ارفع كود (.py) أو مجلد مضغوط (.zip) يحتوي على requirements.txt و main.py
                        </p>
                    </div>
                    <input type="file" id="botFile" accept=".py,.zip" class="hidden" onchange="updateFileName(this)" />
                </label>

                <button type="submit" id="btnUpload" 
                        class="w-full bg-gradient-to-r from-cyan-500 via-indigo-600 to-purple-600 hover:opacity-95 text-slate-950 font-black py-3.5 rounded-2xl flex items-center justify-center gap-2 text-sm transition-all cyber-glow-cyan active:scale-[0.98]">
                    <i class="fa-solid fa-rocket text-base"></i>
                    <span>رفع ونشر المشروع</span>
                </button>
            </form>
        </section>

        <!-- Bot Management List -->
        <section class="glass-card p-5 rounded-3xl space-y-4">
            <div class="flex items-center justify-between border-b border-slate-800/80 pb-3">
                <div class="flex items-center gap-2">
                    <i class="fa-solid fa-layer-group text-indigo-400"></i>
                    <h2 class="text-sm font-bold text-slate-200">مشاريع البوتات المتاحة</h2>
                </div>
                <button onclick="fetchBots()" class="p-2 rounded-xl bg-slate-900 border border-slate-800 text-slate-400 hover:text-white active:rotate-180 transition-all">
                    <i class="fa-solid fa-arrows-rotate text-xs"></i>
                </button>
            </div>

            <div id="botsContainer" class="space-y-3">
                <!-- Dynamic Content -->
            </div>
        </section>
    </main>

    <!-- Mobile Bottom Navigation -->
    <div class="md:hidden fixed bottom-0 left-0 right-0 glass-card border-t border-slate-800/80 px-6 py-2.5 z-40 flex justify-around items-center">
        <button onclick="window.scrollTo({top: 0, behavior: 'smooth'})" class="flex flex-col items-center gap-1 text-cyan-400">
            <i class="fa-solid fa-house-laptop text-lg"></i>
            <span class="text-[10px] font-bold">الرئيسية</span>
        </button>
        <button onclick="document.getElementById('uploadForm').scrollIntoView({behavior: 'smooth'})" class="flex flex-col items-center gap-1 text-slate-400 hover:text-cyan-400">
            <i class="fa-solid fa-cloud-arrow-up text-lg"></i>
            <span class="text-[10px]">رفع المشروع</span>
        </button>
        <button onclick="fetchBots()" class="flex flex-col items-center gap-1 text-slate-400 hover:text-cyan-400">
            <i class="fa-solid fa-list-check text-lg"></i>
            <span class="text-[10px]">البوتات</span>
        </button>
    </div>

    <!-- Live Terminal Console Modal -->
    <div id="logModal" class="fixed inset-0 bg-slate-950/90 backdrop-blur-xl z-50 hidden flex items-center justify-center p-3">
        <div class="bg-slate-950 w-full max-w-3xl h-[85vh] rounded-3xl border border-slate-800 flex flex-col shadow-2xl overflow-hidden">
            <div class="bg-slate-900/90 px-4 py-3 border-b border-slate-800 flex justify-between items-center">
                <div class="flex items-center gap-2">
                    <span class="w-3 h-3 rounded-full bg-cyan-400 animate-pulse"></span>
                    <span id="logModalTitle" class="text-xs font-mono font-bold text-slate-200">Console</span>
                </div>
                <button onclick="closeLogModal()" class="w-8 h-8 rounded-full bg-slate-800 text-slate-400 hover:text-white flex items-center justify-center">
                    <i class="fa-solid fa-xmark"></i>
                </button>
            </div>
            <div id="logContent" class="p-4 flex-grow overflow-y-auto font-mono text-xs text-emerald-400 bg-slate-950/90 leading-relaxed whitespace-pre-wrap">
                [SYSTEM] جاري الاتصال بالسجلات المباشرة...
            </div>
            <div class="bg-slate-900/90 px-4 py-3 border-t border-slate-800 flex justify-between items-center">
                <span class="text-[10px] text-slate-500">تحديث تلقائي كل 3 ثوانٍ</span>
                <button onclick="clearLogWindow()" class="text-xs bg-slate-800 px-3 py-1.5 rounded-xl text-slate-300">
                    مسح الشاشة
                </button>
            </div>
        </div>
    </div>

    {% raw %}
    <script>
        let currentActiveLogFile = null;
        let logInterval = null;

        function updateFileName(input) {
            const fileNameDisplay = document.getElementById('fileNameDisplay');
            if (input.files && input.files[0]) {
                fileNameDisplay.innerText = "تم اختيار: " + input.files[0].name;
                fileNameDisplay.classList.add('text-cyan-400', 'font-bold');
            }
        }

        async function fetchBots() {
            try {
                const res = await fetch('/api/bots');
                const data = await res.json();
                
                document.getElementById('statActiveBots').innerText = data.filter(b => b.status === 'running').length;
                document.getElementById('statTotalBots').innerText = data.length;

                const container = document.getElementById('botsContainer');
                if (data.length === 0) {
                    container.innerHTML = `
                        <div class="text-center py-10 text-slate-500">
                            <i class="fa-solid fa-box-open text-3xl mb-2 block opacity-30"></i>
                            لا توجد أي بوتات مرفوعة حالياً.
                        </div>`;
                    return;
                }

                container.innerHTML = '';
                data.forEach(bot => {
                    const isRunning = bot.status === 'running';
                    const isInstalling = bot.status === 'installing';
                    
                    let statusBadge = `<span class="px-2.5 py-1 rounded-full text-[10px] font-bold bg-red-500/10 text-red-400 border border-red-500/20">○ متوقف</span>`;
                    if(isRunning) {
                        statusBadge = `<span class="px-2.5 py-1 rounded-full text-[10px] font-bold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">● شغال</span>`;
                    } else if(isInstalling) {
                        statusBadge = `<span class="px-2.5 py-1 rounded-full text-[10px] font-bold bg-amber-500/10 text-amber-400 border border-amber-500/20 animate-pulse">⏳ جاري تثبيت المكتبات</span>`;
                    }

                    container.innerHTML += `
                        <div class="bg-slate-900/80 p-4 rounded-2xl border border-slate-800 flex flex-col gap-3">
                            <div class="flex items-center justify-between">
                                <div class="flex items-center gap-3">
                                    <div class="w-10 h-10 rounded-xl ${isRunning ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/30' : 'bg-slate-800 text-slate-500'} flex items-center justify-center text-lg">
                                        <i class="fa-solid fa-robot"></i>
                                    </div>
                                    <div>
                                        <h3 class="font-bold text-slate-100 font-mono text-sm">${bot.name}</h3>
                                        <p class="text-[10px] text-slate-400 font-mono">الملف الرئيسي: ${bot.main_script} ${bot.has_req ? '| 📦 requirements.txt متوفر' : ''}</p>
                                    </div>
                                </div>
                                ${statusBadge}
                            </div>

                            <div class="grid grid-cols-2 sm:grid-cols-5 gap-2 pt-1 border-t border-slate-800/60">
                                ${isRunning 
                                    ? `<button onclick="stopBot('${bot.name}')" class="bg-red-500/10 hover:bg-red-500/20 text-red-400 border border-red-500/20 py-2 rounded-xl text-xs font-bold flex items-center justify-center gap-1">
                                           <i class="fa-solid fa-power-off"></i> إيقاف
                                       </button>
                                       <button onclick="restartBot('${bot.name}')" class="bg-amber-500/10 hover:bg-amber-500/20 text-amber-400 border border-amber-500/20 py-2 rounded-xl text-xs font-bold flex items-center justify-center">
                                           <i class="fa-solid fa-rotate-right"></i> إعادة
                                       </button>`
                                    : `<button onclick="startBot('${bot.name}')" ${isInstalling ? 'disabled' : ''} class="col-span-2 bg-emerald-500/10 hover:bg-emerald-500/20 text-emerald-400 border border-emerald-500/20 py-2 rounded-xl text-xs font-bold flex items-center justify-center gap-1 disabled:opacity-50">
                                           <i class="fa-solid fa-play"></i> تشغيل
                                       </button>`
                                }
                                ${bot.has_req ? 
                                    `<button onclick="installDeps('${bot.name}')" ${isInstalling ? 'disabled' : ''} class="bg-purple-500/10 hover:bg-purple-500/20 text-purple-400 border border-purple-500/20 py-2 rounded-xl text-xs font-bold flex items-center justify-center gap-1 disabled:opacity-50">
                                        <i class="fa-solid fa-download"></i> تثبيت المكتبات
                                    </button>` : ''
                                }
                                <button onclick="openLogModal('${bot.name}')" class="bg-cyan-500/10 hover:bg-cyan-500/20 text-cyan-400 border border-cyan-500/20 py-2 rounded-xl text-xs font-bold flex items-center justify-center gap-1">
                                    <i class="fa-solid fa-terminal"></i> السجل
                                </button>
                                <button onclick="deleteBot('${bot.name}')" class="bg-slate-800 hover:bg-red-500/20 hover:text-red-400 text-slate-400 border border-slate-700 py-2 rounded-xl text-xs font-bold flex items-center justify-center">
                                    <i class="fa-solid fa-trash"></i> حذف
                                </button>
                            </div>
                        </div>`;
                });
            } catch(e) {}
        }

        document.getElementById('uploadForm').onsubmit = async (e) => {
            e.preventDefault();
            const fileInput = document.getElementById('botFile');
            if(!fileInput.files[0]) return;

            const formData = new FormData();
            formData.append('file', fileInput.files[0]);

            const btn = document.getElementById('btnUpload');
            btn.disabled = true;
            btn.innerHTML = '<i class="fa-solid fa-spinner animate-spin"></i> جاري المعالجة والرفع...';

            await fetch('/api/upload', { method: 'POST', body: formData });
            
            fileInput.value = '';
            document.getElementById('fileNameDisplay').innerText = "ارفع كود (.py) أو مجلد مضغوط (.zip) يحتوي على requirements.txt و main.py";
            document.getElementById('fileNameDisplay').classList.remove('text-cyan-400', 'font-bold');
            btn.disabled = false;
            btn.innerHTML = '<i class="fa-solid fa-rocket"></i> <span>رفع ونشر المشروع</span>';
            fetchBots();
        };

        async function startBot(name) { await fetch(`/api/start/${name}`, { method: 'POST' }); fetchBots(); }
        async function stopBot(name) { await fetch(`/api/stop/${name}`, { method: 'POST' }); fetchBots(); }
        async function restartBot(name) { await fetch(`/api/restart/${name}`, { method: 'POST' }); fetchBots(); }
        async function installDeps(name) { 
            alert('بدأ تثبيت مكتبات requirements.txt في الخلفية...');
            await fetch(`/api/install_deps/${name}`, { method: 'POST' }); 
            fetchBots(); 
        }
        async function deleteBot(name) { 
            if(confirm(`هل أنت تأكد من حذف مشروع ${name} بالكامل؟`)) {
                await fetch(`/api/delete/${name}`, { method: 'DELETE' }); 
                fetchBots(); 
            }
        }

        async function openLogModal(name) {
            currentActiveLogFile = name;
            document.getElementById('logModalTitle').innerText = `${name} - Console Output`;
            document.getElementById('logModal').classList.remove('hidden');
            fetchLogs();
            logInterval = setInterval(fetchLogs, 3000);
        }

        function closeLogModal() {
            document.getElementById('logModal').classList.add('hidden');
            if(logInterval) clearInterval(logInterval);
            currentActiveLogFile = null;
        }

        async function fetchLogs() {
            if(!currentActiveLogFile) return;
            const res = await fetch(`/api/logs/${currentActiveLogFile}`);
            const data = await res.json();
            const logBox = document.getElementById('logContent');
            logBox.innerText = data.logs || '[لا توجد سجلات مسجلة]';
            logBox.scrollTop = logBox.scrollHeight;
        }

        function clearLogWindow() {
            document.getElementById('logContent').innerText = '';
        }

        let seconds = 0;
        setInterval(() => {
            seconds++;
            const hrs = String(Math.floor(seconds / 3600)).padStart(2, '0');
            const mins = String(Math.floor((seconds % 3600) / 60)).padStart(2, '0');
            const secs = String(seconds % 60).padStart(2, '0');
            document.getElementById('statUptime').innerText = `${hrs}:${mins}:${secs}`;
        }, 1000);

        fetchBots();
        setInterval(fetchBots, 4000);
    </script>
    {% endraw %}
</body>
</html>
"""


def find_main_script(folder_path):
  candidates = [
      'main.py',
      'bot.py',
      'app.py',
      'index.py',
      'run.py',
      'telegram_bot.py',
  ]
  for c in candidates:
    if os.path.exists(os.path.join(folder_path, c)):
      return c
  files = [f for f in os.listdir(folder_path) if f.endswith('.py')]
  return files[0] if files else None


def run_pip_install(folder_name, req_path, logpath):
  installing_deps[folder_name] = True
  try:
    with open(logpath, 'a', encoding='utf-8') as log_file:
      log_file.write(
          f'\n--- [INSTALLING DEPENDENCIES FOR {folder_name}] ---\n'
      )
      subprocess.run(
          [
              sys.executable,
              '-m',
              'pip',
              'install',
              '--no-cache-dir',
              '-r',
              req_path,
          ],
          stdout=log_file,
          stderr=subprocess.STDOUT,
          check=True,
      )
      log_file.write('\n--- [DEPENDENCIES INSTALLED SUCCESSFULLY] ---\n')
  except Exception as e:
    with open(logpath, 'a', encoding='utf-8') as log_file:
      log_file.write(f'\n[ERROR INSTALLING DEPENDENCIES]: {str(e)}\n')
  finally:
    installing_deps[folder_name] = False


@app.route('/')
def index():
  return render_template_string(HTML_TEMPLATE)


@app.route('/api/bots', methods=['GET'])
def list_bots():
  bot_folders = [
      f
      for f in os.listdir(BOTS_DIR)
      if os.path.isdir(os.path.join(BOTS_DIR, f))
  ]
  status_list = []
  for folder in bot_folders:
    folder_path = os.path.join(BOTS_DIR, folder)
    main_script = find_main_script(folder_path)
    has_req = os.path.exists(os.path.join(folder_path, 'requirements.txt'))

    if installing_deps.get(folder, False):
      status = 'installing'
    elif (
        folder in running_processes
        and running_processes[folder]['proc'].poll() is None
    ):
      status = 'running'
    else:
      status = 'stopped'

    status_list.append({
        'name': folder,
        'status': status,
        'main_script': main_script or 'غير محدد',
        'has_req': has_req,
    })
  return jsonify(status_list)


@app.route('/api/upload', methods=['POST'])
def upload_bot():
  if 'file' not in request.files:
    return jsonify({'error': 'No file uploaded'}), 400
  file = request.files['file']
  if not file or file.filename == '':
    return jsonify({'error': 'Empty filename'}), 400

  filename = file.filename
  if filename.endswith('.zip'):
    folder_name = os.path.splitext(filename)[0]
    target_folder = os.path.join(BOTS_DIR, folder_name)
    os.makedirs(target_folder, exist_ok=True)

    zip_path = os.path.join(target_folder, 'temp.zip')
    file.save(zip_path)
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
      zip_ref.extractall(target_folder)
    os.remove(zip_path)

  elif filename.endswith('.py'):
    folder_name = os.path.splitext(filename)[0]
    target_folder = os.path.join(BOTS_DIR, folder_name)
    os.makedirs(target_folder, exist_ok=True)
    file.save(os.path.join(target_folder, filename))
  else:
    return jsonify({'error': 'الامتداد المسموح به فقط .py أو .zip'}), 400

  req_path = os.path.join(target_folder, 'requirements.txt')
  logpath = os.path.join(LOGS_DIR, f'{folder_name}.log')
  if os.path.exists(req_path):
    threading.Thread(
        target=run_pip_install, args=(folder_name, req_path, logpath)
    ).start()

  return jsonify({'message': 'Uploaded successfully'})


@app.route('/api/install_deps/<folder_name>', methods=['POST'])
def install_dependencies(folder_name):
  target_folder = os.path.join(BOTS_DIR, folder_name)
  req_path = os.path.join(target_folder, 'requirements.txt')
  logpath = os.path.join(LOGS_DIR, f'{folder_name}.log')

  if os.path.exists(req_path):
    threading.Thread(
        target=run_pip_install, args=(folder_name, req_path, logpath)
    ).start()
    return jsonify({'message': 'Installing dependencies...'})
  return jsonify({'error': 'requirements.txt not found'}), 404


@app.route('/api/start/<folder_name>', methods=['POST'])
def start_bot(folder_name):
  target_folder = os.path.join(BOTS_DIR, folder_name)
  main_script = find_main_script(target_folder)
  logpath = os.path.join(LOGS_DIR, f'{folder_name}.log')

  if not main_script:
    return jsonify({'error': 'No main python script found'}), 404

  if (
      folder_name in running_processes
      and running_processes[folder_name]['proc'].poll() is None
  ):
    return jsonify({'message': 'Already running'})

  script_path = os.path.join(target_folder, main_script)
  log_file = open(logpath, 'a', encoding='utf-8')

  proc = subprocess.Popen(
      [sys.executable, script_path],
      cwd=target_folder,
      stdout=log_file,
      stderr=subprocess.STDOUT,
  )

  running_processes[folder_name] = {'proc': proc, 'log_file': log_file}
  return jsonify({'message': 'Started'})


@app.route('/api/stop/<folder_name>', methods=['POST'])
def stop_bot(folder_name):
  if (
      folder_name in running_processes
      and running_processes[folder_name]['proc'].poll() is None
  ):
    running_processes[folder_name]['proc'].terminate()
    try:
      running_processes[folder_name]['proc'].wait(timeout=3)
    except subprocess.TimeoutExpired:
      running_processes[folder_name]['proc'].kill()

    running_processes[folder_name]['log_file'].close()
    del running_processes[folder_name]
    return jsonify({'message': 'Stopped'})
  return jsonify({'error': 'Not running'}), 400


@app.route('/api/restart/<folder_name>', methods=['POST'])
def restart_bot(folder_name):
  stop_bot(folder_name)
  time.sleep(1)
  return start_bot(folder_name)


@app.route('/api/delete/<folder_name>', methods=['DELETE'])
def delete_bot(folder_name):
  stop_bot(folder_name)
  target_folder = os.path.join(BOTS_DIR, folder_name)
  logpath = os.path.join(LOGS_DIR, f'{folder_name}.log')

  if os.path.exists(target_folder):
    shutil.rmtree(target_folder)
  if os.path.exists(logpath):
    os.remove(logpath)

  return jsonify({'message': 'Deleted'})


@app.route('/api/logs/<folder_name>', methods=['GET'])
def get_logs(folder_name):
  logpath = os.path.join(LOGS_DIR, f'{folder_name}.log')
  if os.path.exists(logpath):
    with open(logpath, 'r', encoding='utf-8', errors='ignore') as f:
      content = f.read()[-6000:]
    return jsonify({'logs': content})
  return jsonify({'logs': '[لا توجد سجلات مسجلة حتى الآن]'})


if __name__ == '__main__':
  port = int(os.environ.get('PORT', 8080))
  app.run(host='0.0.0.0', port=port)