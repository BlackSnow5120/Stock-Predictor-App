"""
Storage Repository - Model and metrics persistence.
"""

import os
import json
import joblib
from pathlib import Path


class Storage:
    """Repository for saving and loading models, metrics, and scalers."""
    
    def __init__(self, base_dir="models"):
        """
        Initialize Storage.
        
        Args:
            base_dir: Base directory for storing files
        """
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)
    
    def get_path(self, filename):
        """
        Get full path for a file.
        
        Args:
            filename: Name of the file
        
        Returns:
            Full path as Path object
        """
        return self.base_dir / filename
    
    def save_model(self, model, filename):
        """
        Save a Keras model.
        
        Args:
            model: Keras model to save
            filename: Name of the file
        """
        try:
            model.save(str(self.get_path(filename)))
        except Exception as e:
            raise Exception(f"Error saving model: {e}")
    
    def load_model(self, filename, compile=False):
        """
        Load a Keras model.
        
        Args:
            filename: Name of the file to load
            compile: Whether to compile the model
        
        Returns:
            Loaded Keras model
        """
        try:
            from tensorflow.keras.models import load_model
            return load_model(str(self.get_path(filename)), compile=compile)
        except ImportError:
            raise Exception("TensorFlow not installed. Cannot load Keras model.")
        except Exception as e:
            raise Exception(f"Error loading model: {e}")
    
    def model_exists(self, filename):
        """
        Check if a model file exists.
        
        Args:
            filename: Name of the file
        
        Returns:
            True if file exists, False otherwise
        """
        return self.get_path(filename).exists()
    
    def save_scaler(self, scaler, filename):
        """
        Save a scaler using joblib.
        
        Args:
            scaler: Scaler object to save
            filename: Name of the file
        """
        try:
            joblib.dump(scaler, str(self.get_path(filename)))
        except Exception as e:
            raise Exception(f"Error saving scaler: {e}")
    
    def load_scaler(self, filename):
        """
        Load a scaler using joblib.
        
        Args:
            filename: Name of the file
        
        Returns:
            Loaded scaler
        """
        try:
            return joblib.load(str(self.get_path(filename)))
        except Exception as e:
            raise Exception(f"Error loading scaler: {e}")
    
    def save_metrics(self, metrics, filename):
        """
        Save metrics to a JSON file.
        
        Args:
            metrics: Dictionary with metrics
            filename: Name of the file
        """
        try:
            with open(self.get_path(filename), 'w') as file:
                json.dump(metrics, file, indent=4)
        except Exception as e:
            raise Exception(f"Error saving metrics: {e}")
    
    def load_metrics(self, filename):
        """
        Load metrics from a JSON file.
        
        Args:
            filename: Name of the file
        
        Returns:
            Dictionary with metrics or None if file doesn't exist
        """
        path = self.get_path(filename)
        if path.exists():
            try:
                with open(path, 'r') as file:
                    return json.load(file)
            except Exception as e:
                raise Exception(f"Error loading metrics: {e}")
        return None
    
    def delete_file(self, filename):
        """
        Delete a file.
        
        Args:
            filename: Name of the file to delete
        """
        try:
            path = self.get_path(filename)
            if path.exists():
                path.unlink()
        except Exception as e:
            raise Exception(f"Error deleting file: {e}")
    
    def list_files(self, pattern="*"):
        """
        List files matching a pattern.
        
        Args:
            pattern: Glob pattern to match files
        
        Returns:
            List of matching filenames
        """
        return [f.name for f in self.base_dir.glob(pattern)]
