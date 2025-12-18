"""
Script to organize project files and move existing files to proper locations
"""
import shutil
import os
from pathlib import Path


def setup_project_structure():
    """Set up the complete project structure."""
    
    print("🚀 Setting up MLOps Project Structure...")
    
    # Create directories
    directories = [
        "data",
        "models",
        "logs",
        "src",
        "frontend",
        "monitoring/grafana/dashboards",
        "monitoring/grafana/datasources",
        "tests",
        "docs"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"✓ Created directory: {directory}")
    
    # Move existing files
    moves = [
        ("WA_Fn-UseC_-Telco-Customer-Churn.csv", "data/WA_Fn-UseC_-Telco-Customer-Churn.csv"),
        ("final_churn_prediction_pipeline.pkl", "models/final_churn_prediction_pipeline.pkl"),
    ]
    
    for src, dst in moves:
        if os.path.exists(src) and not os.path.exists(dst):
            shutil.copy2(src, dst)
            print(f"✓ Copied {src} to {dst}")
    
    # Copy preprocessing.py to src if not exists
    if os.path.exists("preprocessing.py") and not os.path.exists("src/preprocessing.py"):
        shutil.copy2("preprocessing.py", "src/preprocessing.py")
        print("✓ Copied preprocessing.py to src/")
    
    print("\n✅ Project structure setup complete!")
    print("\n📂 Project Structure:")
    print("""
    Churn_predection/
    ├── src/                    # Source code
    │   ├── data_preprocessing.py
    │   ├── train_model.py
    │   ├── predict_api.py
    │   └── preprocessing.py
    ├── frontend/               # Web dashboard
    │   ├── index.html
    │   ├── script.js
    │   ├── Dockerfile
    │   └── nginx.conf
    ├── monitoring/             # Monitoring configs
    │   └── prometheus.yml
    ├── models/                 # Trained models
    │   └── *.pkl
    ├── data/                   # Dataset
    │   └── *.csv
    ├── logs/                   # Application logs
    ├── tests/                  # Test suite
    │   ├── test_api.py
    │   └── test_preprocessing.py
    ├── Dockerfile              # API container
    ├── docker-compose.yml      # Orchestration
    ├── requirements.txt        # Dependencies
    └── README.md              # Documentation
    """)


if __name__ == "__main__":
    setup_project_structure()
