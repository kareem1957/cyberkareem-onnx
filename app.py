from fastapi import FastAPI
from pydantic import BaseModel
import numpy as np
from huggingface_hub import hf_hub_download
import onnxruntime as ort

app = FastAPI(title="CyberKareem URL Detector API")

SPAM_KEYWORDS = [
    "win", "winner", "prize", "offer", "deal", "discount", "sale", "free",
    "buy now", "limited time", "click here", "subscribe", "unsubscribe",
    "congratulations", "selected", "reward", "gift", "claim", "promotion",
    "advertisement", "marketing", "shop", "order now", "exclusive", "percent off"
]

print("Loading model...")
model_path = hf_hub_download(
    repo_id="Kareem171833/cyberkareem-model",
    filename="model.onnx"
)
session = ort.InferenceSession(model_path, providers=["CPUExecutionProvider"])
print("Model ready!")

class URLRequest(BaseModel):
    url: str

@app.get("/")
def root():
    return {"status": "CyberKareem URL Detector is running"}

@app.post("/predict")
def predict(req: URLRequest):
    inputs = {"inputs": np.array([req.url])}
    label, probs = session.run(["label", "probabilities"], inputs)

    legit_pct = round(float(probs[0][0]) * 100, 2)
    phish_pct = round(float(probs[0][1]) * 100, 2)

    text_lower = req.url.lower()
    has_spam = any(word in text_lower for word in SPAM_KEYWORDS)

    if label[0] == 1 and phish_pct >= 60:
        result_label = "PHISHING"
    elif has_spam and phish_pct < 60:
        result_label = "SPAM"
    else:
        result_label = "LEGIT"

    return {
        "label": result_label,
        "confidence": max(legit_pct, phish_pct),
        "scores": {
            "legit": legit_pct,
            "phishing": phish_pct
        }
    }