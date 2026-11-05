@echo off
setlocal

cd /d "%~dp0"

if not exist logs mkdir logs

if exist .venv\Scripts\activate.bat (
    call .venv\Scripts\activate.bat
)

if exist requirements.txt (
    python -m pip install -r requirements.txt
)

python src\main_v2.py

endlocal