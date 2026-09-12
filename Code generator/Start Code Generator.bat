@echo off
setlocal

rem Always run from this file's folder, including when launched by a shortcut.
cd /d "%~dp0"

set "PYTHON=%CD%\.venv\Scripts\python.exe"
if not exist "%PYTHON%" (
    echo The project's virtual environment was not found:
    echo %PYTHON%
    echo.
    echo Create it with: python -m venv .venv
    pause
    exit /b 1
)

"%PYTHON%" --version >nul 2>&1
if errorlevel 1 (
    echo The project's virtual environment cannot start Python.
    echo Recreate .venv with an installed Python version, then install requirements.txt.
    pause
    exit /b 1
)

rem Open the local site in the default browser, then keep Flask running here.
start "" "http://127.0.0.1:5000"
"%PYTHON%" app.py

endlocal
