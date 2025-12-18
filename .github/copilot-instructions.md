# Churn Prediction MLOps Project - AI Coding Agent Instructions

## Project Overview
**Enterprise-grade MLOps solution** for telco customer churn prediction featuring:
- Production-ready ML pipeline with scikit-learn
- RESTful API service with FastAPI
- Interactive web dashboard
- Docker containerization & orchestration
- Monitoring with Prometheus & Grafana
- Comprehensive test suite

**Tech Stack**: Python 3.10 | FastAPI | Docker | scikit-learn | Bootstrap | Chart.js | Nginx

## 🏗️ Architecture & System Components

### Service Architecture
```
Frontend (Nginx:80) → API (FastAPI:8000) → ML Model (sklearn Pipeline)
                  ↓
           Prometheus:9090 → Grafana:3001
```

### ML Pipeline (`src/train_model.py`)
1. **Data Preprocessing** (`DataPreprocessor`) - Load, clean, split with stratification
2. **Custom Encoding** (`CustomEncoder`) - Domain-specific feature encoding
3. **One-Hot Encoding** (`ColumnTransformer`) - Nominal categorical features
4. **Feature Selection** (`SelectKBest`) - f_classif scoring, k optimized via CV
5. **Scaling** (`StandardScaler`) - Feature normalization
6. **Classifier** (`SVC`) - RBF/linear kernel with probability estimates
7. **Hyperparameter Tuning** (`RandomizedSearchCV`) - F1-optimized (class imbalance)

**Serialization**: Model → `models/final_churn_prediction_pipeline.pkl` (joblib)

### API Service (`src/predict_api.py`)
- **Framework**: FastAPI with Pydantic validation
- **Endpoints**: `/predict`, `/predict/batch`, `/metrics`, `/health`, `/model-info`
- **Monitoring**: Prediction logging to `logs/predictions.jsonl`
- **Error Handling**: HTTP 400 (validation), 500 (model), 503 (unavailable)

### Frontend Dashboard (`frontend/`)
- **Stack**: HTML5 + Bootstrap 5 + Chart.js + Vanilla JS
- **Features**: Real-time predictions, risk visualization, metrics dashboard
- **Deployment**: Nginx reverse proxy to API

### Custom Transformers (`preprocessing.py`)

**CustomEncoder**: Manual encoding for domain-specific features
- Binary features (`Partner`, `Dependents`, `PhoneService`, `PaperlessBilling`): Yes=1, No=0
- Gender: Male=1, Female=0
- Contract: Month-to-month=0, One year=1, Two year=2
- Always inherits from `BaseEstimator, TransformerMixin` for scikit-learn compatibility

**ThresholdClassifier**: Meta-classifier wrapper for custom decision thresholds
- Wraps any estimator with `decision_function()` method
- Adjusts classification threshold without retraining
- Must implement `fit()`, `predict()`, `predict_proba()`, and `decision_function()`
- Set `self.classes_` attribute during fit for sklearn compatibility

## Key Patterns & Conventions

### Data Preprocessing
- **TotalCharges** is initially loaded as object/string - ALWAYS convert using `pd.to_numeric(..., errors='coerce')` before training
- Drop NaN rows after conversion (handled via `data_to_keep` index filtering)
- Remove `customerID` and `Churn` columns from features (X)
- Target `Churn`: Yes=1, No=0

### Feature Engineering Strategy
- **Binary encodings** for clear yes/no features
- **Ordinal encoding** for contract type (reflects commitment level)
- **OneHotEncoder** for truly nominal features (payment method, internet service type, etc.)
- `remainder='passthrough'` in ColumnTransformer to keep already-encoded features
- `verbose_feature_names_out=False` to maintain clean feature names

### Hyperparameter Tuning
- Use `RandomizedSearchCV` with `scoring="f1"` (imbalanced dataset: 26% churn)
- Pipeline parameter syntax: `'selector__k'`, `'svc__C'`, `'svc__gamma'`
- CV=4, n_iter=40 for reasonable exploration vs. runtime tradeoff
- `stratify=y_cleaned` during train/test split to maintain class balance

### FastAPI Service (`main.py`)

**Data Model**: `CustomerData` (Pydantic) mirrors CSV columns exactly
- `TotalCharges` typed as `object` to accept string input from clients
- Convert to numeric inside prediction endpoint: `pd.to_numeric(df['TotalCharges'], errors='coerce')`
- Raise 400 error if TotalCharges contains invalid values after conversion

**Endpoints**:
- POST `/predict` - Accepts single customer record, returns `churn_prediction` (0/1) and `churn_probability` (float)

**Model Loading**:
- Load pipeline at startup with try-except error handling
- Set `model = None` if loading fails, check in endpoint

## 🔧 Development Workflows

### Setup & Organization
```powershell
# Initial setup (organizes files into proper structure)
python setup_project.py

# Install dependencies
pip install -r requirements.txt
```

### Training Workflow
```powershell
# Full training pipeline with hyperparameter tuning
python src/train_model.py

# Outputs:
# - models/final_churn_prediction_pipeline.pkl
# - models/final_churn_prediction_pipeline_metrics.json
```

### Local API Development
```powershell
# Run with hot-reload
uvicorn src.predict_api:app --reload --host 0.0.0.0 --port 8000

# Test endpoints
Invoke-RestMethod -Uri "http://localhost:8000/health"
Invoke-RestMethod -Uri "http://localhost:8000/docs"  # Swagger UI
```

### Docker Deployment
```powershell
# Build and start all services (API + Frontend + Monitoring)
docker-compose up --build

# Start in background
docker-compose up -d

# View logs
docker-compose logs -f api

# Stop all
docker-compose down
```

### Testing
```powershell
# Run all tests
pytest tests/ -v

# With coverage report
pytest tests/ --cov=src --cov-report=html

# Specific test file
pytest tests/test_api.py -v
```

### Quick Prediction Test
```powershell
$body = @{
    gender = "Female"; SeniorCitizen = 0; Partner = "No"
    Dependents = "No"; tenure = 1; PhoneService = "Yes"
    MultipleLines = "No"; InternetService = "Fiber optic"
    OnlineSecurity = "No"; OnlineBackup = "No"
    DeviceProtection = "No"; TechSupport = "No"
    StreamingTV = "No"; StreamingMovies = "No"
    Contract = "Month-to-month"; PaperlessBilling = "Yes"
    PaymentMethod = "Electronic check"
    MonthlyCharges = 70.35; TotalCharges = "70.35"
} | ConvertTo-Json

Invoke-RestMethod -Method Post -Uri "http://localhost:8000/predict" -Body $body -ContentType "application/json"
```

## Critical Domain Knowledge (from `preparation.txt`)

### Target Distribution
- 73% No Churn (5174 samples)
- 27% Churn (1869 samples)
- **Use F1 score** for evaluation due to class imbalance

### Key Churn Indicators
- **High churn risk**: Month-to-month contract, no partner/dependents, Fiber Optic internet, no online security/backup, PaperlessBilling, Electronic check payment
- **Low churn risk**: Longer tenure, long-term contracts (One/Two year)
- **No significant effect**: Gender, StreamingTV/Movies, age, charges

### Feature Dependencies
Several features depend on others (use "No internet service" or "No phone service" values):
- `MultipleLines` depends on `PhoneService`
- `OnlineSecurity`, `DeviceProtection`, `TechSupport`, `StreamingTV`, `StreamingMovies` depend on `InternetService`

## Dependencies (`requirments.txt`)
- scikit-learn, pandas, numpy - ML pipeline
- fastapi, uvicorn, pydantic - API serving
- joblib - model serialization
- matplotlib - visualization (notebooks only)

## 📁 Project Structure & File Organization

```
Churn_predection/
├── src/                              # ⭐ Core application code
│   ├── data_preprocessing.py         # DataPreprocessor class - ETL pipeline
│   ├── train_model.py                # ModelTrainer class - training workflow
│   ├── predict_api.py                # FastAPI app - prediction service
│   └── preprocessing.py              # CustomEncoder, ThresholdClassifier
├── frontend/                         # 🎨 Web dashboard
│   ├── index.html                    # Main UI (Bootstrap 5)
│   ├── script.js                     # Dashboard logic + Chart.js
│   ├── Dockerfile                    # Nginx container
│   └── nginx.conf                    # Reverse proxy config
├── monitoring/                       # 📊 Observability
│   ├── prometheus.yml                # Metrics collection
│   └── grafana/                      # Dashboard configs
├── tests/                            # ✅ Test suite
│   ├── test_api.py                   # API endpoint tests
│   ├── test_preprocessing.py         # Data pipeline tests
│   └── __init__.py
├── models/                           # 🤖 Trained models
│   ├── *.pkl                         # Serialized pipelines
│   └── *_metrics.json                # Training metrics
├── data/                             # 📂 Datasets
│   └── WA_Fn-UseC_-Telco-Customer-Churn.csv
├── logs/                             # 📝 Application logs
│   └── predictions.jsonl             # Prediction audit trail
├── docs/                             # 📚 Documentation
│   └── DEPLOYMENT.md                 # Deployment guide
├── .github/                          # ⚙️ GitHub configs
│   └── copilot-instructions.md       # This file
├── Dockerfile                        # 🐳 API container image
├── docker-compose.yml                # 🎭 Multi-container orchestration
├── requirements.txt                  # 📦 Python dependencies
├── setup_project.py                  # 🛠️ Project structure setup
├── .dockerignore                     # Docker build exclusions
├── preprocessing.py                  # Legacy (migrated to src/)
└── README.md                         # Project overview
```

**Key Files:**
- **src/predict_api.py**: Production API - start here for API changes
- **src/train_model.py**: Model training - modify for new algorithms
- **docker-compose.yml**: Service orchestration - adjust ports/config here
- **frontend/index.html**: UI - customize dashboard appearance

## 🐳 Docker & Container Architecture

### Service Definitions (docker-compose.yml)

**API Service** (`churn_api`)
- Base: `python:3.10-slim`
- Port: 8000
- Volumes: `logs/`, `models/`, `data/`
- Health check: HTTP GET `/health`
- Auto-restart: `unless-stopped`

**Frontend Service** (`churn_frontend`)
- Base: `nginx:alpine`
- Port: 3000 → nginx:80
- Reverse proxy to API
- CORS enabled for cross-origin requests

**Prometheus** (`churn_prometheus`)
- Port: 9090
- Scrapes API metrics every 15s
- Persistent storage: `prometheus_data` volume

**Grafana** (`churn_grafana`)
- Port: 3001
- Pre-configured datasources
- Dashboard provisioning from `monitoring/grafana/`
- Default: admin/admin

### Container Communication
All services on `churn-network` (bridge driver)
- Frontend → API: `http://api:8000`
- Prometheus → API: `http://api:8000/metrics`
- Grafana → Prometheus: `http://prometheus:9090`

### Build & Deploy Commands
```powershell
# Full rebuild
docker-compose build --no-cache

# Selective rebuild
docker-compose build api frontend

# View service status
docker-compose ps

# Scale API instances
docker-compose up --scale api=3

# Clean slate restart
docker-compose down -v && docker-compose up --build
```

## 🧪 Testing Strategy

### Unit Tests (`tests/test_preprocessing.py`)
- `DataPreprocessor` methods
- Data cleaning and splitting
- Feature preparation
- Uses pytest fixtures for sample data

### Integration Tests (`tests/test_api.py`)
- All API endpoints
- Request validation
- Error handling
- Uses FastAPI TestClient

### Test Execution
```powershell
# Run with verbose output
pytest tests/ -v -s

# Generate HTML coverage report
pytest tests/ --cov=src --cov-report=html
# View at htmlcov/index.html

# Run specific test class
pytest tests/test_api.py::test_predict_endpoint_valid

# Run with markers (if defined)
pytest -m "not slow"
```

## 📊 Monitoring & Observability

### Prediction Logging
All predictions logged to `logs/predictions.jsonl` with:
- Timestamp
- Input features (hashed for privacy in production)
- Prediction & probability
- Risk level
- Execution time

### Metrics Endpoints
- **GET /metrics**: Prometheus-compatible metrics
- **GET /model-info**: Training metrics, hyperparameters
- **GET /health**: Service health & model status

### Key Metrics to Monitor
1. **Prediction latency** - p50, p95, p99
2. **Prediction distribution** - Track risk level shifts
3. **Model drift** - Average probability trends
4. **Error rates** - 4xx vs 5xx responses
5. **Resource usage** - Memory, CPU per container

### Grafana Dashboards
Create panels for:
- Predictions over time (line chart)
- Risk distribution (pie chart)
- Latency histogram
- Error rate gauge
- Model performance tracking

## 🔒 Security & Best Practices

### API Security
- Input validation with Pydantic (type safety)
- SQL injection prevention (no direct DB queries)
- CORS configured (adjust for production domains)
- Rate limiting: **TODO** - implement with `slowapi`

### Container Security
- Non-root user in Dockerfile
- Minimal base images (alpine, slim)
- Multi-stage builds for smaller images
- .dockerignore to exclude sensitive files

### Data Privacy
- No customer IDs in production logs
- PII handling: **TODO** - implement masking
- Audit trail in `predictions.jsonl`

### Production Checklist
- [ ] Change Grafana admin password
- [ ] Enable HTTPS (nginx SSL config)
- [ ] Implement authentication (JWT/OAuth)
- [ ] Add rate limiting
- [ ] Set up log rotation
- [ ] Configure backups for models/
- [ ] Set resource limits in docker-compose
- [ ] Enable Docker Swarm or Kubernetes
- [ ] Set up CI/CD pipeline
- [ ] Configure monitoring alerts

## 🚨 Troubleshooting

### Common Issues

**"Model not loaded" Error**
```powershell
# Check model file exists
Test-Path .\models\final_churn_prediction_pipeline.pkl

# Check API logs
docker-compose logs api | Select-String "Model"

# Retrain if corrupted
python src/train_model.py
```

**Port Conflicts**
```powershell
# Find process using port 8000
netstat -ano | findstr :8000

# Kill process
taskkill /PID <PID> /F

# Or change port in docker-compose.yml
```

**Frontend Can't Reach API**
- Check `script.js` - API_BASE_URL must match API service
- Verify API is healthy: `http://localhost:8000/health`
- Check CORS headers in API response
- Inspect browser console for errors

**Docker Build Failures**
```powershell
# Clear build cache
docker builder prune

# Check disk space
docker system df

# Build with verbose output
docker-compose build --progress=plain
```

**Memory Issues**
- Increase Docker Desktop memory allocation (Settings → Resources)
- Reduce model complexity or use smaller dataset
- Implement model caching instead of reloading

### Debug Commands
```powershell
# Enter running container
docker exec -it churn_api /bin/bash

# Check Python environment
docker exec churn_api python -c "import sklearn; print(sklearn.__version__)"

# View container resource usage
docker stats

# Inspect network connectivity
docker network inspect churn_predection_churn-network

# Test inter-container communication
docker exec churn_frontend ping api
```

## 📚 Additional Resources

- **API Docs (Swagger)**: http://localhost:8000/docs
- **API Redoc**: http://localhost:8000/redoc
- **Deployment Guide**: `docs/DEPLOYMENT.md`
- **FastAPI Docs**: https://fastapi.tiangolo.com
- **scikit-learn Pipeline**: https://scikit-learn.org/stable/modules/compose.html
- **Docker Compose**: https://docs.docker.com/compose/

---

**When modifying code:**
1. Update tests first (TDD approach)
2. Run `pytest` to verify
3. Update this file if architecture changes
4. Rebuild containers: `docker-compose build`
5. Test deployment: `docker-compose up`
6. Update README.md with user-facing changes
