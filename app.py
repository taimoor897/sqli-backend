from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import joblib

# ---------------- App Setup ----------------
app = FastAPI(title="SQL Injection Detection API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------- Load Model & Vectorizer ----------------
model = joblib.load("sqli_rf_model.pkl")
vectorizer = joblib.load("sqli_tfidf_vectorizer.pkl")

# ---------------- Request Schema ----------------
class SQLInput(BaseModel):
    text: str

# ---------------- API Endpoint ----------------
@app.post("/predict_sqli")
def predict_sqli(data: SQLInput):
    try:
        X = vectorizer.transform([data.text])
        prediction = model.predict(X)[0]

        if int(prediction) == 1:
            raise HTTPException(
                status_code=403,
                detail="Blocked: SQL Injection detected"
            )

        return {
            "status": "allowed",
            "message": "Input is safe"
        }

    except HTTPException:
        raise
    except Exception as e:
        print("MODEL ERROR:", e)
        raise HTTPException(
            status_code=500,
            detail="Model processing error"
        )

# ---------------- Health Check ----------------
@app.get("/")
def health():
    return {"status": "API running"}
