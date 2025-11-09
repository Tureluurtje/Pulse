@echo off

:: Change to project root directory
cd /d %~dp0\..

:: Activate virtual environment
call venv\Scripts\activate.bat

echo Starting Pulse Chat Application...
echo api will run on: http://localhost:8000
echo API Docs will be at: http://localhost:8000/docs
echo.
echo Press Ctrl+C to stop the server
echo.

:: Start api
uvicorn asgi_app:app --host 0.0.0.0 --port 8000
