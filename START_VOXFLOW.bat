@echo off
cd /d "%~dp0"
if exist "venv\Scripts\pythonw.exe" (
    start "" "venv\Scripts\pythonw.exe" -m voxflow.main
) else (
    start "" pythonw -m voxflow.main
)
