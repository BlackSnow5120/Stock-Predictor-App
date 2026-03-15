"""
Technical indicators for stock analysis.
"""

import pandas as pd
import numpy as np


def compute_rsi(series, period=14):
    """
    Calculate the Relative Strength Index (RSI).
    
    Args:
        series: pandas Series of prices
        period: RSI period (default: 14)
    
    Returns:
        pandas Series with RSI values
    """
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / (loss + 1e-10)
    return 100 - (100 / (1 + rs))


def compute_macd(series, fast=12, slow=26, signal=9):
    """
    Calculate the Moving Average Convergence Divergence (MACD).
    
    Args:
        series: pandas Series of prices
        fast: Fast EMA period (default: 12)
        slow: Slow EMA period (default: 26)
        signal: Signal line period (default: 9)
    
    Returns:
        pandas Series with MACD histogram values
    """
    exp1 = series.ewm(span=fast, adjust=False).mean()
    exp2 = series.ewm(span=slow, adjust=False).mean()
    macd = exp1 - exp2
    signal_line = macd.ewm(span=signal, adjust=False).mean()
    return macd - signal_line


def compute_technical_indicators(df):
    """
    Add technical indicators to a dataframe.
    
    Args:
        df: pandas DataFrame with 'Close' column
    
    Returns:
        DataFrame with additional columns for technical indicators
    """
    df = df.copy()
    df['returns'] = df['Close'].pct_change()
    df['ma7'] = df['Close'].rolling(window=7).mean()
    df['ma21'] = df['Close'].rolling(window=21).mean()
    df['rsi'] = compute_rsi(df['Close'], 14)
    df['macd'] = compute_macd(df['Close'])
    df = df.fillna(0)
    return df
