@echo off
echo ========================================
echo CaptivePortal - Manual PyInstaller Fix
echo ========================================
echo.

echo This script helps fix PyInstaller installation issues
echo.

echo 🔍 Diagnosing the problem...
echo.

REM Check Python installation
python --version
echo.

REM Check pip version
pip --version
echo.

REM Check current packages
echo 📦 Currently installed packages:
pip list | findstr pyinstaller
echo.

echo 💡 Possible solutions for PyInstaller installation issues:
echo.
echo   1. ADMINISTRATOR RIGHTS:
echo      Right-click this file and "Run as Administrator"
echo.
echo   2. ANTIVIRUS INTERFERENCE:
echo      Temporarily disable real-time protection
echo      Add Python folder to antivirus exclusions
echo.
echo   3. MANUAL INSTALLATION:
echo      Close all Python applications and IDEs
echo      Run: python -m pip install --user pyinstaller
echo.
echo   4. FORCE REINSTALL:
echo      Run: pip uninstall pyinstaller
echo      Run: pip install pyinstaller
echo.
echo   5. ALTERNATIVE LOCATIONS:
echo      Install to user directory: pip install --user pyinstaller
echo      Use virtual environment (run build_safe.bat)
echo.

echo Choose an option:
echo   [1] Try administrator installation
echo   [2] Try user installation  
echo   [3] Try force reinstall
echo   [4] Try virtual environment method
echo   [5] Exit
echo.

set /p choice="Enter your choice (1-5): "

if "%choice%"=="1" goto admin_install
if "%choice%"=="2" goto user_install
if "%choice%"=="3" goto force_install
if "%choice%"=="4" goto venv_method
if "%choice%"=="5" goto exit

echo Invalid choice, exiting...
goto exit

:admin_install
echo.
echo 🔧 Attempting administrator installation...
net session >nul 2>&1
if %errorLevel% == 0 (
    echo ✅ Running as Administrator
    pip install pyinstaller
) else (
    echo ❌ Not running as Administrator
    echo Please right-click this file and "Run as Administrator"
)
goto done

:user_install
echo.
echo 🔧 Attempting user installation...
pip install --user pyinstaller
goto done

:force_install
echo.
echo 🔧 Attempting force reinstall...
pip uninstall pyinstaller -y
pip install pyinstaller
goto done

:venv_method
echo.
echo 🔧 Using virtual environment method...
call build_safe.bat
goto exit

:done
echo.
if errorlevel 1 (
    echo ❌ Installation failed
    echo Try another method or contact support
) else (
    echo ✅ Installation successful!
    echo You can now run build_app.bat
)

:exit
echo.
pause
