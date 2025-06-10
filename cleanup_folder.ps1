# VRCPhoto2URL Folder Cleanup Script
# This script organizes files into proper directories

param([switch]$DryRun)

Write-Host "VRCPhoto2URL Folder Cleanup" -ForegroundColor Green
Write-Host "=" * 50

# Create necessary directories
$directories = @(
    "archive",
    "archive/test-scripts",
    "archive/build-scripts", 
    "archive/documentation",
    "archive/reports",
    "dist",
    "logs"
)

foreach ($dir in $directories) {
    if (-not (Test-Path $dir)) {
        if (-not $DryRun) {
            New-Item -ItemType Directory -Path $dir -Force | Out-Null
        }
        Write-Host "Created directory: $dir" -ForegroundColor Green
    }
}

# Files to move to archive/test-scripts
$testFiles = @(
    "comprehensive_fix_test.py",
    "comprehensive_test.py", 
    "debug_theme_integration.py",
    "demonstrate_fix.py",
    "direct_test.py",
    "final_test.py",
    "final_workflow_test.py",
    "quick_demo.py",
    "simple_test.ps1",
    "simple_test.py",
    "test_*.py",
    "*test*.py"
)

# Files to move to archive/build-scripts  
$buildFiles = @(
    "build_complete.py",
    "build_executable.py", 
    "build_installers.py",
    "create_msi.ps1",
    "create_nsis_installer.py",
    "Create-MSI.ps1",
    "Create-Simple-Installer.ps1"
)

# Files to move to archive/documentation
$docFiles = @(
    "BUILD_SUMMARY.md",
    "FINAL_BUILD_REPORT.md",
    "FINAL_RED_THEME_COMPLETE.md", 
    "FINAL_RESOLUTION_REPORT.md",
    "ISSUES_FIXED_REPORT.md",
    "RED_THEME_MIGRATION_COMPLETE.md",
    "THEME_SYSTEM_COMPLETE_REPORT.md",
    "THEME_SYSTEM_FIX_REPORT.md",
    "ULTRA_CLEAN_COMPLETE.md",
    "UPLOAD_COPY_FIX_COMPLETE.md",
    "UPLOAD_FIX_COMPLETE.md",
    "UPLOAD_FUNCTIONALITY_COMPLETE.md"
)

# Function to move files
function Move-FilesToArchive {
    param($filePatterns, $destination, $description)
    
    Write-Host "`n📁 Moving $description..." -ForegroundColor Yellow
    
    foreach ($pattern in $filePatterns) {
        $files = Get-ChildItem -Path . -Name $pattern -ErrorAction SilentlyContinue
        foreach ($file in $files) {
            if (Test-Path $file) {
                if (-not $DryRun) {
                    Move-Item $file $destination -Force
                }
                Write-Host "  ✅ $file → $destination" -ForegroundColor Cyan
            }
        }
    }
}

# Move files to archive
Move-FilesToArchive $testFiles "archive/test-scripts" "test scripts"
Move-FilesToArchive $buildFiles "archive/build-scripts" "build scripts"  
Move-FilesToArchive $docFiles "archive/documentation" "documentation"

# Keep essential files in root
$keepInRoot = @(
    "README.md",
    "QUICK_START.md",
    ".gitignore",
    "requirements.txt"
)

Write-Host "`n📌 Essential files kept in root:" -ForegroundColor Yellow
foreach ($file in $keepInRoot) {
    if (Test-Path $file) {
        Write-Host "  ✅ $file" -ForegroundColor Green
    }
}

# Clean up empty directories and temp files
Write-Host "`n🗑️ Cleaning temporary files..." -ForegroundColor Yellow

$tempPatterns = @(
    "*.tmp",
    "*.log", 
    "__pycache__",
    "*.pyc",
    ".pytest_cache"
)

foreach ($pattern in $tempPatterns) {
    $items = Get-ChildItem -Path . -Name $pattern -Recurse -ErrorAction SilentlyContinue
    foreach ($item in $items) {
        if (-not $DryRun) {
            Remove-Item $item -Recurse -Force -ErrorAction SilentlyContinue
        }
        Write-Host "  🗑️ Removed: $item" -ForegroundColor Red
    }
}

Write-Host "`n✨ Cleanup complete!" -ForegroundColor Green
Write-Host "📁 Main directories:" -ForegroundColor Yellow
Write-Host "  • client/          - Desktop application" -ForegroundColor Cyan
Write-Host "  • server/          - FastAPI server" -ForegroundColor Cyan  
Write-Host "  • docs-consolidated/ - Documentation" -ForegroundColor Cyan
Write-Host "  • archive/         - Archived files" -ForegroundColor Cyan
Write-Host "  • dist/            - Built executables" -ForegroundColor Cyan

if ($DryRun) {
    Write-Host "`n⚠️ DRY RUN - No files were actually moved" -ForegroundColor Yellow
    Write-Host "Run without -DryRun to perform actual cleanup" -ForegroundColor Yellow
}
