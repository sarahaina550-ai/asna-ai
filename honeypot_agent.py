import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

PERSONA_SYSTEM_PROMPT = """
Kamu adalah Mak Cik Rohani, seorang wanita berumur 52 tahun 
yang tinggal di Ipoh. Kamu bekerja sebagai guru sekolah rendah 
yang sudah bersara. Kamu tidak terlalu mahir teknologi.

PERATURAN PENTING:
1. Balas dalam Bahasa Malaysia yang natural
2. Tunjukkan MINAT tapi jangan terlalu mudah percaya
3. Tanya soalan supaya scammer explain lebih lanjut
4. JANGAN berikan nombor IC, nombor akaun, atau OTP sebenar
5. Kalau scammer minta duit, tanya "macam mana nak hantar?"
6. Tujuan kamu: buat scammer reveal kaedah & script mereka
7. Jangan tunjukkan yang kamu tahu ini scam
"""

class HoneypotAgent:
    def __init__(self):
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        self.conversations = {} 

    def generate_response(self, scammer_message, session_id):
        if session_id not in self.conversations:
            self.conversations[session_id] = []

        self.conversations[session_id].append({
            "role": "user",
            "content": scammer_message
        })

        # Menggunakan model terbaru yang disokong oleh Groq
        response = self.client.chat.completions.create(
            model="llama-3.3-70b-versatile", 
            messages=[
                {"role": "system", "content": PERSONA_SYSTEM_PROMPT},
                *self.conversations[session_id]
            ],
            max_tokens=200,
            temperature=0.7
        )

        agent_reply = response.choices[0].message.content

        self.conversations[session_id].append({
            "role": "assistant",
            "content": agent_reply
        })

        return agent_reply