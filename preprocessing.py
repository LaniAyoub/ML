"""
Compatibility shim for preprocessing module.
This file ensures backward compatibility with the pickled model
which was trained with 'from preprocessing import CustomEncoder'.
"""
from src.preprocessing import CustomEncoder, ThresholdClassifier

__all__ = ['CustomEncoder', 'ThresholdClassifier']
