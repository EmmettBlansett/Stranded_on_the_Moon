@echo off
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python is not installed. Please install Python and try again.
    pause
    exit /b
)

if not exist .venv (
    echo Creating virtual environment...
    python -m venv .venv
)

call .venv\Scripts\activate


echo Installing dependencies...
pip install -r requirements.txt
echo Requirements installed.

echo Setup is complete! Use run.bat to start the game.
pause