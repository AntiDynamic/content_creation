@echo off
title YouTube Channel Analyzer - Quick Start
color 0A

echo.
echo  ╔═══════════════════════════════════════════════════════════╗
echo  ║                                                           ║
echo  ║        YouTube Channel Analyzer - Quick Start            ║
echo  ║                                                           ║
echo  ╚═══════════════════════════════════════════════════════════╝
echo.
echo  Powered by: Google Gemini AI + YouTube Data API v3
echo.
echo ────────────────────────────────────────────────────────────
echo.

REM Check virtual environment
if not exist "%~dp0..\venv\Scripts\python.exe" (
    echo [ERROR] Virtual environment not found!
    echo.
    echo Please run setup first:
    echo   scripts\setup.ps1
    echo.
    pause
    exit /b 1
)

REM Check .env file in backend
cd /d "%~dp0\..\backend"
if not exist ".env" (
    echo [WARNING] .env file not found!
    echo.
    echo Creating .env from template...
    copy .env.example .env > nul
    echo [SUCCESS] .env file created.
    echo.
    echo [ACTION REQUIRED] Please edit backend\.env and add your API keys:
    echo  - YOUTUBE_API_KEY
    echo  - GEMINI_API_KEY
    echo.
    echo Opening .env file for editing...
    timeout /t 2 /nobreak > nul
    notepad .env
    echo.
    echo After saving your API keys, press any key to continue...
    pause > nul
)

echo [INFO] Checking dependencies...
echo.

REM Start backend
echo [STEP 1/3] Starting Backend API Server...
cd /d "%~dp0\..\backend"
start "YouTube Backend API" /MIN "%~dp0\..\venv\Scripts\uvicorn.exe" main:app --host 0.0.0.0 --port 8000 --reload

echo [SUCCESS] Backend starting on http://localhost:8000
timeout /t 3 /nobreak > nul

REM Start frontend
echo.
echo [STEP 2/3] Starting Frontend Server...
cd /d "%~dp0\..\frontend"
start "YouTube Frontend UI" /MIN "%~dp0\..\venv\Scripts\python.exe" -m http.server 3001

echo [SUCCESS] Frontend starting on http://localhost:3001
timeout /t 2 /nobreak > nul

REM Open browser
echo.
echo [STEP 3/3] Opening application in browser...
timeout /t 2 /nobreak > nul
start http://localhost:3001

echo.
echo ════════════════════════════════════════════════════════════
echo.
echo  🚀 Application is now running!
echo.
echo  📱 Frontend:     http://localhost:3001
echo  ⚙️  Backend API:  http://localhost:8000
echo  📚 API Docs:     http://localhost:8000/v1/docs
echo.
echo ════════════════════════════════════════════════════════════
echo.
echo  The backend and frontend are running in minimized windows.
echo  To stop the servers, close those windows or press Ctrl+C.
echo.
echo  Press any key to exit this window (servers will keep running)...
pause > nul

