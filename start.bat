@echo off
title BuyWise AI - Shopping Intelligence Platform
color 0A
echo =====================================================================
echo                BUYWISE AI - 1-CLICK LAUNCHER
echo   Evidence-Grounded Shopping Intelligence System for Amazon
echo =====================================================================
echo.

:: Check for virtual environment
if not exist ".\.venv\Scripts\uvicorn.exe" (
    echo [ERROR] Python virtual environment not found in .\.venv!
    echo Please run:
    echo   py -3.12 -m venv .venv
    echo   .\.venv\Scripts\pip.exe install -e .
    echo   .\.venv\Scripts\pip.exe install -r requirements.txt
    pause
    exit /b 1
)

:: Check for frontend node_modules
if not exist ".\frontend\node_modules" (
    echo [NOTICE] Frontend node_modules not found. Installing dependencies...
    cd frontend && call npm install && cd ..
)

echo [1/3] Launching FastAPI Backend Server on http://localhost:8000 ...
start "BuyWise Backend API" cmd /k "title BuyWise Backend (Port 8000) && .\.venv\Scripts\uvicorn.exe buywise.api.app:app --reload --port 8000"

echo [2/3] Waiting for Backend to initialize...
timeout /t 3 /nobreak >nul

echo [3/3] Launching React+Vite Frontend on http://localhost:5173 ...
start "BuyWise Frontend" cmd /k "title BuyWise Frontend (Port 5173) && cd frontend && npm run dev"

timeout /t 2 /nobreak >nul

echo.
echo =====================================================================
echo  BuyWise AI is now running live!
echo  - Frontend Dashboard: http://localhost:5173
echo  - Interactive Swagger Docs: http://localhost:8000/docs
echo =====================================================================
echo.
echo Launching your browser now...
start http://localhost:5173

pause
