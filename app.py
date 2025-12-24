from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import joblib

app = FastAPI(title="AI SQL Injection Firewall")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Load model AND vectorizer
model = joblib.load("models/sqli_rf_model.pkl")
vectorizer = joblib.load("models/sqli_tfidf_vectorizer.pkl")

class SQLInput(BaseModel):
    text: str

@app.post("/predict_sqli")
def predict_sqli(data: SQLInput):
    X = vectorizer.transform([data.text])
    prediction = model.predict(X)[0]

    if prediction == 1:
        raise HTTPException(
            status_code=403,
            detail="Blocked: SQL Injection detected"
        )

    return {
        "status": "allowed",
        "message": "Input is safe"
    }

@app.get("/")
def health():
    return {"status": "API running"}
