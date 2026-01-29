@echo off
REM Automatically activate virtual environment and run the app
cd /d "%~dp0"
call .venv\Scripts\activate.bat
python app.py
pause
