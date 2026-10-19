# BuyWise AI - PowerShell 1-Click System Launcher
Write-Host "=====================================================================" -ForegroundColor Cyan
Write-Host "             BUYWISE AI - 1-CLICK SYSTEM LAUNCHER                   " -ForegroundColor Yellow
Write-Host "    Evidence-Grounded Shopping Intelligence System for Amazon        " -ForegroundColor Green
Write-Host "=====================================================================" -ForegroundColor Cyan
Write-Host ""

$VenvPython = ".\.venv\Scripts\python.exe"
$VenvUvicorn = ".\.venv\Scripts\uvicorn.exe"

if (-not (Test-Path $VenvUvicorn)) {
    Write-Host "[!] Virtual environment not detected at .\.venv." -ForegroundColor Red
    Write-Host "Setting up Python virtual environment..." -ForegroundColor Yellow
    py -3.12 -m venv .venv
    .\.venv\Scripts\pip.exe install -e .
    .\.venv\Scripts\pip.exe install -r requirements.txt
}

if (-not (Test-Path ".\frontend\node_modules")) {
    Write-Host "[!] Node modules not found. Installing frontend dependencies..." -ForegroundColor Yellow
    Push-Location frontend
    npm install
    Pop-Location
}

Write-Host "[1/3] Starting FastAPI Backend on http://localhost:8000..." -ForegroundColor Cyan
$BackendJob = Start-Process -FilePath "powershell.exe" -ArgumentList "-NoExit", "-Command", "cd '$PWD'; .\.venv\Scripts\uvicorn.exe buywise.api.app:app --reload --port 8000" -PassThru

Start-Sleep -Seconds 3

Write-Host "[2/3] Starting Vite Frontend on http://localhost:5173..." -ForegroundColor Cyan
$FrontendJob = Start-Process -FilePath "powershell.exe" -ArgumentList "-NoExit", "-Command", "cd '$PWD\frontend'; npm run dev" -PassThru

Start-Sleep -Seconds 2

Write-Host "[3/3] Opening Browser..." -ForegroundColor Green
Start-Process "http://localhost:5173"

Write-Host ""
Write-Host "=====================================================================" -ForegroundColor Green
Write-Host " BUYWISE AI IS LIVE!" -ForegroundColor Yellow
Write-Host " - Frontend UI:        http://localhost:5173" -ForegroundColor White
Write-Host " - Backend API Docs:   http://localhost:8000/docs" -ForegroundColor White
Write-Host " - Health Probe:       http://localhost:8000/health" -ForegroundColor White
Write-Host "=====================================================================" -ForegroundColor Green
