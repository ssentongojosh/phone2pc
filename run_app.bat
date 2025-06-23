@echo off
title CaptivePortal - File Transfer Hub

REM Check if running as administrator
net session >nul 2>&1
if %errorLevel% == 0 (
    echo ✅ Running as Administrator
) else (
    echo ⚠️  Not running as Administrator
    echo For full functionality, right-click and "Run as Administrator"
    echo.
)

echo ========================================
echo 📶 CaptivePortal - File Transfer Hub
echo ========================================
echo.
echo Starting GUI application...
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python not found!
    echo Please install Python from https://python.org
    echo Make sure to check "Add Python to PATH" during installation
    pause
    exit /b 1
)

REM Check if required files exist
if not exist "captive_portal_app.py" (
    echo ❌ captive_portal_app.py not found!
    echo Please ensure you're running from the correct directory
    pause
    exit /b 1
)

if not exist "uploader.py" (
    echo ❌ uploader.py not found!
    echo Please ensure all project files are in the same directory
    pause
    exit /b 1
)

REM Start the GUI application
python captive_portal_app.py

if errorlevel 1 (
    echo.
    echo ❌ Application encountered an error
    pause
)
