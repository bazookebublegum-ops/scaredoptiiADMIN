import os, time, secrets
from datetime import datetime
from functools import wraps
from flask import Flask, request, jsonify, render_template_string
import psycopg
from psycopg.rows import dict_row

app = Flask(__name__)

# ТВОЙ API SECRET И ССЫЛКА НА БАЗУ ДАННЫХ
API_SECRET = "ScaredOPTI_OOT_88SDF76"
DATABASE_URL = os.getenv('DATABASE_URL') 

rate_limit_store = {}
RATE_LIMIT = 30
RATE_WINDOW = 60

# ═══════════════════════════════════════════════
#  ВСЕ КЛЮЧИ (120 штук + OWNER)
# ═══════════════════════════════════════════════
ALL_KEYS = [
    # BASIC (60 ключей)
    ("SCARED-BASIC-0GRF5A4M", "BASIC"), ("SCARED-BASIC-0MVAPYIX", "BASIC"),
    ("SCARED-BASIC-0P55CST0", "BASIC"), ("SCARED-BASIC-0UPJ6X4H", "BASIC"),
    ("SCARED-BASIC-16FYFTFQ", "BASIC"), ("SCARED-BASIC-1KX1H92I", "BASIC"),
    ("SCARED-BASIC-39VA4A62", "BASIC"), ("SCARED-BASIC-3DRANVCN", "BASIC"),
    ("SCARED-BASIC-53AF32WY", "BASIC"), ("SCARED-BASIC-5TCSMO0W", "BASIC"),
    ("SCARED-BASIC-5ZX65IFA", "BASIC"), ("SCARED-BASIC-7BY9KLBA", "BASIC"),
    ("SCARED-BASIC-7F969OL7", "BASIC"), ("SCARED-BASIC-7GIU1GUY", "BASIC"),
    ("SCARED-BASIC-7TWIKDSV", "BASIC"), ("SCARED-BASIC-88050UMG", "BASIC"),
    ("SCARED-BASIC-8I0L9S1Y", "BASIC"), ("SCARED-BASIC-B6U9UEJF", "BASIC"),
    ("SCARED-BASIC-B99CKJZ0", "BASIC"), ("SCARED-BASIC-CAU78JM9", "BASIC"),
    ("SCARED-BASIC-CERGLLHO", "BASIC"), ("SCARED-BASIC-ED1AYH81", "BASIC"),
    ("SCARED-BASIC-EXFSSLHB", "BASIC"), ("SCARED-BASIC-EXGIMMN3", "BASIC"),
    ("SCARED-BASIC-FJSNY16U", "BASIC"), ("SCARED-BASIC-G2SJ4AVQ", "BASIC"),
    ("SCARED-BASIC-G94PU2YO", "BASIC"), ("SCARED-BASIC-GYLFJYWQ", "BASIC"),
    ("SCARED-BASIC-HG9LJYEW", "BASIC"), ("SCARED-BASIC-HO4I7JRF", "BASIC"),
    ("SCARED-BASIC-HYKMDOZE", "BASIC"), ("SCARED-BASIC-I0YY22MP", "BASIC"),
    ("SCARED-BASIC-I2KKGZ7Y", "BASIC"), ("SCARED-BASIC-IDU3649G", "BASIC"),
    ("SCARED-BASIC-IEAR3TKM", "BASIC"), ("SCARED-BASIC-JAP4LKQ7", "BASIC"),
    ("SCARED-BASIC-LGWYVT61", "BASIC"), ("SCARED-BASIC-MHU0TIHC", "BASIC"),
    ("SCARED-BASIC-MRJNU1PJ", "BASIC"), ("SCARED-BASIC-N5YCZ0G2", "BASIC"),
    ("SCARED-BASIC-NHQ0K4N7", "BASIC"), ("SCARED-BASIC-O4TGRRZ6", "BASIC"),
    ("SCARED-BASIC-O6GV9ZJ1", "BASIC"), ("SCARED-BASIC-P3MQPS3O", "BASIC"),
    ("SCARED-BASIC-PMZJME7A", "BASIC"), ("SCARED-BASIC-Q0XE3ZJL", "BASIC"),
    ("SCARED-BASIC-Q60ORSWJ", "BASIC"), ("SCARED-BASIC-SIY657E3", "BASIC"),
    ("SCARED-BASIC-SLSRV5EV", "BASIC"), ("SCARED-BASIC-SPHHRT5Z", "BASIC"),
    ("SCARED-BASIC-TB1YJ3KV", "BASIC"), ("SCARED-BASIC-TFVVX548", "BASIC"),
    ("SCARED-BASIC-U6GB3KOY", "BASIC"), ("SCARED-BASIC-V5Z15U46", "BASIC"),
    ("SCARED-BASIC-V9RPP3FY", "BASIC"), ("SCARED-BASIC-VV7IP3O1", "BASIC"),
    ("SCARED-BASIC-XLZQDCKM", "BASIC"), ("SCARED-BASIC-Z9Q2FXE7", "BASIC"),
    ("SCARED-BASIC-ZIMZNHJR", "BASIC"), ("SCARED-BASIC-ZT0JRIYO", "BASIC"),
    # PREMIUM (60 ключей)
    ("SCARED-PREM-01LEM9O1", "PREM"), ("SCARED-PREM-0FBM2MPP", "PREM"),
    ("SCARED-PREM-107RQOJ1", "PREM"), ("SCARED-PREM-10LN3WBH", "PREM"),
    ("SCARED-PREM-1CKMM6R7", "PREM"), ("SCARED-PREM-1MZIFYIK", "PREM"),
    ("SCARED-PREM-3027OZNN", "PREM"), ("SCARED-PREM-329P0GOA", "PREM"),
    ("SCARED-PREM-3PSYL9FS", "PREM"), ("SCARED-PREM-40YBBXCE", "PREM"),
    ("SCARED-PREM-46XTOAMS", "PREM"), ("SCARED-PREM-4BZPTGJ3", "PREM"),
    ("SCARED-PREM-4J9L0ARQ", "PREM"), ("SCARED-PREM-53HEFPAW", "PREM"),
    ("SCARED-PREM-6BVERWWU", "PREM"), ("SCARED-PREM-6HKXW9S3", "PREM"),
    ("SCARED-PREM-7C9OBUS0", "PREM"), ("SCARED-PREM-AFGB3VQI", "PREM"),
    ("SCARED-PREM-AHAA21MF", "PREM"), ("SCARED-PREM-AJH2HHRE", "PREM"),
    ("SCARED-PREM-CT055VX9", "PREM"), ("SCARED-PREM-EGGURNEY", "PREM"),
    ("SCARED-PREM-F38KD12Z", "PREM"), ("SCARED-PREM-F7U9VNZF", "PREM"),
    ("SCARED-PREM-G3HJ1UBF", "PREM"), ("SCARED-PREM-IIHRFPQV", "PREM"),
    ("SCARED-PREM-JG6G8V42", "PREM"), ("SCARED-PREM-JNCWF97A", "PREM"),
    ("SCARED-PREM-K3SP5MWO", "PREM"), ("SCARED-PREM-KEN8FDS8", "PREM"),
    ("SCARED-PREM-KGVM7TBN", "PREM"), ("SCARED-PREM-KJY3WDUE", "PREM"),
    ("SCARED-PREM-KO68N7SD", "PREM"), ("SCARED-PREM-LL2M2Q5C", "PREM"),
    ("SCARED-PREM-M8Y7FF8O", "PREM"), ("SCARED-PREM-OE53FDZ9", "PREM"),
    ("SCARED-PREM-QSI9HVC5", "PREM"), ("SCARED-PREM-QU6VA5BJ", "PREM"),
    ("SCARED-PREM-SZANYS01", "PREM"), ("SCARED-PREM-TGRWR6TF", "PREM"),
    ("SCARED-PREM-THPZLWMV", "PREM"), ("SCARED-PREM-U5VXE1KR", "PREM"),
    ("SCARED-PREM-UPFODCFH", "PREM"), ("SCARED-PREM-VASUPEW2", "PREM"),
    ("SCARED-PREM-VSKC4FV4", "PREM"), ("SCARED-PREM-VUJBV74K", "PREM"),
    ("SCARED-PREM-VXECK2LR", "PREM"), ("SCARED-PREM-W2JPAW11", "PREM"),
    ("SCARED-PREM-WLJOV9NV", "PREM"), ("SCARED-PREM-X1L9H8TS", "PREM"),
    ("SCARED-PREM-XC27B7YC", "PREM"), ("SCARED-PREM-XEG1S1OD", "PREM"),
    ("SCARED-PREM-XMT2J7HZ", "PREM"), ("SCARED-PREM-XOZ3WSIU", "PREM"),
    ("SCARED-PREM-XWQ28MKC", "PREM"), ("SCARED-PREM-YB2JXI6A", "PREM"),
    ("SCARED-PREM-YJUMV7LT", "PREM"), ("SCARED-PREM-YO2EMVKN", "PREM"),
    ("SCARED-PREM-ZR3SGYI0", "PREM"), ("SCARED-PREM-ZUVBT0RX", "PREM"),
]

OWNER_KEYS = [
    "SCARED-OWNER-GODMODE",
    "SCARED-OWNER-ALPHA01",
    "SCARED-OWNER-BETA002",
    "SCARED-OWNER-DELTA03",
]

def get_db():
    return psycopg.connect(DATABASE_URL, autocommit=True)

def init_db():
    with get_db() as conn:
        with conn.cursor() as cur:
            # Таблица лицензий
            cur.execute('''
                CREATE TABLE IF NOT EXISTS licenses (
                    key TEXT PRIMARY KEY,
                    tier TEXT NOT NULL,
                    status TEXT DEFAULT 'unused',
                    hwid TEXT,
                    activated_at TIMESTAMP,
                    is_active BOOLEAN DEFAULT TRUE
                )
            ''')
            
            # Таблица анонсов
            cur.execute('''
                CREATE TABLE IF NOT EXISTS announcements (
                    id SERIAL PRIMARY KEY,
                    title TEXT NOT NULL,
                    content TEXT NOT NULL,
                    type TEXT DEFAULT 'update',
                    created_at TIMESTAMP DEFAULT NOW(),
                    is_active BOOLEAN DEFAULT TRUE
                )
            ''')
            
            # Таблица юзернеймов
            cur.execute('''
                CREATE TABLE IF NOT EXISTS usernames (
                    username TEXT PRIMARY KEY,
                    hwid TEXT NOT NULL,
                    tier TEXT NOT NULL,
                    display_name TEXT,
                    color TEXT DEFAULT '#ffffff',
                    glow INT DEFAULT 10,
                    created_at TIMESTAMP DEFAULT NOW()
                )
            ''')
            
            # Добавляем все ключи
            for key, tier in ALL_KEYS:
                cur.execute('''
                    INSERT INTO licenses (key, tier, status) 
                    VALUES (%s, %s, 'unused')
                    ON CONFLICT (key) DO NOTHING
                ''', (key, tier))
            
            # Добавляем OWNER ключи
            for key in OWNER_KEYS:
                cur.execute('''
                    INSERT INTO licenses (key, tier, status, is_active) 
                    VALUES (%s, 'OWNER', 'used', TRUE)
                    ON CONFLICT (key) DO NOTHING
                ''', (key,))
                
    print(f"[OK] Database initialized with {len(ALL_KEYS)} keys + {len(OWNER_KEYS)} OWNER keys")

def check_rate_limit(ip):
    current_time = time.time()
    if ip not in rate_limit_store:
        rate_limit_store[ip] = []
    rate_limit_store[ip] = [t for t in rate_limit_store[ip] if current_time - t < RATE_WINDOW]
    if len(rate_limit_store[ip]) >= RATE_LIMIT:
        return False
    rate_limit_store[ip].append(current_time)
    return True

def require_api_secret(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        s = request.headers.get('X-API-Secret')
        if not s or not secrets.compare_digest(s, API_SECRET):
            return jsonify({'status': 'error', 'message': 'Invalid API secret'}), 401
        return f(*args, **kwargs)
    return decorated

# ═══════════════════════════════════════════════
#  АДМИНКА (HTML)
# ═══════════════════════════════════════════════
HTML_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>ScaredOpti Admin</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: Arial, sans-serif; background: linear-gradient(135deg, #1a1a2e, #16213e, #0f3460); color: #fff; padding: 20px; min-height: 100vh; }
        .container { max-width: 1400px; margin: 0 auto; }
        h1 { text-align: center; color: #667eea; margin-bottom: 30px; font-size: 36px; }
        .stats { display: flex; gap: 20px; justify-content: center; flex-wrap: wrap; margin-bottom: 30px; }
        .stat { background: rgba(102, 126, 234, 0.1); padding: 25px 40px; border-radius: 15px; text-align: center; border: 1px solid rgba(102, 126, 234, 0.3); }
        .stat h3 { color: #888; font-size: 12px; margin-bottom: 10px; text-transform: uppercase; }
        .stat .num { font-size: 36px; font-weight: bold; color: #667eea; }
        .filters { display: flex; gap: 10px; justify-content: center; flex-wrap: wrap; margin-bottom: 30px; }
        button { padding: 12px 24px; background: rgba(102, 126, 234, 0.3); border: 1px solid #667eea; border-radius: 8px; color: #fff; cursor: pointer; font-weight: 600; transition: all 0.3s; }
        button:hover, button.active { background: #667eea; transform: translateY(-2px); }
        input { padding: 12px 20px; border-radius: 8px; border: 1px solid rgba(102, 126, 234, 0.3); background: rgba(102, 126, 234, 0.1); color: #fff; width: 300px; outline: none; }
        input::placeholder { color: #666; }
        .keys { display: grid; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); gap: 15px; }
        .key { background: rgba(102, 126, 234, 0.05); padding: 20px; border-radius: 12px; border: 1px solid rgba(102, 126, 234, 0.2); border-left: 4px solid #2ecc71; }
        .key.used { border-left-color: #e74c3c; }
        .key-header { display: flex; justify-content: space-between; margin-bottom: 12px; }
        .key-code { font-family: monospace; font-weight: bold; color: #667eea; font-size: 14px; }
        .tier { padding: 4px 12px; border-radius: 12px; font-size: 11px; background: #667eea; font-weight: bold; }
        .tier.prem { background: #e74c3c; }
        .tier.owner { background: #ffd700; color: #000; }
        .status { display: inline-block; padding: 5px 12px; border-radius: 12px; font-size: 11px; font-weight: bold; margin: 8px 0; text-transform: uppercase; }
        .status.unused { background: #2ecc71; color: #000; }
        .status.used { background: #e74c3c; color: #fff; }
        .info { font-size: 12px; color: #888; margin: 8px 0; }
        .toggle { width: 100%; padding: 10px; margin-top: 12px; border: none; border-radius: 8px; cursor: pointer; font-weight: bold; transition: all 0.3s; }
        .toggle.to-used { background: rgba(231, 76, 60, 0.3); color: #e74c3c; border: 1px solid #e74c3c; }
        .toggle.to-unused { background: rgba(46, 204, 113, 0.3); color: #2ecc71; border: 1px solid #2ecc71; }
        .toggle:hover { transform: translateY(-2px); opacity: 0.9; }
        .error { text-align: center; padding: 60px; color: #e74c3c; font-size: 18px; }
        .loading { text-align: center; padding: 60px; color: #667eea; }
        
        /* Анонсы */
        .announcements-section { margin-top: 40px; padding-top: 30px; border-top: 2px solid rgba(102, 126, 234, 0.3); }
        .announcement-form { background: rgba(102, 126, 234, 0.1); padding: 20px; border-radius: 12px; margin-bottom: 20px; border: 1px solid rgba(102, 126, 234, 0.3); }
        .announcement-form h3 { margin-bottom: 15px; color: #667eea; }
        .announcement-form input, .announcement-form textarea, .announcement-form select { width: 100%; margin-bottom: 10px; padding: 10px; border-radius: 6px; border: 1px solid rgba(102, 126, 234, 0.3); background: rgba(0,0,0,0.3); color: #fff; }
        .announcement-form textarea { min-height: 100px; resize: vertical; }
        .announcement-item { background: rgba(102, 126, 234, 0.05); padding: 15px; border-radius: 10px; margin-bottom: 10px; border-left: 4px solid #667eea; }
        .announcement-item h4 { color: #667eea; margin-bottom: 8px; }
        .announcement-item p { color: #aaa; font-size: 13px; margin-bottom: 8px; }
        .announcement-item .meta { font-size: 11px; color: #666; }
        .delete-btn { background: rgba(231, 76, 60, 0.3); color: #e74c3c; border: 1px solid #e74c3c; padding: 5px 12px; border-radius: 6px; cursor: pointer; font-size: 11px; }
        .delete-btn:hover { background: #e74c3c; color: #fff; }
        
        /* Юзернеймы */
        .usernames-section { margin-top: 40px; padding-top: 30px; border-top: 2px solid rgba(102, 126, 234, 0.3); }
        .username-item { background: rgba(102, 126, 234, 0.05); padding: 15px; border-radius: 10px; margin-bottom: 10px; border-left: 4px solid #ffa502; display: flex; justify-content: space-between; align-items: center; }
        .username-info h4 { color: #ffa502; margin-bottom: 5px; }
        .username-info p { color: #aaa; font-size: 12px; }
        .ban-btn { background: rgba(231, 76, 60, 0.3); color: #e74c3c; border: 1px solid #e74c3c; padding: 5px 12px; border-radius: 6px; cursor: pointer; font-size: 11px; }
        .ban-btn:hover { background: #e74c3c; color: #fff; }
    </style>
</head>
<body>
    <div class="container">
        <h1>ScaredOpti Admin Panel</h1>
        <div class="stats">
            <div class="stat"><h3>Total</h3><div class="num" id="total">0</div></div>
            <div class="stat"><h3>Used</h3><div class="num" id="used">0</div></div>
            <div class="stat"><h3>Unused</h3><div class="num" id="unused">0</div></div>
            <div class="stat"><h3>Basic</h3><div class="num" id="basic">0</div></div>
            <div class="stat"><h3>Premium</h3><div class="num" id="prem">0</div></div>
            <div class="stat"><h3>Owner</h3><div class="num" id="owner">0</div></div>
            <div class="stat"><h3>Usernames</h3><div class="num" id="usernames-count">0</div></div>
        </div>
        <div class="filters">
            <button onclick="setFilter('all')" id="btn-all" class="active">All</button>
            <button onclick="setFilter('used')" id="btn-used">Used</button>
            <button onclick="setFilter('unused')" id="btn-unused">Unused</button>
            <button onclick="setFilter('basic')" id="btn-basic">Basic</button>
            <button onclick="setFilter('prem')" id="btn-prem">Premium</button>
            <button onclick="setFilter('owner')" id="btn-owner">Owner</button>
            <input type="text" id="search" placeholder="Search keys..." onkeyup="render()">
        </div>
        <div id="keys" class="keys"><div class="loading">Loading keys...</div></div>
        
        <!-- АНОНСЫ -->
        <div class="announcements-section">
            <h2 style="text-align:center; color:#667eea; margin-bottom:20px">Announcements Management</h2>
            <div class="announcement-form">
                <h3>Create New Announcement</h3>
                <input type="text" id="ann-title" placeholder="Title (e.g., Update v2.1 Released)">
                <textarea id="ann-content" placeholder="Content (what's new, changes, etc.)"></textarea>
                <select id="ann-type">
                    <option value="update">Update</option>
                    <option value="news">News</option>
                    <option value="maintenance">Maintenance</option>
                    <option value="critical">Critical</option>
                </select>
                <button onclick="createAnnouncement()" style="width:100%; margin-top:10px">Publish Announcement</button>
            </div>
            <div id="announcements-list"></div>
        </div>
        
        <!-- ЮЗЕРНЕЙМЫ -->
        <div class="usernames-section">
            <h2 style="text-align:center; color:#ffa502; margin-bottom:20px">Registered Usernames</h2>
            <div id="usernames-list"><div class="loading">Loading usernames...</div></div>
        </div>
    </div>
    <script>
        let keys = [];
        let announcements = [];
        let usernames = [];
        let filter = 'all';
        
        async function load() {
            try {
                const r = await fetch('/api/keys', { headers: {'X-API-Secret': '{{ api_secret }}'} });
                const data = await r.json();
                keys = data.keys;
                updateStats();
                render();
            } catch(e) {
                document.getElementById('keys').innerHTML = '<div class="error">Error: ' + e.message + '</div>';
            }
        }
        
        async function loadAnnouncements() {
            try {
                const r = await fetch('/api/announcements', { headers: {'X-API-Secret': '{{ api_secret }}'} });
                const data = await r.json();
                announcements = data.announcements;
                renderAnnouncements();
            } catch(e) {
                console.error('Failed to load announcements:', e);
            }
        }
        
        async function loadUsernames() {
            try {
                const r = await fetch('/api/usernames', { headers: {'X-API-Secret': '{{ api_secret }}'} });
                const data = await r.json();
                usernames = data.usernames;
                document.getElementById('usernames-count').textContent = usernames.length;
                renderUsernames();
            } catch(e) {
                console.error('Failed to load usernames:', e);
            }
        }
        
        function updateStats() {
            document.getElementById('total').textContent = keys.length;
            document.getElementById('used').textContent = keys.filter(k => k.status === 'used').length;
            document.getElementById('unused').textContent = keys.filter(k => k.status === 'unused').length;
            document.getElementById('basic').textContent = keys.filter(k => k.tier === 'BASIC').length;
            document.getElementById('prem').textContent = keys.filter(k => k.tier === 'PREM').length;
            document.getElementById('owner').textContent = keys.filter(k => k.tier === 'OWNER').length;
        }
        
        function setFilter(f) {
            filter = f;
            document.querySelectorAll('.filters button').forEach(b => b.classList.remove('active'));
            document.getElementById('btn-' + f).classList.add('active');
            render();
        }
        
        function render() {
            const s = document.getElementById('search').value.toLowerCase();
            let filtered = keys.filter(k => {
                if (filter === 'used' && k.status !== 'used') return false;
                if (filter === 'unused' && k.status !== 'unused') return false;
                if (filter === 'basic' && k.tier !== 'BASIC') return false;
                if (filter === 'prem' && k.tier !== 'PREM') return false;
                if (filter === 'owner' && k.tier !== 'OWNER') return false;
                if (s && !k.key.toLowerCase().includes(s)) return false;
                return true;
            });
            if (filtered.length === 0) {
                document.getElementById('keys').innerHTML = '<div class="error" style="color:#888;">No keys found</div>';
                return;
            }
            document.getElementById('keys').innerHTML = filtered.map(k => `
                <div class="key ${k.status}">
                    <div class="key-header">
                        <div class="key-code">${k.key}</div>
                        <div class="tier ${k.tier === 'PREM' ? 'prem' : k.tier === 'OWNER' ? 'owner' : ''}">${k.tier}</div>
                    </div>
                    <div class="status ${k.status}">${k.status}</div>
                    ${k.hwid ? '<div class="info">HWID: ' + k.hwid + '</div>' : ''}
                    ${k.activated_at ? '<div class="info">Activated: ' + new Date(k.activated_at).toLocaleString() + '</div>' : ''}
                    <button class="toggle ${k.status === 'used' ? 'to-unused' : 'to-used'}" 
                            onclick="toggle('${k.key}', '${k.status === 'used' ? 'unused' : 'used'}')">
                        ${k.status === 'used' ? 'Mark as Unused' : 'Mark as Used'}
                    </button>
                </div>
            `).join('');
        }
        
        function renderAnnouncements() {
            const list = document.getElementById('announcements-list');
            if (announcements.length === 0) {
                list.innerHTML = '<div style="text-align:center; color:#888; padding:20px;">No announcements yet</div>';
                return;
            }
            list.innerHTML = announcements.map(a => `
                <div class="announcement-item">
                    <h4>${a.title}</h4>
                    <p>${a.content}</p>
                    <div class="meta">Type: ${a.type} | Created: ${new Date(a.created_at).toLocaleString()}</div>
                    <button class="delete-btn" onclick="deleteAnnouncement(${a.id})">Delete</button>
                </div>
            `).join('');
        }
        
        function renderUsernames() {
            const list = document.getElementById('usernames-list');
            if (usernames.length === 0) {
                list.innerHTML = '<div style="text-align:center; color:#888; padding:20px;">No registered usernames yet</div>';
                return;
            }
            list.innerHTML = usernames.map(u => `
                <div class="username-item">
                    <div class="username-info">
                        <h4>@${u.username}</h4>
                        <p>Tier: ${u.tier} | HWID: ${u.hwid.substring(0, 8)}... | Created: ${new Date(u.created_at).toLocaleString()}</p>
                        ${u.display_name ? `<p>Display Name: ${u.display_name}</p>` : ''}
                    </div>
                    <button class="ban-btn" onclick="banUsername('${u.username}')">Ban</button>
                </div>
            `).join('');
        }
        
        async function toggle(key, status) {
            await fetch('/api/update', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json', 'X-API-Secret': '{{ api_secret }}' },
                body: JSON.stringify({key: key, status: status})
            });
            await load();
        }
        
        async function createAnnouncement() {
            const title = document.getElementById('ann-title').value.trim();
            const content = document.getElementById('ann-content').value.trim();
            const type = document.getElementById('ann-type').value;
            
            if (!title || !content) {
                alert('Please fill in title and content');
                return;
            }
            
            await fetch('/api/announcements', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json', 'X-API-Secret': '{{ api_secret }}' },
                body: JSON.stringify({title, content, type})
            });
            
            document.getElementById('ann-title').value = '';
            document.getElementById('ann-content').value = '';
            await loadAnnouncements();
        }
        
        async function deleteAnnouncement(id) {
            if (!confirm('Delete this announcement?')) return;
            await fetch(`/api/announcements/${id}`, {
                method: 'DELETE',
                headers: { 'X-API-Secret': '{{ api_secret }}' }
            });
            await loadAnnouncements();
        }
        
        async function banUsername(username) {
            if (!confirm(`Ban username @${username}?`)) return;
            await fetch(`/api/usernames/${username}/ban`, {
                method: 'POST',
                headers: { 'X-API-Secret': '{{ api_secret }}' }
            });
            await loadUsernames();
        }
        
        load();
        loadAnnouncements();
        loadUsernames();
        setInterval(load, 5000);
        setInterval(loadAnnouncements, 10000);
        setInterval(loadUsernames, 10000);
        
        document.addEventListener('visibilitychange', () => {
            if (!document.hidden) {
                load();
                loadAnnouncements();
                loadUsernames();
            }
        });
    </script>
</body>
</html>
"""

# ═══════════════════════════════════════════════
#  API ЭНДПОИНТЫ
# ═══════════════════════════════════════════════

@app.route('/')
@app.route('/admin')
def home():
    return render_template_string(HTML_PAGE, api_secret=API_SECRET)

@app.route('/api/keys')
@require_api_secret
def get_keys():
    with get_db() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute('SELECT key, tier, status, hwid, activated_at, is_active FROM licenses ORDER BY tier, key')
            keys = cur.fetchall()
    return jsonify({'status': 'ok', 'keys': keys})

@app.route('/api/update', methods=['POST'])
@require_api_secret
def update():
    data = request.get_json()
    key = data.get('key')
    status = data.get('status')
    with get_db() as conn:
        with conn.cursor() as cur:
            if status == 'unused':
                cur.execute("UPDATE licenses SET status = 'unused', hwid = NULL, activated_at = NULL WHERE key = %s", (key,))
            else:
                cur.execute("UPDATE licenses SET status = 'used' WHERE key = %s", (key,))
    return jsonify({'ok': True})

@app.route('/activate', methods=['POST'])
def activate():
    ip = request.remote_addr
    if not check_rate_limit(ip):
        return jsonify({'status': 'error', 'message': 'Rate limit exceeded'}), 429
    
    data = request.get_json()
    key = data.get('key', '').strip()
    hwid = data.get('hwid', '').strip()
    
    if not key:
        return jsonify({'status': 'invalid', 'message': 'Key required'}), 400
    
    # Проверка формата
    parts = key.split('-')
    if len(parts) != 3 or parts[0] != 'SCARED' or parts[1] not in ['BASIC', 'PREM', 'OWNER']:
        return jsonify({'status': 'invalid', 'message': 'Invalid key format'}), 400
    
    if parts[1] == 'OWNER':
        if key not in OWNER_KEYS:
            return jsonify({'status': 'invalid', 'message': 'Invalid owner key'}), 400
        return jsonify({'status': 'ok', 'tier': 'OWNER', 'message': 'Welcome back, Owner!'})
    
    if len(parts[2]) != 8:
        return jsonify({'status': 'invalid', 'message': 'Invalid key format'}), 400
    
    with get_db() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute('SELECT * FROM licenses WHERE key = %s', (key,))
            row = cur.fetchone()
            
            if not row:
                return jsonify({'status': 'invalid', 'message': 'Key not found'}), 404
            
            if not row['is_active']:
                return jsonify({'status': 'blocked', 'message': 'Key is deactivated'}), 403
            
            tier = row['tier']
            stored_hwid = row['hwid']
            
            # Первая активация
            if row['status'] == 'unused':
                cur.execute("UPDATE licenses SET status = 'used', hwid = %s, activated_at = %s WHERE key = %s", 
                           (hwid, datetime.now(), key))
                return jsonify({'status': 'activated', 'tier': tier, 'message': 'License activated'})
            
            # Уже активирован - проверяем HWID
            if stored_hwid and stored_hwid != hwid:
                return jsonify({'status': 'blocked', 'message': 'HWID mismatch - key bound to another device'})
            
            return jsonify({'status': 'ok', 'tier': tier, 'message': 'License valid'})

@app.route('/api/announcements')
@require_api_secret
def get_announcements():
    with get_db() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute('''
                SELECT id, title, content, type, created_at 
                FROM announcements 
                WHERE is_active = TRUE 
                ORDER BY created_at DESC
            ''')
            announcements = cur.fetchall()
    return jsonify({'status': 'ok', 'announcements': announcements})

@app.route('/api/announcements', methods=['POST'])
@require_api_secret
def create_announcement():
    data = request.get_json()
    title = data.get('title')
    content = data.get('content')
    ann_type = data.get('type', 'update')
    
    if not title or not content:
        return jsonify({'status': 'error', 'message': 'Title and content required'}), 400
    
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute('''
                INSERT INTO announcements (title, content, type) 
                VALUES (%s, %s, %s)
            ''', (title, content, ann_type))
    
    return jsonify({'status': 'ok', 'message': 'Announcement created'})

@app.route('/api/announcements/<int:ann_id>', methods=['DELETE'])
@require_api_secret
def delete_announcement(ann_id):
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute('UPDATE announcements SET is_active = FALSE WHERE id = %s', (ann_id,))
    return jsonify({'status': 'ok', 'message': 'Announcement deleted'})

# ═══════════════════════════════════════════════
#  ЮЗЕРНЕЙМЫ API
# ═══════════════════════════════════════════════

@app.route('/api/check-username', methods=['POST'])
def check_username():
    data = request.get_json()
    username = data.get('username', '').lower().strip()
    hwid = data.get('hwid', '')
    tier = data.get('tier', '')
    
    if len(username) < 3:
        return jsonify({"available": False, "error": "Username must be at least 3 characters"})
    if len(username) > 20:
        return jsonify({"available": False, "error": "Username too long (max 20)"})
    if not username.isalnum():
        return jsonify({"available": False, "error": "Username must be alphanumeric"})
    
    with get_db() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute("SELECT hwid FROM usernames WHERE username = %s", (username,))
            row = cur.fetchone()
            
            if row:
                if row['hwid'] == hwid:
                    return jsonify({"available": True, "owned": True})
                else:
                    return jsonify({"available": False, "error": "Username already taken"})
            
            # Проверяем лимит
            max_usernames = 5 if tier == 'OWNER' else 1
            cur.execute("SELECT COUNT(*) as cnt FROM usernames WHERE hwid = %s", (hwid,))
            count = cur.fetchone()['cnt']
            if count >= max_usernames:
                return jsonify({"available": False, "error": f"Username limit reached ({max_usernames} max for {tier})"})
    
    return jsonify({"available": True, "owned": False})


@app.route('/api/save-username', methods=['POST'])
def save_username():
    data = request.get_json()
    username = data.get('username', '').lower().strip()
    hwid = data.get('hwid', '')
    tier = data.get('tier', '')
    display_name = data.get('display_name', '')
    color = data.get('color', '#ffffff')
    glow = data.get('glow', 10)
    
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO usernames (username, hwid, tier, display_name, color, glow) 
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (username) DO UPDATE SET 
                    hwid = EXCLUDED.hwid,
                    display_name = EXCLUDED.display_name,
                    color = EXCLUDED.color,
                    glow = EXCLUDED.glow
                WHERE usernames.hwid = EXCLUDED.hwid
            """, (username, hwid, tier, display_name, color, glow))
    
    return jsonify({"success": True, "message": "Username saved"})


@app.route('/api/usernames')
@require_api_secret
def get_usernames():
    with get_db() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute('SELECT username, hwid, tier, display_name, color, glow, created_at FROM usernames ORDER BY created_at DESC')
            usernames = cur.fetchall()
    return jsonify({'status': 'ok', 'usernames': usernames})


@app.route('/api/usernames/<username>/ban', methods=['POST'])
@require_api_secret
def ban_username(username):
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute('DELETE FROM usernames WHERE username = %s', (username,))
    return jsonify({'status': 'ok', 'message': f'Username @{username} banned'})

@app.route('/health')
def health():
    return jsonify({'status': 'ok', 'timestamp': datetime.now().isoformat()})

init_db()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)