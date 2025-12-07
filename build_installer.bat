@echo off
REM NetTools Suite - Build Installer Script
REM This script builds the Windows installer with all components

echo ========================================
echo NetTools Suite - Build Installer
echo ========================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    pause
    exit /b 1
)

REM Check if PyInstaller is installed
python -m pip show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo.
    echo ERROR: PyInstaller is not installed
    echo.
    echo Please run: install_build_tools.bat
    echo Or manually: python -m pip install pyinstaller
    echo.
    pause
    exit /b 1
)

echo.
echo Step 1/4: Cleaning previous builds...
if exist "dist" rmdir /s /q dist
if exist "build" rmdir /s /q build
if exist "installer_output" rmdir /s /q installer_output
mkdir installer_output

echo.
echo Step 2/4: Building executable with PyInstaller...
pyinstaller nettools.spec

if errorlevel 1 (
    echo ERROR: PyInstaller build failed
    pause
    exit /b 1
)

echo.
echo Step 3/4: Checking for Inno Setup...
set "INNO_PATH=C:\Program Files (x86)\Inno Setup 6\ISCC.exe"

if not exist "%INNO_PATH%" (
    echo.
    echo WARNING: Inno Setup not found at: %INNO_PATH%
    echo.
    echo Please install Inno Setup from: https://jrsoftware.org/isdl.php
    echo After installation, run this script again to create the installer.
    echo.
    echo The executable is ready in the 'dist\NetTools' folder.
    echo You can run it directly without an installer.
    pause
    exit /b 0
)

echo.
echo Step 4/4: Creating installer with Inno Setup...
"%INNO_PATH%" nettools_setup.iss

if errorlevel 1 (
    echo ERROR: Inno Setup compilation failed
    pause
    exit /b 1
)

echo.
echo ========================================
echo BUILD COMPLETE!
echo ========================================
echo.
echo Installer created in: installer_output\
echo Executable available in: dist\NetTools\
echo.
echo You can now distribute the installer!
echo.
pause
