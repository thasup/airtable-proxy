#!/bin/bash
set -e

if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

source venv/bin/activate
echo "Installing requirements..."
pip install -r requirements.txt

echo "Starting Airtable Proxy on http://0.0.0.0:8000"
exec uvicorn src.main:app --host 0.0.0.0 --port 8000
