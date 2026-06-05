@echo off
echo ============================================
echo   FitForm AI - Starting Application
echo ============================================
echo.

REM Check if virtual environment exists
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
    echo.
)

REM Activate virtual environment
call venv\Scripts\activate.bat 2>nul || (
    echo No venv found, using system Python...
)

REM Install requirements if needed
echo Checking dependencies...
python -m pip install -r requirements.txt --quiet

echo.
echo Starting Flask server at http://localhost:5000
echo Press Ctrl+C to stop
echo.
python app.py
pause
