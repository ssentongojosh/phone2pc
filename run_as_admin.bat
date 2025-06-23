@echo off
echo ========================================
echo CaptivePortal - Administrator Mode
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python from https://python.org
    pause
    exit /b 1
)

echo ✅ Python found
echo 👑 Starting CaptivePortal with Administrator privileges...
echo.

REM Run the Python application as administrator
powershell -Command "Start-Process python -ArgumentList 'captive_portal_app.py' -Verb RunAs"

echo.
echo Note: A UAC prompt may appear requesting administrator access.
echo Please click 'Yes' to grant the necessary permissions.
echo.
pause
