# Telco Customer Churn Prediction - MLOps Project

![Churn Prediction](https://img.shields.io/badge/ML-Churn%20Prediction-blue)
![Python](https://img.shields.io/badge/Python-3.10-green)
![FastAPI](https://img.shields.io/badge/FastAPI-0.103-009688)
![Docker](https://img.shields.io/badge/Docker-Enabled-2496ED)

## 📋 Project Overview

A complete end-to-end MLOps solution for predicting customer churn in the telecommunications industry. This project demonstrates best practices in:

- **Data Science**: EDA, feature engineering, model training with hyperparameter tuning
- **MLOps**: Modular code structure, containerization, API deployment
- **Monitoring**: Real-time metrics, performance tracking, visualization dashboards
- **Production-Ready**: Docker orchestration, health checks, logging

## 🏗️ Architecture

```
┌─────────────────┐     ┌──────────────┐     ┌─────────────┐
│   Frontend      │────▶│  FastAPI     │────▶│  ML Model   │
│   Dashboard     │     │  Service     │     │  Pipeline   │
└─────────────────┘     └──────────────┘     └─────────────┘
         │                      │                     │
         │                      ▼                     │
         │              ┌──────────────┐              │
         └─────────────▶│  Prometheus  │◀─────────────┘
                        │  & Grafana   │
                        └──────────────┘
```

### Components

1. **Data Processing Layer** (`src/data_preprocessing.py`)
   - Data loading and cleaning
   - Feature extraction
   - Train/test splitting with stratification

2. **Model Training Layer** (`src/train_model.py`)
   - Custom transformers for encoding
   - Feature selection with SelectKBest
   - SVM classifier with RandomizedSearchCV
   - Model evaluation and metrics storage

3. **API Service Layer** (`src/predict_api.py`)
   - RESTful API with FastAPI
   - Request validation with Pydantic
   - Prediction logging and tracking
   - Health checks and metrics endpoints

4. **Frontend Dashboard** (`frontend/`)
   - Interactive web interface
   - Real-time predictions
   - Metrics visualization
   - Risk-based recommendations

5. **Monitoring Stack**
   - Prometheus for metrics collection
   - Grafana for visualization
   - Custom prediction tracking

## 🚀 Quick Start

### Prerequisites

- Docker and Docker Compose
- Python 3.10+ (for local development)
- 4GB RAM minimum

### Installation

1. **Clone the repository**
```powershell
git clone <repository-url>
cd Churn_predection
```

2. **Prepare the data**
```powershell
# Ensure data file is in the data/ directory
mkdir data
# Copy WA_Fn-UseC_-Telco-Customer-Churn.csv to data/
```

3. **Train the model (optional - model already included)**
```powershell
python src/train_model.py
```

4. **Start all services with Docker**
```powershell
docker-compose up --build
```

This will start:
- API Service: http://localhost:8000
- Frontend Dashboard: http://localhost:3000
- Prometheus: http://localhost:9090
- Grafana: http://localhost:3001

## 📊 Usage

### Web Dashboard

Navigate to `http://localhost:3000` to access the interactive dashboard:

1. Fill in customer information
2. Click "Predict Churn Risk"
3. View prediction results with risk level
4. Monitor overall statistics and model performance

### API Endpoints

**Health Check**
```powershell
Invoke-RestMethod -Uri "http://localhost:8000/health"
```

**Single Prediction**
```powershell
$body = @{
    gender = "Female"
    SeniorCitizen = 0
    Partner = "No"
    Dependents = "No"
    tenure = 1
    PhoneService = "Yes"
    MultipleLines = "No"
    InternetService = "Fiber optic"
    OnlineSecurity = "No"
    OnlineBackup = "No"
    DeviceProtection = "No"
    TechSupport = "No"
    StreamingTV = "No"
    StreamingMovies = "No"
    Contract = "Month-to-month"
    PaperlessBilling = "Yes"
    PaymentMethod = "Electronic check"
    MonthlyCharges = 70.35
    TotalCharges = "70.35"
} | ConvertTo-Json

Invoke-RestMethod -Method Post -Uri "http://localhost:8000/predict" -Body $body -ContentType "application/json"
```

**Get Metrics**
```powershell
Invoke-RestMethod -Uri "http://localhost:8000/metrics"
```

**Model Information**
```powershell
Invoke-RestMethod -Uri "http://localhost:8000/model-info"
```

## 🔧 Development

### Local Development Setup

1. **Create virtual environment**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

2. **Install dependencies**
```powershell
pip install -r requirements.txt
```

3. **Run API locally**
```powershell
uvicorn src.predict_api:app --reload --host 0.0.0.0 --port 8000
```

### Project Structure

```
Churn_predection/
├── src/
│   ├── data_preprocessing.py    # Data loading and cleaning
│   ├── train_model.py            # Model training pipeline
│   └── predict_api.py            # FastAPI service
├── frontend/
│   ├── index.html                # Dashboard UI
│   ├── script.js                 # Frontend logic
│   ├── Dockerfile                # Frontend container
│   └── nginx.conf                # Nginx configuration
├── monitoring/
│   ├── prometheus.yml            # Prometheus config
│   └── grafana/                  # Grafana dashboards
├── models/
│   ├── *.pkl                     # Trained models
│   └── *_metrics.json            # Model metrics
├── data/
│   └── *.csv                     # Training data
├── logs/
│   └── predictions.jsonl         # Prediction logs
├── preprocessing.py              # Custom transformers
├── Dockerfile                    # API container
├── docker-compose.yml            # Orchestration
├── requirements.txt              # Python dependencies
└── README.md                     # This file
```

## 📈 Model Performance

The SVM-based model achieves:

- **F1 Score**: ~0.62 (optimized for imbalanced data)
- **ROC-AUC**: ~0.85
- **Precision**: High precision for churn prediction
- **Recall**: Balanced to catch most churners

### Feature Engineering

1. **Custom Encoding**
   - Binary features: Yes/No → 1/0
   - Gender: Male/Female → 1/0
   - Contract: Ordinal encoding (Month-to-month=0, One year=1, Two year=2)

2. **One-Hot Encoding**
   - Internet service type
   - Payment method
   - Service add-ons

3. **Feature Selection**
   - SelectKBest with f_classif
   - Optimized through hyperparameter tuning

## 🔍 Monitoring & Observability

### Metrics Available

- Total predictions made
- Predictions by risk level (low/medium/high)
- Average churn probability
- Model performance metrics
- API health status

### Grafana Dashboards

Access Grafana at `http://localhost:3001`:
- Default credentials: admin/admin
- Pre-configured dashboards for:
  - API performance
  - Prediction statistics
  - Model metrics over time

## 🧪 Testing

Run tests with pytest:

```powershell
pytest tests/ -v
```

## 🐳 Docker Commands

**Build and start all services:**
```powershell
docker-compose up --build
```

**Start in detached mode:**
```powershell
docker-compose up -d
```

**View logs:**
```powershell
docker-compose logs -f
```

**Stop all services:**
```powershell
docker-compose down
```

**Remove volumes:**
```powershell
docker-compose down -v
```

## 📝 Data Schema

### Input Features

| Feature | Type | Description |
|---------|------|-------------|
| gender | string | Customer gender (Male/Female) |
| SeniorCitizen | int | Senior citizen (0/1) |
| Partner | string | Has partner (Yes/No) |
| Dependents | string | Has dependents (Yes/No) |
| tenure | int | Months with company |
| PhoneService | string | Has phone service |
| MultipleLines | string | Has multiple lines |
| InternetService | string | Internet service type |
| OnlineSecurity | string | Has online security |
| OnlineBackup | string | Has online backup |
| DeviceProtection | string | Has device protection |
| TechSupport | string | Has tech support |
| StreamingTV | string | Has streaming TV |
| StreamingMovies | string | Has streaming movies |
| Contract | string | Contract type |
| PaperlessBilling | string | Uses paperless billing |
| PaymentMethod | string | Payment method |
| MonthlyCharges | float | Monthly charges ($) |
| TotalCharges | string/float | Total charges ($) |

### Output Schema

```json
{
  "customer_id": "CUST_20231217143022",
  "churn_prediction": 1,
  "churn_probability": 0.78,
  "risk_level": "high",
  "timestamp": "2023-12-17T14:30:22"
}
```

## 🎯 Key Insights

From exploratory data analysis:

**High Churn Risk Factors:**
- Month-to-month contracts
- Fiber optic internet without security/backup services
- Electronic check payment method
- Paperless billing
- No partner or dependents

**Low Churn Risk Factors:**
- Long-term contracts (1-2 years)
- Longer tenure
- Multiple services bundled
- Automatic payment methods

## 🔐 Security

- API validation with Pydantic
- Docker container isolation
- No sensitive data in logs
- Environment variable configuration
- CORS properly configured

## 📄 License

This project is for educational and demonstration purposes.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## 📧 Contact

For questions or support, please open an issue in the repository.

---

**Built with ❤️ using Python, FastAPI, Docker, and modern MLOps practices**
