"""Quick model training without hyperparameter tuning for Docker build"""
import pandas as pd
import joblib
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.feature_selection import SelectKBest, f_classif
from sklearn.svm import SVC
from sklearn.model_selection import train_test_split
import json
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))
from preprocessing import CustomEncoder

print("Loading and preprocessing data...")
# Load data directly
df = pd.read_csv("data/WA_Fn-UseC_-Telco-Customer-Churn.csv")
print(f"Data loaded: {df.shape}")

# Clean TotalCharges
df['TotalCharges'] = pd.to_numeric(df['TotalCharges'], errors='coerce')
df = df.dropna()
print(f"After cleaning: {df.shape}")

# Prepare features and target
X = df.drop(['Churn', 'customerID'], axis=1)
y = df['Churn'].replace({"Yes": 1, 'No': 0})

# Split data
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)
print(f"Train: {X_train.shape}, Test: {X_test.shape}")

print("Building pipeline with default parameters...")
# Define columns
cat_features = ['MultipleLines', 'InternetService', 'OnlineSecurity', 
                'OnlineBackup', 'DeviceProtection', 'TechSupport',
                'StreamingTV', 'StreamingMovies', 'PaymentMethod']

# Build pipeline with good default parameters
pipeline = Pipeline([
    ('encoder', CustomEncoder()),
    ('onehot', ColumnTransformer([
        ('cat', OneHotEncoder(sparse_output=False, handle_unknown='ignore'), cat_features)
    ], remainder='passthrough', verbose_feature_names_out=False)),
    ('selector', SelectKBest(f_classif, k=25)),  # Use 25 features
    ('scaler', StandardScaler()),
    ('svc', SVC(C=10, gamma='scale', kernel='rbf', probability=True, random_state=42))
])

print("Training model...")
pipeline.fit(X_train, y_train)

print("Evaluating...")
from sklearn.metrics import f1_score, roc_auc_score, classification_report
y_pred = pipeline.predict(X_test)
y_proba = pipeline.predict_proba(X_test)[:, 1]

f1 = f1_score(y_test, y_pred)
roc_auc = roc_auc_score(y_test, y_proba)

print(f"\nTest Set Performance:")
print(f"F1 Score: {f1:.4f}")
print(f"ROC-AUC: {roc_auc:.4f}")
print("\nClassification Report:")
print(classification_report(y_test, y_pred))

# Save model
model_path = "models/final_churn_prediction_pipeline.pkl"
print(f"\nSaving model to {model_path}...")
joblib.dump(pipeline, model_path)

# Save metrics
metrics = {
    "f1_score": float(f1),
    "roc_auc": float(roc_auc),
    "model_params": {
        "selector__k": 25,
        "svc__C": 10,
        "svc__kernel": "rbf",
        "svc__gamma": "scale"
    }
}

metrics_path = "models/final_churn_prediction_pipeline_metrics.json"
with open(metrics_path, 'w') as f:
    json.dump(metrics, f, indent=2)

print(f"Metrics saved to {metrics_path}")
print("\n✅ Model training complete!")
