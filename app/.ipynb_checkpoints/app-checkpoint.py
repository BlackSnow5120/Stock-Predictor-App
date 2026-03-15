"""
Flask App Factory - Creates and configures the Flask application.
"""

from flask import Flask, jsonify
from flask_cors import CORS
from werkzeug.exceptions import HTTPException

from .config import Config
from .api import api_blueprint


def create_app(config_class=Config):
    """
    Create and configure Flask application.
    
    Args:
        config_class: Configuration class to use
    
    Returns:
        Configured Flask application
    """
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Enable CORS - Update to allow all origins
    CORS(app, origins="*", supports_credentials=True)
    
    # Register blueprint
    app.register_blueprint(api_blueprint, url_prefix='/')
    
    # Error handlers
    @app.errorhandler(HTTPException)
    def handle_http_exception(e):
        """Handle HTTP exceptions."""
        response = {
            "status": "error",
            "message": e.name,
            "code": e.code
        }
        return jsonify(response), e.code
    
    @app.errorhandler(Exception)
    def handle_generic_exception(e):
        """Handle generic exceptions."""
        response = {
            "status": "error",
            "message": str(e)
        }
        return jsonify(response), 500
    
    # Health check
    @app.route('/health')
    def health():
        """Health check endpoint."""
        return jsonify({
            "status": "healthy",
            "service": "Stock Prediction API"
        })
    
    return app
