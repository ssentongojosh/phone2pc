@echo off
echo ========================================
echo PyInstaller Diagnostic Tool
echo ========================================
echo.

echo 🔍 Checking Python installation...
python --version
if errorlevel 1 (
    echo ❌ Python not found in PATH
    goto end
)
echo ✅ Python found
echo.

echo 🔍 Checking PyInstaller installation...
python -c "import PyInstaller; print(f'PyInstaller version: {PyInstaller.__version__}')" 2>nul
if errorlevel 1 (
    echo ❌ PyInstaller not installed
    echo.
    echo 📦 Installing PyInstaller...
    pip install pyinstaller
    if errorlevel 1 (
        echo ❌ Failed to install PyInstaller
        goto end
    )
    echo ✅ PyInstaller installed
) else (
    echo ✅ PyInstaller already installed
)
echo.

echo 🔍 Finding PyInstaller executable...
where pyinstaller 2>nul
if errorlevel 1 (
    echo ⚠️  pyinstaller command not in PATH
    echo Looking for PyInstaller in Python Scripts directory...
    python -c "import sys, os; scripts_dir = os.path.join(sys.prefix, 'Scripts'); print(f'Scripts directory: {scripts_dir}'); print(f'PyInstaller exists: {os.path.exists(os.path.join(scripts_dir, \"pyinstaller.exe\"))}')"
) else (
    echo ✅ pyinstaller found in PATH
)
echo.

echo 🔍 Testing PyInstaller functionality...
echo import sys; print("Hello from test script") > test_script.py
echo Running PyInstaller test...

REM Try different methods
python -c "import PyInstaller.__main__; PyInstaller.__main__.run(['--onefile', '--name=test', 'test_script.py'])" 2>nul
if errorlevel 1 (
    echo ❌ PyInstaller test failed
    echo.
    echo 💡 Common issues and solutions:
    echo   1. Antivirus blocking PyInstaller
    echo   2. Insufficient permissions (run as Administrator)
    echo   3. Corrupted PyInstaller installation
    echo   4. Missing dependencies
    echo.
    echo Try running as Administrator or temporarily disable antivirus
) else (
    echo ✅ PyInstaller test successful
    if exist "dist\test.exe" (
        echo Test executable created: dist\test.exe
        del dist\test.exe >nul 2>&1
        rmdir dist >nul 2>&1
    )
)

REM Cleanup
del test_script.py >nul 2>&1
del test.spec >nul 2>&1
rmdir /s /q build >nul 2>&1

:end
echo.
echo ========================================
echo Diagnostic complete
echo ========================================
pause
