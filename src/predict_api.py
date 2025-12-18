"""
Prediction API Module
FastAPI service for serving churn predictions with monitoring.
"""
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field, validator
import pandas as pd
import joblib
import logging
from datetime import datetime
from typing import Dict, List, Optional
import json
from pathlib import Path
import numpy as np
import os

from src.preprocessing import CustomEncoder

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Pydantic models
class CustomerData(BaseModel):
    """Customer data schema for prediction."""
    gender: str = Field(..., description="Gender: Male or Female")
    SeniorCitizen: int = Field(..., ge=0, le=1, description="Senior citizen: 0 or 1")
    Partner: str = Field(..., description="Has partner: Yes or No")
    Dependents: str = Field(..., description="Has dependents: Yes or No")
    tenure: int = Field(..., ge=0, description="Months with company")
    PhoneService: str = Field(..., description="Has phone service: Yes or No")
    MultipleLines: str = Field(..., description="Has multiple lines")
    InternetService: str = Field(..., description="Internet service type")
    OnlineSecurity: str = Field(..., description="Has online security")
    OnlineBackup: str = Field(..., description="Has online backup")
    DeviceProtection: str = Field(..., description="Has device protection")
    TechSupport: str = Field(..., description="Has tech support")
    StreamingTV: str = Field(..., description="Has streaming TV")
    StreamingMovies: str = Field(..., description="Has streaming movies")
    Contract: str = Field(..., description="Contract type")
    PaperlessBilling: str = Field(..., description="Uses paperless billing: Yes or No")
    PaymentMethod: str = Field(..., description="Payment method")
    MonthlyCharges: float = Field(..., gt=0, description="Monthly charges")
    TotalCharges: object = Field(..., description="Total charges")
    
    @validator('TotalCharges')
    def validate_total_charges(cls, v):
        """Validate TotalCharges can be converted to numeric."""
        try:
            float(v)
            return v
        except (ValueError, TypeError):
            raise ValueError("TotalCharges must be a valid number")


class PredictionResponse(BaseModel):
    """Response schema for predictions."""
    customer_id: str
    churn_prediction: int
    churn_probability: float
    risk_level: str
    timestamp: str


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    model_loaded: bool
    timestamp: str
    version: str


class MetricsResponse(BaseModel):
    """API metrics response."""
    total_predictions: int
    predictions_by_risk: Dict[str, int]
    average_churn_probability: float
    model_info: Dict[str, str]


# Prediction tracker for monitoring
class PredictionTracker:
    """Track predictions for monitoring and analytics."""
    
    def __init__(self, log_file: str = "logs/predictions.jsonl"):
        self.log_file = log_file
        Path(log_file).parent.mkdir(exist_ok=True)
        self.predictions: List[Dict] = []
        
    def log_prediction(self, customer_data: dict, prediction: int, 
                      probability: float, risk_level: str):
        """Log a prediction for monitoring."""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "prediction": int(prediction),
            "probability": float(probability),
            "risk_level": risk_level,
            "customer_data": customer_data
        }
        
        # Append to in-memory list
        self.predictions.append(log_entry)
        
        # Write to file
        with open(self.log_file, 'a') as f:
            f.write(json.dumps(log_entry) + '\n')
    
    def get_metrics(self) -> dict:
        """Get aggregated metrics."""
        if not self.predictions:
            return {
                "total_predictions": 0,
                "predictions_by_risk": {},
                "average_churn_probability": 0.0
            }
        
        risk_counts = {}
        for pred in self.predictions:
            risk_level = pred['risk_level']
            risk_counts[risk_level] = risk_counts.get(risk_level, 0) + 1
        
        avg_prob = np.mean([p['probability'] for p in self.predictions])
        
        return {
            "total_predictions": len(self.predictions),
            "predictions_by_risk": risk_counts,
            "average_churn_probability": float(avg_prob)
        }


# Initialize FastAPI app
app = FastAPI(
    title="Telco Churn Prediction API",
    description="API for predicting customer churn with ML model",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variables
model = None
tracker = PredictionTracker()
model_info = {}


@app.on_event("startup")
async def load_model():
    """Load model on startup."""
    global model, model_info
    
    try:
        model_path = "models/final_churn_prediction_pipeline.pkl"
        model = joblib.load(model_path)
        logger.info(f"Model loaded successfully from {model_path}")
        
        # Load model metrics if available
        metrics_path = "models/final_churn_prediction_pipeline_metrics.json"
        if Path(metrics_path).exists():
            with open(metrics_path, 'r') as f:
                model_info = json.load(f)
            logger.info("Model metrics loaded")
        
    except Exception as e:
        logger.error(f"Failed to load model: {e}")
        model = None


# Mount static files for frontend
frontend_path = Path("frontend")
if frontend_path.exists():
    app.mount("/static", StaticFiles(directory=str(frontend_path)), name="static")
    logger.info("Frontend static files mounted at /static")


@app.get("/", include_in_schema=False)
async def serve_frontend():
    """Serve the frontend dashboard."""
    frontend_file = frontend_path / "index.html"
    if frontend_file.exists():
        return FileResponse(str(frontend_file))
    else:
        return {"message": "Frontend not available", "api_docs": "/docs"}


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Detailed health check."""
    return HealthResponse(
        status="healthy" if model is not None else "unhealthy",
        model_loaded=model is not None,
        timestamp=datetime.now().isoformat(),
        version="1.0.0"
    )


@app.post("/predict", response_model=PredictionResponse)
async def predict_churn(data: CustomerData):
    """Predict churn for a customer."""
    if model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    try:
        # Convert to DataFrame
        df = pd.DataFrame([data.dict()])
        df['TotalCharges'] = pd.to_numeric(df['TotalCharges'], errors='coerce')
        
        # Validate TotalCharges
        if df['TotalCharges'].isna().any():
            raise HTTPException(status_code=400, detail="Invalid TotalCharges value")
        
        # Make prediction
        prediction = model.predict(df)[0]
        probability = model.predict_proba(df)[0][1]
        
        # Determine risk level
        if probability < 0.3:
            risk_level = "low"
        elif probability < 0.6:
            risk_level = "medium"
        else:
            risk_level = "high"
        
        # Generate customer ID
        customer_id = f"CUST_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # Log prediction
        tracker.log_prediction(
            customer_data=data.dict(),
            prediction=prediction,
            probability=probability,
            risk_level=risk_level
        )
        
        return PredictionResponse(
            customer_id=customer_id,
            churn_prediction=int(prediction),
            churn_probability=float(probability),
            risk_level=risk_level,
            timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        logger.error(f"Prediction failed: {e}")
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")


@app.post("/predict/batch")
async def predict_batch(customers: List[CustomerData]):
    """Batch prediction endpoint."""
    if model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    results = []
    for customer in customers:
        try:
            result = await predict_churn(customer)
            results.append(result)
        except Exception as e:
            logger.error(f"Batch prediction error: {e}")
            results.append({"error": str(e)})
    
    return {"predictions": results, "total": len(customers), "successful": len([r for r in results if "error" not in r])}


@app.get("/metrics", response_model=MetricsResponse)
async def get_metrics():
    """Get API metrics."""
    metrics = tracker.get_metrics()
    
    return MetricsResponse(
        total_predictions=metrics['total_predictions'],
        predictions_by_risk=metrics['predictions_by_risk'],
        average_churn_probability=metrics['average_churn_probability'],
        model_info={
            "model_name": model_info.get('model_name', 'unknown'),
            "training_date": model_info.get('timestamp', 'unknown'),
            "test_f1_score": str(model_info.get('test_f1_score', 'N/A')),
            "test_roc_auc": str(model_info.get('test_roc_auc', 'N/A'))
        }
    )


@app.get("/model-info")
async def get_model_info():
    """Get detailed model information."""
    if not model_info:
        raise HTTPException(status_code=404, detail="Model info not available")
    
    return model_info


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
