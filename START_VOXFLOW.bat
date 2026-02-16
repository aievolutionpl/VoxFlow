@echo off
title VoxFlow - Local Speech-to-Text (AI Evolution Polska)
echo.
echo  ╔═══════════════════════════════════════════╗
echo  ║       🎤 VoxFlow Setup ^& Launch           ║
echo  ║   Local Speech-to-Text  (PL ^& EN)        ║
echo  ║     by AI Evolution Polska                ║
echo  ╚═══════════════════════════════════════════╝
echo.

REM Check if Python is available
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python nie jest zainstalowany!
    echo    Pobierz z: https://python.org
    pause
    exit /b 1
)

REM Check if venv exists, create if not
if not exist "venv" (
    echo 📦 Tworzenie środowiska wirtualnego...
    python -m venv venv
    if %errorlevel% neq 0 (
        echo ❌ Nie udało się stworzyć venv
        pause
        exit /b 1
    )
)

REM Activate venv
call venv\Scripts\activate.bat

REM Install/update dependencies
echo 📦 Sprawdzanie zależności...
pip install -r requirements.txt --quiet --disable-pip-version-check 2>nul

REM Launch VoxFlow
echo.
echo 🚀 Uruchamiam VoxFlow...
echo.
python -m voxflow.main %*

REM Deactivate on exit
deactivate
