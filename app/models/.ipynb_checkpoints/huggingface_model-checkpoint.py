"""
HuggingFace Model - Pre-trained Chronos-2 and Chronos-Bolt models for time series forecasting.
"""

import os
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

# In 2026, Chronos uses its own optimized package rather than raw transformers
try:
    from chronos import Chronos2Pipeline, BaseChronosPipeline
    HAS_CHRONOS = True
except ImportError:
    HAS_CHRONOS = False

try:
    import torch
    HAS_TORCH = True
except ImportError:
    HAS_TORCH = False

from .base_model import BaseModel
from ..repositories import DataFetcher, Storage
from ..utils import get_model_paths, ensure_models_dir


class ChronosModel(BaseModel):
    """Amazon Chronos-2 pre-trained model for time series forecasting."""
    
    def __init__(self, model_name='amazon/chronos-2'):
        """
        Initialize Chronos model.
        """
        super().__init__('chronos')
        self.model_name = model_name
        self.pipeline = None
        self.data_fetcher = DataFetcher()
        self.storage = Storage()
        
        if not HAS_CHRONOS or not HAS_TORCH:
            raise ImportError("chronos-forecasting and torch are required. Install with: pip install chronos-forecasting torch")
    
    def load_model(self):
        """Load the Chronos-2 model if not already loaded."""
        if self.pipeline is None:
            try:
                print(f"Loading Chronos-2 model: {self.model_name}...")
                self.pipeline = Chronos2Pipeline.from_pretrained(
                    self.model_name,
                    device_map="cpu",  # Use CPU for stability on Windows
                    torch_dtype="auto",
                )
                print("Chronos-2 model loaded successfully.")
            except Exception as e:
                print(f"Error loading Chronos-2 model: {e}")
                raise
    
    def train(self, stock_symbol, **kwargs):
        """Validate data fetch (pre-trained model doesn't require training)."""
        df = self.data_fetcher.fetch_historical_data(stock_symbol, range_str='200d', interval_str='1d')
        if df.empty:
            raise ValueError(f"Invalid or unavailable stock data for {stock_symbol}")
        
        ensure_models_dir()
        paths = get_model_paths(self.model_type)
        metrics = {
            "Model": self.model_name,
            "Type": "Pre-trained Chronos-2",
            "Status": "Ready for inference",
            "DataPoints": len(df)
        }
        self.storage.save_metrics({"current_metrics": metrics}, paths['metrics'].split('/')[-1])
        return metrics
    
    def predict(self, stock_symbol, days_to_predict=7, **kwargs):
        if self.pipeline is None:
            self.load_model()
        
        # 1. Fetch
        df = self.data_fetcher.fetch_historical_data(stock_symbol, range_str='365d', interval_str='1d')
        if df.empty:
            raise ValueError(f"No data for {stock_symbol}")

        # 2. Fix Frequency Gaps (The "Market Holiday" Fix)
        # We ensure every business day is present to stop the 'infer frequency' error
        df = df[~df.index.duplicated(keep='first')].sort_index()
        clean_df = pd.DataFrame()
        clean_df['timestamp'] = pd.to_datetime(df.index).tz_localize(None)
        clean_df['target'] = df['Close'].values
        clean_df['id'] = str(stock_symbol)
    
        # Fill missing dates (holidays, etc.) with last known close price
        clean_df = clean_df.set_index('timestamp')
        
        # Create a complete weekday date range
        full_range = pd.date_range(
            start=clean_df.index.min(),
            end=clean_df.index.max(),
            freq='B'  # 'B' = business days (Mon-Fri)
        )
        
        # Reindex to include missing dates, then forward-fill
        clean_df = (
            clean_df
            .reindex(full_range)
            .ffill()                         # fill target with last close
            .fillna({'id': str(stock_symbol)})     # fill any leading NaN ids
            .reset_index()
            .rename(columns={'index': 'timestamp'})
        )
        import logging
        logger = logging.getLogger("uvicorn.error")
        logger.info(f"--- CHRONOS INPUT CHECK ---")
        logger.info(f"Verified Frequency: Business Days (B)")
        logger.info(f"Rows after re-indexing: {len(clean_df)}")

        try:
            # 1. Generate the raw "return" predictions
            pred_df = self.pipeline.predict_df(
                clean_df[['id', 'timestamp', 'target']], 
                prediction_length=days_to_predict,
                quantile_levels=[0.5],
                id_column="id",
                timestamp_column="timestamp",
                target="target"
            )
            
            # 2. Get the last known price to use as a starting point
            last_price = clean_df['target'].iloc[-1]
            
            # 3. Convert returns back to dollar prices
            results = []
            
            for _, row in pred_df.iterrows():
                # The model predicts the change factor (e.g., -0.04 is a 4% drop)
                # Formula: New Price = Old Price * (1 + Change)
                pred_price = float(row['predictions'])
                
                results.append({
                    "date": row['timestamp'].strftime('%Y-%m-%d'),
                    "price": round(pred_price, 2) # Now in Dollars!
                })
            
            return results

        except Exception as e:
            logger.error(f"Chronos-2 Price Reconstruction failed: {str(e)}")
            raise

    def get_metrics(self):
        paths = get_model_paths(self.model_type)
        metrics = self.storage.load_metrics(paths['metrics'].split('/')[-1])
        return metrics.get("current_metrics") if metrics else None


class ChronosT5Model(BaseModel):
    """Amazon Chronos-Bolt model for high-speed time series forecasting."""
    
    def __init__(self, size='small'):
        """
        Chronos-Bolt is the 2026 standard for fast inference (250x faster than T5).
        """
        size_map = {
            'tiny': 'amazon/chronos-bolt-tiny',
            'mini': 'amazon/chronos-bolt-mini',
            'small': 'amazon/chronos-bolt-small',
            'base': 'amazon/chronos-bolt-base'
        }
        self.model_name = size_map.get(size, 'amazon/chronos-bolt-small')
        super().__init__('chronos-bolt')
        self.pipeline = None
        self.data_fetcher = DataFetcher()
        self.storage = Storage()
        
        if not HAS_CHRONOS:
            raise ImportError("chronos-forecasting is required.")

    def get_metrics(self):
        paths = get_model_paths(self.model_type)
        metrics = self.storage.load_metrics(paths['metrics'].split('/')[-1])
        return metrics.get("current_metrics") if metrics else None


    def load_model(self):
        if self.pipeline is None:
            print(f"Loading Chronos-Bolt model: {self.model_name}...")
            self.pipeline = BaseChronosPipeline.from_pretrained(
                self.model_name,
                device_map="cpu",
                torch_dtype="auto",
            )
    def train(self, stock_symbol, **kwargs):
        """Validate data fetch (pre-trained model doesn't require training)."""
        df = self.data_fetcher.fetch_historical_data(stock_symbol, range_str='200d', interval_str='1d')
        if df.empty:
            raise ValueError(f"Invalid or unavailable stock data for {stock_symbol}")
        
        ensure_models_dir()
        paths = get_model_paths(self.model_type)
        metrics = {
            "Model": self.model_name,
            "Type": "Pre-trained Chronos-2",
            "Status": "Ready for inference",
            "DataPoints": len(df)
        }
        self.storage.save_metrics({"current_metrics": metrics}, paths['metrics'].split('/')[-1])
        return metrics
    def predict(self, stock_symbol, days_to_predict=7, **kwargs):
        if self.pipeline is None:
            self.load_model()
        
        # 1. Fetch
        df = self.data_fetcher.fetch_historical_data(stock_symbol, range_str='365d', interval_str='1d')
        if df.empty:
            raise ValueError(f"No data for {stock_symbol}")

        # 2. Fix Frequency Gaps (The "Market Holiday" Fix)
        # We ensure every business day is present to stop the 'infer frequency' error
        df = df[~df.index.duplicated(keep='first')].sort_index()
        clean_df = pd.DataFrame()
        clean_df['timestamp'] = pd.to_datetime(df.index).tz_localize(None)
        clean_df['target'] = df['Close'].values
        clean_df['id'] = str(stock_symbol)
    
        # Fill missing dates (holidays, etc.) with last known close price
        clean_df = clean_df.set_index('timestamp')
        
        # Create a complete weekday date range
        full_range = pd.date_range(
            start=clean_df.index.min(),
            end=clean_df.index.max(),
            freq='B'  # 'B' = business days (Mon-Fri)
        )
        
        # Reindex to include missing dates, then forward-fill
        clean_df = (
            clean_df
            .reindex(full_range)
            .ffill()                         # fill target with last close
            .fillna({'id': str(stock_symbol)})     # fill any leading NaN ids
            .reset_index()
            .rename(columns={'index': 'timestamp'})
        )
        import logging
        logger = logging.getLogger("uvicorn.error")
        logger.info(f"--- CHRONOS INPUT CHECK ---")
        logger.info(f"Verified Frequency: Business Days (B)")
        logger.info(f"Rows after re-indexing: {len(clean_df)}")

        try:
            # 1. Generate the raw "return" predictions
            pred_df = self.pipeline.predict_df(
                clean_df[['id', 'timestamp', 'target']], 
                prediction_length=days_to_predict,
                quantile_levels=[0.5],
                id_column="id",
                timestamp_column="timestamp",
                target="target"
            )
            
            # 2. Get the last known price to use as a starting point
            last_price = clean_df['target'].iloc[-1]
            
            # 3. Convert returns back to dollar prices
            results = []
            
            for _, row in pred_df.iterrows():
                # The model predicts the change factor (e.g., -0.04 is a 4% drop)
                # Formula: New Price = Old Price * (1 + Change)
                pred_price = float(row['predictions'])
                
                results.append({
                    "date": row['timestamp'].strftime('%Y-%m-%d'),
                    "price": round(pred_price, 2) # Now in Dollars!
                })
            
            return results

        except Exception as e:
            logger.error(f"Chronos-2 Price Reconstruction failed: {str(e)}")
            raise
