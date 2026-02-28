@echo off
REM ============================================================================
REM Automated Backup Script for LAN Dashboard
REM Creates daily backup with timestamp
REM Schedule this to run at 6 PM daily
REM ============================================================================

echo.
echo ===============================================
echo   LAN Dashboard - Automated Backup
echo ===============================================
echo.

REM Configuration - EDIT THESE PATHS
set SOURCE=C:\LAN_Dashboard\data\project_data.xlsx
set BACKUP_DIR=C:\LAN_Dashboard\data\backups
set LOG_FILE=C:\LAN_Dashboard\logs\backup.log

REM Create backup filename with date
set TIMESTAMP=%date:~-4,4%%date:~-10,2%%date:~-7,2%_%time:~0,2%%time:~3,2%%time:~6,2%
set TIMESTAMP=%TIMESTAMP: =0%
set BACKUP_FILE=%BACKUP_DIR%\project_data_%TIMESTAMP%.xlsx

REM Create directories if they don't exist
if not exist "%BACKUP_DIR%" mkdir "%BACKUP_DIR%"
if not exist "C:\LAN_Dashboard\logs" mkdir "C:\LAN_Dashboard\logs"

REM Check if source file exists
if not exist "%SOURCE%" (
    echo [ERROR] Source file not found: %SOURCE%
    echo %date% %time% - [ERROR] Source file not found >> "%LOG_FILE%"
    pause
    exit /b 1
)

REM Create backup
echo Creating backup...
echo Source: %SOURCE%
echo Destination: %BACKUP_FILE%
echo.

copy "%SOURCE%" "%BACKUP_FILE%"

if %ERRORLEVEL% EQU 0 (
    echo [SUCCESS] Backup created successfully!
    echo File: %BACKUP_FILE%
    echo %date% %time% - [SUCCESS] Backup created: %BACKUP_FILE% >> "%LOG_FILE%"
) else (
    echo [ERROR] Backup failed!
    echo %date% %time% - [ERROR] Backup failed >> "%LOG_FILE%"
    pause
    exit /b 1
)

REM Delete backups older than 30 days
echo.
echo Cleaning old backups (older than 30 days)...
forfiles /P "%BACKUP_DIR%" /M *.xlsx /D -30 /C "cmd /c del @path" 2>nul
echo Cleanup complete.

echo.
echo ===============================================
echo   Backup Complete!
echo ===============================================
echo.

REM Wait 3 seconds before closing (if run manually)
timeout /t 3 /nobreak >nul

exit /b 0
