import sqlite3
import logging
import asyncio
import json
import re
import time
import secrets
import base64
import hashlib
import random
import uuid
import urllib.parse
import codecs
import html
import math
import zlib
import aiohttp
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
    ContextTypes,
)

# === KONFIGURASI BOT ===
BOT_TOKEN = "8829957582:AAFcBoK0r1L7lgwgAcyqFameAmQfCD9DDzw"
SAWERIA_USERNAME = "ableeins"
SAWERIA_STREAM_KEY = "55e81d1a34c66b46432ee7c8e618bdb1"
ABLEEINS_API_KEY = "87ba49783dac82b3daa71d063e06f002"
ABLEEINS_BASE_URL = "https://typically-bonus-ultram-appearance.trycloudflare.com"

OWNER_ID = 1513275351
HARGA_PER_TOKEN = 5000 
WELCOME_GIF_URL = "https://media1.tenor.com/m/EOniX3w6bVEAAAAd/naruto-uzumaki.gif"

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
SENSITIVE_MSGS = {}

# KODE MORSE DICTIONARY & ATBASH
MORSE = {'A':'.-','B':'-...','C':'-.-.','D':'-..','E':'.','F':'..-.','G':'--.','H':'....','I':'..','J':'.---','K':'-.-','L':'.-..','M':'--','N':'-.','O':'---','P':'.--.','Q':'--.-','R':'.-.','S':'...','T':'-','U':'..-','V':'...-','W':'.--','X':'-..-','Y':'-.--','Z':'--..','1':'.----','2':'..---','3':'...--','4':'....-','5':'.....','6':'-....','7':'--...','8':'---..','9':'----.','0':'-----',' ':'/'}
RMORSE = {v:k for k,v in MORSE.items()}
ATBASH = str.maketrans("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz", "ZYXWVUTSRQPONMLKJIHGFEDCBAzyxwvutsrqponmlkjihgfedcba")

# === UPDATE API TERBARU V10 ===
LAYANAN_API = {
    "cek_nik": {"nama": "Cek NIK", "token": 2, "endpoint": "/api/cek_nik", "param": "nik"},
    "databocor": {"nama": "Data Bocor", "token": 1, "endpoint": "/api/data-bocor", "param": "q"},
    "nama_dukcapil": {"nama": "Nama Dukcapil", "token": 1, "endpoint": "/api/cek_nama", "param": "nama"},
    "nik_kk": {"nama": "Cari KK via NIK", "token": 2, "endpoint": "/api/nik2kk", "param": "nik"},
    "cek_kk": {"nama": "Cek Kartu Keluarga", "token": 2, "endpoint": "/api/kk", "param": "nokk"},
    "getcontact": {"nama": "GetContact", "token": 1, "endpoint": "/api/getcontact", "param": "nomor"},
    "plat": {"nama": "Cek Plat Nomor", "token": 1, "endpoint": "/api/nopol", "param": "plat"},
    "keluarga_bpjs": {"nama": "Keluarga BPJS", "token": 1, "endpoint": "/api/keluargabpjs", "param": "nik"}
}

LAYANAN_MANUAL = {
    "manual_facerec": "Face Recognition", "manual_edabu": "Cek Edabu", "manual_kk": "Cek KK", 
    "manual_siswa": "Cek Siswa", "manual_bpjstk": "Cek BPJSTK", "manual_infodata": "Info Data", 
    "manual_nik_kk": "NIK ➔ No. KK", "manual_perusahaan": "Cek Perusahaan", "manual_gaji": "Cek Gaji", 
    "manual_bpjs": "Cek BPJS", "manual_personal_bu": "Cek Personal BU", "manual_posisi": "Cek Posisi",
}

# 125 FITUR FREE TOOLS V9
LAYANAN_FREE = {
    "f_tt": ("TikTok Down", "URL"), "f_ig": ("IG Down", "URL"), "f_fb": ("FB Down", "URL"), "f_ytv": ("YT Down", "URL"), "f_tw": ("X Down", "URL"),
    "f_otpwa": ("Spam WA", "No"), "f_otpsms": ("Spam SMS", "No"), "f_call": ("Spam Call", "No"), "f_email": ("Spam Email", "Email"),
    "f_ip": ("IP Lookup", "IP"), "f_dns": ("DNS Resolver", "Domain"), "f_mac": ("MAC Lookup", "MAC"), "f_bin": ("BIN Checker", "6 Angka"), "f_asn": ("ASN Lookup", "ASN"), "f_github": ("GitHub OSINT", "User"), "f_http": ("HTTP Headers", "URL"), "f_ping": ("Web Status", "URL"), "f_whois": ("Whois", "Domain"),
    "f_md5": ("MD5", "Teks"), "f_sha1": ("SHA1", "Teks"), "f_sha224": ("SHA224", "Teks"), "f_sha256": ("SHA256", "Teks"), "f_sha384": ("SHA384", "Teks"), "f_sha512": ("SHA512", "Teks"), "f_blk2b": ("Blake2b", "Teks"), "f_blk2s": ("Blake2s", "Teks"), "f_crc32": ("CRC32", "Teks"), "f_adler": ("Adler32", "Teks"), "f_b64e": ("B64 Enc", "Teks"), "f_b64d": ("B64 Dec", "Kode"), "f_b32e": ("B32 Enc", "Teks"), "f_b32d": ("B32 Dec", "Kode"), "f_b85e": ("B85 Enc", "Teks"), "f_b85d": ("B85 Dec", "Kode"),
    "f_urle": ("URL Enc", "Teks"), "f_urld": ("URL Dec", "Kode"), "f_hexe": ("Hex Enc", "Teks"), "f_hexd": ("Hex Dec", "Kode"), "f_bine": ("Binary Enc", "Teks"), "f_bind": ("Binary Dec", "Kode"), "f_rot13e": ("ROT13 Enc", "Teks"), "f_rot13d": ("ROT13 Dec", "Kode"), "f_htmle": ("HTML Enc", "Teks"), "f_htmld": ("HTML Dec", "Kode"),
    "f_upper": ("Upper", "Teks"), "f_lower": ("Lower", "Teks"), "f_title": ("Title Case", "Teks"), "f_swap": ("Swap Case", "Teks"), "f_camel": ("Camel Case", "Teks"), "f_snake": ("Snake Case", "Teks"), "f_kebab": ("Kebab Case", "Teks"), "f_pascal": ("Pascal Case", "Teks"), "f_rev": ("Reverse", "Teks"), "f_len": ("Count Char", "Teks"), "f_wordcnt": ("Count Word", "Teks"), "f_vowel": ("Count Vowel", "Teks"), "f_cons": ("Count Cons", "Teks"), "f_nospace": ("No Space", "Teks"), "f_strip": ("Strip Trim", "Teks"), "f_ascii": ("ASCII Array", "Teks"), "f_morsee": ("Morse Enc", "Teks"), "f_morsed": ("Morse Dec", "Kode"), "f_atbe": ("Atbash Enc", "Teks"), "f_atbd": ("Atbash Dec", "Kode"),
    "f_prime": ("Is Prime", "Angka"), "f_even": ("Even", "Angka"), "f_odd": ("Odd", "Angka"), "f_factm": ("Factorial", "Angka"), "f_sqrt": ("Square Root", "Angka"), "f_cbrt": ("Cube Root", "Angka"), "f_log": ("Log10", "Angka"), "f_sin": ("Sin", "Angka"), "f_cos": ("Cos", "Angka"), "f_tan": ("Tan", "Angka"), "f_deg": ("Radian>Deg", "Angka"), "f_rad": ("Deg>Radian", "Angka"), "f_coin": ("Coin", "Ketik gen"), "f_dice": ("Dice", "Ketik gen"), "f_randnum": ("Rand 1-100", "Ketik gen"), "f_rand1k": ("Rand 1-1k", "Ketik gen"),
    "f_pass": ("Pass Gen", "Panjang"), "f_uuid": ("UUIDv4", "Ketik gen"), "f_fakeid": ("Fake ID", "Ketik gen"), "f_qr": ("QR Maker", "Teks"), "f_short": ("URL Short", "URL"), "f_tempmail": ("Temp Mail", "Ketik gen"), "f_gender": ("Gender Pre", "Nama"), "f_age": ("Age Pre", "Nama"), "f_nat": ("Nation Pre", "Nama"), "f_color": ("Rand Hex", "Ketik gen"), "f_rgb": ("Rand RGB", "Ketik gen"), "f_fakeip": ("Fake IP", "Ketik gen"), "f_fakemac": ("Fake MAC", "Ketik gen"), "f_fakeipv6": ("Fake IPv6", "Ketik gen"),
    "f_crypto": ("Crypto", "BTCUSDT"), "f_country": ("Country", "Negara"), "f_weather": ("Weather", "Kota"), "f_dict": ("Dict", "Kata"), "f_fact": ("Fact", "gen"), "f_joke": ("Joke", "gen"), "f_quote": ("Quote", "gen"), "f_num": ("Num Trivia", "Angka"), "f_yesno": ("Yes/No", "Tanya"), "f_dog": ("Dog Pic", "gen"), "f_cat": ("Cat Pic", "gen"), "f_time": ("UTC Time", "gen"), "f_catfact": ("Cat Fact", "gen"), "f_dogfact": ("Dog Fact", "gen"), "f_fox": ("Fox Pic", "gen"), "f_coffee": ("Coffee", "gen"), "f_advice": ("Advice", "gen"), "f_ghzen": ("GH Zen", "gen"), "f_iss": ("ISS Astros", "gen"), "f_zip": ("US Zip", "Zip"), "f_kanye": ("Kanye Quote", "gen"), "f_excuse": ("Excuse", "gen"), "f_poke": ("Pokedex", "Nama"), "f_year": ("Year Hist", "Tahun"), "f_date": ("Date Hist", "M/D"), "f_math": ("Math Fact", "Angka"), "f_insult": ("Evil Insult", "gen"), "f_univ": ("Universities", "Negara"), "f_meme": ("Meme", "gen"), "f_bored": ("Bored API", "gen")
}

# === DATABASE SETUP ===
def init_db():
    conn = sqlite3.connect("bot_database.db", timeout=10)
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY, balance INTEGER DEFAULT 0, roles TEXT DEFAULT 'MEMBER', email TEXT, phone TEXT, password TEXT, username TEXT, is_logged_in INTEGER DEFAULT 0, tos_agreed INTEGER DEFAULT 0)")
    cursor.execute("CREATE TABLE IF NOT EXISTS transactions (donation_id TEXT PRIMARY KEY, user_id INTEGER, amount INTEGER)")
    cursor.execute("CREATE TABLE IF NOT EXISTS support_tickets (ticket_id TEXT PRIMARY KEY, user_id INTEGER, message TEXT, status TEXT DEFAULT 'OPEN', created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)")
    cursor.execute("CREATE TABLE IF NOT EXISTS activity_logs (log_id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, activity TEXT, timestamp DATETIME DEFAULT (datetime('now', 'localtime')))")
    conn.commit(); conn.close()

def get_total_users():
    try:
        conn = sqlite3.connect("bot_database.db", timeout=10)
        count = conn.cursor().execute("SELECT COUNT(user_id) FROM users").fetchone()[0]
        conn.close()
        return count
    except: return 0

def log_activity(user_id, activity_text):
    try:
        conn = sqlite3.connect("bot_database.db", timeout=10)
        conn.execute("INSERT INTO activity_logs (user_id, activity) VALUES (?, ?)", (user_id, activity_text))
        conn.commit(); conn.close()
    except: pass

def get_user_data(user_id):
    conn = sqlite3.connect("bot_database.db", timeout=10)
    cursor = conn.cursor()
    cursor.execute("SELECT balance, roles, email, phone, password, is_logged_in, tos_agreed, username FROM users WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    default_roles = "OWNER,DEVELOPER,CS" if user_id == OWNER_ID else "MEMBER"
    
    if not row:
        cursor.execute("INSERT INTO users (user_id, balance, roles) VALUES (?, 0, ?)", (user_id, default_roles))
        conn.commit(); conn.close()
        return {"balance": 0, "roles": default_roles, "email": None, "phone": None, "is_logged_in": 0, "tos_agreed": 0, "username": None}
    
    keys = ["balance", "roles", "email", "phone", "password", "is_logged_in", "tos_agreed", "username"]
    udata = dict(zip(keys, row))
    if user_id == OWNER_ID and "OWNER" not in udata["roles"]:
        udata["roles"] = f"OWNER,DEVELOPER,CS,{udata['roles']}"
        cursor.execute("UPDATE users SET roles = ? WHERE user_id = ?", (udata["roles"], user_id))
        conn.commit()
    conn.close()
    return udata

def update_user_field(user_id, field, value):
    try:
        conn = sqlite3.connect("bot_database.db", timeout=10)
        conn.execute(f"UPDATE users SET {field} = ? WHERE user_id = ?", (value, user_id))
        conn.commit(); conn.close()
    except: pass

# === BACKGROUND WORKERS ===
async def check_saweria_stream(app):
    url = f"https://backend.saweria.co/donations/{SAWERIA_STREAM_KEY}?page=1&pageSize=15"
    while True:
        try:
            async with aiohttp.ClientSession(headers={"User-Agent": "Mozilla/5.0"}) as session:
                async with session.get(url, timeout=10) as resp:
                    if resp.status == 200:
                        for item in (await resp.json()).get("data", []):
                            donation_id = str(item.get("id", ""))
                            amount = int(item.get("amount_raw") or item.get("amount") or 0)
                            message = str(item.get("message") or "").strip()
                            notify_uid, token_didapat = None, 0
                            
                            conn = sqlite3.connect("bot_database.db", timeout=10)
                            cur = conn.cursor()
                            cur.execute("SELECT 1 FROM transactions WHERE donation_id = ?", (donation_id,))
                            if not cur.fetchone():
                                match = re.search(r"TOPUP\s*[-:]?\s*(\d+)", message, re.IGNORECASE)
                                if match:
                                    target_uid = int(match.group(1))
                                    conn.execute("INSERT INTO transactions (donation_id, user_id, amount) VALUES (?, ?, ?)", (donation_id, target_uid, amount))
                                    if amount >= HARGA_PER_TOKEN:
                                        token_didapat = amount // HARGA_PER_TOKEN
                                        conn.execute("UPDATE users SET balance = balance + ? WHERE user_id = ?", (token_didapat, target_uid))
                                        notify_uid = target_uid
                                else:
                                    conn.execute("INSERT INTO transactions (donation_id, user_id, amount) VALUES (?, 0, ?)", (donation_id, amount))
                            conn.commit(); conn.close()
                            if notify_uid:
                                log_activity(notify_uid, f"Topup Berhasil: Rp{amount} (+{token_didapat} Token)")
                                try: await app.bot.send_message(chat_id=notify_uid, text=f"✨ *Top Up Berhasil!*\nDana masuk: Rp{amount:,}\nKredit: +{token_didapat} Token", parse_mode="Markdown")
                                except: pass
        except Exception: pass
        await asyncio.sleep(5)

# === LUXURY FORMATTER UI ===
def format_data_ui(judul: str, raw_payload: dict, lebar_kolom: int = 14) -> str:
    garis = "━" * 40
    output = [garis, f" 🏛️ HASIL INTELIJEN: {judul.upper()}", garis, ""]
    data = raw_payload.get("data", raw_payload) if isinstance(raw_payload, dict) else raw_payload
    blacklist_keys = {"foto", "image", "photo", "tokens_remaining", "agent", "usage_info", "success", "status", "message"}

    def parse_dict(d, indent=""):
        for k, v in d.items():
            if str(k).lower() in blacklist_keys: continue
            if isinstance(v, dict):
                output.append(f"\n{indent}⚜️ [{k.upper()}]")
                parse_dict(v, indent + "   ")
            elif isinstance(v, list):
                output.append(f"\n{indent}⚜️ [{k.upper()} ({len(v)})]")
                for idx, item in enumerate(v, 1):
                    if isinstance(item, dict): parse_dict(item, indent + f"   ({idx}) ")
                    else: output.append(f"{indent}   ❖ [{idx}] {item}")
            else:
                k_formatted = str(k).replace('_', ' ').title().ljust(lebar_kolom)
                val_formatted = '-' if v is None or str(v).strip() == '' else str(v)
                output.append(f"{indent}❖ {k_formatted} : {val_formatted}")

    if isinstance(data, dict): parse_dict(data)
    else: output.append(str(data))
    output.append("\n" + garis)
    return f"```text\n{chr(10).join(output)}\n```"

# === HACKER UI MENU (UPDATE EL HUSSEINI) ===
def get_main_menu_text(user_id, udata):
    display_active_users = 1053 + get_total_users()
    date_now = datetime.utcnow().strftime("%d:%B:%Y")
    uname = str(udata['username']).replace('_', '\\_')
    
    return (
        f"```text\n"
        f"   __  ___  _    ___ ___ ___ _  _\n"
        f"  /  \| _ ) |  | __| __|_ _| \| |\n"
        f" | () | _ \ |__| _|| _| | || .` |\n"
        f"  \__/|___/____|___|___|___|_|\_|\n"
        f"      O S I N T   S Y S T E M\n"
        f"```\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"|| Nama       : {uname}\n"
        f"|| Status     : ACTIVE\n"
        f"|| Score      : {udata['balance']} Token\n"
        f"|| Users      : {display_active_users:,}\n"
        f"|| Tanggal    : {date_now}\n"
        f"|| ID User    : {user_id}\n"
        f"|| Role       : {udata['roles']}\n"
        f"|| Developer  : El Husseini ♕\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"✅ `[Response : 200 OK]`\n"
        f"📶 `[Server   : Online]`\n\n"
        f"⚠️ *Pusat Bantuan:* @zyr4nt\n"
        f"Silakan pilih menu operasional di bawah:"
    )

# === KEYBOARDS ===
def get_auth_keyboard():
    return InlineKeyboardMarkup([[InlineKeyboardButton("📝 Register Akun Baru", callback_data="auth_register")], [InlineKeyboardButton("🔐 Login Akses", callback_data="auth_login")]])

def get_main_keyboard(user_id, page="api"):
    if page == "api":
        keyboard = [
            [InlineKeyboardButton("Cek NIK (2 Token)", callback_data="layanan_cek_nik"), InlineKeyboardButton("Data Bocor (1 Token)", callback_data="layanan_databocor")],
            [InlineKeyboardButton("Nama Dukcapil (1 Token)", callback_data="layanan_nama_dukcapil"), InlineKeyboardButton("NIK ➔ KK (2 Token)", callback_data="layanan_nik_kk")],
            [InlineKeyboardButton("Cek KK (2 Token)", callback_data="layanan_cek_kk"), InlineKeyboardButton("GetContact (1 Token)", callback_data="layanan_getcontact")],
            [InlineKeyboardButton("Plat Nomor (1 Token)", callback_data="layanan_plat"), InlineKeyboardButton("Keluarga BPJS (1 Token)", callback_data="layanan_keluarga_bpjs")],
            [InlineKeyboardButton("🎁 HUB FREE PUBLIC TOOLS (125 API)", callback_data="page_free")],
            [InlineKeyboardButton("➡️ MENU MANUAL (VIA ADMIN)", callback_data="page_manual")],
            [InlineKeyboardButton("💳 Beli Saldo / Topup", callback_data="beli_token"), InlineKeyboardButton("🪪 Profil & Akun", callback_data="cek_profil")],
            [InlineKeyboardButton("🎧 Live Chat / Bantuan Support", callback_data="support")]
        ]
    elif page == "free":
        keyboard = [
            [InlineKeyboardButton("📥 Media Downloader", callback_data="fcat_down"), InlineKeyboardButton("💣 Spam Tools", callback_data="fcat_spam")],
            [InlineKeyboardButton("🛡️ Cyber Security", callback_data="fcat_cyb"), InlineKeyboardButton("🔄 Hash Crypto", callback_data="fcat_hash")],
            [InlineKeyboardButton("🔀 Converter", callback_data="fcat_conv"), InlineKeyboardButton("📝 Text Tools", callback_data="fcat_text")],
            [InlineKeyboardButton("🔢 Math & Logic", callback_data="fcat_math"), InlineKeyboardButton("🛠️ Utilities", callback_data="fcat_util")],
            [InlineKeyboardButton("ℹ️ Global Info & Fun Tools", callback_data="fcat_info")],
            [InlineKeyboardButton("⬅️ KEMBALI KE MENU OSINT", callback_data="page_api")]
        ]
    else:
        keyboard = [
            [InlineKeyboardButton("Face Recognition AI (Private)", callback_data="manual_facerec")],
            [InlineKeyboardButton("Edabu (Via Admin)", callback_data="manual_edabu"), InlineKeyboardButton("KK (Via Admin)", callback_data="manual_kk")],
            [InlineKeyboardButton("Siswa (Via Admin)", callback_data="manual_siswa"), InlineKeyboardButton("BPJSTK (Via Admin)", callback_data="manual_bpjstk")],
            [InlineKeyboardButton("Info Data (Via Admin)", callback_data="manual_infodata"), InlineKeyboardButton("NIK ➔ No. KK (Via Admin)", callback_data="manual_nik_kk")],
            [InlineKeyboardButton("Perusahaan (Via Admin)", callback_data="manual_perusahaan"), InlineKeyboardButton("Gaji (Via Admin)", callback_data="manual_gaji")],
            [InlineKeyboardButton("BPJS (Via Admin)", callback_data="manual_bpjs"), InlineKeyboardButton("Personal BU (Via Admin)", callback_data="manual_personal_bu")],
            [InlineKeyboardButton("Posisi Geolocation (Via Admin)", callback_data="manual_posisi")],
            [InlineKeyboardButton("⬅️ KEMBALI KE OSINT VIP", callback_data="page_api")]
        ]
    if user_id == OWNER_ID and page != "free":
        keyboard.append([InlineKeyboardButton("🛠️ MASUK KE PANEL KONTROL OWNER", callback_data="panel_admin")])
    return InlineKeyboardMarkup(keyboard)

def get_free_cat_keyboard(category):
    kb = []
    if category == "down": keys = ["f_tt", "f_ig", "f_fb", "f_ytv", "f_tw"]
    elif category == "spam": keys = ["f_otpwa", "f_otpsms", "f_call", "f_email"]
    elif category == "cyb": keys = ["f_ip", "f_dns", "f_mac", "f_bin", "f_asn", "f_github", "f_http", "f_ping", "f_whois"]
    elif category == "hash": keys = ["f_md5", "f_sha1", "f_sha224", "f_sha256", "f_sha384", "f_sha512", "f_blk2b", "f_blk2s", "f_crc32", "f_adler", "f_b64e", "f_b64d", "f_b32e", "f_b32d", "f_b85e", "f_b85d"]
    elif category == "conv": keys = ["f_urle", "f_urld", "f_hexe", "f_hexd", "f_bine", "f_bind", "f_rot13e", "f_rot13d", "f_htmle", "f_htmld"]
    elif category == "text": keys = ["f_upper", "f_lower", "f_title", "f_swap", "f_camel", "f_snake", "f_kebab", "f_pascal", "f_rev", "f_len", "f_wordcnt", "f_vowel", "f_cons", "f_nospace", "f_strip", "f_ascii", "f_morsee", "f_morsed", "f_atbe", "f_atbd"]
    elif category == "math": keys = ["f_prime", "f_even", "f_odd", "f_factm", "f_sqrt", "f_cbrt", "f_log", "f_sin", "f_cos", "f_tan", "f_deg", "f_rad", "f_coin", "f_dice", "f_randnum", "f_rand1k"]
    elif category == "util": keys = ["f_pass", "f_uuid", "f_fakeid", "f_qr", "f_short", "f_tempmail", "f_gender", "f_age", "f_nat", "f_color", "f_rgb", "f_fakeip", "f_fakemac", "f_fakeipv6"]
    elif category == "info": keys = ["f_crypto", "f_country", "f_weather", "f_dict", "f_fact", "f_joke", "f_quote", "f_num", "f_yesno", "f_dog", "f_cat", "f_time", "f_catfact", "f_dogfact", "f_fox", "f_coffee", "f_advice", "f_ghzen", "f_iss", "f_zip", "f_kanye", "f_excuse", "f_poke", "f_year", "f_date", "f_math", "f_insult", "f_univ", "f_meme", "f_bored"]
    else: keys = []
    
    for i in range(0, len(keys), 3):
        row = []
        row.append(InlineKeyboardButton(LAYANAN_FREE[keys[i]][0], callback_data=f"fbtn_{keys[i]}"))
        if i+1 < len(keys): row.append(InlineKeyboardButton(LAYANAN_FREE[keys[i+1]][0], callback_data=f"fbtn_{keys[i+1]}"))
        if i+2 < len(keys): row.append(InlineKeyboardButton(LAYANAN_FREE[keys[i+2]][0], callback_data=f"fbtn_{keys[i+2]}"))
        kb.append(row)
    kb.append([InlineKeyboardButton("⬅️ Kembali ke Kategori", callback_data="page_free")])
    return InlineKeyboardMarkup(kb)

# === COMMAND HANDLERS ===
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    context.user_data.clear()
    update_user_field(user_id, "username", update.effective_user.username or "Tidak_Ada_Username")
    udata = get_user_data(user_id)

    try: await update.message.reply_animation(animation=WELCOME_GIF_URL)
    except: pass

    if not udata["is_logged_in"]:
        text = "🔒 *SISTEM KEAMANAN TERENKRIPSI*\n━━━━━━━━━━━━━━━━━━━━━━━━━━━\nSistem OSINT mensyaratkan pengguna teregistrasi guna mematuhi standar hukum cyber.\n\nSilakan *Register* atau *Login*:"
        await update.message.reply_text(text, parse_mode="Markdown", reply_markup=get_auth_keyboard())
        return

    await update.message.reply_text(get_main_menu_text(user_id, udata), parse_mode="Markdown", reply_markup=get_main_keyboard(user_id, "api"))

async def balas_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    udata = get_user_data(user_id)
    if "CS" not in udata['roles'].split(",") and "OWNER" not in udata['roles'].split(","): return
    try:
        target_uid, pesan_balasan = int(context.args[0]), " ".join(context.args[1:])
        conn = sqlite3.connect("bot_database.db", timeout=10)
        conn.execute("UPDATE support_tickets SET status = 'CLOSED' WHERE user_id = ? AND status = 'OPEN'", (target_uid,))
        conn.commit(); conn.close()
        await context.bot.send_message(chat_id=target_uid, text=f"💬 *RESPON RESMI CUSTOMER SUPPORT*\n━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n{pesan_balasan}", parse_mode="Markdown")
        await update.message.reply_text(f"✅ Balasan berhasil dikirim ke ID `{target_uid}`.")
        log_activity(user_id, f"Membalas tiket ke user {target_uid}")
    except: await update.message.reply_text("❌ Format salah! Ketik:\n`/balas <id_user> <isi_pesan>`")

# === CALLBACK QUERY ===
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    udata = get_user_data(user_id)
    data = query.data

    if data == "auth_register":
        msg = await query.edit_message_text("📝 *REGISTRASI AKUN*\n\nSilakan ketik *Alamat Email* Anda:", parse_mode="Markdown")
        context.user_data["action"], context.user_data["prompt_msg_id"] = "reg_email", query.message.message_id
        return
    elif data == "auth_login":
        msg = await query.edit_message_text("🔐 *LOGIN AKUN*\n\nSilakan ketik *Alamat Email* terdaftar:", parse_mode="Markdown")
        context.user_data["action"], context.user_data["prompt_msg_id"] = "login_email", query.message.message_id
        return

    if not udata["is_logged_in"]:
        await query.edit_message_text("⚠️ Autentikasi diperlukan. Anda harus login terlebih dahulu!", reply_markup=get_auth_keyboard())
        return

    # --- MENU NAVIGATION ---
    if data == "page_api":
        context.user_data.pop("action", None)
        await query.edit_message_text(get_main_menu_text(user_id, udata), parse_mode="Markdown", reply_markup=get_main_keyboard(user_id, "api"))
        return
    elif data == "page_manual":
        context.user_data.pop("action", None)
        await query.edit_message_text("⚙️ *MENU MANUAL (PRIVATE ORDER)*\nPencarian khusus yang ditangani oleh Tim Investigasi.", parse_mode="Markdown", reply_markup=get_main_keyboard(user_id, "manual"))
        return
    elif data == "page_free":
        context.user_data.pop("action", None)
        await query.edit_message_text("🎁 *HUB FREE PUBLIC TOOLS (125 API)*\n\nAkses 125 fitur API publik gratis secara native. Pilih kategori operasi di bawah ini:", parse_mode="Markdown", reply_markup=get_main_keyboard(user_id, "free"))
        return
    elif data.startswith("fcat_"):
        cat = data.split("_")[1]
        cat_names = {"down": "📥 Media Downloader", "spam": "💣 Spam & Stresser", "cyb": "🛡️ Cyber Security", "hash": "🔄 Hash & Crypto", "conv": "🔀 Converter", "text": "📝 Text Tools", "math": "🔢 Math & Logic", "util": "🛠️ Public Utilities", "info": "ℹ️ Info & Fun"}
        await query.edit_message_text(f"{cat_names[cat]}\nSilakan pilih layanan API gratis:", parse_mode="Markdown", reply_markup=get_free_cat_keyboard(cat))
        return
    elif data.startswith("fbtn_"):
        key = data.replace("fbtn_", "")
        nama, hint = LAYANAN_FREE[key]
        context.user_data["action"] = f"free_act_{key}"
        await query.edit_message_text(f"🎁 *FREE API: {nama}*\n\nSilakan ketik *{hint}* di chat ini sekarang:", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("❌ Batal", callback_data="page_free")]]))
        context.user_data["prompt_msg_id"] = query.message.message_id
        return

    # --- ADMIN SMART PANEL & OWNER FEATURES ---
    if data == "panel_admin":
        if user_id != OWNER_ID: return
        keyboard = [
            [InlineKeyboardButton("👥 Kelola User Aktif (Klik Nama)", callback_data="adm_allusers")],
            [InlineKeyboardButton("🔍 Kelola User (Cari ID)", callback_data="adm_carimanual")],
            [InlineKeyboardButton("🎫 Cek Tiket Laporan Masuk", callback_data="adm_tickets")],
            [InlineKeyboardButton("🛠️ Fitur Owner VIP 🛠️", callback_data="adm_owner_vip")],
            [InlineKeyboardButton("⬅️ Tutup Panel Admin", callback_data="page_api")]
        ]
        await query.edit_message_text("🛠️ *PANEL KONTROL OWNER*\nSilakan pilih menu manajemen sistem:", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))
        return
    elif data == "adm_owner_vip":
        if user_id != OWNER_ID: return
        keyboard = [
            [InlineKeyboardButton("📢 Broadcast Global", callback_data="own_bc")],
            [InlineKeyboardButton("🗑️ Clean Database Logs", callback_data="own_clean")],
            [InlineKeyboardButton("⬅️ Kembali", callback_data="panel_admin")]
        ]
        await query.edit_message_text("🛠️ *FITUR OWNER VIP*\nAkses kendali penuh tingkat dewa:", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))
        return
    elif data == "own_bc":
        if user_id != OWNER_ID: return
        context.user_data["action"] = "owner_bc"
        await query.edit_message_text("📢 *BROADCAST GLOBAL*\nKetik pesan yang akan dikirim ke SELURUH user bot:", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("❌ Batal", callback_data="adm_owner_vip")]]))
        context.user_data["prompt_msg_id"] = query.message.message_id
        return
    elif data == "own_clean":
        if user_id != OWNER_ID: return
        try:
            conn = sqlite3.connect("bot_database.db", timeout=10)
            conn.execute("DELETE FROM activity_logs")
            conn.commit(); conn.close()
            await query.edit_message_text("✅ *SUKSES!*\nSemua riwayat aktivitas (Activity Logs) telah dihapus dari database.", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Kembali", callback_data="adm_owner_vip")]]))
        except Exception as e: await query.edit_message_text(f"❌ Error: {e}")
        return
    elif data == "adm_allusers":
        if user_id != OWNER_ID: return
        try:
            conn = sqlite3.connect("bot_database.db", timeout=10)
            cursor = conn.cursor()
            cursor.execute("SELECT user_id, email, username FROM users ORDER BY user_id DESC LIMIT 10")
            rows, keyboard = cursor.fetchall(), []
            conn.close()
            for r in rows:
                uid, email, uname = r
                label = f"{str(uname)[:12] if uname else 'Belum_Reg'} | {str(email)[:15] if email else 'No_Email'}"
                keyboard.append([InlineKeyboardButton(label, callback_data=f"admu_{uid}")])
            keyboard.append([InlineKeyboardButton("⬅️ Kembali", callback_data="panel_admin")])
            await query.edit_message_text("👥 *PILIH USER UNTUK MENGAKSES TOMBOL KELOLA (+/- TOKEN/ROLE)*:", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))
        except Exception as e: await query.edit_message_text(f"❌ Error DB: {e}", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Kembali", callback_data="panel_admin")]]))
        return
    elif data == "adm_tickets":
        if user_id != OWNER_ID: return
        try:
            conn = sqlite3.connect("bot_database.db", timeout=10)
            cursor = conn.cursor()
            cursor.execute("SELECT ticket_id, user_id, message, created_at FROM support_tickets WHERE status = 'OPEN' ORDER BY created_at DESC LIMIT 5")
            tickets = cursor.fetchall()
            conn.close()
            if not tickets: await query.edit_message_text("🎫 *DAFTAR TIKET*\nSaat ini tidak ada laporan aktif.", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Kembali", callback_data="panel_admin")]]))
            else:
                teks = "🎫 *DAFTAR TIKET (OPEN)*\n━━━━━━━━━━━━━━\n\n"
                for tid, uid, msg, time_created in tickets:
                    teks += f"📌 *ID Tiket:* `{tid}`\n👤 *User ID:* `{uid}`\n🕒 *Waktu:* {time_created}\n💬 *Pesan:* {str(msg)[:100]}...\n_Balas via chat: /balas {uid} pesan_\n━━━━━━━━━━━━━━\n"
                await query.edit_message_text(teks, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Kembali", callback_data="panel_admin")]]))
        except Exception as e: await query.edit_message_text(f"❌ Error DB: {e}", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Kembali", callback_data="panel_admin")]]))
        return
    elif data.startswith("admu_"):
        if user_id != OWNER_ID: return
        target_id = int(data.split("_")[1])
        t_udata = get_user_data(target_id)
        teks = f"👤 *USER KONTROL PANEL*\n━━━━━━━━━━━━━━━━\nID: `{target_id}`\nUsername: @{t_udata['username']}\nEmail: {t_udata['email']}\nPhone: {t_udata['phone']}\nRoles: `{t_udata['roles']}`\nSaldo: *{t_udata['balance']} Token*"
        keyboard = [[InlineKeyboardButton("📜 Cek Log Aktivitas", callback_data=f"admlog_{target_id}")], [InlineKeyboardButton("🪙 + Token", callback_data=f"addtok_{target_id}"), InlineKeyboardButton("🗑️ - Token", callback_data=f"deltok_{target_id}")], [InlineKeyboardButton("🏷️ Tambah Role", callback_data=f"addrol_{target_id}"), InlineKeyboardButton("❌ Cabut Role", callback_data=f"delrol_{target_id}")], [InlineKeyboardButton("⬅️ Kembali", callback_data="adm_allusers")]]
        await query.edit_message_text(teks, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))
        return
    elif data.startswith("admlog_"):
        if user_id != OWNER_ID: return
        target_id = int(data.split("_")[1])
        conn = sqlite3.connect("bot_database.db", timeout=10)
        cursor = conn.cursor()
        cursor.execute("SELECT activity, timestamp FROM activity_logs WHERE user_id = ? ORDER BY log_id DESC LIMIT 15", (target_id,))
        logs, teks_log = cursor.fetchall(), f"📜 *HISTORY AKTIVITAS ID: {target_id}*\n━━━━━━━━━━━━━━\n"
        conn.close()
        if not logs: teks_log += "ℹ️ Belum ada catatan aktivitas."
        else:
            for act, ts in logs: teks_log += f"• `[{ts[11:16]}]` - {act}\n"
        await query.edit_message_text(teks_log, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Kembali", callback_data=f"admu_{target_id}")]]))
        return
    elif data.startswith("addtok_"):
        context.user_data["action"] = f"admin_act_addtok_{data.split('_')[1]}"
        await query.edit_message_text("🪙 Ketik **Jumlah Token** untuk ditambahkan:", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("❌ Batal", callback_data=f"admu_{data.split('_')[1]}")]]))
        context.user_data["prompt_msg_id"] = query.message.message_id
        return
    elif data.startswith("deltok_"):
        context.user_data["action"] = f"admin_act_deltok_{data.split('_')[1]}"
        await query.edit_message_text("🗑️ Ketik **Jumlah Token** yang akan dihapus:", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("❌ Batal", callback_data=f"admu_{data.split('_')[1]}")]]))
        context.user_data["prompt_msg_id"] = query.message.message_id
        return
    elif data.startswith("addrol_"):
        context.user_data["action"] = f"admin_act_addrol_{data.split('_')[1]}"
        await query.edit_message_text("🏷️ Ketik **Nama Role** (misal: VIP/CS):", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("❌ Batal", callback_data=f"admu_{data.split('_')[1]}")]]))
        context.user_data["prompt_msg_id"] = query.message.message_id
        return
    elif data.startswith("delrol_"):
        context.user_data["action"] = f"admin_act_delrol_{data.split('_')[1]}"
        await query.edit_message_text("❌ Ketik **Nama Role** yang akan DICABUT:", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("❌ Batal", callback_data=f"admu_{data.split('_')[1]}")]]))
        context.user_data["prompt_msg_id"] = query.message.message_id
        return
    elif data == "adm_carimanual":
        context.user_data["action"] = "admin_act_carimanual"
        await query.edit_message_text("🔍 Ketik *ID Telegram* user yang ingin dicari:", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("❌ Batal", callback_data="panel_admin")]]))
        context.user_data["prompt_msg_id"] = query.message.message_id
        return

    # --- DIGITAL SIGNATURE (TOS) ---
    if data == "sign_tos":
        update_user_field(user_id, "tos_agreed", 1)
        log_activity(user_id, "Menyetujui Terms of Service")
        await query.edit_message_text("✅ *TANDA TANGAN DIGITAL DITERIMA*\nStatus hukum tercatat. Otoritas dibuka.", parse_mode="Markdown", reply_markup=get_main_keyboard(user_id, "api"))
        return

    # --- LAYANAN OSINT API (BERBAYAR TOKEN) ---
    if data.startswith("layanan_"):
        key = data.replace("layanan_", "")
        item = LAYANAN_API.get(key)
        if not item: return
        if udata["tos_agreed"] == 0:
            tos_text = "⚠️ *PERINGATAN HUKUM & TERMS OF SERVICE (TOS)*\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\nSistem ini dilengkapi perlindungan Anti-SS.\n\n1. *IDENTITAS TERCATAT:* Seluruh aktivitas direkam.\n2. *NO REFUND:* Top-up bersifat mutlak.\n3. *TANGGUNG JAWAB MUTLAK:* Pelanggaran berakibat pelaporan otomatis ke pihak berwajib (POLRI).\n\nKlik tombol di bawah ini sebagai **Tanda Tangan Digital**."
            await query.edit_message_text(tos_text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("✍️ SAYA SETUJU & TANDA TANGAN", callback_data="sign_tos")], [InlineKeyboardButton("❌ TOLAK & KEMBALI", callback_data="page_api")]]))
            return
        if udata['balance'] < item["token"]:
            await query.edit_message_text("⚠️ *Otorisasi Gagal: Saldo Token Tidak Mencukupi*\nSilakan Top-Up melalui kanal Saweria resmi.", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("💳 Beli Token", callback_data="beli_token")], [InlineKeyboardButton("⬅️ Kembali", callback_data="page_api")]]))
            return
        context.user_data["action"] = f"api_{key}"
        await query.edit_message_text(f"🎯 *Layanan OSINT: {item['nama']}*\nKirimkan *Parameter Target* ke chat ini sekarang:", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("❌ Batal", callback_data="page_api")]]))
        context.user_data["prompt_msg_id"] = query.message.message_id
        return

    # --- LAYANAN MANUAL ---
    elif data.startswith("manual_"):
        layanan_nama = LAYANAN_MANUAL.get(data, "Private Order")
        context.user_data["action"] = f"manual_order_{layanan_nama}"
        harga_est = "Rp 500.000 - Rp 1.000.000" if "Face Rec" in layanan_nama else "Rp 250.000 - Rp 300.000"
        teks_manual = f"⚙️ *LAYANAN {layanan_nama.upper()}*\n━━━━━━━━━━━━━━━━━━━━━━━━━━━\n⚠️ *Biaya Estimasi: {harga_est}*.\n\nPembayaran dan eksekusi dikoordinasikan oleh Admin. Ketik *Target* dan *Kronologi* kasus Anda detail di bawah ini:"
        await query.edit_message_text(teks_manual, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("❌ Batal", callback_data="page_manual")]]))
        context.user_data["prompt_msg_id"] = query.message.message_id
        return
    elif data == "support":
        context.user_data["action"] = "sending_support"
        await query.edit_message_text("💬 *LIVE CHAT SUPPORT*\n(Gratis) Silakan ketik pertanyaan atau laporan yang ingin disampaikan ke tim CS:", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("❌ Batal", callback_data="page_api")]]))
        context.user_data["prompt_msg_id"] = query.message.message_id
    elif data == "cek_profil":
        await query.edit_message_text(f"🪪 *PROFIL IDENTITAS AKUN*\n━━━━━━━━━━━━━━━━━━━━━\n🆔 *ID* : `{user_id}`\n👤 *Username* : @{udata['username']}\n📧 *Email* : {udata['email']}\n📱 *Phone* : {udata['phone']}\n🪙 *Saldo* : *{udata['balance']} Token*\n🏷️ *Role* : `{udata['roles']}`", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Kembali", callback_data="page_api")]]))
    elif data == "beli_token":
        await query.edit_message_text(f"💳 *TOP UP OTOMATIS (Rp5.000 / Token)*\nKirim ke: https://saweria.co/{SAWERIA_USERNAME}\n\n⚠️ *CRITICAL WARNING:*\nAnda **WAJIB** mengisi kolom pesan donasi dengan:\n`TOPUP-{user_id}`", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Kembali", callback_data="page_api")]]))

# === TEXT INPUT HANDLER & CLEAN CHAT ===
async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text.strip()
    
    if text.startswith("/"):
        context.user_data.clear()
        return

    action = context.user_data.get("action")
    if not action: return
    
    udata = get_user_data(user_id)

    # 🧹 CLEAN CHAT
    try: await update.message.delete()
    except: pass
    
    prompt_id = context.user_data.get("prompt_msg_id")
    if prompt_id:
        try: await context.bot.delete_message(chat_id=user_id, message_id=prompt_id)
        except: pass
        context.user_data.pop("prompt_msg_id", None)

    # --- OWNER BROADCAST ---
    if action == "owner_bc":
        if user_id != OWNER_ID: return
        context.user_data.pop("action", None)
        wait_msg = await context.bot.send_message(chat_id=user_id, text="⏳ Mengirim broadcast ke semua user...")
        try:
            conn = sqlite3.connect("bot_database.db", timeout=10)
            cur = conn.cursor()
            cur.execute("SELECT user_id FROM users")
            all_users = cur.fetchall()
            conn.close()
            sent_count = 0
            for u in all_users:
                try: 
                    await context.bot.send_message(chat_id=u[0], text=f"📢 *BROADCAST DARI OWNER*\n━━━━━━━━━━━━━━━━\n\n{text}", parse_mode="Markdown")
                    sent_count += 1
                except: pass
            await wait_msg.edit_text(f"✅ *BROADCAST SELESAI*\nBerhasil terkirim ke {sent_count} user aktif.", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Kembali", callback_data="adm_owner_vip")]]))
        except Exception as e: await wait_msg.edit_text(f"❌ Error Broadcast: {e}")
        return

    # --- FLOW REGISTRASI & LOGIN ---
    if action == "reg_email":
        context.user_data["reg_email"] = text
        context.user_data["action"] = "reg_phone"
        msg = await context.bot.send_message(chat_id=user_id, text="📱 Masukkan *Nomor Telepon* aktif:", parse_mode="Markdown")
        context.user_data["prompt_msg_id"] = msg.message_id
        return
    elif action == "reg_phone":
        context.user_data["reg_phone"] = text
        context.user_data["action"] = "reg_pass"
        msg = await context.bot.send_message(chat_id=user_id, text="🔑 Buat *Password* keamanan:", parse_mode="Markdown")
        context.user_data["prompt_msg_id"] = msg.message_id
        return
    elif action == "reg_pass":
        update_user_field(user_id, "email", context.user_data["reg_email"])
        update_user_field(user_id, "phone", context.user_data["reg_phone"])
        update_user_field(user_id, "password", text)
        update_user_field(user_id, "is_logged_in", 1)
        update_user_field(user_id, "balance", 0) 
        log_activity(user_id, "Registrasi Akun Baru")
        context.user_data.clear()
        await context.bot.send_message(chat_id=user_id, text="✅ *REGISTRASI BERHASIL!*\nOtoritas disahkan. Saldo Anda saat ini adalah **0 Token**.\nSilakan lakukan Top-Up untuk menggunakan OSINT, lalu ketik `/start`.", parse_mode="Markdown")
        return

    if action == "login_email":
        if text != udata.get("email"):
            msg = await context.bot.send_message(chat_id=user_id, text="❌ Email tidak terdaftar. Coba lagi atau ketik /start.")
            context.user_data["prompt_msg_id"] = msg.message_id
            return
        context.user_data["action"] = "login_pass"
        msg = await context.bot.send_message(chat_id=user_id, text="🔑 Masukkan *Password* Anda:", parse_mode="Markdown")
        context.user_data["prompt_msg_id"] = msg.message_id
        return
    elif action == "login_pass":
        if text != udata.get("password"):
            msg = await context.bot.send_message(chat_id=user_id, text="❌ Password salah. Coba lagi atau ketik /start.")
            context.user_data["prompt_msg_id"] = msg.message_id
            return
        update_user_field(user_id, "is_logged_in", 1)
        log_activity(user_id, "Login ke sistem")
        context.user_data.clear()
        await context.bot.send_message(chat_id=user_id, text="✅ *AUTENTIKASI BERHASIL!*\nKetik `/start` untuk membuka menu.", parse_mode="Markdown")
        return

    # --- ADMIN INPUTS ---
    if action.startswith("admin_act_"):
        if user_id != OWNER_ID: return
        context.user_data.pop("action", None)
        try:
            if action == "admin_act_carimanual":
                target_id = int(text)
                t_udata = get_user_data(target_id)
                teks = f"👤 *USER PANEL: {target_id}*\n━━━━━━━━━━━━━━━━\nEmail: {t_udata['email']}\nRoles: `{t_udata['roles']}`\nSaldo: *{t_udata['balance']}*"
                keyboard = [[InlineKeyboardButton("📜 Cek Log", callback_data=f"admlog_{target_id}")], [InlineKeyboardButton("🪙 + Token", callback_data=f"addtok_{target_id}"), InlineKeyboardButton("🗑️ - Token", callback_data=f"deltok_{target_id}")], [InlineKeyboardButton("🏷️ + Role", callback_data=f"addrol_{target_id}"), InlineKeyboardButton("❌ - Role", callback_data=f"delrol_{target_id}")], [InlineKeyboardButton("⬅️ Kembali ke Menu Utama", callback_data="panel_admin")]]
                await context.bot.send_message(chat_id=user_id, text=teks, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))
                return

            target_id = int(action.split("_")[3])
            conn = sqlite3.connect("bot_database.db", timeout=10)
            cur = conn.cursor()
            if action.startswith("admin_act_addtok_"):
                val = int(text)
                cur.execute("UPDATE users SET balance = balance + ? WHERE user_id = ?", (val, target_id))
                await context.bot.send_message(chat_id=user_id, text=f"✅ Ditambahkan {val} token ke user `{target_id}`", parse_mode="Markdown")
            elif action.startswith("admin_act_deltok_"):
                val = int(text)
                cur.execute("SELECT balance FROM users WHERE user_id=?", (target_id,))
                new_bal = max(0, cur.fetchone()[0] - val)
                cur.execute("UPDATE users SET balance = ? WHERE user_id = ?", (new_bal, target_id))
                await context.bot.send_message(chat_id=user_id, text=f"🗑️ Dikurangi {val} token. Sisa saldo `{target_id}`: {new_bal}", parse_mode="Markdown")
            elif action.startswith("admin_act_addrol_"):
                val = text.upper()
                cur.execute("SELECT roles FROM users WHERE user_id=?", (target_id,))
                curr_roles = cur.fetchone()[0].split(',')
                if val not in curr_roles: curr_roles.append(val)
                cur.execute("UPDATE users SET roles = ? WHERE user_id = ?", (",".join(curr_roles), target_id))
                await context.bot.send_message(chat_id=user_id, text=f"🏷️ Otoritas `{val}` diberikan kepada `{target_id}`", parse_mode="Markdown")
            elif action.startswith("admin_act_delrol_"):
                val = text.upper()
                cur.execute("SELECT roles FROM users WHERE user_id=?", (target_id,))
                curr_roles = cur.fetchone()[0].split(',')
                if val in curr_roles: 
                    curr_roles.remove(val)
                    if not curr_roles: curr_roles = ["MEMBER"]
                    cur.execute("UPDATE users SET roles = ? WHERE user_id = ?", (",".join(curr_roles), target_id))
                    await context.bot.send_message(chat_id=user_id, text=f"❌ Otoritas `{val}` DICABUT dari `{target_id}`", parse_mode="Markdown")
            conn.commit(); conn.close()
            await context.bot.send_message(chat_id=user_id, text="Operasi Selesai.", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Kembali ke Profil User", callback_data=f"admu_{target_id}")]]))
        except: await context.bot.send_message(chat_id=user_id, text="❌ Input tidak valid.")
        return

    # --- EKSEKUSI API FREE ACCESS ---
    if action.startswith("free_act_"):
        key = action.replace("free_act_", "")
        nama_fitur = LAYANAN_FREE[key][0]
        context.user_data.pop("action", None)
        
        wait_msg = await context.bot.send_message(chat_id=user_id, text=f"⏳ Mengeksekusi modul publik *{nama_fitur}*...", parse_mode="Markdown")
        hasil_dict = {}
        maintenance_keys = ["f_tt", "f_ig", "f_fb", "f_ytv", "f_tw", "f_otpwa", "f_otpsms", "f_call", "f_email"]
        
        try:
            if key in maintenance_keys:
                hasil_dict = {"Status": "MAINTENANCE ⚠️", "Message": "Modul ini sedang diupdate bypass security."}
            elif key == "f_tempmail":
                domains = ["1secmail.com", "1secmail.org", "1secmail.net", "kzccv.com", "qiott.com", "wuuvo.com", "igjxs.com"]
                rnd_email = f"{uuid.uuid4().hex[:10]}@{random.choice(domains)}"
                hasil_dict = {"Temp_Email": rnd_email, "Check_Inbox": f"https://www.1secmail.com/mailbox/?action=mailbox&email={rnd_email}", "Status": "Active"}
            elif key in ["f_b64e", "f_b64d", "f_b32e", "f_b32d", "f_b85e", "f_b85d", "f_md5", "f_sha1", "f_sha224", "f_sha256", "f_sha384", "f_sha512", "f_blk2b", "f_blk2s", "f_crc32", "f_adler", "f_urle", "f_urld", "f_hexe", "f_hexd", "f_bine", "f_bind", "f_rot13e", "f_rot13d", "f_htmle", "f_htmld", "f_upper", "f_lower", "f_title", "f_swap", "f_camel", "f_snake", "f_kebab", "f_pascal", "f_rev", "f_len", "f_wordcnt", "f_vowel", "f_cons", "f_nospace", "f_strip", "f_ascii", "f_morsee", "f_morsed", "f_atbe", "f_atbd", "f_prime", "f_even", "f_odd", "f_factm", "f_sqrt", "f_cbrt", "f_log", "f_sin", "f_cos", "f_tan", "f_deg", "f_rad", "f_coin", "f_dice", "f_randnum", "f_rand1k", "f_pass", "f_uuid", "f_color", "f_rgb", "f_fakeip", "f_fakemac", "f_fakeipv6", "f_time"]:
                if key == "f_b64e": hasil_dict = {"Base64_Encode": base64.b64encode(text.encode()).decode()}
                elif key == "f_b64d": hasil_dict = {"Base64_Decode": base64.b64decode(text.encode()).decode()}
                elif key == "f_b32e": hasil_dict = {"Base32_Encode": base64.b32encode(text.encode()).decode()}
                elif key == "f_b32d": hasil_dict = {"Base32_Decode": base64.b32decode(text.encode()).decode()}
                elif key == "f_b85e": hasil_dict = {"Base85_Encode": base64.b85encode(text.encode()).decode()}
                elif key == "f_b85d": hasil_dict = {"Base85_Decode": base64.b85decode(text.encode()).decode()}
                elif key == "f_md5": hasil_dict = {"MD5_Hash": hashlib.md5(text.encode()).hexdigest()}
                elif key == "f_sha1": hasil_dict = {"SHA1_Hash": hashlib.sha1(text.encode()).hexdigest()}
                elif key == "f_sha224": hasil_dict = {"SHA224_Hash": hashlib.sha224(text.encode()).hexdigest()}
                elif key == "f_sha256": hasil_dict = {"SHA256_Hash": hashlib.sha256(text.encode()).hexdigest()}
                elif key == "f_sha384": hasil_dict = {"SHA384_Hash": hashlib.sha384(text.encode()).hexdigest()}
                elif key == "f_sha512": hasil_dict = {"SHA512_Hash": hashlib.sha512(text.encode()).hexdigest()}
                elif key == "f_blk2b": hasil_dict = {"Blake2b_Hash": hashlib.blake2b(text.encode()).hexdigest()}
                elif key == "f_blk2s": hasil_dict = {"Blake2s_Hash": hashlib.blake2s(text.encode()).hexdigest()}
                elif key == "f_crc32": hasil_dict = {"CRC32": zlib.crc32(text.encode())}
                elif key == "f_adler": hasil_dict = {"Adler32": zlib.adler32(text.encode())}
                elif key == "f_urle": hasil_dict = {"URL_Encode": urllib.parse.quote(text)}
                elif key == "f_urld": hasil_dict = {"URL_Decode": urllib.parse.unquote(text)}
                elif key == "f_hexe": hasil_dict = {"Hex_Encode": text.encode().hex()}
                elif key == "f_hexd": hasil_dict = {"Hex_Decode": bytes.fromhex(text).decode('utf-8', 'ignore')}
                elif key == "f_bine": hasil_dict = {"Binary_Encode": ' '.join(format(ord(x), 'b') for x in text)}
                elif key == "f_bind": hasil_dict = {"Binary_Decode": ''.join(chr(int(x, 2)) for x in text.split())}
                elif key in ["f_rot13e", "f_rot13d"]: hasil_dict = {"ROT13": codecs.encode(text, 'rot_13')}
                elif key == "f_htmle": hasil_dict = {"HTML_Encode": html.escape(text)}
                elif key == "f_htmld": hasil_dict = {"HTML_Decode": html.unescape(text)}
                elif key == "f_upper": hasil_dict = {"Result": text.upper()}
                elif key == "f_lower": hasil_dict = {"Result": text.lower()}
                elif key == "f_title": hasil_dict = {"Result": text.title()}
                elif key == "f_swap": hasil_dict = {"Result": text.swapcase()}
                elif key == "f_camel": hasil_dict = {"Result": ''.join(word.title() for word in text.split())}
                elif key == "f_snake": hasil_dict = {"Result": text.replace(' ', '_').lower()}
                elif key == "f_kebab": hasil_dict = {"Result": text.replace(' ', '-').lower()}
                elif key == "f_pascal": hasil_dict = {"Result": ''.join(word.title() for word in text.split())}
                elif key == "f_rev": hasil_dict = {"Result": text[::-1]}
                elif key == "f_len": hasil_dict = {"Characters": len(text)}
                elif key == "f_wordcnt": hasil_dict = {"Words": len(text.split())}
                elif key == "f_vowel": hasil_dict = {"Vowels": sum(1 for c in text.lower() if c in 'aeiou')}
                elif key == "f_cons": hasil_dict = {"Consonants": sum(1 for c in text.lower() if c in 'bcdfghjklmnpqrstvwxyz')}
                elif key == "f_nospace": hasil_dict = {"Result": text.replace(" ", "")}
                elif key == "f_strip": hasil_dict = {"Result": text.strip()}
                elif key == "f_ascii": hasil_dict = {"ASCII_Array": str([ord(c) for c in text])}
                elif key == "f_morsee": hasil_dict = {"Morse_Encode": ' '.join(MORSE.get(c, c) for c in text.upper())}
                elif key == "f_morsed": hasil_dict = {"Morse_Decode": ''.join(RMORSE.get(c, c) for c in text.split(' '))}
                elif key == "f_atbe" or key == "f_atbd": hasil_dict = {"Atbash": text.translate(ATBASH)}
                elif key == "f_prime": 
                    try: 
                        n = int(text); isp = n > 1 and all(n % i != 0 for i in range(2, int(math.isqrt(n)) + 1))
                        hasil_dict = {"Number": n, "Is_Prime": isp}
                    except: hasil_dict = {"Error": "Harus angka"}
                elif key == "f_even": 
                    try: hasil_dict = {"Number": int(text), "Is_Even": int(text)%2==0}
                    except: hasil_dict = {"Error": "Harus angka"}
                elif key == "f_odd": 
                    try: hasil_dict = {"Number": int(text), "Is_Odd": int(text)%2!=0}
                    except: hasil_dict = {"Error": "Harus angka"}
                elif key == "f_factm": 
                    try: hasil_dict = {"Number": int(text), "Factorial": math.factorial(int(text)) if int(text)<=100 else "Too Large"}
                    except: hasil_dict = {"Error": "Harus angka <= 100"}
                elif key == "f_sqrt": 
                    try: hasil_dict = {"Number": int(text), "Sqrt": math.sqrt(int(text))}
                    except: hasil_dict = {"Error": "Harus angka positif"}
                elif key == "f_cbrt": 
                    try: hasil_dict = {"Number": int(text), "Cbrt": math.pow(int(text), 1/3)}
                    except: hasil_dict = {"Error": "Harus angka"}
                elif key == "f_log": 
                    try: hasil_dict = {"Number": int(text), "Log10": math.log10(int(text))}
                    except: hasil_dict = {"Error": "Harus angka positif"}
                elif key == "f_sin": 
                    try: hasil_dict = {"Number": int(text), "Sin": math.sin(int(text))}
                    except: hasil_dict = {"Error": "Harus angka"}
                elif key == "f_cos": 
                    try: hasil_dict = {"Number": int(text), "Cos": math.cos(int(text))}
                    except: hasil_dict = {"Error": "Harus angka"}
                elif key == "f_tan": 
                    try: hasil_dict = {"Number": int(text), "Tan": math.tan(int(text))}
                    except: hasil_dict = {"Error": "Harus angka"}
                elif key == "f_deg": 
                    try: hasil_dict = {"Number": float(text), "Degrees": math.degrees(float(text))}
                    except: hasil_dict = {"Error": "Harus angka"}
                elif key == "f_rad": 
                    try: hasil_dict = {"Number": float(text), "Radians": math.radians(float(text))}
                    except: hasil_dict = {"Error": "Harus angka"}
                elif key == "f_coin": hasil_dict = {"Coin_Flip": random.choice(["Heads", "Tails"])}
                elif key == "f_dice": hasil_dict = {"Dice_Roll": random.randint(1, 6)}
                elif key == "f_randnum": hasil_dict = {"Random_1_100": random.randint(1, 100)}
                elif key == "f_rand1k": hasil_dict = {"Random_1_1000": random.randint(1, 1000)}
                elif key == "f_pass":
                    length = int(text) if text.isdigit() and int(text) <= 128 else 16
                    chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*"
                    hasil_dict = {"Length": length, "Password": "".join(secrets.choice(chars) for _ in range(length))}
                elif key == "f_uuid": hasil_dict = {"UUID_v4": str(uuid.uuid4())}
                elif key == "f_color": hasil_dict = {"Random_Hex_Color": f"#{random.randint(0, 0xFFFFFF):06x}"}
                elif key == "f_rgb": hasil_dict = {"Random_RGB": f"rgb({random.randint(0,255)}, {random.randint(0,255)}, {random.randint(0,255)})"}
                elif key == "f_fakeip": hasil_dict = {"Fake_IP": f"{random.randint(1,255)}.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(1,255)}"}
                elif key == "f_fakemac": hasil_dict = {"Fake_MAC": ":".join(["%02x" % random.randint(0, 255) for _ in range(6)])}
                elif key == "f_fakeipv6": hasil_dict = {"Fake_IPv6": ":".join(["%x" % random.randint(0, 65535) for _ in range(8)])}
                elif key == "f_time": hasil_dict = {"UTC_Time": datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}
            
            # EXTERNALS
            else:
                headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
                async with aiohttp.ClientSession(headers=headers) as session:
                    if key == "f_ip":
                        async with session.get(f"http://ip-api.com/json/{text}", timeout=10) as resp: hasil_dict = await resp.json()
                    elif key == "f_dns":
                        async with session.get(f"https://dns.google/resolve?name={text}", timeout=10) as resp:
                            res = await resp.json()
                            hasil_dict = {"Domain": text, "Answers": [r.get("data") for r in res.get("Answer", [])]}
                    elif key == "f_mac":
                        async with session.get(f"https://api.maclookup.app/v2/macs/{text}", timeout=10) as resp: 
                            r = await resp.json() if resp.status == 200 else {}
                            hasil_dict = {"MAC": text, "Vendor": r.get("company", "Not Found / Rate Limit")}
                    elif key == "f_bin":
                        async with session.get(f"https://lookup.binlist.net/{text}", timeout=10) as resp: hasil_dict = await resp.json() if resp.status == 200 else {"Status": "Failed"}
                    elif key == "f_asn":
                        async with session.get(f"https://api.bgpview.io/asn/{text.replace('AS', '')}", timeout=10) as resp: 
                            r = await resp.json() if resp.status == 200 else {}
                            hasil_dict = {"ASN": r.get("data", {}).get("asn"), "Name": r.get("data", {}).get("name"), "Country": r.get("data", {}).get("country_code")}
                    elif key == "f_github":
                        async with session.get(f"https://api.github.com/users/{text}", timeout=10) as resp: hasil_dict = await resp.json()
                    elif key == "f_http":
                        async with session.head(text if text.startswith("http") else f"http://{text}", timeout=10) as resp: hasil_dict = {"Status_Code": resp.status, "Headers": dict(resp.headers)}
                    elif key == "f_ping":
                        async with session.get(text if text.startswith("http") else f"http://{text}", timeout=10) as resp: hasil_dict = {"Target": text, "Status_Code": resp.status}
                    elif key == "f_whois":
                        async with session.get(f"https://networkcalc.com/api/dns/whois/{text}", timeout=10) as resp: hasil_dict = (await resp.json()).get("whois", {}) if resp.status == 200 else {"Status": "Failed"}
                    elif key == "f_fakeid":
                        async with session.get("https://randomuser.me/api/", timeout=10) as resp:
                            r = (await resp.json())["results"][0]
                            hasil_dict = {"Name": f"{r['name']['first']} {r['name']['last']}", "Gender": r['gender'], "City": r['location']['city'], "Country": r['location']['country'], "Email": r['email']}
                    elif key == "f_qr": hasil_dict = {"Status": "Success", "QR_Link": f"https://api.qrserver.com/v1/create-qr-code/?size=500x500&data={text}"}
                    elif key == "f_short":
                        async with session.get(f"https://is.gd/create.php?format=json&url={text}", timeout=10) as resp:
                            hasil_dict = {"Original": text, "Short_URL": (await resp.json()).get("shorturl", "Error")}
                    elif key == "f_gender":
                        async with session.get(f"https://api.genderize.io/?name={text}", timeout=10) as resp: hasil_dict = await resp.json()
                    elif key == "f_age":
                        async with session.get(f"https://api.agify.io/?name={text}", timeout=10) as resp: hasil_dict = await resp.json()
                    elif key == "f_nat":
                        async with session.get(f"https://api.nationalize.io/?name={text}", timeout=10) as resp: hasil_dict = await resp.json()
                    elif key == "f_crypto":
                        async with session.get(f"https://api.binance.com/api/v3/ticker/price?symbol={text.upper()}", timeout=10) as resp:
                            hasil_dict = await resp.json() if resp.status == 200 else {"Error": "Simbol salah (ex: BTCUSDT)"}
                    elif key == "f_country":
                        async with session.get(f"https://restcountries.com/v3.1/name/{text}", timeout=10) as resp:
                            r = (await resp.json())[0] if resp.status == 200 else {}
                            hasil_dict = {"Country": r.get("name", {}).get("common"), "Capital": r.get("capital", [""])[0], "Region": r.get("region")}
                    elif key == "f_weather":
                        async with session.get(f"https://wttr.in/{text}?format=j1", timeout=10) as resp:
                            cc = (await resp.json()).get("current_condition", [{}])[0] if resp.status == 200 else {}
                            hasil_dict = {"City": text, "Temp_C": cc.get("temp_C"), "Weather": cc.get("weatherDesc", [{}])[0].get("value")}
                    elif key == "f_dict":
                        async with session.get(f"https://api.dictionaryapi.dev/api/v2/entries/en/{text}", timeout=10) as resp:
                            m = (await resp.json())[0].get("meanings", [{}])[0].get("definitions", [{}])[0].get("definition") if resp.status == 200 else "Not Found"
                            hasil_dict = {"Word": text, "Definition": m}
                    elif key == "f_fact":
                        async with session.get("https://uselessfacts.jsph.pl/api/v2/facts/random", timeout=10) as resp: hasil_dict = {"Random_Fact": (await resp.json()).get("text")}
                    elif key == "f_joke":
                        async with session.get("https://official-joke-api.appspot.com/random_joke", timeout=10) as resp: 
                            r = await resp.json() if resp.status == 200 else {}
                            hasil_dict = {"Setup": r.get("setup"), "Punchline": r.get("punchline")}
                    elif key == "f_quote":
                        async with session.get("https://dummyjson.com/quotes/random", timeout=10) as resp: 
                            r = await resp.json() if resp.status == 200 else {}
                            hasil_dict = {"Quote": r.get("quote"), "Author": r.get("author")}
                    elif key == "f_num":
                        async with session.get(f"http://numbersapi.com/{text}", timeout=10) as resp: hasil_dict = {"Number": text, "Trivia": await resp.text()}
                    elif key == "f_yesno":
                        async with session.get("https://yesno.wtf/api", timeout=10) as resp: hasil_dict = {"Question": text, "Answer": (await resp.json()).get("answer", "").upper()}
                    elif key == "f_dog":
                        async with session.get("https://dog.ceo/api/breeds/image/random", timeout=10) as resp: hasil_dict = {"Status": "Success", "Image_URL": (await resp.json()).get("message")}
                    elif key == "f_cat":
                        async with session.get("https://api.thecatapi.com/v1/images/search", timeout=10) as resp: hasil_dict = {"Status": "Success", "Image_URL": (await resp.json())[0].get("url")}
                    elif key == "f_catfact":
                        async with session.get("https://catfact.ninja/fact", timeout=10) as resp: hasil_dict = {"Cat_Fact": (await resp.json()).get("fact")}
                    elif key == "f_dogfact":
                        async with session.get("https://dog-api.kinduff.com/api/facts", timeout=10) as resp: hasil_dict = {"Dog_Fact": (await resp.json()).get("facts", [""])[0]}
                    elif key == "f_fox":
                        async with session.get("https://randomfox.ca/floof/", timeout=10) as resp: hasil_dict = {"Fox_Pic": (await resp.json()).get("image")}
                    elif key == "f_coffee":
                        async with session.get("https://coffee.alexflipnote.dev/random.json", timeout=10) as resp: hasil_dict = {"Coffee_Pic": (await resp.json()).get("file")}
                    elif key == "f_advice":
                        async with session.get("https://api.adviceslip.com/advice", timeout=10) as resp: hasil_dict = {"Advice": (await resp.json()).get("slip", {}).get("advice")}
                    elif key == "f_ghzen":
                        async with session.get("https://api.github.com/zen", timeout=10) as resp: hasil_dict = {"GitHub_Zen": await resp.text()}
                    elif key == "f_iss":
                        async with session.get("http://api.open-notify.org/astros.json", timeout=10) as resp: 
                            r = await resp.json() if resp.status == 200 else {}
                            hasil_dict = {"Total_People_In_Space": r.get("number"), "Names": ", ".join([p["name"] for p in r.get("people", [])])}
                    elif key == "f_zip":
                        async with session.get(f"https://api.zippopotam.us/us/{text}", timeout=10) as resp: 
                            r = await resp.json() if resp.status == 200 else {}
                            hasil_dict = {"Zip": text, "City": r.get("places", [{}])[0].get("place name"), "State": r.get("places", [{}])[0].get("state")}
                    elif key == "f_kanye":
                        async with session.get("https://api.kanye.rest", timeout=10) as resp: hasil_dict = {"Kanye_West_Quote": (await resp.json()).get("quote")}
                    elif key == "f_excuse":
                        async with session.get("https://excuser-three.vercel.app/v1/excuse", timeout=10) as resp: hasil_dict = {"Excuse": (await resp.json())[0].get("excuse")}
                    elif key == "f_poke":
                        async with session.get(f"https://pokeapi.co/api/v2/pokemon/{text.lower()}", timeout=10) as resp: 
                            r = await resp.json() if resp.status == 200 else {}
                            hasil_dict = {"Name": r.get("name"), "Height": r.get("height"), "Weight": r.get("weight")}
                    elif key == "f_year":
                        async with session.get(f"http://numbersapi.com/{text}/year", timeout=10) as resp: hasil_dict = {"Year": text, "Fact": await resp.text()}
                    elif key == "f_date":
                        async with session.get(f"http://numbersapi.com/{text}/date", timeout=10) as resp: hasil_dict = {"Date": text, "Fact": await resp.text()}
                    elif key == "f_math":
                        async with session.get(f"http://numbersapi.com/{text}/math", timeout=10) as resp: hasil_dict = {"Number": text, "Math_Fact": await resp.text()}
                    elif key == "f_insult":
                        async with session.get("https://evilinsult.com/generate_insult.php?lang=en&type=json", timeout=10) as resp: hasil_dict = {"Evil_Insult": (await resp.json()).get("insult")}
                    elif key == "f_univ":
                        async with session.get(f"http://universities.hipolabs.com/search?country={text}", timeout=10) as resp: 
                            r = await resp.json() if resp.status == 200 else []
                            hasil_dict = {"Country": text, "Top_Universities": [u["name"] for u in r[:3]] if r else "Not Found"}
                    elif key == "f_meme":
                        async with session.get("https://meme-api.com/gimme", timeout=10) as resp: hasil_dict = {"Meme_Title": (await resp.json()).get("title"), "Meme_URL": (await resp.json()).get("url")}
                    elif key == "f_bored":
                        async with session.get("https://www.boredapi.com/api/activity", timeout=10) as resp: hasil_dict = {"Activity": (await resp.json()).get("activity")}
            
            await wait_msg.edit_text(format_data_ui(nama_fitur, hasil_dict), parse_mode="Markdown")
        except Exception as e:
            await wait_msg.edit_text(f"⚠️ *ERROR SISTEM:* Modul {nama_fitur} gagal dieksekusi. Pastikan input valid.", parse_mode="Markdown")
        return

    # --- EKSEKUSI API OSINT (UPDATE V10.1) ---
    if action.startswith("api_"):
        key = action.replace("api_", "")
        item = LAYANAN_API[key]
        context.user_data.pop("action", None)
        
        wait_msg = await context.bot.send_message(chat_id=user_id, text=f"⏳ Mengakses satelit server untuk ekstraksi data *{item['nama']}*...", parse_mode="Markdown")
        
        conn = sqlite3.connect("bot_database.db", timeout=10)
        conn.execute("UPDATE users SET balance = balance - ? WHERE user_id = ?", (item['token'], user_id))
        conn.commit(); conn.close()
        log_activity(user_id, f"Eksekusi OSINT API: {item['nama']}")

        url = f"{ABLEEINS_BASE_URL}{item['endpoint']}"
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params={item["param"]: text, "key": ABLEEINS_API_KEY}, timeout=35) as resp:
                    if resp.status != 200:
                        await wait_msg.edit_text("⚠️ *AKSES DITOLAK: DATA KOSONG ATAU TIDAK DITEMUKAN*", parse_mode="Markdown")
                        return
                    data = await resp.json()
                    await wait_msg.delete()
                    
                    msg = await context.bot.send_message(chat_id=user_id, text=format_data_ui(item['nama'], data), parse_mode="Markdown", protect_content=True)
                    if user_id not in SENSITIVE_MSGS: SENSITIVE_MSGS[user_id] = []
                    SENSITIVE_MSGS[user_id].append(msg.message_id)
        except: await wait_msg.edit_text("⚠️ *GANGGUAN KONEKSI KE SERVER CLOUDFLARE*", parse_mode="Markdown")
        return

    # --- ORDER MANUAL & TIKET SUPPORT ---
    if action.startswith("manual_order_") or action == "sending_support":
        tipe = "PESANAN MANUAL" if "manual" in action else "LIVE CHAT TIKET"
        context.user_data.pop("action", None)
        ticket_id = f"TIC-{secrets.token_hex(3).upper()}"
        log_activity(user_id, f"Membuat {tipe} ({ticket_id})")
        
        try:
            conn = sqlite3.connect("bot_database.db", timeout=10)
            conn.execute("INSERT INTO support_tickets (ticket_id, user_id, message) VALUES (?, ?, ?)", (ticket_id, user_id, text))
            conn.commit()
            cursor = conn.cursor()
            cursor.execute("SELECT user_id, roles FROM users")
            all_db_users = cursor.fetchall()
            conn.close()

            notified_ids = {OWNER_ID}
            for uid, r_str in all_db_users:
                if "CS" in [r.strip().upper() for r in r_str.split(",")]: notified_ids.add(uid)

            for staff_id in notified_ids:
                try: await context.bot.send_message(chat_id=staff_id, text=f"📬 *{tipe} [{ticket_id}]*\nPengirim: `{user_id}` (@{udata['username']})\nNo HP: {udata['phone']}\n\n*Detail:*\n{text}\n\nBalas: `/balas {user_id} pesan_anda`", parse_mode="Markdown")
                except: pass
            await context.bot.send_message(chat_id=user_id, text=f"✅ Laporan sukses dikirim ke sistem pusat dengan nomor tiket `{ticket_id}`. Silakan tunggu tanggapan.")
        except: pass
        return

async def post_init(application):
    asyncio.create_task(check_saweria_stream(application))

def main():
    init_db()
    app = ApplicationBuilder().token(BOT_TOKEN).post_init(post_init).build()
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("balas", balas_command))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))
    
    print("Sistem Bot Enterprise V10.1 (El Husseini Edition) Aktif!")
    app.run_polling()

if __name__ == '__main__':
    main()
