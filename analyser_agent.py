import os
import json
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

ANALYSER_PROMPT = """
Kamu adalah pakar cybersecurity yang menganalisis mesej scam.
Analisis mesej scammer dan return HANYA JSON (tiada teks lain).

Format JSON yang mesti return:
{
  "tactic": "URGENCY/AUTHORITY/FEAR/GREED/ROMANCE/TRUST_BUILDING/UNKNOWN",
  "confidence": 0.0,
  "manipulation_level": "LOW/MEDIUM/HIGH",
  "keywords": ["keyword1", "keyword2"],
  "scam_category": "JOB/LOVE/PARCEL/LOAN/LOTTERY/IMPERSONATION/OTHER",
  "explanation": "Kenapa ini taktik tersebut dalam 1 ayat"
}
"""

class AnalyserAgent:
    def __init__(self):
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))

    def analyse(self, scammer_message):
        response = self.client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": ANALYSER_PROMPT},
                {"role": "user", "content": f"Analisis mesej ini: {scammer_message}"}
            ],
            max_tokens=300,
            temperature=0.1
        )

        raw = response.choices[0].message.content

        # Parse JSON
        try:
            clean = raw.replace("```json", "").replace("```", "").strip()
            analysis = json.loads(clean)
        except json.JSONDecodeError:
            analysis = {
                "tactic": "UNKNOWN",
                "confidence": 0.0,
                "manipulation_level": "LOW",
                "keywords": [],
                "scam_category": "OTHER",
                "explanation": "Failed to parse"
            }

        return analysis