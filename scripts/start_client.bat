@echo off
title VRCPhoto2URL Client
echo.
echo ========================================
echo  VRCPhoto2URL - VRChat Screenshot Tool
echo ========================================
echo.
echo Starting desktop client...
echo.

REM Change to the scripts directory where launch_client.py is located
cd /d "%~dp0"
python launch_client.py

echo.
pause
