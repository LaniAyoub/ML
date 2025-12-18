"""
Model Training Module
Handles model training, hyperparameter tuning, and evaluation.
"""
import pandas as pd
import numpy as np
import joblib
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.feature_selection import SelectKBest, f_classif
from sklearn.svm import SVC
from sklearn.model_selection import RandomizedSearchCV
from sklearn.metrics import (
    classification_report, 
    confusion_matrix, 
    f1_score, 
    roc_auc_score,
    precision_recall_curve,
    roc_curve
)
import logging
import json
from datetime import datetime
from pathlib import Path
import sys

# Add parent directory to path to import preprocessing module
sys.path.insert(0, str(Path(__file__).parent.parent))

from preprocessing import CustomEncoder
from src.data_preprocessing import DataPreprocessor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ModelTrainer:
    """Train and evaluate churn prediction models."""
    
    def __init__(self, model_name: str = "churn_svm_model"):
        self.model_name = model_name
        self.pipeline = None
        self.best_model = None
        self.training_metrics = {}
        
    def build_pipeline(self) -> Pipeline:
        """Build the complete ML pipeline."""
        logger.info("Building ML pipeline...")
        
        # Define nominal columns for one-hot encoding
        nominal_cols = [
            'MultipleLines', 'InternetService', 'OnlineSecurity', 'OnlineBackup', 
            'DeviceProtection', 'TechSupport', 'StreamingTV', 'StreamingMovies', 
            'PaymentMethod'
        ]
        
        # Column transformer for one-hot encoding
        one_hot_preprocessor = ColumnTransformer(
            transformers=[
                ('onehot', 
                 OneHotEncoder(handle_unknown='ignore', sparse_output=False), 
                 nominal_cols)
            ],
            remainder='passthrough',
            verbose_feature_names_out=False
        )
        
        # Preprocessing pipeline
        preprocessing_pipeline = Pipeline(steps=[
            ('custom_encoder', CustomEncoder()),
            ('one_hot_encode', one_hot_preprocessor),
        ])
        
        # Full model pipeline
        self.pipeline = Pipeline(steps=[
            ('preprocessor', preprocessing_pipeline),
            ('selector', SelectKBest(f_classif)),
            ('scaler', StandardScaler()),
            ('svc', SVC(random_state=42, probability=True))
        ])
        
        logger.info("Pipeline built successfully")
        return self.pipeline
    
    def train_with_tuning(self, X_train: pd.DataFrame, y_train: pd.Series,
                          cv: int = 4, n_iter: int = 40) -> Pipeline:
        """Train model with hyperparameter tuning."""
        logger.info("Starting hyperparameter tuning...")
        
        # Define hyperparameter grid
        hyper_params = {
            'selector__k': range(7, 100),
            'svc__C': [1, 10, 100, 1000],
            'svc__gamma': [1e-3, 1e-4, 1e-2],
            'svc__kernel': ['rbf', 'linear']
        }
        
        # Randomized search
        grid = RandomizedSearchCV(
            self.pipeline,
            hyper_params,
            scoring="f1",
            cv=cv,
            n_iter=n_iter,
            n_jobs=-1,
            verbose=2,
            random_state=42
        )
        
        grid.fit(X_train, y_train)
        
        self.best_model = grid.best_estimator_
        self.training_metrics['best_params'] = grid.best_params_
        self.training_metrics['best_score'] = grid.best_score_
        self.training_metrics['cv_results'] = {
            'mean_test_score': grid.cv_results_['mean_test_score'].tolist(),
            'std_test_score': grid.cv_results_['std_test_score'].tolist()
        }
        
        logger.info(f"Best parameters: {grid.best_params_}")
        logger.info(f"Best F1 score: {grid.best_score_:.4f}")
        
        return self.best_model
    
    def evaluate_model(self, X_test: pd.DataFrame, y_test: pd.Series) -> dict:
        """Evaluate the trained model on test data."""
        logger.info("Evaluating model on test set...")
        
        # Predictions
        y_pred = self.best_model.predict(X_test)
        y_proba = self.best_model.predict_proba(X_test)[:, 1]
        
        # Calculate metrics
        f1 = f1_score(y_test, y_pred)
        roc_auc = roc_auc_score(y_test, y_proba)
        conf_matrix = confusion_matrix(y_test, y_pred)
        class_report = classification_report(y_test, y_pred, output_dict=True)
        
        # Store metrics
        self.training_metrics['test_f1_score'] = f1
        self.training_metrics['test_roc_auc'] = roc_auc
        self.training_metrics['confusion_matrix'] = conf_matrix.tolist()
        self.training_metrics['classification_report'] = class_report
        self.training_metrics['test_samples'] = len(X_test)
        
        # Log results
        logger.info(f"Test F1 Score: {f1:.4f}")
        logger.info(f"Test ROC-AUC Score: {roc_auc:.4f}")
        logger.info(f"Confusion Matrix:\n{conf_matrix}")
        
        return self.training_metrics
    
    def save_model(self, output_dir: str = "models") -> str:
        """Save the trained model and metrics."""
        Path(output_dir).mkdir(exist_ok=True)
        
        # Save model
        model_path = f"{output_dir}/{self.model_name}.pkl"
        joblib.dump(self.best_model, model_path)
        logger.info(f"Model saved to {model_path}")
        
        # Save metrics with timestamp
        self.training_metrics['timestamp'] = datetime.now().isoformat()
        self.training_metrics['model_name'] = self.model_name
        
        metrics_path = f"{output_dir}/{self.model_name}_metrics.json"
        with open(metrics_path, 'w') as f:
            json.dump(self.training_metrics, f, indent=4)
        logger.info(f"Metrics saved to {metrics_path}")
        
        return model_path
    
    def train_and_save(self, X_train: pd.DataFrame, y_train: pd.Series,
                       X_test: pd.DataFrame, y_test: pd.Series) -> str:
        """Complete training pipeline: build, train, evaluate, and save."""
        self.build_pipeline()
        self.train_with_tuning(X_train, y_train)
        self.evaluate_model(X_test, y_test)
        model_path = self.save_model()
        
        return model_path


if __name__ == "__main__":
    # Complete training workflow
    logger.info("=== Starting Model Training Workflow ===")
    
    # Load and preprocess data
    preprocessor = DataPreprocessor("data/WA_Fn-UseC_-Telco-Customer-Churn.csv")
    X_train, X_test, y_train, y_test = preprocessor.run_full_pipeline()
    
    # Train model
    trainer = ModelTrainer("final_churn_prediction_pipeline")
    model_path = trainer.train_and_save(X_train, y_train, X_test, y_test)
    
    logger.info(f"=== Training Complete ===")
    logger.info(f"Model saved at: {model_path}")
