#!/bin/bash
# Run FastAPI server

echo "=========================================="
echo "Starting FastAPI Server"
echo "=========================================="
echo "API will be available at: http://127.0.0.1:8000"
echo "Interactive docs: http://127.0.0.1:8000/docs"
echo "ReDoc docs: http://127.0.0.1:8000/redoc"
echo "=========================================="
echo ""

cd "$(dirname "$0")"

# Run FastAPI
python3 -m uvicorn app.fastapi_main:app --host 127.0.0.1 --port 8000 --reload
