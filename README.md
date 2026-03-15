# Stock Prediction App

A stock price prediction application with machine learning models (LSTM, Chronos, Chronos-T5), news sentiment analysis, and an interactive dashboard.

## Features

- **Multiple ML Models**: LSTM (local training), Chronos, Chronos-T5 (pre-trained from HuggingFace)
- **Interactive Dashboard**: Streamlit-based UI with candlestick charts
- **FastAPI Backend**: Modern async API with automatic OpenAPI documentation
- **News Sentiment**: VADER-based sentiment analysis with 30-day news window
- **Technical Indicators**: RSI, MACD, Moving Averages built-in

## ScreenShots
<img width="1916" height="882" alt="Screenshot 2026-03-15 182131" src="https://github.com/user-attachments/assets/ef1faae1-36f6-42fa-972f-39ea8232db31" />
<img width="1908" height="839" alt="Screenshot 2026-03-15 182208" src="https://github.com/user-attachments/assets/7db3517a-3785-4e81-b7e1-fb916d96126f" />
<img width="816" height="856" alt="Screenshot 2026-03-15 193643" src="https://github.com/user-attachments/assets/ff414a31-3078-4f17-9616-b2da679d7871" />
<img width="1508" height="849" alt="Screenshot 2026-03-15 193707" src="https://github.com/user-attachments/assets/b245ace4-8a3c-4dc1-993b-8f0c379a26b7" />

## Quick Start

### Installation

```bash
cd ~/Desktop/StcokPredApp
pip install -r requirements.txt
```

### Running the App

**Option 1: FastAPI + Streamlit (Recommended)**

Terminal 1 (API):
```bash
./run_api_fastapi.sh
```

Terminal 2 (Dashboard):
```bash
./run_streamlit.sh
```

**Option 2: Flask Legacy (3-layer architecture)**

```bash
cd /home/bhuvain/Desktop/StcokPredApp
python3 app/app.py
```

## Access Points

| Service | URL |
|---------|-----|
| Streamlit Dashboard | http://127.0.0.1:8501 |
| FastAPI | http://127.0.0.1:8000 |
| API Docs (Swagger) | http://127.0.0.1:8000/docs |
| API Docs (ReDoc) | http://127.0.0.1:8000/redoc |
| Flask (legacy) | http://127.0.0.1:5000 |

## Project Structure

```
StcokPredApp/
├── app/                          # Application package
│   ├── __init__.py
│   ├── config.py                 # Configuration
│   ├── app.py                    # Flask app factory (legacy)
│   ├── fastapi_main.py           # FastAPI application
│   ├── streamlit_dashboard.py    # Streamlit frontend
│   ├── api/                      # API routes (Flask)
│   │   ├── endpoints.py
│   │   └── schemas.py
│   ├── models/                   # ML Models
│   │   ├── base_model.py
│   │   ├── lstm_model.py
│   │   └── huggingface_model.py
│   ├── services/                 # Business Logic
│   │   ├── model_service.py
│   │   ├── stock_service.py
│   │   └── news_service.py
│   ├── repositories/             # Data Access
│   │   ├── data_fetcher.py       # Yahoo Finance API
│   │   └── storage.py
│   └── utils/                    # Helpers
│       ├── helpers.py
│       └── technical_indicators.py
├── models/                       # Saved model files
├── data/                         # Data files
├── old_backup/                   # Legacy files (removed from main dir)
├── run_api_fastapi.sh            # Start FastAPI script
├── run_streamlit.sh              # Start Streamlit script
├── requirements.txt              # All dependencies
└── SETUP_GUIDE.md                # Detailed setup guide
```

## Available Models

| Model | Training | Description |
|-------|----------|-------------|
| `lstm` | Required | Bidirectional LSTM with attention |
| `chronos2` | Pre-trained | HuggingFace Chronos model |
| `chronos-bolt` | Pre-trained | Amazon Chronos-T5 model |

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | API information |
| GET | `/models` | List available models |
| POST | `/train` | Train a model |
| POST | `/predict` | Make predictions |
| POST | `/sentiment` | Get news sentiment |
| GET | `/metrics` | Get model metrics |
| POST | `/data` | Fetch historical data |
| GET | `/health` | Health check |

## Using the Dashboard

### Stock Data Tab
1. Enter stock symbol (e.g., AAPL)
2. Select date range
3. Click "Fetch Data"
4. View candlestick chart and data table

### Predictions Tab
1. Select model type
2. Set prediction days (1-30)
3. Click "Train Model" (for LSTM only)
4. Click "Predict Prices"
5. View predictions table and chart

### News & Sentiment Tab
1. Select number of articles (1-20)
2. Click "Fetch News"
3. View sentiment summary and articles
4. Articles from last 30 days

## API Usage Examples

### Fetch Historical Data
```bash
curl -X POST "http://127.0.0.1:8000/data" \
  -H "Content-Type: application/json" \
  -d '{"symbol":"AAPL","range":"1y","interval":"1d"}'
```

### Train Model
```bash
curl -X POST "http://127.0.0.1:8000/train" \
  -H "Content-Type: application/json" \
  -d '{"symbol":"AAPL","model_type":"lstm","epochs":50,"batch_size":32}'
```

### Predict Prices
```bash
curl -X POST "http://127.0.0.1:8000/predict" \
  -H "Content-Type: application/json" \
  -d '{"symbol":"AAPL","model_type":"lstm","days":7}'
```

### Get News Sentiment
```bash
curl -X POST "http://127.0.0.1:8000/sentiment" \
  -H "Content-Type: application/json" \
  -d '{"symbol":"AAPL","snippet_count":10}'
```

## Dependencies

- **FastAPI**: Modern async web framework
- **Streamlit**: Dashboard frontend
- **TensorFlow**: Deep learning (LSTM)
- **Transformers**: HuggingFace models (Chronos, Chronos-T5)
- **Pandas/NumPy**: Data processing
- **NLTK**: Sentiment analysis

## Notes

- The Streamlit dashboard connects to the FastAPI backend on `http://127.0.0.1:8000`
- Make sure FastAPI is running before starting the Streamlit dashboard
- All models work with both FastAPI and Flask backends
- For Chronos/Chronos-T5, models are downloaded automatically on first use

## Troubleshooting

### FastAPI not starting
```bash
pip install uvicorn[standard]
```

### Streamlit not starting
```bash
pip install streamlit plotly
```

### TensorFlow errors
```bash
pip install tensorflow[and-cuda]
```

### HuggingFace model errors
```bash
pip install transformers torch
```
