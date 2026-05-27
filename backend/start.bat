@echo off
REM Weibo Daily Sentence - Development Server Startup Script (Windows)

echo Starting Weibo Daily Sentence Backend...

REM Check if virtual environment exists
if not exist "venv\" (
    echo Virtual environment not found. Creating...
    python -m venv venv
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Install dependencies
echo Installing dependencies...
pip install -r requirements.txt

REM Check if .env exists
if not exist ".env" (
    echo Warning: .env file not found. Copying from .env.example...
    copy .env.example .env
    echo Please edit .env file with your actual configuration.
    pause
    exit /b 1
)

REM Start the server
echo Starting FastAPI server...
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
