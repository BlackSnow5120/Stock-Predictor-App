"""
Helper functions for the application.
"""

import os
import json
import numpy as np
import joblib
from sklearn.metrics import mean_squared_error, mean_absolute_error


def ensure_models_dir():
    """
    Ensure the models directory exists.
    
    Returns:
        Path to models directory
    """
    models_dir = "models"
    os.makedirs(models_dir, exist_ok=True)
    return models_dir


save_metrics = None  # Placeholder for backwards compatibility
load_metrics = None  # Placeholder for backwards compatibility


def get_model_paths(model_type):
    """
    Generate file paths for a given model type.
    
    Args:
        model_type: Model type identifier
    
    Returns:
        Dictionary with model, metrics, and scaler file paths
    """
    ensure_models_dir()
    return {
        "model": f"models/Stock_{model_type.upper()}.keras",
        "metrics": f"models/metrics_{model_type}.json",
        "scaler": f"models/scaler_{model_type}.pkl"
    }


def create_dataset(dataset, time_step=100):
    """
    Create sequences for time series training/prediction.
    
    Args:
        dataset: numpy array of shape (n_samples, n_features)
        time_step: Look-back window size
    
    Returns:
        Tuple of (X, y) where X has shape (n_samples, time_step, n_features)
        and y has shape (n_samples,)
    """
    X, y = [], []
    for i in range(len(dataset) - time_step - 1):
        X.append(dataset[i:(i + time_step)])
        y.append(dataset[i + time_step, 0])
    return np.array(X), np.array(y)


def calculate_metrics(y_true, y_pred):
    """
    Calculate evaluation metrics for model performance.
    
    Args:
        y_true: True values
        y_pred: Predicted values
    
    Returns:
        Dictionary with RMSE, MAE, and accuracy metrics
    """
    rmse = np.sqrt(mean_squared_error(y_true, y_pred))
    mae = mean_absolute_error(y_true, y_pred)
    
    if np.mean(y_true) != 0:
        accuracy = max(0, 100 - (rmse / np.mean(y_true) * 100))
    else:
        accuracy = 0
    
    return {
        "RMSE": float(rmse),
        "MAE": float(mae),
        "Accuracy": f"{accuracy:.2f}%"
    }


def save_metrics(metrics, metrics_path):
    """
    Save metrics to a JSON file.
    
    Args:
        metrics: Dictionary with metrics to save
        metrics_path: Path to save the metrics JSON file
    """
    try:
        os.makedirs(os.path.dirname(metrics_path), exist_ok=True)
        with open(metrics_path, 'w') as file:
            json.dump(metrics, file, indent=4)
    except Exception as e:
        raise Exception(f"Error saving metrics: {e}")


def load_metrics(metrics_path):
    """
    Load metrics from a JSON file.
    
    Args:
        metrics_path: Path to the metrics JSON file
    
    Returns:
        Dictionary with metrics or None if file doesn't exist
    """
    if os.path.exists(metrics_path):
        try:
            with open(metrics_path, 'r') as file:
                return json.load(file)
        except Exception as e:
            raise Exception(f"Error loading metrics: {e}")
    return None
