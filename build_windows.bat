@echo off
REM ====================================================================
REM NetTools Suite - Windows Build Script
REM ====================================================================
REM
REM This batch file automates the build process for Windows users.
REM Simply double-click this file to build the executable.
REM
REM Requirements:
REM   - Python 3.8 or higher installed
REM   - Python added to PATH during installation
REM
REM Output:
REM   - dist\NetToolsSuite.exe (single executable file)
REM
REM ====================================================================

echo.
echo ============================================================
echo NetTools Suite - Windows Build Script
echo ============================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH!
    echo.
    echo Please install Python from: https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation.
    echo.
    pause
    exit /b 1
)

echo [1/4] Python found:
python --version
echo.

REM Check if pip is available
pip --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] pip is not installed!
    echo.
    echo Please reinstall Python with pip included.
    echo.
    pause
    exit /b 1
)

echo [2/4] Installing dependencies...
echo.
pip install -r requirements.txt
if errorlevel 1 (
    echo.
    echo [ERROR] Failed to install dependencies!
    echo.
    pause
    exit /b 1
)

echo.
echo [3/4] Building executable...
echo.
python build_exe.py
if errorlevel 1 (
    echo.
    echo [ERROR] Build failed!
    echo.
    pause
    exit /b 1
)

echo.
echo ============================================================
echo [4/4] Build completed successfully!
echo ============================================================
echo.
echo Your executable is ready at:
echo   dist\NetToolsSuite.exe
echo.
echo You can now:
echo   1. Run dist\NetToolsSuite.exe to test it
echo   2. Copy it to any Windows computer (no installation needed)
echo   3. Distribute it to users
echo.
echo Note: Windows Defender may show a warning (false positive).
echo       Click "More info" and "Run anyway" if prompted.
echo.

REM Ask if user wants to run the executable
set /p runapp="Do you want to run the application now? (Y/N): "
if /i "%runapp%"=="Y" (
    echo.
    echo Launching NetToolsSuite...
    start "" "dist\NetToolsSuite.exe"
)

echo.
echo Press any key to exit...
pause >nul
