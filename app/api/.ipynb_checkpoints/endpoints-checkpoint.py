"""
Endpoints - Flask routes for the API.
"""

from flask import Blueprint, request, jsonify
import traceback

from .schemas import TrainRequest, PredictRequest, SentimentRequest, DataRequest
from ..services import StockService, NewsService, ModelService


api_blueprint = Blueprint('api', __name__)


# Initialize services
stock_service = StockService()
news_service = NewsService()
model_service = ModelService()


@api_blueprint.route('/')
def home():
    """
    Home endpoint with API information.
    
    Returns:
        JSON with API details and available endpoints
    """
    return jsonify({
        "name": "Stock Prediction API",
        "version": "1.0",
        "description": "RESTful API for stock price prediction with multiple ML models",
        "architecture": "3-Layer (API → Services → Repositories)",
        "endpoints": {
            "GET /": "API information",
            "GET /models": "List available models",
            "POST /train": "Train a model",
            "POST /predict": "Make predictions",
            "POST /sentiment": "Get news sentiment",
            "GET /metrics": "Get training metrics",
            "POST /data": "Fetch historical stock data"
        }
    })


@api_blueprint.route('/models', methods=['GET'])
def list_models():
    """
    List all available model types.
    
    Returns:
        JSON with list of available models and descriptions
    """
    try:
        models_info = model_service.get_available_models()
        return jsonify({
            "status": "success",
            **models_info
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


@api_blueprint.route('/train', methods=['POST'])
def train():
    """
    Train a selected model.
    
    Request Body:
        {
            "symbol": "AAPL",
            "model_type": "lstm",
            "epochs": 10,
            "batch_size": 32
        }
    
    Returns:
        JSON with training metrics
    """
    try:
        data = request.get_json()
        
        # Validate request
        train_req = TrainRequest(
            symbol=data.get('symbol', 'AAPL'),
            model_type=data.get('model_type', 'lstm'),
            epochs=int(data.get('epochs', 10)),
            batch_size=int(data.get('batch_size', 32))
        )
        train_req.validate()
        
        # Train model
        result = model_service.train_model(
            stock_symbol=train_req.symbol,
            model_type=train_req.model_type,
            epochs=train_req.epochs,
            batch_size=train_req.batch_size
        )
        
        return jsonify(result)
        
    except ValueError as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 400
    except Exception as e:
        print(f"Error during training: {traceback.format_exc()}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


@api_blueprint.route('/predict', methods=['POST'])
def predict():
    """
    Predict future stock prices.
    
    Request Body:
        {
            "symbol": "AAPL",
            "model_type": "lstm",
            "days": 7
        }
    
    Returns:
        JSON with predicted prices
    """
    try:
        data = request.get_json()
        
        # Validate request
        predict_req = PredictRequest(
            symbol=data.get('symbol', 'AAPL'),
            model_type=data.get('model_type', 'lstm'),
            days=int(data.get('days', 7))
        )
        predict_req.validate()
        
        # Generate predictions
        result = model_service.predict_prices(
            stock_symbol=predict_req.symbol,
            model_type=predict_req.model_type,
            days_to_predict=predict_req.days
        )
        
        return jsonify(result)
        
    except ValueError as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 400
    except FileNotFoundError as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 404
    except Exception as e:
        print(f"Error during prediction: {traceback.format_exc()}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


@api_blueprint.route('/sentiment', methods=['POST'])
def sentiment():
    """
    Get news sentiment for a stock.
    
    Request Body:
        {
            "symbol": "AAPL",
            "snippet_count": 10
        }
    
    Returns:
        JSON with news articles and sentiment analysis
    """
    try:
        data = request.get_json()
        
        # Validate request
        sentiment_req = SentimentRequest(
            symbol=data.get('symbol', 'AAPL'),
            snippet_count=int(data.get('snippet_count', 10))
        )
        sentiment_req.validate()
        
        # Get sentiment
        result = news_service.get_news_with_sentiment(
            symbol=sentiment_req.symbol,
            snippet_count=sentiment_req.snippet_count
        )
        
        return jsonify(result)
        
    except ValueError as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 400
    except Exception as e:
        print(f"Error analyzing sentiment: {traceback.format_exc()}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


@api_blueprint.route('/metrics', methods=['GET'])
def metrics():
    """
    Get training metrics for a model.
    
    Query Parameters:
        model_type: Type of model (default: lstm)
    
    Returns:
        JSON with metrics
    """
    try:
        model_type = request.args.get('model_type', 'lstm')
        
        # Get metrics
        result = model_service.get_model_metrics(model_type)
        
        return jsonify(result)
        
    except FileNotFoundError as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 404
    except Exception as e:
        print(f"Error fetching metrics: {traceback.format_exc()}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


@api_blueprint.route('/data', methods=['POST'])
def get_data():
    """
    Fetch historical stock data.
    
    Request Body:
        {
            "symbol": "AAPL",
            "range": "1y",
            "interval": "1d"
        }
    
    Returns:
        JSON with historical data
    """
    try:
        data = request.get_json()
        
        # Validate request
        data_req = DataRequest(
            symbol=data.get('symbol', 'AAPL'),
            range=data.get('range', '1y'),
            interval=data.get('interval', '1d')
        )
        data_req.validate()
        
        # Get historical data
        result = stock_service.get_historical_data(
            symbol=data_req.symbol,
            range_str=data_req.range,
            interval_str=data_req.interval
        )
        
        return jsonify(result)
        
    except ValueError as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 400
    except Exception as e:
        print(f"Error fetching stock data: {traceback.format_exc()}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


@api_blueprint.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({
        "status": "error",
        "message": "Endpoint not found"
    }), 404


@api_blueprint.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    return jsonify({
        "status": "error",
        "message": "Internal server error"
    }), 500
