import telebot
import cv2
from pyzbar.pyzbar import decode
from database.db_manager import DatabaseManager

# Konfigurasi Bot
bot = telebot.TeleBot("8854468526:AAEsr7DJpQ8VS4DQ2IbiOenTJuW145FQ_do")
db = DatabaseManager()

def analyze_scam(text):
    text = text.lower()
    
    # 1. Definisi Keyword & Skor Risiko
    if any(word in text for word in ["tahniah", "menang"]):
        return "Scam Tawaran", 75
    elif any(word in text for word in ["bank", "akaun"]):
        return "Phishing", 95
    elif any(word in text for word in ["saham", "pelaburan", "trade", "pendapatan", "sampingan", "untung"]):
        return "Investment", 85
    elif len(text.split()) >= 3:
        return "Mesej Mencurigakan", 50
    
    return None, 0

def detect_qr(image_path):
    img = cv2.imread(image_path)
    if img is None: return None
    decoded_objects = decode(img)
    if not decoded_objects: return None
    return decoded_objects[0].data.decode('utf-8')

def is_scam_link(url):
    url = url.lower()
    scam_keywords = ["money", "claim", "free", "duit", "bonus", "win", "tng", "wallet", "lucky"]
    return any(keyword in url for keyword in scam_keywords)

# --- HANDLER ---
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "ASNA Cyber Shield AI sedia berkhidmat!")

# ... (atas kod bot sama macam Aina)

@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    file_info = bot.get_file(message.photo[-1].file_id)
    downloaded_file = bot.download_file(file_info.file_path)
    file_path = "temp_qr.jpg"
    with open(file_path, "wb") as new_file:
        new_file.write(downloaded_file)
    
    qr_data = detect_qr(file_path)
    if qr_data:
        tactic = "QR Phishing" if is_scam_link(qr_data) else "QR Selamat"
        analysis = {"tactic": tactic, "risk_score": 90 if "Phishing" in tactic else 10, "confidence": 0.9}
        
        # PERUBAHAN DI SINI: Tambah parameter ke-6
        db.save_conversation(str(message.from_user.id), f"QR Data: {qr_data}", tactic, "Telegram", analysis, str(message.from_user.id))
        
        bot.reply_to(message, f"🚨 Status QR: {tactic}\nData: {qr_data}")
    else:
        bot.reply_to(message, "❌ Tiada QR dikesan.")

@bot.message_handler(func=lambda message: True)
def handle_text(message):
    if message.text.startswith('/'): return
    
    tactic, risk = analyze_scam(message.text)
    print(f"DEBUG: Mesej diterima: '{message.text}' -> Taktik: {tactic}")

    if tactic: 
        analysis = {
            "tactic": tactic, 
            "risk_score": risk, 
            "confidence": 0.9
        } 
        
        # PERUBAHAN DI SINI: Tambah parameter ke-6
        db.save_conversation(str(message.from_user.id), message.text, tactic, "Telegram", analysis, str(message.from_user.id))
        
        pesan_amaran = f"""
⚠️ ASNA mengesan ancaman!
🔹 Taktik: {tactic}
🔹 Tahap Risiko: {risk}/100
"""
        bot.reply_to(message, pesan_amaran)

print("🤖 ASNA sedang berjalan...")
# Gunakan non_stop=True untuk pastikan bot tak 'tidur' bila terima mesej bertubi-tubi
bot.infinity_polling(none_stop=True, interval=0)