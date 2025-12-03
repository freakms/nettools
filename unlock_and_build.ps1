# Force unlock and build script
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "NetTools Suite - Unlock and Build" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Kill processes
Write-Host "Step 1: Killing all related processes..." -ForegroundColor Yellow
Get-Process | Where-Object {$_.ProcessName -like "*NetToolsSuite*" -or $_.ProcessName -like "*python*"} | Stop-Process -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 2
Write-Host "Processes killed" -ForegroundColor Green
Write-Host ""

# Step 2: Restart Explorer (this often releases locks)
Write-Host "Step 2: Restarting Windows Explorer..." -ForegroundColor Yellow
taskkill /f /im explorer.exe | Out-Null
Start-Sleep -Seconds 1
Start-Process explorer.exe
Start-Sleep -Seconds 2
Write-Host "Explorer restarted" -ForegroundColor Green
Write-Host ""

# Step 3: Try to remove folders
Write-Host "Step 3: Removing build folders..." -ForegroundColor Yellow

if (Test-Path "build") {
    try {
        Remove-Item "build" -Recurse -Force -ErrorAction Stop
        Write-Host "Build folder removed" -ForegroundColor Green
    } catch {
        Write-Host "Could not remove build folder" -ForegroundColor Yellow
    }
}

if (Test-Path "dist") {
    try {
        Remove-Item "dist" -Recurse -Force -ErrorAction Stop
        Write-Host "Dist folder removed" -ForegroundColor Green
    } catch {
        Write-Host "Dist folder is still locked!" -ForegroundColor Red
        Write-Host ""
        Write-Host "MANUAL SOLUTION REQUIRED:" -ForegroundColor Yellow
        Write-Host "1. Open Task Manager (Ctrl+Shift+Esc)" -ForegroundColor White
        Write-Host "2. Go to 'Details' tab" -ForegroundColor White
        Write-Host "3. Look for any NetToolsSuite.exe or python.exe" -ForegroundColor White
        Write-Host "4. Right-click and 'End Task'" -ForegroundColor White
        Write-Host "5. Manually delete the dist folder in File Explorer" -ForegroundColor White
        Write-Host "6. Run this script again" -ForegroundColor White
        Write-Host ""
        pause
        exit 1
    }
}

Write-Host ""

# Step 4: Build
Write-Host "Step 4: Building executable..." -ForegroundColor Yellow
Write-Host ""
python build_exe_fast.py

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
if (Test-Path "dist\NetToolsSuite\NetToolsSuite.exe") {
    Write-Host "BUILD SUCCESSFUL!" -ForegroundColor Green
    Write-Host "Executable: dist\NetToolsSuite\NetToolsSuite.exe" -ForegroundColor White
} else {
    Write-Host "BUILD FAILED - Check errors above" -ForegroundColor Red
}
Write-Host "============================================================" -ForegroundColor Cyan
