#!/bin/bash
# Run Streamlit Dashboard

echo "=========================================="
echo "Starting Streamlit Dashboard"
echo "=========================================="
echo "Dashboard will be available at: http://127.0.0.1:8501"
echo "Note: Make sure FastAPI is running on port 8000"
echo "=========================================="
echo ""

cd "$(dirname "$0")"

# Run streamlit
streamlit run app/streamlit_dashboard.py
