@echo off
REM Simple FAST build - Direct PyInstaller command
REM No Python script, just pure PyInstaller

echo.
echo ============================================================
echo NetTools Suite - Simple FAST Build
echo ============================================================
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found!
    pause
    exit /b 1
)

echo Building FAST version with PyInstaller...
echo.

REM Direct PyInstaller command
pyinstaller --onedir --windowed --name=NetToolsSuite --clean --add-data=oui_database.json;. --icon=nettools_icon.ico --version-file=version_info.txt --hidden-import=PIL._tkinter_finder --hidden-import=customtkinter --hidden-import=pythonping nettools_app.py

if errorlevel 1 (
    echo.
    echo BUILD FAILED!
    pause
    exit /b 1
)

echo.
echo ============================================================
echo BUILD COMPLETE!
echo ============================================================
echo.
echo Location: dist\NetToolsSuite\NetToolsSuite.exe
echo.
echo Run it now? (Y/N)
set /p run=">"
if /i "%run%"=="Y" start "" "dist\NetToolsSuite\NetToolsSuite.exe"

pause
