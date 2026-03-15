"""
Stock Service - Business logic for stock data, training, and predictions.
"""

from ..repositories import DataFetcher
from ..utils import compute_technical_indicators


class StockService:
    """Service for stock-related operations."""
    
    def __init__(self):
        """Initialize StockService."""
        self.data_fetcher = DataFetcher()
    
    def get_historical_data(self, symbol, range_str='1y', interval_str='1d'):
        """
        Get historical stock data with technical indicators.
        
        Args:
            symbol: Stock symbol
            range_str: Time range
            interval_str: Data interval
        
        Returns:
            Dictionary with status and data
        
        Raises:
            ValueError: If no data is found
        """
        try:
            df = self.data_fetcher.fetch_historical_data(symbol, range_str, interval_str)
            
            if df.empty:
                raise ValueError(f"No data found for symbol {symbol}")
            
            # Add technical indicators
            df = compute_technical_indicators(df)
            
            # Reset index to include Timestamp in the data
            df = df.reset_index()
            
            # Convert Timestamp to string for JSON serialization
            if 'Timestamp' in df.columns:
                df['Timestamp'] = df['Timestamp'].dt.strftime('%Y-%m-%d %H:%M:%S')
            
            # Convert DataFrame to dict for JSON serialization
            result = df.tail(100).to_dict(orient='records')
            
            return {
                "status": "success",
                "symbol": symbol,
                "data_points": len(result),
                "data": result
            }
            
        except Exception as e:
            raise Exception(f"Error fetching stock data: {e}")
    
    def get_stock_with_technical_indicators(self, symbol, range_str='max', interval_str='1d'):
        """
        Get stock data with technical indicators (returns DataFrame).
        
        Args:
            symbol: Stock symbol
            range_str: Time range
            interval_str: Data interval
        
        Returns:
            DataFrame with technical indicators
        """
        df = self.data_fetcher.fetch_historical_data(symbol, range_str, interval_str)
        if not df.empty:
            df = compute_technical_indicators(df)
        return df
    
    def get_current_price(self, symbol):
        """
        Get current stock price context.
        
        Args:
            symbol: Stock symbol
        
        Returns:
            Dictionary with price data or None
        """
        return self.data_fetcher.fetch_stock_with_price_context(symbol)
