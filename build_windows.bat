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
    echo After installing Python, run this script again.
    echo.
    pause
    exit /b 1
)

echo [1/5] Python found:
python --version
echo.

REM Check if pip is available
pip --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] pip is not installed!
    echo.
    echo Trying to use python -m pip instead...
    python -m pip --version >nul 2>&1
    if errorlevel 1 (
        echo [ERROR] pip is not available!
        echo Please reinstall Python with pip included.
        echo.
        pause
        exit /b 1
    )
    echo Using python -m pip
    set PIP_CMD=python -m pip
) else (
    set PIP_CMD=pip
)

echo [2/5] Upgrading pip to latest version...
echo.
%PIP_CMD% install --upgrade pip --quiet
echo pip upgraded successfully!
echo.

echo [3/5] Installing dependencies...
echo.
echo This may take a few minutes on first run...
echo.
%PIP_CMD% install -r requirements.txt
if errorlevel 1 (
    echo.
    echo [ERROR] Failed to install dependencies!
    echo.
    echo Troubleshooting:
    echo   1. Check your internet connection
    echo   2. Run Command Prompt as Administrator
    echo   3. Try: python -m pip install --upgrade pip
    echo   4. Then run this script again
    echo.
    pause
    exit /b 1
)

echo.
echo Dependencies installed successfully!
echo.

echo [4/5] Building executable...
echo.
echo This will take 2-5 minutes. Please wait...
echo.
python build_exe.py
if errorlevel 1 (
    echo.
    echo [ERROR] Build failed!
    echo.
    echo Common solutions:
    echo   1. Make sure all dependencies installed correctly
    echo   2. Try running: pip install --upgrade pyinstaller
    echo   3. Check if antivirus is blocking PyInstaller
    echo.
    pause
    exit /b 1
)

echo.
echo ============================================================
echo [5/5] Build completed successfully!
echo ============================================================
echo.
echo Your executable is ready at:
echo   dist\NetToolsSuite.exe
echo.
echo File size: approximately 30-40 MB
echo.
echo You can now:
echo   1. Run dist\NetToolsSuite.exe to test it
echo   2. Copy it to any Windows computer (no installation needed)
echo   3. Distribute it to users (single file, no dependencies)
echo.
echo IMPORTANT NOTE:
echo   Windows Defender may show a SmartScreen warning (false positive).
echo   This is normal for unsigned executables built with PyInstaller.
echo   Click "More info" and "Run anyway" if prompted.
echo.

REM Check if executable exists
if exist "dist\NetToolsSuite.exe" (
    echo Executable verified: dist\NetToolsSuite.exe exists
    echo.
    
    REM Ask if user wants to run the executable
    set /p runapp="Do you want to run the application now? (Y/N): "
    if /i "%runapp%"=="Y" (
        echo.
        echo Launching NetToolsSuite...
        echo.
        start "" "dist\NetToolsSuite.exe"
    )
) else (
    echo [WARNING] Could not find dist\NetToolsSuite.exe
    echo Please check the build output above for errors.
    echo.
)

echo.
echo Build script completed!
echo Press any key to exit...
pause >nul
