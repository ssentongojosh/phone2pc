@echo off
echo ========================================
echo CaptivePortal - Safe Build (Virtual Environment)
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
echo.

REM Create virtual environment
echo 🔧 Creating virtual environment...
if exist "build_env" (
    echo Removing existing build environment...
    rmdir /s /q "build_env"
)

python -m venv build_env

if errorlevel 1 (
    echo ❌ Failed to create virtual environment
    echo Try running as Administrator or check Python installation
    pause
    exit /b 1
)

echo ✅ Virtual environment created
echo.

REM Activate virtual environment
echo 🔄 Activating virtual environment...
call "build_env\Scripts\activate.bat"

if errorlevel 1 (
    echo ❌ Failed to activate virtual environment
    pause
    exit /b 1
)

echo ✅ Virtual environment activated
echo.

REM Upgrade pip
echo 📈 Upgrading pip...
python -m pip install --upgrade pip

REM Install PyInstaller
echo 📦 Installing PyInstaller...
pip install pyinstaller

if errorlevel 1 (
    echo ❌ Failed to install PyInstaller in virtual environment
    pause
    exit /b 1
)

echo ✅ PyInstaller installed
echo.

REM Create the executable
echo 🔨 Building executable...
pyinstaller --onefile --windowed --name="CaptivePortal" captive_portal_app.py

if errorlevel 1 (
    echo ❌ Build failed
    call "build_env\Scripts\deactivate.bat"
    pause
    exit /b 1
)

echo ✅ Build successful!
echo.

REM Deactivate virtual environment
call "build_env\Scripts\deactivate.bat"

REM Copy required files to dist folder
echo 📁 Copying required files...
if not exist "dist" mkdir dist
copy "style.css" "dist\" >nul
copy "index.html" "dist\" >nul  
copy "uploader.py" "dist\" >nul
copy "README.md" "dist\" >nul

if exist "icon.ico" copy "icon.ico" "dist\" >nul

echo ✅ Files copied
echo.

REM Clean up virtual environment
echo 🧹 Cleaning up...
rmdir /s /q "build_env"

echo ✅ Virtual environment cleaned up
echo.

echo ========================================
echo ✅ BUILD COMPLETE!
echo ========================================
echo.
echo Your executable is ready in the 'dist' folder:
echo   📁 dist\CaptivePortal.exe
echo.
echo Required files included:
echo   📄 style.css
echo   📄 index.html  
echo   📄 uploader.py
echo   📄 README.md
echo.
echo To distribute:
echo   1. Copy the entire 'dist' folder
echo   2. Run CaptivePortal.exe as Administrator
echo   3. Enjoy your portable CaptivePortal app!
echo.

pause
