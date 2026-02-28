@echo off
cd /d "%~dp0"
call venv\Scripts\activate.bat
start "" pythonw -m voxflow.main
if errorlevel 1 start "" python -m voxflow.main
