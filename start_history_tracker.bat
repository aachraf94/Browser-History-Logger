@echo off
REM Browser History Logger - Startup Script
REM Monitors browser history every 5 minutes
REM No proxy required - No internet speed impact

REM Change to script directory
cd /d "%~dp0"

echo ================================================================================
echo Browser History Logger - Non-Intrusive Monitoring
echo ================================================================================
echo.
echo Starting browser history monitoring...
echo - Monitors: Chrome, Edge, Brave, Firefox
echo - Check interval: Every 5 minutes
echo - No proxy required
echo - No internet speed impact
echo.
echo Press Ctrl+C to stop monitoring
echo ================================================================================
echo.

REM Check if virtual environment exists
if exist "..\venv\Scripts\activate.bat" (
    echo Using virtual environment
    call ..\venv\Scripts\activate.bat
    python browser_history_logger.py
) else if exist "venv\Scripts\activate.bat" (
    echo Using virtual environment
    call venv\Scripts\activate.bat
    python browser_history_logger.py
) else (
    echo Using system Python
    python browser_history_logger.py
)

pause
