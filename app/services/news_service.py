"""
News Service - Business logic for news fetching and sentiment analysis.
"""

from datetime import datetime
from ..repositories import DataFetcher


class NewsService:
    """Service for news-related operations."""
    
    def __init__(self):
        """Initialize NewsService."""
        self.data_fetcher = DataFetcher()
    
    def get_news_with_sentiment(self, symbol, snippet_count=10):
        """
        Get news articles with sentiment analysis (last 30 days).
        
        Args:
            symbol: Stock symbol
            snippet_count: Number of news snippets to fetch
        
        Returns:
            Dictionary with status, sentiment data, and articles
        
        Raises:
            Exception: If error occurs during fetching/analysis
        """
        try:
            # Use the process_stock_news method which includes news from last 30 days
            articles = self.data_fetcher.process_stock_news(symbol, snippet_count)
            
            if not articles:
                return {
                    "status": "success",
                    "symbol": symbol,
                    "message": "No news articles found for the last 30 days",
                    "articles": []
                }
            
            # Calculate overall sentiment summary
            positive = sum(1 for a in articles if a['Sentiment'] == 'Positive')
            negative = sum(1 for a in articles if a['Sentiment'] == 'Negative')
            neutral = sum(1 for a in articles if a['Sentiment'] == 'Neutral')
            
            sentiment_scores = [a['SentimentScore'] for a in articles]
            avg_sentiment = sum(sentiment_scores) / len(sentiment_scores) if sentiment_scores else 0.0
            
            if avg_sentiment >= 0.05:
                overall_sentiment = "Positive"
            elif avg_sentiment <= -0.05:
                overall_sentiment = "Negative"
            else:
                overall_sentiment = "Neutral"
            
            return {
                "status": "success",
                "symbol": symbol,
                "count": len(articles),
                "summary": {
                    "positive": positive,
                    "negative": negative,
                    "neutral": neutral,
                    "total": len(articles),
                    "overall_sentiment": overall_sentiment,
                    "average_score": avg_sentiment
                },
                "articles": articles
            }
            
        except Exception as e:
            raise Exception(f"Error analyzing news sentiment: {e}")
    
    def get_sentiment_only(self, text):
        """
        Analyze sentiment for a given text.
        
        Args:
            text: Text to analyze
        
        Returns:
            Dictionary with sentiment label and score
        """
        sentiment_label, sentiment_score, clean_text = self.data_fetcher.analyze_sentiment(text)
        return {
            "sentiment": sentiment_label,
            "score": sentiment_score,
            "cleaned_text": clean_text
        }
