@echo off
REM Manual step-by-step build process

echo ========================================
echo Manual Build Process
echo ========================================
echo.

echo Step 1: Clean previous builds
echo ------------------------------
if exist dist rmdir /s /q dist
if exist build rmdir /s /q build
if exist installer_output rmdir /s /q installer_output
mkdir installer_output
echo Done!
echo.
pause

echo Step 2: Build with PyInstaller
echo ------------------------------
python -m PyInstaller nettools.spec --noconfirm
echo.
echo Check if dist\NetTools\NetTools.exe exists:
dir dist\NetTools\NetTools.exe
echo.
pause

echo Step 3: Run Inno Setup Compiler
echo ------------------------------
echo Running Inno Setup...
"C:\Program Files (x86)\Inno Setup 6\ISCC.exe" nettools_setup.iss
echo.
pause

echo Step 4: Check result
echo ------------------------------
dir installer_output
echo.
echo If you see NetTools_Setup_1.0.0.exe above, build succeeded!
echo.
pause
