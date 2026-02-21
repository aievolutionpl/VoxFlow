@echo off
chcp 65001 >nul
cd /d "%~dp0"
title VoxFlow — Instalacja (AI Evolution Polska)
echo.
echo  ╔══════════════════════════════════════════════════════╗
echo  ║        VoxFlow — Instalacja jednym kliknięciem       ║
echo  ║           by AI Evolution Polska  ^|  Open Source    ║
echo  ╚══════════════════════════════════════════════════════╝
echo.

REM ─── Check Python ───────────────────────────────────────────────
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo  ❌ Python nie jest zainstalowany!
    echo.
    echo  Pobierz Python 3.10+ ze strony:
    echo     https://www.python.org/downloads/
    echo.
    echo  WAŻNE: Podczas instalacji zaznacz opcję "Add Python to PATH"
    echo.
    pause
    start https://www.python.org/downloads/
    exit /b 1
)

for /f "tokens=2" %%v in ('python --version 2^>^&1') do set PY_VERSION=%%v
echo  ✅ Python %PY_VERSION% znaleziony

REM ─── Check Python version (need 3.9+) ───────────────────────────
for /f "tokens=1,2 delims=." %%a in ("%PY_VERSION%") do (
    set PY_MAJOR=%%a
    set PY_MINOR=%%b
)
if %PY_MAJOR% LSS 3 (
    echo  ❌ Wymagany Python 3.9+, znaleziono %PY_VERSION%
    pause
    exit /b 1
)
if %PY_MAJOR%==3 if %PY_MINOR% LSS 9 (
    echo  ❌ Wymagany Python 3.9+, znaleziono %PY_VERSION%
    pause
    exit /b 1
)

echo.
echo ═══════════════════════════════════════════════════════
echo  KROK 1: Tworzenie środowiska wirtualnego (venv)...
echo ═══════════════════════════════════════════════════════
echo.

if exist venv (
    echo  ℹ️ Środowisko venv już istnieje — pomijam tworzenie.
) else (
    python -m venv venv
    if %errorlevel% neq 0 (
        echo  ❌ Nie udało się stworzyć venv!
        pause
        exit /b 1
    )
    echo  ✅ Środowisko venv stworzone.
)

echo.
echo ═══════════════════════════════════════════════════════
echo  KROK 2: Instalacja wymaganych pakietów...
echo ═══════════════════════════════════════════════════════
echo.

call venv\Scripts\activate.bat

pip install --upgrade pip --quiet --disable-pip-version-check
pip install -r requirements.txt --quiet --disable-pip-version-check

if %errorlevel% neq 0 (
    echo.
    echo  ❌ Instalacja pakietów nie powiodła się!
    echo.
    echo  Spróbuj ręcznie uruchomić:
    echo     venv\Scripts\activate
    echo     pip install -r requirements.txt
    echo.
    pause
    exit /b 1
)

echo  ✅ Wszystkie pakiety zainstalowane!

echo.
echo ═══════════════════════════════════════════════════════
echo  KROK 3: Weryfikacja instalacji...
echo ═══════════════════════════════════════════════════════
echo.

python -m voxflow.main --test

if %errorlevel% neq 0 (
    echo.
    echo  ⚠️ Weryfikacja nie powiodła się. Sprawdź komunikaty błędów powyżej.
    echo.
    pause
    exit /b 1
)

echo.
echo ═══════════════════════════════════════════════════════
echo  ✅ VoxFlow zainstalowany pomyślnie!

REM ─── Stwórz START_VOXFLOW.bat ──────────────────────────────
echo @echo off > START_VOXFLOW.bat
echo chcp 65001 ^>nul >> START_VOXFLOW.bat
echo cd /d "%%~dp0" >> START_VOXFLOW.bat
echo call venv\Scripts\activate.bat >> START_VOXFLOW.bat
echo start "" venv\Scripts\pythonw.exe -m voxflow.main >> START_VOXFLOW.bat

echo.
echo ═══════════════════════════════════════════════════════
echo  ✅ Instalacja zakończona!
echo.
echo  Uruchom aplikację:
echo    👉 Kliknij dwukrotnie START_VOXFLOW.bat
echo.
echo  Lub ręcznie:
echo    venv\Scripts\activate
echo    python -m voxflow.main
echo ═══════════════════════════════════════════════════════
echo.

set /p LAUNCH="Czy uruchomić VoxFlow teraz? [T/n]: "
if /i "%LAUNCH%"=="n" goto :end

echo.
echo  🚀 Uruchamianie VoxFlow...
start "" venv\Scripts\pythonw.exe -m voxflow.main
:end
deactivate
echo.
pause
