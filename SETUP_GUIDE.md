# Setup Guide

## Quick Start (5 minutes)

### 1. Install Dependencies

```bash
cd ~/Desktop/StcokPredApp
pip install -r requirements.txt
```

### 2. Run the App

**Recommended: FastAPI + Streamlit**

Open **two terminal windows**:

**Terminal 1 (API Server):**
```bash
cd ~/Desktop/StcokPredApp
./run_api_fastapi.sh
```

**Terminal 2 (Dashboard):**
```bash
cd ~/Desktop/StcokPredApp
./run_streamlit.sh
```

### 3. Access the App

- 📊 **Dashboard**: http://127.0.0.1:8501
- 🚀 **API**: http://127.0.0.1:8000
- 📖 **API Docs**: http://127.0.0.1:8000/docs

## Choosing a Backend

### FastAPI (Recommended)
- Automatic API documentation
- Type-safe with Pydantic
- Async support
- Modern features

Use: `./run_api_fastapi.sh`

### Flask (Legacy)
- 3-layer architecture
- Blueprint-based routes
- Traditional setup

Use: `python3 app/app.py`

## Running Options

### Option 1: FastAPI + Streamlit
```bash
# Terminal 1
./run_api_fastapi.sh

# Terminal 2
./run_streamlit.sh
```

### Option 2: Just FastAPI
```bash
python3 -m uvicorn app.fastapi_main:app --host 127.0.0.1 --port 8000 --reload
```

### Option 3: Just Flask
```bash
python3 app/app.py
```

## What's What

- **FastAPI** (port 8000) - REST API backend
- **Streamlit** (port 8501) - Frontend dashboard
- **Flask** (port 5000) - Legacy API option

## Folder Structure

```
app/
├── fastapi_main.py       # FastAPI app
├── streamlit_dashboard.py # Streamlit UI
├── models/               # ML models
├── services/             # Business logic
├── repositories/         # Data access
└── api/                  # Routes (Flask)
```

## Next Steps

1. **Fetch Data**: In the dashboard, enter a stock symbol and click "Fetch Data"
2. **Predict Prices**: Select a model and predict future prices
3. **Check News**: View recent news and sentiment analysis

See [README.md](README.md) for full documentation.
