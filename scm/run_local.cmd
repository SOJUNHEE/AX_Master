@echo off
setlocal
cd /d "%~dp0"

echo [Flow SCM] Local server start

if not exist ".venv\Scripts\python.exe" (
    echo [1/3] Creating virtual environment...
    py -m venv .venv
    if errorlevel 1 goto :error
) else (
    echo [1/3] Existing virtual environment found.
)

echo [2/3] Checking required packages...
".venv\Scripts\python.exe" -c "import flask, requests" >nul 2>&1
if errorlevel 1 (
    echo Installing packages from requirements.txt...
    ".venv\Scripts\python.exe" -m pip install -r requirements.txt
    if errorlevel 1 goto :error
) else (
    echo Required packages are already installed.
)

echo [3/3] Starting http://127.0.0.1:5000
start "" http://127.0.0.1:5000
".venv\Scripts\python.exe" app.py
goto :eof

:error
echo.
echo Failed to start Flow SCM. Check the error message above.
pause
exit /b 1
