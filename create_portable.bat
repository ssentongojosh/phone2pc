@echo off
echo ========================================
echo CaptivePortal - Create Portable Package
echo ========================================
echo.

echo This creates a portable version without PyInstaller
echo.

REM Create portable directory
set PORTABLE_DIR=CaptivePortal_Portable
if exist "%PORTABLE_DIR%" (
    echo Removing existing portable directory...
    rmdir /s /q "%PORTABLE_DIR%"
)

echo 📁 Creating portable directory...
mkdir "%PORTABLE_DIR%"

REM Copy all required files
echo 📄 Copying application files...
copy "captive_portal_app.py" "%PORTABLE_DIR%\" >nul
copy "uploader.py" "%PORTABLE_DIR%\" >nul
copy "style.css" "%PORTABLE_DIR%\" >nul
copy "index.html" "%PORTABLE_DIR%\" >nul
copy "README.md" "%PORTABLE_DIR%\" >nul
copy "Set_up.ps1" "%PORTABLE_DIR%\" >nul

if exist "icon.ico" copy "icon.ico" "%PORTABLE_DIR%\" >nul

REM Create launcher script
echo 📝 Creating launcher script...
(
echo @echo off
echo title CaptivePortal - File Transfer Hub
echo.
echo REM Check if running as administrator
echo net session ^>nul 2^>^&1
echo if %%errorLevel%% == 0 ^(
echo     echo ✅ Running as Administrator
echo ^) else ^(
echo     echo ⚠️  Not running as Administrator
echo     echo For full functionality, right-click and "Run as Administrator"
echo     echo.
echo ^)
echo.
echo echo ========================================
echo echo 📶 CaptivePortal - File Transfer Hub
echo echo ========================================
echo echo.
echo echo Starting GUI application...
echo echo.
echo.
echo REM Check if Python is available
echo python --version ^>nul 2^>^&1
echo if errorlevel 1 ^(
echo     echo ❌ Python not found!
echo     echo Please install Python from https://python.org
echo     echo Make sure to check "Add Python to PATH" during installation
echo     pause
echo     exit /b 1
echo ^)
echo.
echo REM Start the GUI application
echo python captive_portal_app.py
echo.
echo if errorlevel 1 ^(
echo     echo.
echo     echo ❌ Application encountered an error
echo     pause
echo ^)
) > "%PORTABLE_DIR%\CaptivePortal.bat"

REM Create README for portable version
echo 📚 Creating portable README...
(
echo # CaptivePortal Portable Version
echo.
echo ## Requirements
echo - Windows 10 or later
echo - Python 3.7+ installed and added to PATH
echo - Administrator privileges ^(recommended^)
echo.
echo ## How to Run
echo 1. Double-click `CaptivePortal.bat`
echo 2. Or run: `python captive_portal_app.py`
echo.
echo ## Features
echo - WiFi Hotspot creation
echo - File upload server
echo - Directory browsing
echo - Dark mode support
echo - Responsive mobile interface
echo.
echo ## Files Included
echo - `captive_portal_app.py` - Main GUI application
echo - `uploader.py` - HTTP server backend  
echo - `style.css` - Web interface styling
echo - `index.html` - Upload page
echo - `Set_up.ps1` - Original PowerShell script
echo - `README.md` - Complete documentation
echo.
echo ## Troubleshooting
echo - Run as Administrator for hotspot functionality
echo - Ensure Python is in PATH
echo - Check Windows Firewall settings
echo - Verify WiFi adapter supports hosted networks
echo.
echo For more information, see the main README.md file.
) > "%PORTABLE_DIR%\PORTABLE_README.txt"

echo ✅ Files copied successfully!
echo.

echo ========================================
echo ✅ PORTABLE PACKAGE CREATED!
echo ========================================
echo.
echo Your portable CaptivePortal is ready:
echo   📁 %PORTABLE_DIR%\
echo.
echo Files included:
echo   🚀 CaptivePortal.bat ^(launcher^)
echo   🐍 captive_portal_app.py ^(GUI app^)
echo   🌐 uploader.py ^(server^)
echo   🎨 style.css ^(styling^)
echo   📄 index.html ^(upload page^)
echo   📚 README files
echo.
echo To use:
echo   1. Copy the entire '%PORTABLE_DIR%' folder
echo   2. Double-click CaptivePortal.bat
echo   3. No installation required!
echo.
echo Note: Requires Python to be installed on target machine
echo.

pause
