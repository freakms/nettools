@echo off
REM Diagnostic script to check build environment

echo ========================================
echo NetTools Build Environment Diagnostic
echo ========================================
echo.

echo [1/6] Checking Python...
python --version
if errorlevel 1 (
    echo   ERROR: Python not found
) else (
    echo   OK: Python found
)
echo.

echo [2/6] Checking PyInstaller...
python -m pip show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo   ERROR: PyInstaller not installed
) else (
    echo   OK: PyInstaller installed
)
echo.

echo [3/6] Checking for dist folder...
if exist "dist\NetTools\NetTools.exe" (
    echo   OK: PyInstaller build succeeded
    echo   File: dist\NetTools\NetTools.exe exists
    dir "dist\NetTools\NetTools.exe"
) else (
    echo   ERROR: dist\NetTools\NetTools.exe not found
    echo   PyInstaller did not create the executable
)
echo.

echo [4/6] Checking Inno Setup...
set "INNO_PATH=C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
if exist "%INNO_PATH%" (
    echo   OK: Inno Setup found at: %INNO_PATH%
    "%INNO_PATH%" /? 2>nul
) else (
    echo   ERROR: Inno Setup NOT FOUND at: %INNO_PATH%
    echo   This is why no installer was created!
    echo.
    echo   Please install from: https://jrsoftware.org/isdl.php
)
echo.

echo [5/6] Checking installer_output folder...
if exist "installer_output" (
    echo   OK: installer_output folder exists
    dir /b "installer_output"
    if errorlevel 1 (
        echo   WARNING: Folder is empty
    )
) else (
    echo   ERROR: installer_output folder does not exist
)
echo.

echo [6/6] Checking for .iss file...
if exist "nettools_setup.iss" (
    echo   OK: nettools_setup.iss exists
) else (
    echo   ERROR: nettools_setup.iss not found
)
echo.

echo ========================================
echo Diagnostic Complete
echo ========================================
echo.
echo SUMMARY:
echo --------
if not exist "%INNO_PATH%" (
    echo.
    echo   ISSUE FOUND: Inno Setup is not installed!
    echo.
    echo   SOLUTION:
    echo   1. Download Inno Setup from: https://jrsoftware.org/isdl.php
    echo   2. Install it (use default installation path)
    echo   3. Run build_installer.bat again
    echo.
) else (
    if not exist "dist\NetTools\NetTools.exe" (
        echo.
        echo   ISSUE FOUND: PyInstaller failed to create executable
        echo.
        echo   SOLUTION:
        echo   1. Run: pip install -r requirements.txt
        echo   2. Run: build_installer.bat again
        echo.
    ) else (
        echo.
        echo   Everything looks good. Checking for other issues...
        echo.
    )
)

pause
