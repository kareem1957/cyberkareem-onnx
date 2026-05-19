from fastapi import FastAPI
from pydantic import BaseModel
import subprocess
import json
import sys
from huggingface_hub import hf_hub_download

app = FastAPI(title="CyberKareem URL Detector API")

print("Loading model...")
model_path = hf_hub_download(
    repo_id="Kareem171833/cyberkareem-model",
    filename="model.onnx"
)

app_code = '''
import onnxruntime as ort
import numpy as np
import sys
import json

model_path = sys.argv[1]
url = sys.argv[2]
session = ort.InferenceSession(model_path)
inputs = {"inputs": np.array([url])}
label, probs = session.run(["label", "probabilities"], inputs)
print(json.dumps({
    "label": int(label[0]),
    "legit": float(probs[0][0]),
    "phishing": float(probs[0][1])
}))
'''

with open("/app/run_model.py", "w") as f:
    f.write(app_code)

print("Model ready!")

class URLRequest(BaseModel):
    url: str

@app.get("/")
def root():
    return {"status": "CyberKareem URL Detector is running"}

@app.post("/predict")
def predict(req: URLRequest):
    result = subprocess.run(
        [sys.executable, "/app/run_model.py", model_path, req.url],
        capture_output=True, text=True
    )

    if result.returncode != 0:
        return {"error": result.stderr}

    data = json.loads(result.stdout)
    legit_pct = round(data["legit"] * 100, 2)
    phish_pct = round(data["phishing"] * 100, 2)

    return {
        "label": "PHISHING" if data["label"] == 1 else "LEGIT",
        "confidence": max(legit_pct, phish_pct),
        "scores": {
            "legit": legit_pct,
            "phishing": phish_pct
        }
    }