"""
LSTM Model - Bidirectional LSTM with attention for stock prediction.
"""

import time
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from sklearn.preprocessing import MinMaxScaler

try:
    from tensorflow.keras.models import Sequential, Model, load_model
    from tensorflow.keras.layers import LSTM, Dense, Dropout, Bidirectional, Input
    HAS_TENSORFLOW = True
except ImportError:
    HAS_TENSORFLOW = False

from .base_model import BaseModel
from ..repositories import DataFetcher, Storage
from ..utils import (
    compute_technical_indicators,
    create_dataset,
    calculate_metrics,
    get_model_paths
)


class LSTMModel(BaseModel):
    """Bidirectional LSTM model with attention for stock price prediction."""
    
    def __init__(self, time_step=100):
        """
        Initialize LSTM model.
        
        Args:
            time_step: Look-back window size
        """
        super().__init__('lstm')
        self.time_step = time_step
        self.scaler = None
        self.data_fetcher = DataFetcher()
        self.storage = Storage()
        
        if not HAS_TENSORFLOW:
            raise ImportError("TensorFlow is required for LSTM model. Install with: pip install tensorflow")
    
    def _build_model(self, input_shape):
        """
        Build the LSTM model architecture.
        
        Args:
            input_shape: Input shape tuple (time_step, n_features)
        
        Returns:
            Compiled Keras model
        """
        inputs = Input(shape=input_shape)
        x = Bidirectional(LSTM(64, return_sequences=True))(inputs)
        x = Dropout(0.2)(x)
        x = LSTM(50, return_sequences=True)(x)
        x = LSTM(50, return_sequences=True)(x)
        x = LSTM(50)(x)
        outputs = Dense(1)(x)
        
        model = Model(inputs, outputs)
        model.compile(loss='mean_squared_error', optimizer='adam')
        return model
    
    def train(self, stock_symbol, epochs=10, batch_size=32, **kwargs):
        """
        Train the LSTM model on historical stock data.
        
        Args:
            stock_symbol: Stock symbol to train on
            epochs: Number of training epochs
            batch_size: Batch size for training
            **kwargs: Additional arguments (ignored)
        
        Returns:
            Dictionary with training metrics
        """
        print(f"Fetching historical data for {stock_symbol}...")
        df = self.data_fetcher.fetch_historical_data(
            stock_symbol, 
            range_str='max', 
            interval_str='1d'
        )
        if df.empty:
            raise ValueError(f"Invalid or unavailable stock data for {stock_symbol}")
        
        # Add technical indicators
        df = compute_technical_indicators(df)
        feature_cols = ['Close', 'Volume', 'returns', 'ma7', 'ma21', 'rsi', 'macd']
        
        # Scale data
        self.scaler = MinMaxScaler(feature_range=(0, 1))
        scaled_data = self.scaler.fit_transform(df[feature_cols])
        
        # Create sequences
        X_data, y_data = create_dataset(scaled_data, self.time_step)
        
        # Build and train model
        print(f"Building and training LSTM model...")
        self.model = self._build_model(input_shape=(self.time_step, X_data.shape[2]))
        
        paths = get_model_paths(self.model_type)
        if self.storage.model_exists(paths['model'].split('/')[-1]):
            print(f"Loading existing model from {paths['model']}")
            self.model = load_model(paths['model'])
        
        start_time = time.time()
        history = self.model.fit(
            X_data, 
            y_data, 
            epochs=epochs, 
            batch_size=batch_size, 
            verbose=1, 
            validation_split=0.2
        )
        training_time = time.time() - start_time
        
        # Save model and scaler
        self.storage.save_model(self.model, paths['model'].split('/')[-1])
        self.storage.save_scaler(self.scaler, paths['scaler'].split('/')[-1])
        
        # Calculate metrics
        predicted = self.model.predict(X_data).flatten()
        metrics = calculate_metrics(y_data, predicted)
        metrics["Training Time"] = f"{int(training_time)}s"
        metrics["Epochs"] = epochs
        
        # Save metrics
        self.storage.save_metrics(
            {"current_metrics": metrics, "history": {"loss": [float(l) for l in history.history['loss']]}},
            paths['metrics'].split('/')[-1]
        )
        
        print(f"Training complete. Model saved to {paths['model']}")
        return metrics
    
    def predict(self, stock_symbol, days_to_predict=7, **kwargs):
        """
        Predict future stock prices.
        
        Args:
            stock_symbol: Stock symbol
            days_to_predict: Number of days to predict
            **kwargs: Additional arguments (ignored)
        
        Returns:
            List of dictionaries with date and predicted price
        """
        paths = get_model_paths(self.model_type)
        model_file = paths['model'].split('/')[-1]
        scaler_file = paths['scaler'].split('/')[-1]
        
        if not self.storage.model_exists(model_file):
            raise FileNotFoundError(f"LSTM model not found. Please train it first.")
        if not self.storage.model_exists(scaler_file):
            raise FileNotFoundError("Scaler file not found. Cannot proceed with prediction.")
        
        self.model = self.storage.load_model(model_file, compile=False)
        self.scaler = self.storage.load_scaler(scaler_file)
        
        # Fetch recent data
        df = self.data_fetcher.fetch_historical_data(
            stock_symbol, 
            range_str='200d', 
            interval_str='1d'
        )
        if df.empty or len(df) < self.time_step:
            raise ValueError("Could not fetch sufficient recent stock data for prediction.")
        
        # Add technical indicators
        df = compute_technical_indicators(df)
        feature_cols = ['Close', 'Volume', 'returns', 'ma7', 'ma21', 'rsi', 'macd']
        scaled_data = self.scaler.transform(df[feature_cols])
        
        # Generate predictions
        temp_input = scaled_data[-self.time_step:].tolist()
        lst_output = []
        
        for _ in range(days_to_predict):
            x_input = np.array(temp_input[-self.time_step:]).reshape(1, self.time_step, scaled_data.shape[1])
            yhat = self.model.predict(x_input, verbose=0)
            
            # Append prediction as new row
            last_row = temp_input[-1].copy()
            last_row[0] = yhat[0][0]
            temp_input.append(last_row)
            lst_output.append(yhat[0][0])
        
        # Inverse scale predictions
        dummy_full = np.zeros((len(lst_output), scaled_data.shape[1]))
        dummy_full[:, 0] = lst_output
        future_prices_rescaled = self.scaler.inverse_transform(dummy_full)[:, 0]
        
        future_dates = [
            (datetime.today() + timedelta(days=i+1)).strftime('%Y-%m-%d')
            for i in range(days_to_predict)
        ]
        
        return [
            {"date": date, "price": float(price)} 
            for date, price in zip(future_dates, future_prices_rescaled)
        ]
    
    def get_metrics(self):
        """
        Get the training metrics for this model.
        
        Returns:
            Dictionary with metrics or None if not trained yet
        """
        paths = get_model_paths(self.model_type)
        metrics = self.storage.load_metrics(paths['metrics'].split('/')[-1])
        return metrics.get("current_metrics") if metrics else None
