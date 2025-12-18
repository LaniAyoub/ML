"""
Test suite for data preprocessing module
"""
import pytest
import pandas as pd
import numpy as np
from src.data_preprocessing import DataPreprocessor


class TestDataPreprocessor:
    
    @pytest.fixture
    def sample_data(self):
        """Create sample data for testing."""
        return pd.DataFrame({
            'customerID': ['001', '002', '003'],
            'gender': ['Male', 'Female', 'Male'],
            'SeniorCitizen': [0, 1, 0],
            'Partner': ['Yes', 'No', 'Yes'],
            'Dependents': ['No', 'No', 'Yes'],
            'tenure': [12, 24, 36],
            'PhoneService': ['Yes', 'Yes', 'No'],
            'MultipleLines': ['No', 'Yes', 'No phone service'],
            'InternetService': ['DSL', 'Fiber optic', 'No'],
            'OnlineSecurity': ['Yes', 'No', 'No internet service'],
            'OnlineBackup': ['No', 'No', 'No internet service'],
            'DeviceProtection': ['Yes', 'No', 'No internet service'],
            'TechSupport': ['No', 'Yes', 'No internet service'],
            'StreamingTV': ['Yes', 'No', 'No internet service'],
            'StreamingMovies': ['No', 'Yes', 'No internet service'],
            'Contract': ['Month-to-month', 'One year', 'Two year'],
            'PaperlessBilling': ['Yes', 'No', 'Yes'],
            'PaymentMethod': ['Electronic check', 'Mailed check', 'Bank transfer (automatic)'],
            'MonthlyCharges': [50.0, 70.0, 90.0],
            'TotalCharges': ['600', '1680', '3240'],
            'Churn': ['No', 'Yes', 'No']
        })
    
    def test_data_loading(self, sample_data, tmp_path):
        """Test data loading functionality."""
        # Save sample data to temporary file
        csv_path = tmp_path / "test_data.csv"
        sample_data.to_csv(csv_path, index=False)
        
        # Load data
        preprocessor = DataPreprocessor(str(csv_path))
        df = preprocessor.load_data()
        
        assert df is not None
        assert len(df) == 3
        assert 'customerID' in df.columns
    
    def test_data_cleaning(self, sample_data, tmp_path):
        """Test data cleaning functionality."""
        # Add some invalid TotalCharges
        sample_data.loc[2, 'TotalCharges'] = 'invalid'
        
        csv_path = tmp_path / "test_data.csv"
        sample_data.to_csv(csv_path, index=False)
        
        preprocessor = DataPreprocessor(str(csv_path))
        preprocessor.load_data()
        cleaned_df = preprocessor.clean_data()
        
        # Should have dropped the invalid row
        assert len(cleaned_df) == 2
        assert cleaned_df['TotalCharges'].dtype in [np.float64, np.int64]
    
    def test_feature_preparation(self, sample_data, tmp_path):
        """Test feature and target preparation."""
        csv_path = tmp_path / "test_data.csv"
        sample_data.to_csv(csv_path, index=False)
        
        preprocessor = DataPreprocessor(str(csv_path))
        preprocessor.load_data()
        preprocessor.clean_data()
        X, y = preprocessor.prepare_features()
        
        # Check features don't include customerID or Churn
        assert 'customerID' not in X.columns
        assert 'Churn' not in X.columns
        
        # Check target is binary
        assert set(y.unique()).issubset({0, 1})
        
        # Check shapes match
        assert len(X) == len(y)
    
    def test_data_splitting(self, sample_data, tmp_path):
        """Test train/test splitting."""
        csv_path = tmp_path / "test_data.csv"
        sample_data.to_csv(csv_path, index=False)
        
        preprocessor = DataPreprocessor(str(csv_path))
        preprocessor.load_data()
        preprocessor.clean_data()
        X, y = preprocessor.prepare_features()
        X_train, X_test, y_train, y_test = preprocessor.split_data(X, y, test_size=0.33)
        
        # Check splits are not empty
        assert len(X_train) > 0
        assert len(X_test) > 0
        
        # Check total samples preserved
        assert len(X_train) + len(X_test) == len(X)
