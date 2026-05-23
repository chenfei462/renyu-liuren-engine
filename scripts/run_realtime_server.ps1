$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
$env:PYTHONPATH = Join-Path $Root "src"
python -m uvicorn liuren_engine.webapp:app --host 127.0.0.1 --port 8000
