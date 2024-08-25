@echo off
if not exist .venv (
    echo The virtual environment has not been set up.
    echo Please run setup.bat first to create the environment and install dependencies.
    pause
    exit /b
)

call .venv\Scripts\activate

echo Starting the game...
python src\game.py

echo Done!
pause