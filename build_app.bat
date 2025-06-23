@echo off
echo ========================================
echo CaptivePortal - Build Windows Application
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

REM Install required packages
echo 📦 Installing required packages...

REM Method 1: Try installing with user flag
echo Attempting installation with --user flag...
pip install --user pyinstaller

if errorlevel 1 (
    echo ⚠️  User installation failed, trying alternative methods...
    
    REM Method 2: Try with force reinstall
    echo Attempting force reinstall...
    pip install --force-reinstall --no-deps pyinstaller
    
    if errorlevel 1 (
        echo ⚠️  Force reinstall failed, trying upgrade...
        
        REM Method 3: Try upgrade
        pip install --upgrade pyinstaller
        
        if errorlevel 1 (
            echo ❌ All installation methods failed!
            echo.
            echo 💡 Possible solutions:
            echo   1. Run this batch file as Administrator
            echo   2. Temporarily disable antivirus
            echo   3. Close all Python/IDE applications
            echo   4. Manual install: python -m pip install pyinstaller
            echo.
            echo Press Enter to try manual installation...
            pause >nul
            
            REM Method 4: Manual installation
            python -m pip install pyinstaller
            
            if errorlevel 1 (
                echo ❌ Manual installation also failed
                echo Please install PyInstaller manually and run build again
                pause
                exit /b 1
            )
        )
    )
)

echo ✅ PyInstaller installed
echo.

REM Create the executable
echo 🔨 Building executable...

REM Try different ways to run pyinstaller
echo Attempting to run PyInstaller...

REM Method 1: Direct command
pyinstaller --onefile --windowed --name="CaptivePortal" --icon=icon.ico captive_portal_app.py 2>nul

if errorlevel 1 (
    echo ⚠️  Direct command failed, trying python -m method...
    
    REM Method 2: Python module method
    python -m PyInstaller --onefile --windowed --name="CaptivePortal" --icon=icon.ico captive_portal_app.py 2>nul
    
    if errorlevel 1 (
        echo ⚠️  Module method failed, trying script path...
        
        REM Method 3: Direct script path
        python "C:\Python311\Scripts\pyinstaller.exe" --onefile --windowed --name="CaptivePortal" --icon=icon.ico captive_portal_app.py 2>nul
        
        if errorlevel 1 (
            echo ⚠️  Script path failed, trying pip approach...
              REM Method 4: Using PyInstaller directly via Python
            python -c "import PyInstaller.__main__; PyInstaller.__main__.run(['--onefile', '--windowed', '--name=CaptivePortal', '--icon=icon.ico', 'captive_portal_app.py'])" 2>nul
            
            if errorlevel 1 (
                echo ❌ All PyInstaller methods failed!
                echo.
                echo 💡 This usually means PyInstaller installation is corrupted.
                echo.
                echo Solutions:
                echo   1. Run: pip uninstall pyinstaller
                echo   2. Run: pip install pyinstaller
                echo   3. Or use the portable version: create_portable.bat
                echo.
                pause
                exit /b 1
            )
        )
    )
)

echo ✅ Build successful!
echo.

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
