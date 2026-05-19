from fastapi import FastAPI
from pydantic import BaseModel
import numpy as np
from huggingface_hub import hf_hub_download
import onnxruntime as ort

app = FastAPI(title="CyberKareem URL Detector API")

class URLRequest(BaseModel):
    url: str

print("Loading model...")
model_path = hf_hub_download(
    repo_id="Kareem171833/cyberkareem-model",
    filename="model.onnx"
)
session = ort.InferenceSession(model_path, providers=["CPUExecutionProvider"])
print("Model ready!")

@app.get("/")
def root():
    return {"status": "CyberKareem URL Detector is running"}

@app.post("/predict")
def predict(req: URLRequest):
    inputs = {"inputs": np.array([req.url])}
    label, probs = session.run(["label", "probabilities"], inputs)
    legit_pct = round(float(probs[0][0]) * 100, 2)
    phish_pct = round(float(probs[0][1]) * 100, 2)
    return {
        "label": "PHISHING" if label[0] == 1 else "LEGIT",
        "confidence": max(legit_pct, phish_pct),
        "scores": {
            "legit": legit_pct,
            "phishing": phish_pct
        }
    }