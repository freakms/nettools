@echo off
REM Install build tools for NetTools Suite

echo ========================================
echo Installing Build Tools
echo ========================================
echo.

REM Check Python
echo Checking Python installation...
python --version
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python from: https://www.python.org/downloads/
    pause
    exit /b 1
)
echo Python found!
echo.

REM Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip
echo.

REM Install PyInstaller
echo Installing PyInstaller...
python -m pip install pyinstaller
if errorlevel 1 (
    echo ERROR: Failed to install PyInstaller
    pause
    exit /b 1
)
echo PyInstaller installed!
echo.

REM Install requirements
echo Installing application requirements...
python -m pip install -r requirements.txt
if errorlevel 1 (
    echo WARNING: Some requirements may have failed
)
echo.

REM Verify installations
echo ========================================
echo Verifying installations...
echo ========================================
echo.

echo PyInstaller version:
python -m PyInstaller --version
echo.

echo Installed packages:
python -m pip list | findstr "pyinstaller customtkinter pythonping pillow matplotlib"
echo.

echo ========================================
echo Installation complete!
echo ========================================
echo.
echo You can now run: build_installer.bat
echo.
pause
