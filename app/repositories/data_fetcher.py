"""
Data Fetcher Repository - Access Yahoo Finance API for stock data and news.
"""

import requests
import pandas as pd
import urllib.parse
from datetime import datetime, timedelta

try:
    import yfinance as yf
    HAS_YFINANCE = True
except ImportError:
    HAS_YFINANCE = False


class DataFetcher:
    """Repository for fetching stock data from Yahoo Finance."""
    
    def __init__(self, user_agent=None, referer=None):
        """
        Initialize DataFetcher.
        
        Args:
            user_agent: User-Agent header for requests
            referer: Referer header for requests
        """
        self.user_agent = user_agent or "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
        self.referer = referer or "https://finance.yahoo.com/"
        self.headers = {
            "User-Agent": self.user_agent,
            "Referer": self.referer,
        }
    
    def fetch_historical_data(self, symbol, range_str='max', interval_str='1d'):
        """
        Fetch historical OHLCV data from Yahoo Finance.
        
        Args:
            symbol: Stock symbol (e.g., 'AAPL')
            range_str: Time range ('1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', 'max')
            interval_str: Data interval ('1m', '2m', '5m', '15m', '60m', '90m', '1h', '1d', '5d', '1wk', '1mo', '3mo')
        
        Returns:
            pandas DataFrame with columns: Timestamp (index), Open, High, Low, Close, Volume
        """
        try:
            encoded_symbol = urllib.parse.quote(symbol, safe="")
            url = (
                f"https://query1.finance.yahoo.com/v8/finance/chart/{encoded_symbol}?"
                f"range={range_str}&interval={interval_str}&"
                "includePrePost=true&events=div%7Csplit%7Cearn&lang=en-US&region=US&source=cosaic"
            )
            
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if not data.get('chart', {}).get('result'):
                return pd.DataFrame()
            
            chart_data = data['chart']['result'][0]
            timestamps = chart_data['timestamp']
            prices = chart_data['indicators']['quote'][0]
            
            df = pd.DataFrame({
                'Timestamp': pd.to_datetime(timestamps, unit='s'),
                'Open': prices['open'],
                'High': prices['high'],
                'Low': prices['low'],
                'Close': prices['close'],
                'Volume': prices['volume']
            }).set_index('Timestamp')
            
            df.dropna(subset=['Open', 'High', 'Low', 'Close', 'Volume'], inplace=True)
            return df
            
        except Exception as e:
            raise Exception(f"Error fetching historical data for {symbol}: {e}")
    
    def fetch_news(self, symbol, snippet_count=10):
        """
        Fetch news data from Yahoo Finance.
        
        Args:
            symbol: Stock symbol
            snippet_count: Number of news snippets to fetch
        
        Returns:
            JSON response with news data
        """
        try:
            encoded_symbol = urllib.parse.quote(symbol, safe="")
            url = (
                f"https://finance.yahoo.com/xhr/ncp?location=US&queryRef=qsp&serviceKey=ncp_fin"
                f"&symbols={encoded_symbol}&lang=en-US&region=US"
            )
            
            headers = self.headers.copy()
            headers["Content-Type"] = "application/json"
            headers["Origin"] = "https://finance.yahoo.com"
            
            response = requests.post(
                url, 
                headers=headers, 
                json={"serviceConfig": {"count": 40, "snippetCount": snippet_count}}, 
                timeout=10
            )
            response.raise_for_status()
            return response.json()
            
        except Exception as e:
            raise Exception(f"Error fetching news for {symbol}: {e}")
    
    def analyze_sentiment(self, text):
        """
        Analyze sentiment using VADER.
        
        Args:
            text: Text to analyze
        
        Returns:
            Tuple of (sentiment_label, compound_score, clean_text)
        """
        try:
            from nltk.sentiment.vader import SentimentIntensityAnalyzer
            import nltk
            
            # Download VADER lexicon if needed
            try:
                nltk.data.find('sentiment/vader_lexicon.zip')
            except LookupError:
                nltk.download('vader_lexicon', quiet=True)
            
            analyzer = SentimentIntensityAnalyzer()
            clean_text = text.replace('&nbsp;', ' ').strip()
            sentiment_scores = analyzer.polarity_scores(clean_text)
            compound_score = sentiment_scores['compound']
            
            if compound_score >= 0.05:
                sentiment_label = "Positive"
            elif compound_score <= -0.05:
                sentiment_label = "Negative"
            else:
                sentiment_label = "Neutral"
            
            return sentiment_label, compound_score, clean_text
            
        except Exception as e:
            print(f"Error analyzing sentiment: {e}")
            return "Neutral", 0.0, text
    
    def process_stock_news(self, symbol, snippet_count=10):
        """
        Process stock news and return structured data with sentiment.
        
        Args:
            symbol: Stock symbol
            snippet_count: Number of news snippets to fetch
        
        Returns:
            List of dictionaries containing news data with sentiment
        """
        # Fetch historical data for price context
        df_hist = self.fetch_historical_data(symbol, range_str='1d', interval_str='1d')
        if df_hist.empty:
            return []

        today_data = df_hist.iloc[-1]
        open_price = today_data["Open"]
        close_price = today_data["Close"]
        movement_ratio = (close_price - open_price) / open_price if open_price > 0 else 0

        # Fetch news
        news_json = self.fetch_news(symbol, snippet_count=snippet_count)
        if not news_json:
            return []
        
        stream_items = (
            news_json.get("data", {})
                 .get("tickerStream", {})
                 .get("stream", [])
        )

        # Get date from 30 days ago to include recent news
        thirty_days_ago = (datetime.now() - timedelta(days=30)).date().isoformat()

        articles = []

        for item in stream_items:
            content = item.get("content", {})
            headline = content.get("title", "").strip()
            summary = content.get("summary", "").strip()
            pub_date = content.get("pubDate", datetime.now().isoformat())

            # Only keep articles from last 30 days
            article_date = pub_date.split("T")[0]
            if article_date < thirty_days_ago:
                continue

            if not headline:
                continue

            sentiment_label, sentiment_score, clean_text = self.analyze_sentiment(headline)

            articles.append({
                "Date": pub_date.split("T")[0],
                "Symbol": symbol,
                "Headline": clean_text,
                "Summary": summary if summary else "",  # Ensure Summary exists even if empty
                "Sentiment": sentiment_label,
                "SentimentScore": float(sentiment_score),
                "Open": float(open_price),
                "Close": float(close_price),
                "MovementRatio": float(movement_ratio)
            })

        return articles
    
    def fetch_stock_with_price_context(self, symbol):
        """
        Fetch stock data with current price context.
        
        Args:
            symbol: Stock symbol
        
        Returns:
            Dictionary with current price data
        """
        df = self.fetch_historical_data(symbol, range_str='1d', interval_str='1d')
        if df.empty:
            return None
        
        today_data = df.iloc[-1]
        return {
            "Open": float(today_data["Open"]),
            "Close": float(today_data["Close"]),
            "High": float(today_data["High"]),
            "Low": float(today_data["Low"]),
            "Volume": int(today_data["Volume"])
        }
