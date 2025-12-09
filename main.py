
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import pandas as pd
import joblib


from preprocessing import CustomEncoder,ThresholdClassifier

class CustomerData(BaseModel):
    gender: str
    SeniorCitizen: int
    Partner: str
    Dependents: str
    tenure: int
    PhoneService: str
    MultipleLines: str
    InternetService: str
    OnlineSecurity: str
    OnlineBackup: str
    DeviceProtection: str
    TechSupport: str
    StreamingTV: str
    StreamingMovies: str
    Contract: str
    PaperlessBilling: str
    PaymentMethod: str
    MonthlyCharges: float
    TotalCharges: object

app = FastAPI()

try:
    model = joblib.load('final_churn_prediction_pipeline.pkl')
    print("Final Model Pipeline loaded successfully.")
except Exception as e:
    print(f"CRITICAL ERROR: {e}")
    model = None

@app.post("/predict")
def predict_churn(data: CustomerData):
    if model is None:
        raise HTTPException(status_code=500, detail="Model not loaded.")
    
    df = pd.DataFrame([data.dict()])
    df['TotalCharges'] = pd.to_numeric(df['TotalCharges'], errors='coerce')

    if df['TotalCharges'].isna().any():
        raise HTTPException(status_code=400, detail="Invalid TotalCharges.")

    try:
        prediction = model.predict(df)
        probability = model.predict_proba(df)[0][1]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Pipeline failed: {e}")

    return {
        "churn_prediction": int(prediction[0]),
        "churn_probability": float(probability)
    }