# PowerShell script to find what's locking the dist folder
Write-Host "Finding processes locking files in dist folder..." -ForegroundColor Yellow
Write-Host ""

$distPath = ".\dist"

# Method 1: Using Handle (if available)
if (Get-Command handle.exe -ErrorAction SilentlyContinue) {
    Write-Host "Using handle.exe to find locks..." -ForegroundColor Green
    handle.exe $distPath
} else {
    # Method 2: Check common culprits
    Write-Host "Checking common processes..." -ForegroundColor Green
    
    $suspects = @(
        "*NetToolsSuite*",
        "*python*",
        "*explorer*"
    )
    
    foreach ($pattern in $suspects) {
        $procs = Get-Process | Where-Object { $_.ProcessName -like $pattern }
        if ($procs) {
            Write-Host "`nFound potentially locking processes:" -ForegroundColor Cyan
            $procs | Select-Object Id, ProcessName, Path | Format-Table
        }
    }
}

Write-Host "`n=== Solutions ===" -ForegroundColor Yellow
Write-Host "1. Kill NetToolsSuite processes: Get-Process *NetToolsSuite* | Stop-Process -Force"
Write-Host "2. Restart Windows Explorer: taskkill /f /im explorer.exe && start explorer.exe"
Write-Host "3. Reboot your computer"
Write-Host "4. Rename dist folder instead of deleting it"
