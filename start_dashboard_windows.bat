@echo off
REM ============================================================================
REM LAN Dashboard Startup Script (Windows)
REM Starts the Streamlit dashboard automatically
REM Place shortcut to this file in Windows Startup folder
REM ============================================================================

echo.
echo ===============================================
echo   Starting LAN Dashboard...
echo ===============================================
echo.

REM Configuration - EDIT THESE PATHS
set DASHBOARD_DIR=C:\LAN_Dashboard
set PYTHON_PATH=python
set APP_FILE=app_enhanced.py
set LOG_FILE=%DASHBOARD_DIR%\logs\startup.log

REM Create logs directory if it doesn't exist
if not exist "%DASHBOARD_DIR%\logs" mkdir "%DASHBOARD_DIR%\logs"

REM Log startup
echo %date% %time% - Starting dashboard >> "%LOG_FILE%"

REM Change to dashboard directory
cd /d "%DASHBOARD_DIR%"

REM Check if directory exists
if not exist "%DASHBOARD_DIR%" (
    echo [ERROR] Dashboard directory not found: %DASHBOARD_DIR%
    echo %date% %time% - [ERROR] Directory not found >> "%LOG_FILE%"
    pause
    exit /b 1
)

REM Check if app file exists
if not exist "%APP_FILE%" (
    echo [ERROR] Application file not found: %APP_FILE%
    echo %date% %time% - [ERROR] App file not found >> "%LOG_FILE%"
    pause
    exit /b 1
)

echo Dashboard directory: %DASHBOARD_DIR%
echo Application file: %APP_FILE%
echo.
echo Starting dashboard...
echo.
echo Once started, the dashboard will open in your browser at:
echo http://localhost:8501
echo.
echo Keep this window open - DO NOT CLOSE!
echo.

REM Start the dashboard
%PYTHON_PATH% -m streamlit run "%APP_FILE%" --server.headless true

REM Log shutdown
echo %date% %time% - Dashboard stopped >> "%LOG_FILE%"

echo.
echo Dashboard has stopped.
pause
