# preprocessing.py
from sklearn.base import BaseEstimator, TransformerMixin,ClassifierMixin

class CustomEncoder(BaseEstimator, TransformerMixin):
    def fit(self, X, y=None):
        return self

    def transform(self, X):
        X_copy = X.copy()
        
        binary_cols = ['Partner', 'Dependents', 'PhoneService', 'PaperlessBilling']
        for col in binary_cols:
            if col in X_copy.columns:
                X_copy[col] = X_copy[col].replace({"Yes": 1, 'No': 0}).astype(int)

        if 'gender' in X_copy.columns:
            X_copy['gender'] = X_copy['gender'].replace({'Male': 1, 'Female': 0}).astype(int)

        contract_mapping = {'Month-to-month': 0, 'One year': 1, 'Two year': 2}
        if 'Contract' in X_copy.columns:
            X_copy['Contract'] = X_copy['Contract'].map(contract_mapping).astype(int)
            
        return X_copy
    
class ThresholdClassifier(BaseEstimator, ClassifierMixin):
    def __init__(self, estimator, threshold=0.0):
        self.estimator = estimator
        self.threshold = threshold

    def fit(self, X, y):
      
        self.estimator.fit(X, y)
   
        self.classes_ = self.estimator.classes_
        return self

    def predict(self, X):
    
        scores = self.estimator.decision_function(X)
        return (scores > self.threshold).astype(int)

    def predict_proba(self, X):
       
        return self.estimator.predict_proba(X)
    
    def decision_function(self, X):
      
        return self.estimator.decision_function(X)