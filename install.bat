@echo off
chcp 65001 >nul 2>&1
cd /d "%~dp0"
title VoxFlow - Instalacja

echo.
echo ============================================================
echo   VoxFlow - Instalacja jednym kliknieciem
echo   by AI Evolution Polska  ^|  Open Source
echo ============================================================
echo.

REM --- Sprawdz Python ---
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [BLAD] Python nie jest zainstalowany!
    echo.
    echo Pobierz Python 3.10+ ze strony:
    echo   https://www.python.org/downloads/
    echo.
    echo WAZNE: podczas instalacji zaznacz opcje "Add Python to PATH"
    echo.
    pause
    start https://www.python.org/downloads/
    exit /b 1
)

for /f "tokens=2" %%v in ('python --version 2^>^&1') do set PY_VERSION=%%v
echo [OK] Python %PY_VERSION% znaleziony

REM --- Sprawdz wersje (wymagany 3.9+) ---
for /f "tokens=1,2 delims=." %%a in ("%PY_VERSION%") do (
    set PY_MAJOR=%%a
    set PY_MINOR=%%b
)
if %PY_MAJOR% LSS 3 (
    echo [BLAD] Wymagany Python 3.9+, znaleziono %PY_VERSION%
    pause
    exit /b 1
)
if %PY_MAJOR%==3 if %PY_MINOR% LSS 9 (
    echo [BLAD] Wymagany Python 3.9+, znaleziono %PY_VERSION%
    pause
    exit /b 1
)

echo.
echo ------------------------------------------------------------
echo  KROK 1: Tworzenie srodowiska wirtualnego (venv)...
echo ------------------------------------------------------------
echo.

if exist venv (
    echo [INFO] Srodowisko venv juz istnieje - pomijam tworzenie.
) else (
    python -m venv venv
    if %errorlevel% neq 0 (
        echo [BLAD] Nie udalo sie stworzyc venv!
        pause
        exit /b 1
    )
    echo [OK] Srodowisko venv stworzone.
)

echo.
echo ------------------------------------------------------------
echo  KROK 2: Instalacja wymaganych pakietow...
echo  (to moze zajac 2-5 minut - prosze czekac)
echo ------------------------------------------------------------
echo.

call venv\Scripts\activate.bat

venv\Scripts\python.exe -m pip install --upgrade pip --quiet --disable-pip-version-check
venv\Scripts\python.exe -m pip install -r requirements.txt --disable-pip-version-check

if %errorlevel% neq 0 (
    echo.
    echo [BLAD] Instalacja pakietow nie powiodla sie!
    echo.
    echo Sprobuj recznie:
    echo   venv\Scripts\activate
    echo   pip install -r requirements.txt
    echo.
    pause
    exit /b 1
)

echo [OK] Wszystkie pakiety zainstalowane!

echo.
echo ------------------------------------------------------------
echo  KROK 3: Weryfikacja instalacji...
echo ------------------------------------------------------------
echo.

python -m voxflow.main --test

if %errorlevel% neq 0 (
    echo.
    echo [UWAGA] Weryfikacja nie powiodla sie. Sprawdz komunikaty powyzej.
    echo.
    pause
    exit /b 1
)

echo.
echo ------------------------------------------------------------
echo  KROK 4: Tworzenie pliku startowego START_VOXFLOW.bat...
echo ------------------------------------------------------------

(
echo @echo off
echo cd /d "%%~dp0"
echo call venv\Scripts\activate.bat
echo start "" pythonw -m voxflow.main
echo if errorlevel 1 start "" python -m voxflow.main
) > START_VOXFLOW.bat

echo [OK] Plik START_VOXFLOW.bat stworzony!

echo.
echo ============================================================
echo   [OK] VoxFlow zainstalowany pomyslnie!
echo.
echo   Uruchom aplikacje:
echo     --^> Kliknij dwukrotnie START_VOXFLOW.bat
echo ============================================================
echo.

set /p LAUNCH=Czy uruchomic VoxFlow teraz? [T/n]: 
if /i "%LAUNCH%"=="n" goto :end

echo.
echo Uruchamianie VoxFlow...
start "" pythonw -m voxflow.main
if errorlevel 1 start "" python -m voxflow.main

:end
deactivate 2>nul
echo.
pause
