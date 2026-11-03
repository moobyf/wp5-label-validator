@echo off
REM run_local.bat - Run Label Validator locally on Windows

echo ===========================================
echo Label Validator - Local Mode
echo ===========================================

cd /d "%~dp0"

REM Check for virtual environment
if exist "venv\Scripts\activate.bat" (
    echo Using local venv...
    call venv\Scripts\activate.bat
)

REM Check dependencies
python -c "import dash, pandas, PIL, plotly" 2>nul
if errorlevel 1 (
    echo.
    echo Missing dependencies. Installing...
    pip install dash pandas pillow plotly numpy opencv-python
)

set DASH_DISABLE_JUPYTER=1
set PORT=8050

echo.
echo Opening: http://localhost:%PORT%
echo Press Ctrl+C to stop
echo.

REM Open browser
start http://localhost:%PORT%

python index.py --port %PORT% --host 127.0.0.1
