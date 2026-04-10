"""
FastAPI Application - Stock Prediction API with Streamlit support.
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from typing import Optional, List
import sys
import os

# Add parent directory to path so 'app' package can be resolved
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

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


# Mount static files correctly
static_dir = os.path.join(os.path.dirname(__file__), 'static')
os.makedirs(static_dir, exist_ok=True)
app.mount("/static", StaticFiles(directory=static_dir), name="static")

@app.get("/", tags=["Dashboard"])
def serve_dashboard():
    """Serve the real-time stock dashboard."""
    index_path = os.path.join(static_dir, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"message": "Static frontend not built yet. Create app/static/index.html."}

@app.get("/api/info", tags=["System"])
def api_info():
    """API information and available endpoints."""
    return {
        "name": "Stock Prediction Dashboard API",
        "version": "2.0.0",
        "description": "FastAPI for stock price prediction with unified dashboard",
        "architecture": "3-Layer (API → Services → Repositories)",
        "endpoints": {
            "GET /": "Dashboard Web UI",
            "GET /api/info": "API information",
            "GET /models": "List available models",
            "POST /train": "Train a model",
            "POST /predict": "Make predictions",
            "POST /sentiment": "Get news sentiment",
            "GET /metrics": "Get model metrics",
            "POST /data": "Fetch historical stock data",
            "GET /health": "Health check",
            "GET /docs": "Interactive API documentation"
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


@app.get("/api/market/trending", tags=["Market Data"])
def get_trending_stocks():
    """Fetch Day Gainers from Yahoo Finance screener."""
    import requests
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    url = "https://query1.finance.yahoo.com/v1/finance/screener/predefined/saved?formatted=true&scrIds=day_gainers&count=6"
    try:
        r = requests.get(url, headers=headers, timeout=5)
        if r.ok:
            data = r.json()
            quotes = data.get("finance", {}).get("result", [])[0].get("quotes", [])
            movers = []
            for q in quotes:
                movers.append({
                    "symbol": q.get("symbol"),
                    "name": q.get("shortName", q.get("symbol")),
                    "change": q.get("regularMarketChangePercent", {}).get("fmt", "0.00%"),
                    "price": q.get("regularMarketPrice", {}).get("fmt", "0.00")
                })
            return {"status": "success", "movers": movers}
    except Exception as e:
        print(f"Error fetching trending stocks: {e}")
    return {"status": "error", "movers": []}

@app.get("/api/social/reddit", tags=["Market Data"])
def get_reddit_sentiment(ticker: str = Query(..., description="Stock symbol")):
    """Fetch recent social sentiment from Reddit r/stocks and r/wallstreetbets."""
    import requests
    headers = {'User-Agent': 'Windows:StockPredictorApp:v1.0 (by /u/Developer)'}
    subreddits = ["wallstreetbets", "stocks", "investing"]
    posts = []
    
    for sub in subreddits:
        url = f"https://www.reddit.com/r/{sub}/search.json?q={ticker}&restrict_sr=1&sort=new&limit=2"
        try:
            r = requests.get(url, headers=headers, timeout=5)
            if r.ok:
                data = r.json().get("data", {}).get("children", [])
                for item in data:
                    post = item["data"]
                    posts.append({
                        "id": post.get("id"),
                        "title": post.get("title"),
                        "subreddit": post.get("subreddit_name_prefixed"),
                        "score": post.get("score", 0),
                        "url": f"https://www.reddit.com{post.get('permalink')}"
                    })
        except Exception as e:
            print(f"Reddit error for {sub}: {e}")
            
    # Deduplicate and sort by most upvotes
    unique_posts = {p['id']: p for p in posts}.values()
    sorted_posts = sorted(unique_posts, key=lambda x: x['score'], reverse=True)
    return {"status": "success", "reddit": sorted_posts[:5]}

@app.get("/api/proxy/article", tags=["Intel"])
def process_article(url: str):
    """Fetches pure text and images from a news URL using NLP, bypassing strict iframing blocks."""
    from feedparser import util
    try:
        import newspaper
        article = newspaper.Article(url)
        article.download()
        article.parse()
        
        # Format text to have HTML paragraphs
        formatted_text = ""
        if article.text:
            formatted_text = "".join([f"<p style='margin-bottom:16px; line-height:1.6;'>{p}</p>" for p in article.text.split('\n\n') if p.strip()])
            
        return {
            "status": "success",
            "title": article.title,
            "text": formatted_text,
            "top_image": article.top_image,
            "authors": article.authors
        }
    except Exception as e:
        print(f"Extraction failed for {url}: {e}")
        return {"status": "error", "message": str(e)}

@app.get("/api/youtube/channels", tags=["Media"])
def get_youtube_channels():
    """Fetch latest video thumbnails from multiple geopolitical news channels."""
    import requests, re
    from concurrent.futures import ThreadPoolExecutor, as_completed

    CHANNELS = [
        {"name": "Firstpost",      "handle": "Firstpost"},
        {"name": "WION",           "handle": "WION"},
        {"name": "Al Jazeera",     "handle": "AlJazeeraEnglish"},
        {"name": "DW News",        "handle": "dwnews"},
        {"name": "France 24",      "handle": "France24English"},
        {"name": "Times Now",      "handle": "TimesNow"},
    ]

    def fetch_channel(ch):
        scraped_videos = []
        try:
            handle = f"@{ch['handle']}"
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

            # Fetch live 
            r_live = requests.get(f"https://www.youtube.com/{handle}/live", headers=headers, timeout=8)
            if r_live.ok:
                html = r_live.text
                vid_match = re.search(r'"videoId":"([a-zA-Z0-9_-]{11})"', html)
                live_match = bool(re.search(r'"isLive"\s*:\s*true', html))
                if vid_match and live_match:
                    video_id = vid_match.group(1)
                    title_match = re.search(r'"title"\s*:\s*\{"runs"\s*:\s*\[\{"text"\s*:\s*"([^"]+)"', html)
                    scraped_videos.append({
                        "name": ch["name"],
                        "videoId": video_id,
                        "isLive": True,
                        "title": title_match.group(1) if title_match else ch["name"] + " Live",
                        "url": f"https://www.youtube.com/watch?v={video_id}",
                        "thumbnail": f"https://img.youtube.com/vi/{video_id}/maxresdefault.jpg"
                    })

            # Fetch recent videos
            r_vids = requests.get(f"https://www.youtube.com/{handle}/videos", headers=headers, timeout=8)
            if r_vids.ok:
                html = r_vids.text
                # Find all video IDs
                matches = re.finditer(r'"videoId":"([a-zA-Z0-9_-]{11})"', html)
                seen = {v['videoId'] for v in scraped_videos}
                added = 0
                for match in matches:
                    vid = match.group(1)
                    if vid not in seen:
                        seen.add(vid)
                        scraped_videos.append({
                            "name": ch["name"],
                            "videoId": vid,
                            "isLive": False,
                            "title": ch["name"] + " Latest News", # Simplified title extraction for speed
                            "url": f"https://www.youtube.com/watch?v={vid}",
                            "thumbnail": f"https://img.youtube.com/vi/{vid}/hqdefault.jpg"
                        })
                        added += 1
                        if added >= 2: # Keep max 2 non-live videos per channel
                            break

        except Exception as e:
            print(f"Channel fetch error {ch['name']}: {e}")
        return scraped_videos

    results = []
    with ThreadPoolExecutor(max_workers=6) as ex:
        futures = {ex.submit(fetch_channel, ch): ch for ch in CHANNELS}
        for future in as_completed(futures):
            res_list = future.result()
            if res_list:
                results.extend(res_list)

    # Sort: live channels first
    results.sort(key=lambda x: (0 if x["isLive"] else 1))
    return {"status": "success", "channels": results}

@app.get("/api/youtube/live", tags=["Media"])
def get_youtube_live(channel: str = Query(..., description="YouTube channel handle without @, e.g., 'Firstpost'")):
    """Scrape YouTube to find the current live or latest video for a channel without requiring an API key."""
    import requests
    import re
    try:
        channel_handle = channel if channel.startswith('@') else f"@{channel}"
        url = f"https://www.youtube.com/{channel_handle}/live"
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        
        response = requests.get(url, headers=headers, timeout=10)
        
        if not response.ok:
            return {"videoId": None, "isLive": False, "error": "Channel fetch failed"}
            
        html = response.text
        
        # Regex to find videoId
        video_id = None
        is_live = False
        
        details_idx = html.find('"videoDetails"')
        if details_idx != -1:
            block = html[details_idx:details_idx + 5000]
            vid_match = re.search(r'"videoId":"([a-zA-Z0-9_-]{11})"', block)
            live_match = re.search(r'"isLive"\s*:\s*true', block)
            
            if vid_match:
                video_id = vid_match.group(1)
            if live_match:
                is_live = True
                
        # If no live video is found, fallback to their latest videos route
        if not video_id:
            url_latest = f"https://www.youtube.com/{channel_handle}/videos"
            response_latest = requests.get(url_latest, headers=headers, timeout=10)
            if response_latest.ok:
                html_latest = response_latest.text
                vid_match = re.search(r'"videoId":"([a-zA-Z0-9_-]{11})"', html_latest)
                if vid_match:
                    video_id = vid_match.group(1)
                    
        return {"videoId": video_id, "isLive": is_live, "channel": channel_handle}
    except Exception as e:
        return {"videoId": None, "isLive": False, "error": str(e)}

@app.get("/api/news/global", tags=["Media"])
def get_global_news():
    """Scrape Bing News for Geopolitics via Playwright."""
    try:
        from app.repositories.browser_scraper import BrowserScraper
        scraper = BrowserScraper()
        news = scraper.scrape_global_news()
        return {"status": "success", "news": news}
    except Exception as e:
        return {"status": "error", "message": str(e)}

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
