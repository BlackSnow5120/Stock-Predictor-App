# Final Structure - 2026-02-09

## Reorganization Summary

All app-related files are now in the `app/` folder. Main directory contains only:
- Run scripts (`*.sh`)
- Documentation (`*.md`)
- Dependencies (`requirements.txt`)
- Data and model folders

## What's in `app/` Folder

### Application Files
- `__init__.py` - Package init
- `config.py` - Configuration settings
- `app.py` - Flask app factory (legacy, 3-layer architecture)
- `fastapi_main.py` - FastAPI application (recommended)
- `streamlit_dashboard.py` - Streamlit frontend

### Subdirectories
- `api/` - Flask routes and request schemas
- `models/` - ML models (LSTM, Chronos, Chronos-T5)
- `services/` - Business logic layer
- `repositories/` - Data access layer (Yahoo Finance)
- `utils/` - Helper functions and technical indicators

## Files Moved to `old_backup/`

These were duplicate/legacy files that are now in `old_backup/` for reference:

### Old Main Directory Files
- `app.py` - Old Flask app (same as app_simple.py)
- `app_simple.py` - Simple Flask API using main directory modules
- `dashboard.py` - Old Streamlit dashboard
- `dashboard_simple.py` - Streamlit dashboard for app_simple.py
- `data_fetcher.py` - Latest version (now in `app/repositories/`)
- `models.py` - Latest version (now in `app/models/` and `app/models/` implementation)
- `utils.py` - Latest version (now in `app/utils/`)
- `run_api.py` - Old run script
- `run_dashboard.py` - Old run script
- `run.py` - Old run script
- `test_3_layer.py` - Test file
- `test_app.py` - Test file
- `test_setup.py` - Test file

### Old Reference Files (from app/)
- `models_reference.py` - Reference copy
- `data_fetcher_reference.py` - Reference copy
- `utils_reference.py` - Reference copy

## Files Removed

### Duplicate Documentation
- `BUILD_SUMMARY.md` - Merged into main README
- `QUICK_START.md` - Replaced by simplified SETUP_GUIDE
- `README_3_LAYER.md` - Merged into main README
- `README_FASTAPI.md` - Merged into main README

### Duplicate Requirements
- `requirements_fastapi.txt` - Merged into main requirements.txt
- `requirements_light.txt` - No longer needed

## What's Now in Main Directory

### Scripts
- `run_api_fastapi.sh` - Start FastAPI server
- `run_streamlit.sh` - Start Streamlit dashboard

### Documentation
- `README.md` - Complete documentation
- `SETUP_GUIDE.md` - Quick start guide

### Configuration
- `requirements.txt` - All dependencies

### Folders
- `app/` - Application package
- `models/` - Saved model files
- `data/` - Data files
- `old_backup/` - Legacy files (for reference)

## How to Run

### FastAPI + Streamlit (Recommended)
```bash
# Terminal 1
./run_api_fastapi.sh

# Terminal 2
./run_streamlit.sh
```

### Flask (Legacy)
```bash
python3 app/app.py
```

## Benefits of New Structure

1. **Clean Separation**: All app code is in `app/`
2. **No Duplicates**: Removed redundant files
3. **Easy to Navigate**: Clear folder structure
4. **Two Backend Options**: FastAPI (modern) or Flask (legacy work)
5. **Better Documentation**: Consolidated READMEs
