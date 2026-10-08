@echo off
setlocal
cd /d "%~dp0"
set PYTHONIOENCODING=utf-8
if exist ".venv\Scripts\python.exe" (
    ".venv\Scripts\python.exe" -m app.local_launcher --port 8001
) else (
    python -m app.local_launcher --port 8001
)
if errorlevel 1 pause