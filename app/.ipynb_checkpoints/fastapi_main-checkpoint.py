"""
FastAPI Application - Stock Prediction API with Streamlit support.
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List
import sys
import os

# Add app directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.services import StockService, NewsService, ModelService


# Pydantic models for request/response
class TrainRequest(BaseModel):
    symbol: str = Field(..., description="Stock symbol (e.g., AAPL)")
    model_type: str = Field(default='lstm', description="Model type: lstm, chronos, chronos-t5")
    epochs: int = Field(default=10, ge=1, le=100, description="Training epochs (for LSTM)")
    batch_size: int = Field(default=32, ge=1, le=256, description="Batch size (for LSTM)")


class PredictRequest(BaseModel):
    symbol: str = Field(..., description="Stock symbol (e.g., AAPL)")
    model_type: str = Field(default='lstm', description="Model type: lstm, chronos, chronos-t5")
    days: int = Field(default=7, ge=1, le=30, description="Number of days to predict")


class SentimentRequest(BaseModel):
    symbol: str = Field(..., description="Stock symbol (e.g., AAPL)")
    snippet_count: int = Field(default=10, ge=1, le=50, description="Number of news snippets")


class DataRequest(BaseModel):
    symbol: str = Field(..., description="Stock symbol (e.g., AAPL)")
    range: str = Field(default='1y', description="Time range: 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, max")
    interval: str = Field(default='1d', description="Interval: 1m, 2m, 5m, 15m, 60m, 1h, 1d, 1wk, 1mo")


class PredictionResponse(BaseModel):
    date: str
    price: float


class ArticleResponse(BaseModel):
    Date: str
    Symbol: str
    Headline: str
    Summary: str
    Sentiment: str
    SentimentScore: float
    Open: float
    Close: float
    MovementRatio: float


# Create FastAPI app
app = FastAPI(
    title="Stock Prediction API",
    description="FastAPI for stock price prediction with LSTM, Chronos, and Chronos-T5 models",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
stock_service = StockService()
news_service = NewsService()
model_service = ModelService()


@app.get("/", tags=["Root"])
def home():
    """API information and available endpoints."""
    return {
        "name": "Stock Prediction API",
        "version": "2.0.0",
        "description": "FastAPI for stock price prediction with multiple ML models",
        "architecture": "3-Layer (API → Services → Repositories)",
        "endpoints": {
            "GET /": "API information",
            "GET /models": "List available models",
            "POST /train": "Train a model",
            "POST /predict": "Make predictions",
            "POST /sentiment": "Get news sentiment",
            "GET /metrics": "Get model metrics",
            "POST /data": "Fetch historical stock data",
            "GET /health": "Health check",
            "GET /docs": "Interactive API documentation (Swagger)",
            "GET /redoc": "API documentation (ReDoc)"
        }
    }


@app.get("/models", tags=["Models"])
def list_models():
    """List all available model types with descriptions."""
    return model_service.get_available_models()


@app.post("/train", tags=["Models"], response_model=dict)
def train(request: TrainRequest):
    """
    Train a model on historical stock data.
    
    - LSTM: Requires training, takes epochs and batch_size
    - Chronos/Chronos-T5: Pre-trained, just validates data fetch
    """
    try:
        if request.model_type not in ['lstm', 'chronos', 'chronos-t5']:
            raise HTTPException(
                status_code=400,
                detail=f"model_type must be 'lstm', 'chronos', or 'chronos-t5'"
            )
        
        result = model_service.train_model(
            stock_symbol=request.symbol,
            model_type=request.model_type,
            epochs=request.epochs,
            batch_size=request.batch_size
        )
        return result
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/predict", tags=["Models"], response_model=dict)
def predict(request: PredictRequest):
    """Predict future stock prices using a trained or pre-trained model."""
    try:
        if request.model_type not in ['lstm', 'chronos', 'chronos-t5']:
            raise HTTPException(
                status_code=400,
                detail=f"model_type must be 'lstm', 'chronos', or 'chronos-t5'"
            )
        
        result = model_service.predict_prices(
            stock_symbol=request.symbol,
            model_type=request.model_type,
            days_to_predict=request.days
        )
        return result
        
    except FileNotFoundError as e:
        raise HTTPException(
            status_code=404,
            detail=f"Model not found. Please train the {request.model_type} model first."
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/sentiment", tags=["News"], response_model=dict)
def sentiment(request: SentimentRequest):
    """Get news sentiment for a stock (last 30 days)."""
    try:
        result = news_service.get_news_with_sentiment(
            symbol=request.symbol,
            snippet_count=request.snippet_count
        )
        return result
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/metrics", tags=["Models"])
def metrics(model_type: str = Query(default='lstm', description="Model type")):
    """Get training metrics for a model."""
    try:
        result = model_service.get_model_metrics(model_type)
        return result
        
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/data", tags=["Data"])
def get_data(request: DataRequest):
    """Fetch historical stock data with technical indicators."""
    try:
        result = stock_service.get_historical_data(
            symbol=request.symbol,
            range_str=request.range,
            interval_str=request.interval
        )
        return result
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health", tags=["Health"])
def health():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "Stock Prediction FastAPI"
    }


if __name__ == "__main__":
    import uvicorn
    
    print("=" * 60)
    print("Stock Prediction API - FastAPI")
    print("=" * 60)
    print("Running at: http://127.0.0.1:8000")
    print("Interactive docs: http://127.0.0.1:8000/docs")
    print("ReDoc docs: http://127.0.0.1:8000/redoc")
    print("=" * 60)
    print("\nPress Ctrl+C to stop the server\n")
    
    uvicorn.run(app, host="127.0.0.1", port=8000)
