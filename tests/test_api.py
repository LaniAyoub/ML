"""
Test suite for API endpoints
"""
import pytest
from fastapi.testclient import TestClient
from src.predict_api import app


client = TestClient(app)


def test_health_endpoint():
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "model_loaded" in data
    assert "timestamp" in data


def test_root_endpoint():
    """Test root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data


def test_metrics_endpoint():
    """Test metrics endpoint."""
    response = client.get("/metrics")
    assert response.status_code == 200
    data = response.json()
    assert "total_predictions" in data
    assert "predictions_by_risk" in data
    assert "average_churn_probability" in data


def test_predict_endpoint_valid():
    """Test prediction with valid data."""
    customer_data = {
        "gender": "Female",
        "SeniorCitizen": 0,
        "Partner": "No",
        "Dependents": "No",
        "tenure": 1,
        "PhoneService": "Yes",
        "MultipleLines": "No",
        "InternetService": "Fiber optic",
        "OnlineSecurity": "No",
        "OnlineBackup": "No",
        "DeviceProtection": "No",
        "TechSupport": "No",
        "StreamingTV": "No",
        "StreamingMovies": "No",
        "Contract": "Month-to-month",
        "PaperlessBilling": "Yes",
        "PaymentMethod": "Electronic check",
        "MonthlyCharges": 70.35,
        "TotalCharges": "70.35"
    }
    
    response = client.post("/predict", json=customer_data)
    assert response.status_code == 200
    
    data = response.json()
    assert "churn_prediction" in data
    assert "churn_probability" in data
    assert "risk_level" in data
    assert "customer_id" in data
    assert data["churn_prediction"] in [0, 1]
    assert 0 <= data["churn_probability"] <= 1
    assert data["risk_level"] in ["low", "medium", "high"]


def test_predict_endpoint_invalid_totalcharges():
    """Test prediction with invalid TotalCharges."""
    customer_data = {
        "gender": "Female",
        "SeniorCitizen": 0,
        "Partner": "No",
        "Dependents": "No",
        "tenure": 1,
        "PhoneService": "Yes",
        "MultipleLines": "No",
        "InternetService": "Fiber optic",
        "OnlineSecurity": "No",
        "OnlineBackup": "No",
        "DeviceProtection": "No",
        "TechSupport": "No",
        "StreamingTV": "No",
        "StreamingMovies": "No",
        "Contract": "Month-to-month",
        "PaperlessBilling": "Yes",
        "PaymentMethod": "Electronic check",
        "MonthlyCharges": 70.35,
        "TotalCharges": "invalid_value"
    }
    
    response = client.post("/predict", json=customer_data)
    assert response.status_code == 422  # Validation error


def test_predict_endpoint_missing_field():
    """Test prediction with missing required field."""
    customer_data = {
        "gender": "Female",
        "SeniorCitizen": 0,
        # Missing Partner field
        "Dependents": "No",
        "tenure": 1,
    }
    
    response = client.post("/predict", json=customer_data)
    assert response.status_code == 422  # Validation error


def test_batch_predict_endpoint():
    """Test batch prediction endpoint."""
    customers = [
        {
            "gender": "Female",
            "SeniorCitizen": 0,
            "Partner": "No",
            "Dependents": "No",
            "tenure": 1,
            "PhoneService": "Yes",
            "MultipleLines": "No",
            "InternetService": "Fiber optic",
            "OnlineSecurity": "No",
            "OnlineBackup": "No",
            "DeviceProtection": "No",
            "TechSupport": "No",
            "StreamingTV": "No",
            "StreamingMovies": "No",
            "Contract": "Month-to-month",
            "PaperlessBilling": "Yes",
            "PaymentMethod": "Electronic check",
            "MonthlyCharges": 70.35,
            "TotalCharges": "70.35"
        }
    ]
    
    response = client.post("/predict/batch", json=customers)
    assert response.status_code == 200
    
    data = response.json()
    assert "predictions" in data
    assert "total" in data
    assert "successful" in data
    assert data["total"] == len(customers)
