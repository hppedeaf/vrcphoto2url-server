# VRCPhoto2URL Folder Cleanup Script
param([switch]$DryRun)

Write-Host "VRCPhoto2URL Folder Cleanup" -ForegroundColor Green
Write-Host "==============================="

# Create directories
$directories = @("archive", "archive/test-scripts", "archive/build-scripts", "archive/documentation", "dist")

foreach ($dir in $directories) {
    if (-not (Test-Path $dir)) {
        if (-not $DryRun) {
            New-Item -ItemType Directory -Path $dir -Force | Out-Null
        }
        Write-Host "Created directory: $dir" -ForegroundColor Green
    }
}

# Move test files
Write-Host "`nMoving test files..." -ForegroundColor Yellow
$testFiles = Get-ChildItem -Name "*test*.py", "comprehensive_*.py", "debug_*.py", "demonstrate_*.py", "direct_test.py", "final_*.py", "quick_demo.py", "simple_test.*"
foreach ($file in $testFiles) {
    if (Test-Path $file) {
        if (-not $DryRun) {
            Move-Item $file "archive/test-scripts/" -Force
        }
        Write-Host "  $file -> archive/test-scripts/" -ForegroundColor Cyan
    }
}

# Move build files  
Write-Host "`nMoving build files..." -ForegroundColor Yellow
$buildFiles = Get-ChildItem -Name "build_*.py", "create_*.ps1", "Create-*.ps1"
foreach ($file in $buildFiles) {
    if (Test-Path $file) {
        if (-not $DryRun) {
            Move-Item $file "archive/build-scripts/" -Force
        }
        Write-Host "  $file -> archive/build-scripts/" -ForegroundColor Cyan
    }
}

# Move documentation
Write-Host "`nMoving documentation..." -ForegroundColor Yellow  
$docFiles = Get-ChildItem -Name "*_REPORT.md", "*_COMPLETE.md", "*_SUMMARY.md", "*FIX*.md", "*THEME*.md"
foreach ($file in $docFiles) {
    if (Test-Path $file) {
        if (-not $DryRun) {
            Move-Item $file "archive/documentation/" -Force
        }
        Write-Host "  $file -> archive/documentation/" -ForegroundColor Cyan
    }
}

# Clean temp files
Write-Host "`nCleaning temporary files..." -ForegroundColor Yellow
$tempItems = Get-ChildItem -Path . -Name "__pycache__", "*.pyc", "*.tmp", "*.log" -Recurse
foreach ($item in $tempItems) {
    if (-not $DryRun) {
        Remove-Item $item -Recurse -Force -ErrorAction SilentlyContinue
    }
    Write-Host "  Removed: $item" -ForegroundColor Red
}

Write-Host "`nCleanup complete!" -ForegroundColor Green

if ($DryRun) {
    Write-Host "`nDRY RUN - No files were actually moved" -ForegroundColor Yellow
}
