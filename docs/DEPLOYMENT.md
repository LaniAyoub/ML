# Deployment Guide - Telco Churn Prediction MLOps Project

## 🎯 Overview

This guide will walk you through deploying the complete churn prediction system from scratch.

## 📋 Prerequisites

### System Requirements
- **OS**: Windows 10/11, Linux, or macOS
- **RAM**: Minimum 4GB, Recommended 8GB
- **Disk Space**: 5GB free space
- **Software**:
  - Docker Desktop (latest version)
  - Git
  - Python 3.10+ (for local development)
  - PowerShell or Bash

### Verify Installation
```powershell
# Check Docker
docker --version
docker-compose --version

# Check Python
python --version

# Check Git
git --version
```

## 🚀 Quick Deployment (5 Minutes)

### Step 1: Clone and Setup
```powershell
# Clone repository
git clone <repository-url>
cd Churn_predection

# Run setup script
python setup_project.py
```

### Step 2: Start All Services
```powershell
# Build and start all containers
docker-compose up --build
```

Wait for all services to start (approximately 2-3 minutes). You should see:
```
✅ api_1          | Model loaded successfully
✅ frontend_1     | nginx started
✅ prometheus_1   | Server is ready to receive requests
✅ grafana_1      | HTTP Server Listen
```

### Step 3: Access Services

| Service | URL | Credentials |
|---------|-----|-------------|
| Frontend Dashboard | http://localhost:3000 | N/A |
| API Documentation | http://localhost:8000/docs | N/A |
| API Health | http://localhost:8000/health | N/A |
| Prometheus | http://localhost:9090 | N/A |
| Grafana | http://localhost:3001 | admin/admin |

## 📦 Detailed Deployment Steps

### 1. Project Organization

After cloning, your structure should look like:

```
Churn_predection/
├── data/                          # Dataset
│   └── WA_Fn-UseC_-Telco-Customer-Churn.csv
├── models/                        # Trained models
│   └── final_churn_prediction_pipeline.pkl
├── src/                          # Source code
│   ├── data_preprocessing.py
│   ├── train_model.py
│   ├── predict_api.py
│   └── preprocessing.py
├── frontend/                     # Web interface
├── monitoring/                   # Monitoring configs
├── tests/                        # Test suite
├── docker-compose.yml
└── README.md
```

### 2. Environment Configuration (Optional)

Create `.env` file for custom configuration:

```env
# API Configuration
API_PORT=8000
API_HOST=0.0.0.0

# Model Configuration
MODEL_PATH=models/final_churn_prediction_pipeline.pkl

# Frontend Configuration
FRONTEND_PORT=3000

# Monitoring
PROMETHEUS_PORT=9090
GRAFANA_PORT=3001
GRAFANA_ADMIN_PASSWORD=your_secure_password
```

### 3. Data Preparation

Ensure your dataset is in place:

```powershell
# Check if data file exists
Test-Path .\data\WA_Fn-UseC_-Telco-Customer-Churn.csv

# If missing, download or copy it to data/ directory
```

### 4. Model Training (Optional)

If you need to retrain the model:

```powershell
# Install dependencies
pip install -r requirements.txt

# Run training
python src/train_model.py
```

This will:
- Load and preprocess data
- Train SVM with hyperparameter tuning
- Save model to `models/` directory
- Generate metrics file

### 5. Docker Deployment

#### Build Images
```powershell
# Build all images
docker-compose build

# Build specific service
docker-compose build api
docker-compose build frontend
```

#### Start Services
```powershell
# Start in foreground (see logs)
docker-compose up

# Start in background
docker-compose up -d

# Start specific services
docker-compose up api frontend
```

#### Monitor Services
```powershell
# View logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f api

# Check service status
docker-compose ps
```

#### Stop Services
```powershell
# Stop all services
docker-compose down

# Stop and remove volumes
docker-compose down -v

# Stop specific service
docker-compose stop api
```

## 🧪 Testing Deployment

### 1. Health Check
```powershell
# API health
Invoke-RestMethod -Uri "http://localhost:8000/health"

# Expected output:
# {
#   "status": "healthy",
#   "model_loaded": true,
#   "timestamp": "2023-12-17T...",
#   "version": "1.0.0"
# }
```

### 2. Test Prediction
```powershell
# Single prediction test
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

### 3. Run Test Suite
```powershell
# Install test dependencies
pip install -r requirements.txt

# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_api.py -v

# Run with coverage
pytest tests/ --cov=src --cov-report=html
```

## 📊 Using the Dashboard

### Making Predictions

1. **Navigate** to http://localhost:3000
2. **Fill in** customer information in the form
3. **Click** "Predict Churn Risk"
4. **View** results with risk level and recommendations

### Monitoring Metrics

The dashboard displays:
- Total predictions made
- Risk distribution (low/medium/high)
- Average churn probability
- Model performance metrics

### Real-time Updates

- Metrics refresh automatically every 30 seconds
- Manual refresh available with refresh button
- Health status indicator shows API connectivity

## 🔍 Monitoring & Observability

### Prometheus Metrics

1. Access Prometheus at http://localhost:9090
2. Query available metrics:
   - `predictions_total` - Total predictions made
   - `predictions_by_risk` - Predictions grouped by risk
   - `api_response_time` - API latency

### Grafana Dashboards

1. Access Grafana at http://localhost:3001
2. Login with admin/admin
3. Import pre-configured dashboards
4. View:
   - API performance metrics
   - Prediction trends over time
   - Model accuracy tracking

## 🐛 Troubleshooting

### Common Issues

#### 1. Port Already in Use
```powershell
# Find process using port 8000
netstat -ano | findstr :8000

# Kill the process (use PID from above)
taskkill /PID <PID> /F

# Or change port in docker-compose.yml
```

#### 2. Model Not Loading
```powershell
# Check if model file exists
Test-Path .\models\final_churn_prediction_pipeline.pkl

# Check API logs
docker-compose logs api

# Retrain model if needed
python src/train_model.py
```

#### 3. Docker Build Failures
```powershell
# Clean Docker cache
docker system prune -a

# Rebuild without cache
docker-compose build --no-cache
```

#### 4. Memory Issues
```powershell
# Increase Docker memory in Docker Desktop settings
# Recommended: 4GB minimum

# Check Docker stats
docker stats
```

#### 5. Frontend Not Loading
```powershell
# Check frontend logs
docker-compose logs frontend

# Verify nginx configuration
docker exec -it churn_frontend cat /etc/nginx/conf.d/default.conf

# Rebuild frontend
docker-compose build frontend
docker-compose up -d frontend
```

### Debugging

#### View Container Logs
```powershell
# All containers
docker-compose logs

# Specific container with tail
docker-compose logs --tail=100 api

# Follow logs in real-time
docker-compose logs -f api
```

#### Execute Commands in Container
```powershell
# Access API container shell
docker exec -it churn_api /bin/bash

# Check Python environment
docker exec churn_api python -c "import sklearn; print(sklearn.__version__)"

# Test prediction locally
docker exec churn_api python -c "import joblib; model = joblib.load('models/final_churn_prediction_pipeline.pkl'); print('Model loaded')"
```

#### Network Issues
```powershell
# List networks
docker network ls

# Inspect churn network
docker network inspect churn_predection_churn-network

# Test connectivity between containers
docker exec churn_frontend ping api
```

## 🔒 Security Best Practices

1. **Change Default Passwords**
   ```env
   GRAFANA_ADMIN_PASSWORD=your_secure_password
   ```

2. **Use Environment Variables**
   - Don't commit `.env` files
   - Use secrets management in production

3. **Enable HTTPS**
   - Configure SSL certificates
   - Use reverse proxy (nginx/traefik)

4. **API Rate Limiting**
   - Implement rate limiting middleware
   - Use API keys for authentication

## 🚀 Production Deployment

### For Cloud Deployment (AWS/Azure/GCP)

1. **Container Registry**
   ```powershell
   # Tag images
   docker tag churn_api:latest registry.example.com/churn_api:v1.0
   
   # Push to registry
   docker push registry.example.com/churn_api:v1.0
   ```

2. **Kubernetes Deployment**
   - Convert docker-compose to k8s manifests
   - Use Helm charts
   - Configure ingress and load balancing

3. **CI/CD Pipeline**
   - Set up GitHub Actions / Jenkins
   - Automated testing
   - Automated deployment

### Scaling Considerations

1. **Horizontal Scaling**
   ```yaml
   # In docker-compose.yml
   api:
     deploy:
       replicas: 3
   ```

2. **Load Balancing**
   - Use nginx or cloud load balancer
   - Distribute traffic across API instances

3. **Database for Predictions**
   - Store predictions in PostgreSQL/MongoDB
   - Enable prediction history and analytics

## 📈 Performance Optimization

1. **Model Optimization**
   - Use model compression
   - Implement model caching
   - Consider ONNX for faster inference

2. **API Optimization**
   - Enable async endpoints
   - Use Redis for caching
   - Implement request batching

3. **Frontend Optimization**
   - Enable CDN
   - Minify assets
   - Implement lazy loading

## 📝 Maintenance

### Regular Tasks

1. **Update Dependencies**
   ```powershell
   pip list --outdated
   pip install -U package_name
   ```

2. **Monitor Logs**
   ```powershell
   # Check log size
   docker-compose logs --tail=1000 api | Measure-Object -Line
   ```

3. **Backup Models**
   ```powershell
   # Backup models directory
   Compress-Archive -Path .\models -DestinationPath "backup_$(Get-Date -Format 'yyyyMMdd').zip"
   ```

4. **Clean Up**
   ```powershell
   # Remove old containers
   docker system prune

   # Remove unused volumes
   docker volume prune
   ```

## 🎓 Next Steps

1. **Enhance Model**
   - Try other algorithms (Random Forest, XGBoost)
   - Implement ensemble methods
   - Add model versioning

2. **Improve API**
   - Add authentication
   - Implement rate limiting
   - Add more endpoints

3. **Expand Dashboard**
   - Add more visualizations
   - Implement export functionality
   - Add user management

4. **Add Features**
   - Batch prediction upload
   - Email alerts for high-risk customers
   - A/B testing framework

## 📞 Support

For issues or questions:
1. Check troubleshooting section
2. Review logs
3. Open GitHub issue
4. Contact team

---

**Happy Deploying! 🚀**
