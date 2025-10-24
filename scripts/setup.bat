@echo off
echo Setting up Pulse Chat Application...

:: Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Python 3 is required but not installed. Please install Python 3.8+
    pause
    exit /b 1
)

:: Create virtual environment in project root
python -m venv ..\venv
call ..\venv\Scripts\activate.bat

:: Install dependencies
pip install -r ..\requirements.txt

:: Install frontend dependencies if package.json exists
if exist "..\frontend\package.json" (
    echo Installing frontend dependencies...
    cd ..\frontend
    npm install
    cd ..\scripts
)

echo Setup complete! Run the application with: scripts\run.bat
pause