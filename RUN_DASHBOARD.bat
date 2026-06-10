@echo off
REM ECG Dashboard Launcher
REM Runs both predict.py and streamlit dashboard in separate terminals

echo.
echo ========================================
echo   ECG Monitoring Dashboard
echo ========================================
echo.

REM Test Python availability
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found in PATH
    pause
    exit /b 1
)

REM Test required packages
echo Testing dependencies...
python -c "import streamlit, plotly, pandas" 2>nul
if errorlevel 1 (
    echo.
    echo ERROR: Missing dependencies
    echo Run: pip install streamlit plotly pandas
    pause
    exit /b 1
)

echo ✓ All dependencies OK
echo.

REM Start predict.py in new terminal
echo Starting prediction pipeline...
start cmd /k "cd /d %~dp0 && python predict.py"
timeout /t 2 >nul

REM Start streamlit dashboard in new terminal
echo Starting dashboard...
start cmd /k "cd /d %~dp0 && streamlit run dashboard.py --logger.level=off"

echo.
echo ========================================
echo Dashboard launching...
echo - Predictions: terminal 1
echo - Dashboard: terminal 2 (browser tab)
echo - Auto-refresh: every 3 seconds
echo ========================================
echo.
timeout /t 3 >nul
