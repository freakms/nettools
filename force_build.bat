@echo off
echo ============================================================
echo NetTools Suite - Force Build Script
echo ============================================================
echo.

echo Step 1: Killing processes...
taskkill /F /IM NetToolsSuite.exe >nul 2>&1
taskkill /F /IM python.exe >nul 2>&1
timeout /t 2 /nobreak >nul

echo Step 2: Attempting to remove build folders...
if exist build (
    rd /s /q build 2>nul
    if exist build (
        echo Warning: Could not delete build folder
    ) else (
        echo Build folder removed
    )
)

if exist dist (
    rd /s /q dist 2>nul
    if exist dist (
        echo Warning: dist folder is locked, trying alternative...
        echo Please close ALL File Explorer windows and try again
        echo.
        echo Alternative: Manually delete or rename the dist folder
        pause
        exit /b 1
    ) else (
        echo Dist folder removed
    )
)

echo.
echo Step 3: Building executable...
python build_exe_fast.py

echo.
echo ============================================================
if exist dist\NetToolsSuite\NetToolsSuite.exe (
    echo BUILD SUCCESSFUL!
    echo Executable: dist\NetToolsSuite\NetToolsSuite.exe
) else (
    echo BUILD FAILED - Check errors above
)
echo ============================================================
pause
