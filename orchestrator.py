import os
import sys
from dotenv import load_dotenv

# 1. Load env awal-awal supaya semua library ada akses kepada kunci/config
load_dotenv()

# 2. Setup path supaya Python boleh jumpa folder 'agents' dan 'database'
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from agents.honeypot_agent import HoneypotAgent
from agents.analyser_agent import AnalyserAgent
# Tukar import ini:
from database.db_manager import DatabaseManager

class Orchestrator:
    def __init__(self):
        # Sekarang database dan agent boleh akses load_dotenv() yang dipanggil di atas
        self.honeypot = HoneypotAgent()
        self.analyser = AnalyserAgent()
        self.db = DatabaseManager()

    def process_scammer_message(self, scammer_msg, session_id, platform="web"):
        # Kod proses mesej Aina yang asal
        print(f"\n[SCAMMER] {scammer_msg}")
        
        victim_response = self.honeypot.generate_response(scammer_msg, session_id)
        analysis = self.analyser.analyse(scammer_msg)
        
        self.db.save_conversation(
            session_id=session_id,
            scammer_message=scammer_msg,
            agent_response=victim_response,
            platform=platform,
            analysis=analysis
        )
        
        return {
            "victim_response": victim_response,
            "analysis": analysis
        }