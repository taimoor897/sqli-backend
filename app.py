from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import joblib
import re
import os

# ---------------- App Setup ----------------
app = FastAPI(title="AI SQL Injection Firewall API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # GitHub Pages + public access
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------- Load ML Model ----------------
model = joblib.load("sqli_rf_model.pkl")

# ---------------- Request Schema ----------------
class SQLInput(BaseModel):
    text: str

# ---------------- Feature Engineering ----------------
def extract_features(text: str):
    return [
        len(text),
        int(bool(re.search(r"('|--|;|/\*|\*/)", text))),
        int(bool(re.search(r"\b(select|union|drop|insert|delete|update)\b", text.lower())))
    ]

# ---------------- Prediction Endpoint ----------------
@app.post("/predict_sqli")
def analyze_input(data: SQLInput):
    text = data.text.lower()

    # 🔥 hard rule for classic SQLi
    if re.search(r"\bor\b\s+1\s*=\s*1", text):
        raise HTTPException(
            status_code=403,
            detail="Blocked: Boolean-based SQL Injection detected"
        )

    features = [extract_features(data.text)]
    prediction = model.predict(features)[0]

    if prediction == 1:
        raise HTTPException(
            status_code=403,
            detail="Blocked: SQL Injection detected by ML"
        )

    return {
        "status": "allowed",
        "message": "Input is safe"
    }


# ---------------- Health Check ----------------
@app.get("/")
def health():
    return {"status": "API running"}

# ---------------- Railway Entry ----------------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 8000))
    )
