@echo off
REM GR Cup Dashboard Automation Script
REM This script automates the complete dashboard update process

echo ========================================
echo GR Cup Dashboard Automation
echo ========================================
echo.

REM Set working directory
cd /d "%~dp0\.."

echo [1/4] Processing new telemetry data...
python scripts/process_real_data.py
if errorlevel 1 (
    echo ERROR: Data processing failed
    pause
    exit /b 1
)

echo.
echo [2/4] Generating dashboard data...
python scripts/dashboard_automation.py
if errorlevel 1 (
    echo ERROR: Dashboard generation failed
    pause
    exit /b 1
)

echo.
echo [3/4] Creating version backup...
python dashboard/version_manager.py create auto_%date:~-4,4%%date:~-10,2%%date:~-7,2%_%time:~0,2%%time:~3,2%%time:~6,2% "Automated update"

echo.
echo [4/4] Deploying to S3...
python dashboard/version_manager.py deploy
if errorlevel 1 (
    echo ERROR: S3 deployment failed
    pause
    exit /b 1
)

echo.
echo ========================================
echo Dashboard automation completed successfully!
echo ========================================
echo.
echo Dashboard URL: https://gr-cup-data-dev-us-east-1-v2.s3.amazonaws.com/dashboard/track_dashboard.html
echo.

REM Optional: Open dashboard in browser
REM start https://gr-cup-data-dev-us-east-1-v2.s3.amazonaws.com/dashboard/track_dashboard.html

pause
