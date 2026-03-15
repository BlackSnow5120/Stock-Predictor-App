"""
Model Service - Business logic for model training and prediction.
"""

import traceback
from ..models import LSTMModel, ChronosModel, ChronosT5Model, BaseModel
from ..config import Config


class ModelService:
    """Service for model-related operations."""
    
    def __init__(self):
        """Initialize ModelService."""
        self.available_models = Config.AVAILABLE_MODELS
        self.model_descriptions = {
            "lstm": "Local Bidirectional LSTM with attention - requires training",
            "chronos": "HuggingFace Chronos pre-trained model",
            "chronos-t5": "Amazon Chronos-T5 pre-trained model"
        }
        self._loaded_models = {}
    
    def get_available_models(self):
        """
        Get list of available models with descriptions.
        
        Returns:
            Dictionary with models list and descriptions
        """
        return {
            "models": self.available_models,
            "descriptions": self.model_descriptions
        }
    
    def get_model(self, model_type) -> BaseModel:
        """
        Factory method to get a model instance.
        
        Args:
            model_type: Type of model
        
        Returns:
            Model instance
        
        Raises:
            ValueError: If model type is unknown
        """
        model_type = model_type.lower()
        
        # Return cached model if available
        if model_type in self._loaded_models:
            return self._loaded_models[model_type]
        
        if model_type == 'lstm':
            model = LSTMModel()
        elif model_type == 'chronos':
            model = ChronosModel()
        elif model_type == 'chronos-t5':
            model = ChronosT5Model()
        else:
            raise ValueError(
                f"Unknown model type: {model_type}. "
                f"Available: {self.available_models}"
            )
        
        self._loaded_models[model_type] = model
        return model
    
    def train_model(self, stock_symbol, model_type, **kwargs):
        """
        Train a model on historical data.
        
        Args:
            stock_symbol: Stock symbol
            model_type: Type of model to train
            **kwargs: Additional training arguments (epochs, batch_size, etc.)
        
        Returns:
            Dictionary with training status and metrics
        
        Raises:
            Exception: If training fails
        """
        try:
            model = self.get_model(model_type)
            
            print(f"Training {model_type.upper()} model for {stock_symbol}...")
            metrics = model.train(stock_symbol, **kwargs)
            
            return {
                "status": "success",
                "symbol": stock_symbol,
                "model_type": model_type,
                "metrics": metrics
            }
            
        except ImportError as e:
            raise Exception(
                f"Missing dependencies for {model_type} model. "
                f"Error: {str(e)}"
            )
        except Exception as e:
            print(f"Error during training: {traceback.format_exc()}")
            raise Exception(f"Training failed: {e}")
    
    def predict_prices(self, stock_symbol, model_type, days_to_predict=7, **kwargs):
        """
        Predict future stock prices using a trained model.
        
        Args:
            stock_symbol: Stock symbol
            model_type: Type of model to use
            days_to_predict: Number of days to predict
            **kwargs: Additional prediction arguments
        
        Returns:
            Dictionary with prediction status and data
        
        Raises:
            FileNotFoundError: If model is not trained
            Exception: If prediction fails
        """
        try:
            if days_to_predict < 1 or days_to_predict > Config.MAX_PREDICTION_DAYS:
                raise ValueError(
                    f"Days must be between 1 and {Config.MAX_PREDICTION_DAYS}"
                )
            
            model = self.get_model(model_type)
            
            print(f"Predicting {days_to_predict} days for {stock_symbol} using {model_type}...")
            predictions = model.predict(stock_symbol, days_to_predict, **kwargs)
            
            return {
                "status": "success",
                "symbol": stock_symbol,
                "model_type": model_type,
                "predictions": predictions
            }
            
        except FileNotFoundError as e:
            raise FileNotFoundError(
                f"Model not found. Please train the {model_type} model first."
            )
        except Exception as e:
            print(f"Error during prediction: {traceback.format_exc()}")
            raise Exception(f"Prediction failed: {e}")
    
    def get_model_metrics(self, model_type):
        """
        Get training metrics for a model.
        
        Args:
            model_type: Type of model
        
        Returns:
            Dictionary with metrics
        
        Raises:
            FileNotFoundError: If no metrics found
            Exception: If error occurs
        """
        try:
            model = self.get_model(model_type)
            metrics = model.get_metrics()
            
            if metrics:
                return {
                    "status": "success",
                    "model_type": model_type,
                    "metrics": metrics
                }
            else:
                raise FileNotFoundError(
                    f"No metrics found for {model_type}. "
                    f"Train the model first."
                )
                
        except Exception as e:
            print(f"Error fetching metrics: {traceback.format_exc()}")
            raise Exception(f"Failed to get metrics: {e}")
