@echo off
REM ====================================================================
REM NetTools Suite - CLEAN REBUILD Script
REM ====================================================================
REM
REM This script performs a COMPLETE CLEAN rebuild:
REM   1. Deletes all build artifacts
REM   2. Clears Python cache
REM   3. Removes old executables
REM   4. Rebuilds from scratch
REM
REM Use this when:
REM   - You updated the code but exe shows old version
REM   - Previous build had issues
REM   - You want to ensure a fresh build
REM
REM ====================================================================

echo.
echo ============================================================
echo NetTools Suite - CLEAN REBUILD
echo ============================================================
echo.
echo This will DELETE all previous builds and rebuild from scratch.
echo.
set /p confirm="Continue? (Y/N): "
if /i not "%confirm%"=="Y" (
    echo.
    echo Rebuild cancelled.
    pause
    exit /b 0
)

echo.
echo ============================================================
echo Step 1/5: Deleting old build artifacts...
echo ============================================================
echo.

REM Delete build folders
if exist "build" (
    echo Deleting build\ folder...
    rmdir /s /q "build"
)

if exist "dist" (
    echo Deleting dist\ folder...
    rmdir /s /q "dist"
)

REM Delete spec files
if exist "*.spec" (
    echo Deleting .spec files...
    del /q *.spec
)

echo Build artifacts deleted!
echo.

echo ============================================================
echo Step 2/5: Clearing Python cache...
echo ============================================================
echo.

REM Delete __pycache__ folders
for /d /r . %%d in (__pycache__) do @if exist "%%d" (
    echo Deleting %%d
    rmdir /s /q "%%d"
)

REM Delete .pyc files
for /r . %%f in (*.pyc) do @if exist "%%f" (
    del /q "%%f"
)

echo Python cache cleared!
echo.

echo ============================================================
echo Step 3/5: Verifying critical files...
echo ============================================================
echo.

REM Check for critical files
if not exist "nettools_app.py" (
    echo [ERROR] nettools_app.py not found!
    pause
    exit /b 1
)
echo ✓ nettools_app.py found

if not exist "oui_database.json" (
    echo [ERROR] oui_database.json not found!
    echo This file is CRITICAL for vendor lookup!
    pause
    exit /b 1
)
echo ✓ oui_database.json found

if not exist "build_exe_fast.py" (
    echo [ERROR] build_exe_fast.py not found!
    pause
    exit /b 1
)
echo ✓ build_exe_fast.py found

echo.
echo All critical files verified!
echo.

echo ============================================================
echo Step 4/5: Checking Python and dependencies...
echo ============================================================
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found!
    pause
    exit /b 1
)
echo ✓ Python found:
python --version
echo.

REM Check PyInstaller
python -c "import PyInstaller" >nul 2>&1
if errorlevel 1 (
    echo [WARNING] PyInstaller not found, installing...
    pip install pyinstaller
)
echo ✓ PyInstaller ready
echo.

echo ============================================================
echo Step 5/5: Building FRESH executable...
echo ============================================================
echo.
echo Building with FAST mode (directory structure)...
echo This will take 2-5 minutes...
echo.

REM Build with fast script
python build_exe_fast.py

if errorlevel 1 (
    echo.
    echo [ERROR] Build failed!
    echo.
    echo Troubleshooting:
    echo   1. Check the error messages above
    echo   2. Try: pip install --upgrade pyinstaller
    echo   3. Check if antivirus is blocking PyInstaller
    echo   4. Run this script as Administrator
    echo.
    pause
    exit /b 1
)

echo.
echo ============================================================
echo CLEAN REBUILD COMPLETE!
echo ============================================================
echo.
echo Your NEW executable is at:
echo   dist\NetToolsSuite\NetToolsSuite.exe
echo.
echo IMPORTANT - Version Check:
echo   1. Run the executable
echo   2. Check the sidebar says "NetTools" (not "NetTools Suite")
echo   3. Navigation buttons should be on the LEFT (not tabs on top)
echo   4. Theme selector should be at BOTTOM of sidebar
echo.
echo If you still see the old design:
echo   • Make sure you're running the NEW .exe from dist\NetToolsSuite\
echo   • Close ALL old instances of the app first
echo   • Delete any desktop shortcuts and recreate them
echo.

REM Check if executable exists
if exist "dist\NetToolsSuite\NetToolsSuite.exe" (
    echo ✓ Executable verified: dist\NetToolsSuite\NetToolsSuite.exe exists
    echo.
    
    REM Ask if user wants to run the executable
    set /p runapp="Run the NEW executable now? (Y/N): "
    if /i "%runapp%"=="Y" (
        echo.
        echo Launching NEW NetToolsSuite...
        echo Watch for the modern sidebar design!
        echo.
        start "" "dist\NetToolsSuite\NetToolsSuite.exe"
    )
) else (
    echo [ERROR] Executable not found!
    echo The build may have failed. Check the output above.
    echo.
)

echo.
echo Press any key to exit...
pause >nul
