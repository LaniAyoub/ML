"""
Quick Start Guide - Run this after cloning the repository
"""

print("""
╔══════════════════════════════════════════════════════════════════════════╗
║                                                                          ║
║         🚀 TELCO CHURN PREDICTION - MLOps PROJECT                        ║
║                                                                          ║
║         Quick Start Guide                                                ║
║                                                                          ║
╚══════════════════════════════════════════════════════════════════════════╝

This guide will help you get the project running in 5 minutes!

STEP 1: PROJECT SETUP
═══════════════════════

Run the setup script to organize files:

    python setup_project.py

STEP 2: DOCKER DEPLOYMENT
═══════════════════════════

Start all services with Docker:

    docker-compose up --build

This will start:
  • API Service (port 8000)
  • Frontend Dashboard (port 3000)
  • Prometheus (port 9090)
  • Grafana (port 3001)

STEP 3: ACCESS SERVICES
═══════════════════════════

Once all services are running, access:

  📊 Dashboard:  http://localhost:3000
  🔌 API Docs:   http://localhost:8000/docs
  ❤️  Health:     http://localhost:8000/health
  📈 Grafana:    http://localhost:3001 (admin/admin)
  📉 Prometheus: http://localhost:9090

STEP 4: TEST PREDICTION
═══════════════════════════

Use PowerShell to test the API:

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

ADDITIONAL COMMANDS
═══════════════════════════

View logs:
    docker-compose logs -f

Stop services:
    docker-compose down

Rebuild specific service:
    docker-compose build api
    docker-compose up -d api

Run tests:
    pytest tests/ -v

TROUBLESHOOTING
═══════════════════════════

If you encounter issues:

1. Port already in use:
   netstat -ano | findstr :8000
   taskkill /PID <PID> /F

2. Model not loading:
   Check models/final_churn_prediction_pipeline.pkl exists

3. Docker issues:
   docker system prune -a
   docker-compose build --no-cache

DOCUMENTATION
═══════════════════════════

📚 Full README:         README.md
📖 Deployment Guide:    docs/DEPLOYMENT.md
🎯 Project Summary:     PROJECT_SUMMARY.md
🤖 AI Instructions:     .github/copilot-instructions.md

═══════════════════════════════════════════════════════════════════════════

Ready to start? Run: python setup_project.py

═══════════════════════════════════════════════════════════════════════════
""")
