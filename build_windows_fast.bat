@echo off
REM ====================================================================
REM NetTools Suite - Windows FAST Build Script (Directory Mode)
REM ====================================================================
REM
REM This creates a FOLDER with the executable for FASTER startup.
REM
REM Performance:
REM   - Single file: 2-3 seconds startup
REM   - Directory:   0.5-1 second startup (THIS VERSION)
REM
REM Distribution:
REM   - Single file: dist\NetToolsSuite.exe (one file)
REM   - Directory:   dist\NetToolsSuite\ folder (multiple files)
REM
REM Output:
REM   - dist\NetToolsSuite\NetToolsSuite.exe (+ dependencies)
REM
REM ====================================================================

echo.
echo ============================================================
echo NetTools Suite - Windows FAST Build (Directory Mode)
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

echo [4/5] Building FAST version (directory mode)...
echo.
echo This will take 2-5 minutes. Please wait...
echo.
echo Building with --onedir for faster startup...
echo.
python build_exe_fast.py
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
echo [5/5] FAST Build completed successfully!
echo ============================================================
echo.
echo Your application is ready at:
echo   dist\NetToolsSuite\NetToolsSuite.exe
echo.
echo Performance:
echo   Startup time: ~0.5-1 second (MUCH FASTER!)
echo   (Single-file version: 2-3 seconds)
echo.
echo Folder structure:
echo   dist\NetToolsSuite\
echo     NetToolsSuite.exe     (main executable)
echo     *.dll                 (required libraries)
echo     _internal\            (dependencies folder)
echo.
echo IMPORTANT - Distribution:
echo   • ZIP the entire "NetToolsSuite" folder
echo   • Users must extract ALL files
echo   • Run: NetToolsSuite\NetToolsSuite.exe
echo   • All files must stay together!
echo.
echo Total folder size: ~40-50 MB
echo.

REM Check if executable exists
if exist "dist\NetToolsSuite\NetToolsSuite.exe" (
    echo Executable verified: dist\NetToolsSuite\NetToolsSuite.exe exists
    echo.
    
    REM Ask if user wants to run the executable
    set /p runapp="Do you want to run the application now? (Y/N): "
    if /i "%runapp%"=="Y" (
        echo.
        echo Launching NetToolsSuite (FAST version)...
        echo.
        start "" "dist\NetToolsSuite\NetToolsSuite.exe"
    )
) else (
    echo [WARNING] Could not find dist\NetToolsSuite\NetToolsSuite.exe
    echo Please check the build output above for errors.
    echo.
)

echo.
echo Build script completed!
echo.
echo To create a ZIP for distribution:
echo   Right-click dist\NetToolsSuite folder
echo   Select "Send to" -> "Compressed (zipped) folder"
echo.
echo Press any key to exit...
pause >nul
