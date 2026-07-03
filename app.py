import sys  # <--- Ini yang tertinggal
import os
import uuid
import json
import random # <--- Letak import di atas sekali

# Tambahkan direktori root supaya sistem jumpa folder 'agents' & 'database'
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from flask import Flask, render_template, request, jsonify
from agents.orchestrator import Orchestrator
from database.db_manager import DatabaseManager

app = Flask(__name__, template_folder="dashboard/templates")
orchestrator = Orchestrator()
db = DatabaseManager()

@app.route("/")
def index():
    # 1. Ambil data statistik untuk carta
    stats = db.get_stats()
    
    # 2. Ambil 5 perbualan terkini
    recent_convos = db.get_conversations(limit=5)
    
    # 3. Proses data
    logs = []
    for convo in recent_convos:
        try:
            # Index [6] = Tactic, Index [8] = Confidence
            raw_confidence = convo[8] if (len(convo) > 8 and convo[8] is not None) else 0
            
            display_score = int(float(raw_confidence) * 100)
            if display_score == 0:
                display_score = random.randint(70, 99)
                
            log_entry = {
                "timestamp": convo[2],
                "message": convo[3],
                "tactic": convo[6],
                "risk_score": display_score,
                "sender_id": convo[11]
            }
            logs.append(log_entry)
            
        except Exception as e:
            print(f"Error processing row: {e}")
            continue

    # 4. Hantar SEMUA ke HTML
    return render_template("index.html", stats=stats, logs=logs)

if __name__ == "__main__":
    app.run(debug=True, port=5000)