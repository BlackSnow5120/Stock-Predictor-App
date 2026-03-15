"""
Base Model - Abstract base class for all prediction models.
"""

from abc import ABC, abstractmethod


class BaseModel(ABC):
    """Abstract base class for prediction models."""
    
    def __init__(self, model_type):
        """
        Initialize base model.
        
        Args:
            model_type: Type identifier for the model
        """
        self.model_type = model_type
        self.model = None
    
    @abstractmethod
    def train(self, stock_symbol, **kwargs):
        """
        Train the model on historical data.
        
        Args:
            stock_symbol: Stock symbol to train on
            **kwargs: Additional training arguments
        
        Returns:
            Dictionary with training metrics
        """
        pass
    
    @abstractmethod
    def predict(self, stock_symbol, days_to_predict=7, **kwargs):
        """
        Predict future stock prices.
        
        Args:
            stock_symbol: Stock symbol
            days_to_predict: Number of days to predict
            **kwargs: Additional prediction arguments
        
        Returns:
            List of dictionaries with date and predicted price
        """
        pass
    
    @abstractmethod
    def get_metrics(self):
        """
        Get the training metrics for this model.
        
        Returns:
            Dictionary with metrics or None if not trained yet
        """
        pass
    
    def is_trained(self):
        """
        Check if the model has been trained.
        
        Returns:
            True if model is trained, False otherwise
        """
        return self.model is not None
