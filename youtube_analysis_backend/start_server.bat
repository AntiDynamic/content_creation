@echo off
echo ========================================
echo  YouTube Channel Analyzer - Backend
echo ========================================
echo.

REM Check if virtual environment exists
if not exist "venv\" (
    echo Virtual environment not found!
    echo Please run setup.ps1 first
    pause
    exit /b 1
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Check if .env file exists
if not exist ".env" (
    echo .env file not found!
    echo Please copy .env.example to .env and add your API keys
    pause
    exit /b 1
)

echo.
echo Starting FastAPI server...
echo API will be available at: http://localhost:8000
echo API Docs: http://localhost:8000/v1/docs
echo.
echo Press Ctrl+C to stop the server
echo.

REM Start the server
python main.py
