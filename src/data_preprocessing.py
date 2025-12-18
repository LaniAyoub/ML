"""
Data Preprocessing Module
Handles data loading, cleaning, and transformation for churn prediction.
"""
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from typing import Tuple
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataPreprocessor:
    """Handle all data preprocessing operations."""
    
    def __init__(self, data_path: str = "data/WA_Fn-UseC_-Telco-Customer-Churn.csv"):
        self.data_path = data_path
        self.df = None
        
    def load_data(self) -> pd.DataFrame:
        """Load the dataset from CSV file."""
        logger.info(f"Loading data from {self.data_path}")
        self.df = pd.read_csv(self.data_path)
        logger.info(f"Data loaded successfully. Shape: {self.df.shape}")
        return self.df
    
    def clean_data(self) -> pd.DataFrame:
        """Clean the dataset - handle TotalCharges conversion and missing values."""
        logger.info("Starting data cleaning...")
        
        # Convert TotalCharges from object to numeric
        self.df['TotalCharges'] = pd.to_numeric(self.df['TotalCharges'], errors='coerce')
        
        # Log missing values
        missing_count = self.df['TotalCharges'].isna().sum()
        logger.info(f"Found {missing_count} missing values in TotalCharges")
        
        # Drop rows with missing TotalCharges
        self.df = self.df.dropna(subset=['TotalCharges'])
        
        logger.info(f"Data cleaned. Final shape: {self.df.shape}")
        return self.df
    
    def prepare_features(self) -> Tuple[pd.DataFrame, pd.Series]:
        """Prepare features and target variable."""
        logger.info("Preparing features and target...")
        
        # Drop customerID and Churn columns from features
        X = self.df.drop(['Churn', 'customerID'], axis=1)
        
        # Convert target to binary
        y = self.df['Churn'].replace({"Yes": 1, 'No': 0})
        
        logger.info(f"Features shape: {X.shape}, Target shape: {y.shape}")
        logger.info(f"Target distribution - Churn: {y.sum()} ({y.mean()*100:.2f}%), No Churn: {(1-y).sum()} ({(1-y.mean())*100:.2f}%)")
        
        return X, y
    
    def split_data(self, X: pd.DataFrame, y: pd.Series, 
                   test_size: float = 0.2, 
                   random_state: int = 42) -> Tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series]:
        """Split data into training and testing sets with stratification."""
        logger.info(f"Splitting data with test_size={test_size}")
        
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, 
            test_size=test_size, 
            random_state=random_state, 
            stratify=y
        )
        
        logger.info(f"Train set: {X_train.shape[0]} samples")
        logger.info(f"Test set: {X_test.shape[0]} samples")
        
        return X_train, X_test, y_train, y_test
    
    def get_feature_info(self) -> dict:
        """Get information about features for monitoring."""
        if self.df is None:
            raise ValueError("Data not loaded. Call load_data() first.")
        
        info = {
            "total_samples": len(self.df),
            "features": list(self.df.columns),
            "numeric_features": list(self.df.select_dtypes(include=[np.number]).columns),
            "categorical_features": list(self.df.select_dtypes(include=['object']).columns),
            "missing_values": self.df.isnull().sum().to_dict()
        }
        
        return info
    
    def run_full_pipeline(self) -> Tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series]:
        """Run the complete preprocessing pipeline."""
        self.load_data()
        self.clean_data()
        X, y = self.prepare_features()
        X_train, X_test, y_train, y_test = self.split_data(X, y)
        
        return X_train, X_test, y_train, y_test


if __name__ == "__main__":
    # Example usage
    preprocessor = DataPreprocessor()
    X_train, X_test, y_train, y_test = preprocessor.run_full_pipeline()
    
    print("\n=== Preprocessing Complete ===")
    print(f"Training samples: {len(X_train)}")
    print(f"Testing samples: {len(X_test)}")
    print(f"Churn rate in training: {y_train.mean()*100:.2f}%")
