from fastapi import FastAPI
from pydantic import BaseModel
import re

app = FastAPI(title="CyberKareem URL Detector API")

class URLRequest(BaseModel):
    url: str

PHISHING_PATTERNS = [
    r'paypal.*secure', r'secure.*paypal', r'bank.*login', r'login.*bank',
    r'verify.*account', r'account.*verify', r'confirm.*identity',
    r'update.*credentials', r'credentials.*update', r'suspended.*account',
    r'account.*suspended', r'unusual.*activity', r'security.*alert',
    r'click.*here.*verify', r'limited.*time.*offer', r'winner.*prize',
    r'free.*gift', r'congratulations.*won', r'reset.*password.*now',
]

SUSPICIOUS_DOMAINS = [
    'secure-', 'login-', 'verify-', 'account-', 'update-', 'confirm-',
    '-secure', '-login', '-verify', '-account', '-update', '-confirm',
    'paypal', 'amazon', 'apple', 'microsoft', 'google', 'facebook',
    'instagram', 'netflix', 'bank', 'signin', 'webscr'
]

SUSPICIOUS_TLDS = [
    '.xyz', '.top', '.club', '.online', '.site', '.tk', '.ml', '.ga',
    '.cf', '.gq', '.work', '.click', '.link', '.loan', '.win', '.download'
]

def analyze_url(url: str) -> dict:
    url_lower = url.lower()
    score = 0

    for pattern in PHISHING_PATTERNS:
        if re.search(pattern, url_lower):
            score += 30
            break

    try:
        domain = url_lower.split('/')[2] if '/' in url_lower else url_lower
        for keyword in SUSPICIOUS_DOMAINS:
            if keyword in domain:
                score += 20
                break
    except:
        pass

    for tld in SUSPICIOUS_TLDS:
        if url_lower.endswith(tld) or tld + '/' in url_lower:
            score += 25
            break

    if re.search(r'https?://\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', url_lower):
        score += 40

    try:
        domain = url_lower.split('/')[2] if '/' in url_lower else url_lower
        if domain.count('.') > 3:
            score += 15
    except:
        pass

    if len(url) > 100:
        score += 10

    if '@' in url:
        score += 30

    if url_lower.startswith('http://'):
        score += 10

    score = min(score, 100)
    legit_pct = round(100 - score, 2)
    phish_pct = round(float(score), 2)

    return {
        "label": "PHISHING" if score >= 40 else "LEGIT",
        "confidence": max(legit_pct, phish_pct),
        "scores": {
            "legit": legit_pct,
            "phishing": phish_pct
        }
    }

@app.get("/")
def root():
    return {"status": "CyberKareem URL Detector is running"}

@app.post("/predict")
def predict(req: URLRequest):
    return analyze_url(req.url)