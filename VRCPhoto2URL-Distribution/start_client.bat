@echo off
setlocal enabledelayedexpansion
title VRCPhoto2URL Client
echo.
echo ========================================
echo  VRCPhoto2URL - VRChat Screenshot Tool
echo ========================================
echo.

REM Check if configuration exists
cd /d "%~dp0\.."
if not exist "client\client_config.json" (
    echo ⚠️  No configuration found
    echo.
    echo Choose setup option:
    echo   1. Interactive setup (recommended)
    echo   2. Quick demo setup (for testing)
    echo   3. Exit
    echo.
    set /p choice="Enter choice (1-3): "
    
    if "!choice!"=="1" (
        echo Running interactive setup...
        python setup_config.py
        if errorlevel 1 (
            echo.
            echo ❌ Setup failed or cancelled
            pause
            exit /b 1
        )
    ) else if "!choice!"=="2" (
        echo Setting up demo configuration...
        python setup_demo.py
    ) else (
        echo Exiting...
        exit /b 0
    )
    echo.
)

echo Starting desktop client...
echo.

REM Change to the scripts directory where launch_client_safe.py is located
cd /d "%~dp0"
python launch_client_safe.py

echo.
pause
