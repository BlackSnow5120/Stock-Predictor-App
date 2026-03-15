"""
Configuration settings for the application.
"""

import os

class Config:
    """Base configuration."""
    
    # Flask settings
    DEBUG = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    HOST = os.getenv('FLASK_HOST', '127.0.0.1')
    PORT = int(os.getenv('FLASK_PORT', 5000))
    
    # Data fetching
    YAHOO_USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
    YAHOO_REFERER = "https://finance.yahoo.com/"
    
    # Model settings
    MODELS_DIR = "models"
    LSTM_DEFAULT_TIMESTEP = 100
    LSTM_DEFAULT_EPOCHS = 10
    LSTM_BATCH_SIZE = 32
    
    # Prediction limits
    MAX_PREDICTION_DAYS = 30
    MAX_SNIPPET_COUNT = 50
    
    # Model types
    AVAILABLE_MODELS = ['lstm', 'chronos', 'chronos-t5']
    
    # HuggingFace models
    CHRONOS_MODEL = "amazon/chronos-t5-small"
    CHRONOS_T5_SIZES = {
        'tiny': 'amazon/chronos-t5-tiny',
        'mini': 'amazon/chronos-t5-mini',
        'small': 'amazon/chronos-t5-small',
        'base': 'amazon/chronos-t5-base',
        'large': 'amazon/chronos-t5-large'
    }
