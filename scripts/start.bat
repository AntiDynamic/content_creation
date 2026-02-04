@echo off
echo ========================================
echo YouTube Channel Analysis Backend
echo ========================================
echo.

REM Check if .env exists
if not exist .env (
    echo ERROR: .env file not found!
    echo Please copy .env.example to .env and configure your API keys.
    pause
    exit /b 1
)

echo Starting FastAPI server...
echo.
echo Backend will be available at: http://localhost:8000
echo API Documentation: http://localhost:8000/v1/docs
echo.

cd /d "%~dp0\..\backend"
start "YouTube Backend" C:\Users\pares\OneDrive\Desktop\content_creation\.venv\Scripts\uvicorn.exe main:app --host 0.0.0.0 --port 8000 --reload

timeout /t 3 /nobreak > nul

echo.
echo Starting frontend server...
echo Frontend will be available at: http://localhost:3001
echo.

start "YouTube Frontend" C:\Users\pares\OneDrive\Desktop\content_creation\.venv\Scripts\python.exe -m http.server 3001 --directory frontend

echo.
echo ========================================
echo Services started successfully!
echo ========================================
echo Backend: http://localhost:8000
echo Frontend: http://localhost:3001
echo API Docs: http://localhost:8000/v1/docs
echo.
echo Press any key to open the frontend...
pause > nul

start http://localhost:3001

echo.
echo Servers are running in separate windows.
echo Close those windows to stop the servers.
echo.
pause

