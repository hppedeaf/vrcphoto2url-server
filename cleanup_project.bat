@echo off
echo.
echo ==========================================
echo VRCPhoto2URL Project Cleanup Script
echo ==========================================
echo.

echo 🧹 Starting cleanup process...
echo.

REM Create archive directories
echo 📁 Creating archive directories...
if not exist "archives" mkdir "archives"
if not exist "archives\completion-reports" mkdir "archives\completion-reports"
if not exist "archives\development-files" mkdir "archives\development-files"

REM Archive completion reports
echo 📋 Archiving completion reports...
if exist "*_COMPLETE.md" move "*_COMPLETE.md" "archives\completion-reports\" >nul 2>&1
if exist "*_COMPLETION_REPORT.md" move "*_COMPLETION_REPORT.md" "archives\completion-reports\" >nul 2>&1
if exist "ADMIN_*_COMPLETE.md" move "ADMIN_*_COMPLETE.md" "archives\completion-reports\" >nul 2>&1
if exist "PROJECT_CLEANUP_*.md" move "PROJECT_CLEANUP_*.md" "archives\completion-reports\" >nul 2>&1
if exist "PERFORMANCE_*.md" move "PERFORMANCE_*.md" "archives\completion-reports\" >nul 2>&1

REM Archive development files
echo 🔧 Archiving development files...
if exist "comprehensive_test.py" move "comprehensive_test.py" "archives\development-files\" >nul 2>&1
if exist "final_integration_test.py" move "final_integration_test.py" "archives\development-files\" >nul 2>&1
if exist "connection_verification_test.py" move "connection_verification_test.py" "archives\development-files\" >nul 2>&1
if exist "test_upload.txt" move "test_upload.txt" "archives\development-files\" >nul 2>&1
if exist "setup_*.py" move "setup_*.py" "archives\development-files\" >nul 2>&1
if exist "build_executable.py" move "build_executable.py" "archives\development-files\" >nul 2>&1

REM Clean build artifacts
echo 🏗️ Cleaning build artifacts...
if exist "build" rmdir /s /q "build" >nul 2>&1
if exist "VRCPhoto2URL.spec" del "VRCPhoto2URL.spec" >nul 2>&1

REM Clean Python cache
echo 🐍 Cleaning Python cache files...
for /d /r . %%d in (__pycache__) do @if exist "%%d" rmdir /s /q "%%d" >nul 2>&1
del /s /q "*.pyc" >nul 2>&1

REM Create distribution package
echo 📦 Creating clean distribution package...
if not exist "VRCPhoto2URL-Distribution" mkdir "VRCPhoto2URL-Distribution"
if exist "dist\VRCPhoto2URL.exe" copy "dist\VRCPhoto2URL.exe" "VRCPhoto2URL-Distribution\" >nul 2>&1
if exist "client" xcopy "client" "VRCPhoto2URL-Distribution\client\" /e /i /q >nul 2>&1
if exist "docs-consolidated" xcopy "docs-consolidated" "VRCPhoto2URL-Distribution\docs-consolidated\" /e /i /q >nul 2>&1
if exist "README.md" copy "README.md" "VRCPhoto2URL-Distribution\" >nul 2>&1
if exist "scripts\start_client.bat" copy "scripts\start_client.bat" "VRCPhoto2URL-Distribution\" >nul 2>&1

echo.
echo ✅ Cleanup completed successfully!
echo.
echo 📂 Clean distribution package created at: VRCPhoto2URL-Distribution\
echo 📁 Development files archived at: archives\
echo.
echo 🎯 Your VRCPhoto2URL executable is ready at: VRCPhoto2URL-Distribution\VRCPhoto2URL.exe
echo 💡 Users can run this executable without needing Python installed!
echo.
echo 🌐 Server is running at: https://vrcphoto2url-server-production.up.railway.app
echo 👑 Admin interface: https://vrcphoto2url-server-production.up.railway.app/admin
echo.
pause
