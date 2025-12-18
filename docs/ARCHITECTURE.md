# System Architecture Documentation

## Overview Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                          CLIENT LAYER                                   │
│                                                                         │
│  ┌──────────────────┐                    ┌──────────────────┐          │
│  │   Web Browser    │                    │   API Clients    │          │
│  │   (Dashboard)    │                    │   (External)     │          │
│  └────────┬─────────┘                    └────────┬─────────┘          │
│           │                                       │                    │
└───────────┼───────────────────────────────────────┼─────────────────────┘
            │                                       │
            │ HTTP/HTTPS                            │ REST API
            ▼                                       ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                       PRESENTATION LAYER                                │
│                                                                         │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │                    Nginx Web Server                              │  │
│  │                    (Frontend Container)                          │  │
│  │                                                                  │  │
│  │  • Static files serving (HTML, CSS, JS)                        │  │
│  │  • Reverse proxy to API                                        │  │
│  │  • CORS handling                                               │  │
│  │  • Port: 3000 → 80                                            │  │
│  └────────────────────────┬─────────────────────────────────────────┘  │
│                           │                                            │
└───────────────────────────┼─────────────────────────────────────────────┘
                            │ HTTP
                            ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                        APPLICATION LAYER                                │
│                                                                         │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │                    FastAPI Application                           │  │
│  │                    (API Container)                               │  │
│  │                                                                  │  │
│  │  ┌─────────────────┐     ┌──────────────────┐                  │  │
│  │  │   Endpoints     │     │   Middleware     │                  │  │
│  │  │                 │     │                  │                  │  │
│  │  │ • /predict      │────▶│ • CORS           │                  │  │
│  │  │ • /health       │     │ • Logging        │                  │  │
│  │  │ • /metrics      │     │ • Validation     │                  │  │
│  │  │ • /model-info   │     │ • Error Handler  │                  │  │
│  │  └─────────────────┘     └──────────────────┘                  │  │
│  │                                                                  │  │
│  │  ┌─────────────────────────────────────────┐                   │  │
│  │  │      Pydantic Models                    │                   │  │
│  │  │  • CustomerData (Input validation)      │                   │  │
│  │  │  • PredictionResponse (Output schema)   │                   │  │
│  │  └─────────────────────────────────────────┘                   │  │
│  │                                                                  │  │
│  │  ┌─────────────────────────────────────────┐                   │  │
│  │  │      Prediction Tracker                 │                   │  │
│  │  │  • Logs predictions to JSONL            │                   │  │
│  │  │  • Tracks metrics                       │                   │  │
│  │  │  • Calculates statistics                │                   │  │
│  │  └─────────────────────────────────────────┘                   │  │
│  │                                                                  │  │
│  │  Port: 8000                                                     │  │
│  └────────────────────────┬─────────────────────────────────────────┘  │
│                           │                                            │
└───────────────────────────┼─────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                         ML PIPELINE LAYER                               │
│                                                                         │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │               Scikit-learn Pipeline                              │  │
│  │               (Loaded from .pkl file)                            │  │
│  │                                                                  │  │
│  │  1. Data Preprocessing                                          │  │
│  │     └─▶ Convert datatypes, validate                            │  │
│  │                                                                  │  │
│  │  2. Custom Encoder (preprocessing.py)                          │  │
│  │     └─▶ Binary encoding: Partner, Dependents, etc.            │  │
│  │     └─▶ Ordinal encoding: Contract                            │  │
│  │     └─▶ Gender encoding                                        │  │
│  │                                                                  │  │
│  │  3. Column Transformer                                          │  │
│  │     └─▶ OneHotEncoder for nominal features                    │  │
│  │     └─▶ Passthrough for already encoded                       │  │
│  │                                                                  │  │
│  │  4. Feature Selection                                           │  │
│  │     └─▶ SelectKBest (f_classif)                               │  │
│  │     └─▶ k optimized via hyperparameter tuning                │  │
│  │                                                                  │  │
│  │  5. Standard Scaler                                             │  │
│  │     └─▶ Normalize features                                     │  │
│  │                                                                  │  │
│  │  6. SVM Classifier                                              │  │
│  │     └─▶ RBF/Linear kernel                                      │  │
│  │     └─▶ Probability estimates enabled                         │  │
│  │     └─▶ Hyperparameters: C, gamma (tuned)                    │  │
│  │                                                                  │  │
│  │  Output: Prediction (0/1) + Probability (0.0-1.0)             │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│                         DATA LAYER                                      │
│                                                                         │
│  ┌─────────────────┐  ┌─────────────────┐  ┌──────────────────┐       │
│  │  Training Data  │  │  Trained Model  │  │  Prediction Logs │       │
│  │                 │  │                 │  │                  │       │
│  │  CSV Dataset    │  │  .pkl File      │  │  JSONL File      │       │
│  │  7043 rows      │  │  ~2MB size      │  │  Time-series     │       │
│  │  21 features    │  │  Serialized     │  │  Audit trail     │       │
│  └─────────────────┘  └─────────────────┘  └──────────────────┘       │
│                                                                         │
│  Volumes:                                                               │
│  • data/    - Training datasets                                        │
│  • models/  - Serialized pipelines                                     │
│  • logs/    - Application logs                                         │
└─────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│                     MONITORING & OBSERVABILITY LAYER                    │
│                                                                         │
│  ┌────────────────────────────────┐  ┌──────────────────────────────┐  │
│  │        Prometheus              │  │         Grafana              │  │
│  │        (Metrics Storage)       │  │         (Visualization)      │  │
│  │                                │  │                              │  │
│  │  • Scrapes /metrics endpoint   │─▶│  • Connects to Prometheus   │  │
│  │  • Time-series database        │  │  • Pre-built dashboards     │  │
│  │  • Alerting rules              │  │  • Custom queries           │  │
│  │  • Port: 9090                  │  │  • Port: 3001               │  │
│  │                                │  │  • Login: admin/admin       │  │
│  └────────────────────────────────┘  └──────────────────────────────┘  │
│                                                                         │
│  Metrics Collected:                                                     │
│  • Total predictions count                                              │
│  • Predictions by risk level                                            │
│  • Average churn probability                                            │
│  • API response times                                                   │
│  • Error rates                                                          │
│  • Container resource usage                                             │
└─────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│                        DOCKER NETWORK LAYER                             │
│                                                                         │
│  Network: churn-network (bridge)                                        │
│                                                                         │
│  ┌──────────────┐   ┌──────────────┐   ┌──────────────┐               │
│  │   frontend   │   │      api     │   │  prometheus  │               │
│  │   :3000      │──▶│    :8000     │◀──│    :9090     │               │
│  └──────────────┘   └──────┬───────┘   └──────────────┘               │
│                            │                    │                       │
│                            │                    ▼                       │
│                            │            ┌──────────────┐               │
│                            │            │   grafana    │               │
│                            │            │    :3001     │               │
│                            │            └──────────────┘               │
│                            │                                            │
│  Inter-container communication:                                        │
│  • frontend → api:8000                                                 │
│  • prometheus → api:8000/metrics                                       │
│  • grafana → prometheus:9090                                           │
└─────────────────────────────────────────────────────────────────────────┘
```

## Component Details

### 1. Frontend Container
- **Image**: nginx:alpine
- **Purpose**: Serve static dashboard files
- **Components**:
  - index.html (Bootstrap UI)
  - script.js (API integration, Chart.js)
  - nginx.conf (reverse proxy config)

### 2. API Container
- **Image**: python:3.10-slim
- **Purpose**: ML prediction service
- **Components**:
  - FastAPI application
  - Pydantic models
  - Prediction tracking
  - Model loading

### 3. Prometheus Container
- **Image**: prom/prometheus:latest
- **Purpose**: Metrics collection and storage
- **Configuration**: prometheus.yml

### 4. Grafana Container
- **Image**: grafana/grafana:latest
- **Purpose**: Metrics visualization
- **Features**: Pre-configured dashboards

## Data Flow Diagrams

### Prediction Request Flow

```
User Input (Dashboard)
    │
    ├─▶ Fill customer form
    │
    ├─▶ Click "Predict"
    │
    ▼
JavaScript (script.js)
    │
    ├─▶ Collect form data
    │
    ├─▶ Convert to JSON
    │
    ├─▶ POST to /predict
    │
    ▼
Nginx
    │
    ├─▶ Receive request
    │
    ├─▶ Forward to API
    │
    ▼
FastAPI Endpoint
    │
    ├─▶ Validate with Pydantic
    │
    ├─▶ Convert to DataFrame
    │
    ├─▶ Handle TotalCharges
    │
    ▼
ML Pipeline
    │
    ├─▶ 1. Custom Encoding
    │
    ├─▶ 2. One-Hot Encoding
    │
    ├─▶ 3. Feature Selection
    │
    ├─▶ 4. Scaling
    │
    ├─▶ 5. SVM Prediction
    │
    ▼
Response Generation
    │
    ├─▶ Calculate risk level
    │
    ├─▶ Generate customer ID
    │
    ├─▶ Log to JSONL
    │
    ├─▶ Return JSON response
    │
    ▼
Dashboard Update
    │
    ├─▶ Display result card
    │
    ├─▶ Update charts
    │
    └─▶ Show recommendations
```

### Training Pipeline Flow

```
Raw Data (CSV)
    │
    ├─▶ Load dataset
    │
    ▼
Data Preprocessing
    │
    ├─▶ Convert TotalCharges to numeric
    │
    ├─▶ Drop missing values
    │
    ├─▶ Separate features and target
    │
    ▼
Train/Test Split
    │
    ├─▶ Stratified split (80/20)
    │
    ├─▶ Preserve class balance
    │
    ▼
Pipeline Construction
    │
    ├─▶ Custom Encoder
    │
    ├─▶ ColumnTransformer
    │
    ├─▶ SelectKBest
    │
    ├─▶ StandardScaler
    │
    ├─▶ SVC
    │
    ▼
Hyperparameter Tuning
    │
    ├─▶ RandomizedSearchCV
    │
    ├─▶ F1 scoring (imbalanced data)
    │
    ├─▶ 4-fold cross-validation
    │
    ├─▶ 40 iterations
    │
    ▼
Model Evaluation
    │
    ├─▶ Test set predictions
    │
    ├─▶ Calculate metrics
    │
    ├─▶ Generate report
    │
    ▼
Model Serialization
    │
    ├─▶ Save as .pkl
    │
    ├─▶ Save metrics as JSON
    │
    └─▶ Ready for deployment
```

## Security Architecture

```
┌─────────────────────────────────────────┐
│          Security Layers                │
└─────────────────────────────────────────┘

1. Network Security
   ├─▶ Docker network isolation
   ├─▶ Port exposure control
   └─▶ Container-to-container communication only

2. API Security
   ├─▶ Pydantic input validation
   ├─▶ Type checking
   ├─▶ Error handling
   └─▶ CORS configuration

3. Container Security
   ├─▶ Minimal base images
   ├─▶ No root user
   ├─▶ .dockerignore for secrets
   └─▶ Health checks

4. Data Security
   ├─▶ No PII in logs
   ├─▶ Prediction audit trail
   ├─▶ Volume permissions
   └─▶ Data encryption (TODO)

5. Monitoring Security
   ├─▶ Grafana authentication
   ├─▶ Prometheus access control
   └─▶ Metrics endpoint security
```

## Scalability Architecture

```
┌─────────────────────────────────────────────────┐
│           Current Setup (Single Host)           │
└─────────────────────────────────────────────────┘
    Frontend (1 instance)
    API (1 instance)
    Prometheus (1 instance)
    Grafana (1 instance)

┌─────────────────────────────────────────────────┐
│         Scaled Setup (Production Ready)         │
└─────────────────────────────────────────────────┘

Load Balancer (nginx/HAProxy)
    │
    ├─▶ Frontend (n instances)
    │       └─▶ CDN (static assets)
    │
    └─▶ API (n instances)
            ├─▶ Shared model cache (Redis)
            ├─▶ Database (PostgreSQL)
            └─▶ Message queue (RabbitMQ)

Monitoring Cluster
    ├─▶ Prometheus (HA setup)
    └─▶ Grafana (clustered)

Strategies:
• Horizontal scaling of API containers
• Load balancing across instances
• Shared cache for model predictions
• Database for persistent storage
• Message queue for async processing
```

## Deployment Environments

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│              │     │              │     │              │
│  Development │────▶│   Staging    │────▶│  Production  │
│              │     │              │     │              │
└──────────────┘     └──────────────┘     └──────────────┘
      │                    │                     │
      │                    │                     │
      ▼                    ▼                     ▼
  Docker Compose      Docker Compose      Kubernetes/ECS
  localhost           Test environment    Cloud deployment
  Hot reload          QA testing          Auto-scaling
  Debug mode          Integration tests   Monitoring
                      Performance tests   High availability
```

---

**Last Updated**: December 17, 2025
**Version**: 1.0.0
