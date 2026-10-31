# Starts the ORBIT backend (port 8000) and frontend (port 5500) locally.
# Usage:  powershell -ExecutionPolicy Bypass -File run_demo.ps1 [-Mock]
#   -Mock  serves backend/demo_outputs instead of calling Gemini (no API key needed).
param([switch]$Mock)

$root = $PSScriptRoot
if ($Mock) { $env:LLM_MODE = "mock" }

Start-Process powershell -WorkingDirectory "$root\backend" -ArgumentList "-NoExit", "-Command", "python -m uvicorn main:app --port 8000"
Start-Process powershell -WorkingDirectory "$root\frontend" -ArgumentList "-NoExit", "-Command", "python -m http.server 5500"

Start-Sleep -Seconds 3
Start-Process "http://localhost:5500/index.html"
Write-Host "Backend: http://localhost:8000/docs   Frontend: http://localhost:5500/index.html"
