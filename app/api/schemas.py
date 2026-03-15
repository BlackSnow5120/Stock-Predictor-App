"""
Schemas - Request and response validation schemas.
"""

from dataclasses import dataclass, asdict
from typing import List, Optional, Dict, Any


@dataclass
class TrainRequest:
    """Request schema for model training."""
    symbol: str
    model_type: str = 'lstm'
    epochs: int = 10
    batch_size: int = 32
    
    def validate(self):
        """Validate request data."""
        if not self.symbol or not isinstance(self.symbol, str):
            raise ValueError("symbol is required and must be a string")
        if self.model_type not in ['lstm', 'chronos', 'chronos-t5']:
            raise ValueError("model_type must be 'lstm', 'chronos', or 'chronos-t5'")
        if self.epochs < 1 or self.epochs > 100:
            raise ValueError("epochs must be between 1 and 100")
        if self.batch_size < 1 or self.batch_size > 256:
            raise ValueError("batch_size must be between 1 and 256")


@dataclass
class PredictRequest:
    """Request schema for price prediction."""
    symbol: str
    model_type: str = 'lstm'
    days: int = 7
    
    def validate(self):
        """Validate request data."""
        if not self.symbol or not isinstance(self.symbol, str):
            raise ValueError("symbol is required and must be a string")
        if self.model_type not in ['lstm', 'chronos', 'chronos-t5']:
            raise ValueError("model_type must be 'lstm', 'chronos', or 'chronos-t5'")
        if self.days < 1 or self.days > 30:
            raise ValueError("days must be between 1 and 30")


@dataclass
class SentimentRequest:
    """Request schema for sentiment analysis."""
    symbol: str
    snippet_count: int = 10
    
    def validate(self):
        """Validate request data."""
        if not self.symbol or not isinstance(self.symbol, str):
            raise ValueError("symbol is required and must be a string")
        if self.snippet_count < 1 or self.snippet_count > 50:
            raise ValueError("snippet_count must be between 1 and 50")


@dataclass
class DataRequest:
    """Request schema for historical data."""
    symbol: str
    range: str = '1y'
    interval: str = '1d'
    
    def validate(self):
        """Validate request data."""
        if not self.symbol or not isinstance(self.symbol, str):
            raise ValueError("symbol is required and must be a string")
        valid_ranges = ['1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', 'max']
        if self.range not in valid_ranges:
            raise ValueError(f"range must be one of {valid_ranges}")
        valid_intervals = ['1m', '2m', '5m', '15m', '60m', '90m', '1h', '1d', '5d', '1wk', '1mo', '3mo']
        if self.interval not in valid_intervals:
            raise ValueError(f"interval must be one of {valid_intervals}")


@dataclass
class PredictionResponse:
    """Response schema for price prediction."""
    date: str
    price: float


@dataclass
class ArticleResponse:
    """Response schema for news article."""
    Date: str
    Symbol: str
    Headline: str
    Summary: str
    Sentiment: str
    SentimentScore: float
    Open: float
    Close: float
    MovementRatio: float


@dataclass
class ErrorResponse:
    """Response schema for errors."""
    status: str
    message: str
    details: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)
