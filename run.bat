@echo off
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python is not installed. Please install Python to run this game.
    pause
    exit /b
)

if not exist venv (
    echo Creating virtual environment...
    python -m venv .venv
)

call .venv\Scripts\activate

python -c "import pygame" >nul 2>&1
if %errorlevel% neq 0 (
    echo Installing dependencies for the first time...
    pip install -r requirements.txt
    echo Requirements installed.
    echo done
) else (
    echo Dependencies are already installed.
)

echo Starting the game...
python src\game.py

echo Done!
exit
