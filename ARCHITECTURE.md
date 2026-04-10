# Stock Predictor Dashboard Architecture

This document provides a comprehensive map of the project structure. It is designed to help AI assistants immediately understand the system architecture, component responsibilities, and routing logic to make future modifications seamless.

## High-Level Architecture
The project heavily follows an **API-First, 3-Layer System**:
1. **Frontend (Client-Side)**: Static HTML/CSS/JS driving a highly dynamic, Single Page Application (SPA).
2. **Backend (FastAPI)**: Serves the static files, handles complex API requests, and brokers data between external systems and the client.
3. **Services/Repositories**: Encapsulated Python logic handling ML models, financial data extraction, and web scraping.

---

## Directory Structure & File Responsibilities

### 1. Frontend: The Static Layer (`app/static/`)
This is where the entire UI is constructed. There is no server-side rendering (e.g. Jinja2 templates) — the frontend actively fetches JSON from the FastAPI backend.

- `index.html`: The core dashboard layout. 
    - **Responsibilities**: Defines the Skeleton Loading Screen, Stock Radar Tab, Analytics Grid, and the Geopolitics Media Grid.
- `css/style.css`: The "World Monitor" inspired design system.
    - **Responsibilities**: Dark theme CSS variables, glassmorphism UI elements, glowing accents, pulsing LIVE badges, grid system parameters.
- `js/dashboard.js`: The central nervous system of the client app.
    - **Responsibilities**: 
        - Orchestrates API calls to `/data`, `/sentiment`, `/api/youtube/channels`, `/api/market/trending`, etc.
        - Mounts the dynamic embedded `YT.Player` instances for YouTube streams.
        - Auto-wires the "Top Movers 🔥" cards to trigger the `Chronos-T5` prediction model passively.

### 2. Backend: The Server Engine (`app/fastapi_main.py`)
This script boots Uvicorn and manages all traffic routing.
- **Responsibilities**:
    - Mounts the `app/static` directory to `/` to serve the web UI.
    - Exposes strict endpoints like `@app.post("/data")` and `@app.post("/sentiment")`.
    - Handles dynamic API proxies combining external resources cleanly into JSON payloads:
        - `/api/youtube/channels`: Scrapes 6 major geopolitical YouTube channels concurrently for latest/live videos.
        - `/api/market/trending`: Scrapes Yahoo Finance's `day_gainers` screener.
        - `/api/news/global`: Aggregates the latest RSS intel feeds for breaking news.
        - `/api/social/reddit`: Directly maps to Reddit's `.json` frontend endpoints avoiding hard rate-limits by using custom `User-Agent` headers.

### 3. Services: The Business Logic (`app/services/`)
- `stock_service.py`: 
    - Handles the mathematical abstraction of downloading historical market prices using `yfinance`.
    - Preps the dataset matrices. Handles JSON un-serializability (converting `NaN` to `None`).
- `model_service.py`:
    - Handles calling and predicting using ML models like `LSTM`, `Chronos`, and `Chronos-T5`.
- `news_service.py`:
    - Basic financial news fetchers connected to Yahoo Finance feeds.

### 4. Repositories: External Scraping (`app/repositories/`)
- `browser_scraper.py`:
    - Originally built for Playwright, currently rebuilt safely to ingest RSS logic from global networks (BBC, Al Jazeera, Reuters). 

### 5. Config
- `requirements.txt`: 
    - Strict Python dependency tracking. Managed natively via `uv pip install -r requirements.txt`.

---

## Modifying the App: AI Guidelines

**When adding new APIs or external Data Sources:**
1. Create a route in `fastapi_main.py` explicitly wrapped safely in `try/except` returning JSON (`{"status": "success", "data": ...}`).
2. In `dashboard.js`, build an `async function loadNewFeature()` that hits the route.
3. Never mutate global state synchronously. Update UI elements (`document.getElementById().innerHTML = ...`) once the promise resolves.

**When editing CSS or the Grid Layout:**
- Check `.geopolitics-layout` or `.analytics-grid`. The app heavily relies on Flex/CSS Grid. If you expand a section, make sure `overflow-y` behaviors are respected on parent elements so the SPA "App" feel isn't broken.

**When handling YouTube logic:**
- We strictly rely on the standard `window.YT.Player` script injection protocol. Due to copyright protections by mass media (e.g. Firstpost), the embedding script always checks for `onError(150)` and falls back to a physical image banner linking directly to YouTube. Maintain this fallback logic in `dashboard.js`.
