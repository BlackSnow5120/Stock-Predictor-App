"""
Stock Prediction App - 3-Layer Architecture
"""

from .app import create_app
from .config import Config

__all__ = ['create_app', 'Config']
