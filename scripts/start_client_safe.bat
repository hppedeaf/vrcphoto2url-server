@echo off
setlocal enabledelayedexpansion
title VRCPhoto2URL Client Launcher - Safe Mode
echo.
echo ==========================================
echo  VRCPhoto2URL - VRChat Screenshot Tool
echo  Safe Launch Mode (No Input Errors)
echo ==========================================
echo.

REM Change to project directory
cd /d "%~dp0\.."

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python not found in PATH
    echo.
    echo Please install Python 3.8+ and make sure it's in your PATH
    echo Or use the standalone VRCPhoto2URL.exe from VRCPhoto2URL-Distribution folder
    echo.
    echo Exiting in 10 seconds...
    timeout /t 10 /nobreak >nul
    exit /b 1
)

REM Check if client configuration exists
if not exist "client\client_config.json" (
    echo ⚠️  No configuration found
    echo.
    echo Please create client\client_config.json from the example file
    echo or run the interactive setup first.
    echo.
    echo Exiting in 10 seconds...
    timeout /t 10 /nobreak >nul
    exit /b 1
)

echo 🔍 Configuration found - launching client...
echo.

REM Try to launch with the safe launcher first
if exist "scripts\launch_client_safe.py" (
    echo Using safe launcher...
    python "scripts\launch_client_safe.py"
    set "exit_code=!errorlevel!"
) else (
    echo Using standard launcher...
    python "scripts\launch_client.py"
    set "exit_code=!errorlevel!"
)

echo.
if !exit_code! == 0 (
    echo ✅ Client closed successfully
) else (
    echo ❌ Client exited with error code: !exit_code!
    echo.
    echo 🔧 Troubleshooting tips:
    echo   - Make sure requirements are installed: pip install -r client\requirements.txt
    echo   - Check internet connection
    echo   - Verify server URL in client\client_config.json
    echo   - Try using VRCPhoto2URL.exe from VRCPhoto2URL-Distribution folder
)

echo.
echo Press any key to exit...
pause >nul
exit /b !exit_code!
