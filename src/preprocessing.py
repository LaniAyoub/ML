"""
Custom Preprocessing Transformers
Domain-specific encoders and transformers for the churn prediction pipeline.
"""
import pandas as pd
import numpy as np
from sklearn.base import BaseEstimator, TransformerMixin


class CustomEncoder(BaseEstimator, TransformerMixin):
    """
    Custom encoder for domain-specific feature encoding.
    
    Encodes binary and ordinal features manually for better interpretability:
    - Binary features (Partner, Dependents, PhoneService, PaperlessBilling): Yes=1, No=0
    - Gender: Male=1, Female=0
    - Contract: Month-to-month=0, One year=1, Two year=2 (ordinal)
    - SeniorCitizen: Already numeric (0/1)
    """
    
    def __init__(self):
        self.binary_features = ['Partner', 'Dependents', 'PhoneService', 'PaperlessBilling']
        self.gender_map = {'Male': 1, 'Female': 0}
        self.contract_map = {'Month-to-month': 0, 'One year': 1, 'Two year': 2}
    
    def fit(self, X, y=None):
        """Fit the encoder (no-op for this transformer)."""
        return self
    
    def transform(self, X):
        """Transform the features with custom encoding."""
        # Create a copy to avoid modifying original data
        X_transformed = X.copy()
        
        # Encode binary features (Yes=1, No=0)
        for feature in self.binary_features:
            if feature in X_transformed.columns:
                X_transformed[feature] = X_transformed[feature].map({'Yes': 1, 'No': 0})
        
        # Encode gender
        if 'gender' in X_transformed.columns:
            X_transformed['gender'] = X_transformed['gender'].map(self.gender_map)
        
        # Encode contract (ordinal: Month-to-month < One year < Two year)
        if 'Contract' in X_transformed.columns:
            X_transformed['Contract'] = X_transformed['Contract'].map(self.contract_map)
        
        return X_transformed
    
    def get_feature_names_out(self, input_features=None):
        """Get output feature names for transformation."""
        if input_features is None:
            return None
        return input_features


class ThresholdClassifier(BaseEstimator):
    """
    Meta-classifier wrapper for custom decision thresholds.
    
    Wraps any estimator with decision_function() method and applies
    a custom threshold for classification without retraining.
    """
    
    def __init__(self, estimator, threshold=0.0):
        """
        Parameters:
        -----------
        estimator : sklearn estimator
            Base estimator that implements decision_function()
        threshold : float
            Decision threshold (default: 0.0)
        """
        self.estimator = estimator
        self.threshold = threshold
        self.classes_ = None
    
    def fit(self, X, y):
        """Fit the base estimator."""
        self.estimator.fit(X, y)
        self.classes_ = self.estimator.classes_
        return self
    
    def predict(self, X):
        """Predict class labels using custom threshold."""
        decision = self.decision_function(X)
        return (decision > self.threshold).astype(int)
    
    def predict_proba(self, X):
        """Predict class probabilities (delegates to base estimator)."""
        if hasattr(self.estimator, 'predict_proba'):
            return self.estimator.predict_proba(X)
        else:
            raise AttributeError("Base estimator does not have predict_proba method")
    
    def decision_function(self, X):
        """Compute decision function (delegates to base estimator)."""
        return self.estimator.decision_function(X)
