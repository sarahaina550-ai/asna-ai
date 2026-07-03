# Tactic Classifier — Label & score setiap mesej
import re

# Keywords untuk setiap taktik
TACTIC_KEYWORDS = {
    "URGENCY": [
        "segera", "cepat", "24 jam", "hari ini", "sekarang",
        "akan tamat", "tarikh akhir", "deadline", "urgent",
        "immediately", "expire", "last chance"
    ],
    "AUTHORITY": [
        "polis", "pdrm", "bank negara", "mahkamah", "kerajaan",
        "jabatan", "pegawai", "officer", "detective", "judge",
        "court", "malaysia", "official", "department"
    ],
    "FEAR": [
        "didakwa", "ditangkap", "saman", "blacklist", "denda",
        "penjara", "arrested", "charged", "warrant", "blocked",
        "frozen", "suspend", "tangkap"
    ],
    "GREED": [
        "menang", "hadiah", "rm", "bonus", "untung", "lumayan",
        "prize", "winner", "lucky", "reward", "cash", "free",
        "rebate", "komisyen", "commission"
    ],
    "ROMANCE": [
        "sayang", "cinta", "rindu", "love", "dear", "honey",
        "darling", "miss you", "together", "relationship",
        "marry", "beautiful", "handsome", "lonely"
    ],
    "TRUST_BUILDING": [
        "kerja di", "bekerja", "doktor", "engineer", "un", "dubai",
        "luar negara", "overseas", "professional", "experience",
        "trusted", "verified", "certified", "legit"
    ]
}

def classify_tactic(message):
    message_lower = message.lower()
    scores = {}

    for tactic, keywords in TACTIC_KEYWORDS.items():
        count = sum(1 for kw in keywords if kw in message_lower)
        scores[tactic] = count

    # Ambil taktik dengan score tertinggi
    top_tactic = max(scores, key=scores.get)
    top_score = scores[top_tactic]

    if top_score == 0:
        return "UNKNOWN", 0.0, scores

    confidence = min(top_score / 3.0, 1.0)  # Max 1.0
    return top_tactic, round(confidence, 2), scores


def extract_features(message):
    """Extract features untuk ML model"""
    return {
        "length": len(message),
        "exclamation_count": message.count("!"),
        "question_count": message.count("?"),
        "caps_ratio": sum(1 for c in message if c.isupper()) / max(len(message), 1),
        "has_money_symbol": bool(re.search(r'rm\s?\d+|\$\d+', message.lower())),
        "has_phone_number": bool(re.search(r'(\+?6?01[0-9]{8,9})', message)),
        "has_url": bool(re.search(r'http[s]?://', message)),
        "word_count": len(message.split())
    }