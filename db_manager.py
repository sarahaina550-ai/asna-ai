import sqlite3
import json
import os

DB_PATH = "database/asna.db"

class DatabaseManager:
    def __init__(self):
        os.makedirs("database", exist_ok=True)
        self.init_db()

    def get_connection(self):
        return sqlite3.connect(DB_PATH)

    def init_db(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.executescript("""
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                scammer_message TEXT,
                agent_response TEXT,
                platform TEXT DEFAULT 'web',
                tactic TEXT,
                manipulation_level TEXT,
                scam_category TEXT,
                confidence REAL,
                keywords TEXT,
                sender_phone TEXT
            );
            CREATE TABLE IF NOT EXISTS threat_intel (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tactic_type TEXT,
                scam_category TEXT,
                frequency INTEGER DEFAULT 1,
                last_seen DATE DEFAULT CURRENT_DATE
            );
        """)
        conn.commit()
        conn.close()
        print("✅ Database initialized!")

    def save_conversation(self, session_id, scammer_message, agent_response, platform, analysis, sender_phone=None):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO conversations 
            (session_id, scammer_message, agent_response, platform,
             tactic, manipulation_level, scam_category, confidence, keywords, sender_phone)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            session_id, scammer_message, agent_response, platform,
            analysis.get("tactic"), analysis.get("manipulation_level"),
            analysis.get("scam_category"), analysis.get("confidence"),
            json.dumps(analysis.get("keywords", [])), sender_phone
        ))
        self.update_threat_intel(analysis, cursor)
        conn.commit()
        conn.close()

    def update_threat_intel(self, analysis, cursor):
        tactic = analysis.get("tactic", "UNKNOWN")
        category = analysis.get("scam_category", "OTHER")
        cursor.execute("SELECT id, frequency FROM threat_intel WHERE tactic_type=? AND scam_category=?", (tactic, category))
        existing = cursor.fetchone()
        if existing:
            cursor.execute("UPDATE threat_intel SET frequency = frequency + 1, last_seen = CURRENT_DATE WHERE id = ?", (existing[0],))
        else:
            cursor.execute("INSERT INTO threat_intel (tactic_type, scam_category) VALUES (?, ?)", (tactic, category))

    def check_if_number_is_scammer(self, phone_number):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM conversations WHERE sender_phone = ?", (phone_number,))
        count = cursor.fetchone()[0]
        conn.close()
        return count > 0

    def get_stats(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        stats = {}
        cursor.execute("SELECT COUNT(*) FROM conversations")
        stats["total_messages"] = cursor.fetchone()[0]
        cursor.execute("SELECT tactic, COUNT(*) FROM conversations WHERE tactic IS NOT NULL GROUP BY tactic")
        stats["tactic_breakdown"] = cursor.fetchall()
        conn.close()
        return stats

    def get_conversations(self, limit=5):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM conversations ORDER BY id DESC LIMIT ?", (limit,))
        rows = cursor.fetchall()
        conn.close()
        return rows