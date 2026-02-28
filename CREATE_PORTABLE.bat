@echo off
chcp 65001 >nul 2>&1
cd /d "%~dp0"
title VoxFlow - Tworzenie wersji Portable

echo.
echo ============================================================
echo   VoxFlow - Tworzenie wersji Portable (venv-based)
echo   by AI Evolution Polska
echo ============================================================
echo.

set VER=1.2.0
set PORTABLE_DIR=portable\VoxFlow_Portable_v%VER%

REM --- Sprawdz venv ---
if not exist "venv\Scripts\activate.bat" (
    echo [BLAD] Nie znaleziono srodowiska venv.
    echo        Uruchom najpierw install.bat
    echo.
    pause & exit /b 1
)

REM ==============================================================
REM  KROK 1: Przygotuj katalog portable
REM ==============================================================
echo [1/5] Przygotowanie katalogu portable...
if exist "%PORTABLE_DIR%" (
    echo        Usuwam stary folder %PORTABLE_DIR%...
    rmdir /s /q "%PORTABLE_DIR%"
)
mkdir "%PORTABLE_DIR%"
mkdir "%PORTABLE_DIR%\assets"

REM ==============================================================
REM  KROK 2: Skopiuj zrodla VoxFlow
REM ==============================================================
echo [2/5] Kopiowanie zrodel VoxFlow...
xcopy "voxflow\*" "%PORTABLE_DIR%\voxflow\" /E /I /Q /Y
if %errorlevel% neq 0 (
    echo [BLAD] Blad kopiowania zrodel!
    pause & exit /b 1
)

REM --- Skopiuj ikone i zasoby ---
if exist "assets\voxflow.ico"     copy /Y "assets\voxflow.ico"     "%PORTABLE_DIR%\assets\" >nul
if exist "assets\voxflow_256.png" copy /Y "assets\voxflow_256.png" "%PORTABLE_DIR%\assets\" >nul
if exist "requirements.txt"       copy /Y "requirements.txt"       "%PORTABLE_DIR%\"        >nul

echo [OK] Zrodla skopiowane

REM ==============================================================
REM  KROK 3: Skopiuj i zregeneruj srodowisko venv (site-packages)
REM ==============================================================
echo.
echo [3/5] Kopiowanie srodowiska Python (venv)...
echo       (to moze chwile potrwac)
xcopy "venv\*" "%PORTABLE_DIR%\venv\" /E /I /Q /Y
if %errorlevel% neq 0 (
    echo [BLAD] Blad kopiowania venv!
    pause & exit /b 1
)
echo [OK] venv skopiowany

REM ==============================================================
REM  KROK 4: Stworz launcher START_VOXFLOW.bat w katalogu portable
REM ==============================================================
echo.
echo [4/5] Tworzenie launchera i skrotu na pulpicie...

(
echo @echo off
echo chcp 65001 ^>nul 2^>^&1
echo cd /d "%%~dp0"
echo call venv\Scripts\activate.bat
echo start "" pythonw -m voxflow.main
echo if errorlevel 1 start "" python -m voxflow.main
) > "%PORTABLE_DIR%\START_VOXFLOW.bat"

REM --- Skrot na pulpicie wskazujacy na launcher portable ---
call venv\Scripts\activate.bat
set PORTABLE_ABS=%~dp0%PORTABLE_DIR%
venv\Scripts\python.exe -c "import sys; sys.path.insert(0,'%~dp0'); from voxflow.create_shortcut import create_desktop_shortcut_for_bat; create_desktop_shortcut_for_bat(r'%PORTABLE_ABS%')"
if %errorlevel% equ 0 (
    echo [OK] Skrot VoxFlow Portable pojawil sie na pulpicie!
) else (
    echo [UWAGA] Skrotu nie udalo sie utworzyc automatycznie.
    echo         Mozesz recznie przeniesc START_VOXFLOW.bat na pulpit.
)

REM ==============================================================
REM  KROK 5: Stworz README_PORTABLE.txt
REM ==============================================================
(
echo VoxFlow v%VER% - Wersja Portable
echo =================================
echo.
echo JAK URUCHOMIC:
echo   1. Kliknij skrot "VoxFlow" na Pulpicie
echo   lub
echo   2. Kliknij dwukrotnie START_VOXFLOW.bat w tym folderze
echo.  
echo CO NOWEGO:
echo   - Jezyki: Polski + Angielski + Niemiecki + Francuski + inne
echo   - Tlumaczenie glosu -^> Angielski (100%% offline)
echo   - Skrot na Pulpicie tworzony automatycznie
echo.
echo JAK DZIALA:
echo   - Przytrzymaj F2 i mow ^(pojawi sie animacja fal^)
echo   - Zwolnij F2 ^- tekst zostanie wklejony w aktywnym oknie
echo   - Kliknij przycisk klawisza w UI aby zmienic skrot
echo   - Ustawienia: przelacznik Tlumaczenie w panelu Ustawien
echo.
echo WYMAGANIA:
echo   - Windows 10/11 (64-bit)
echo   - Mikrofon
echo   - Internet TYLKO przy pierwszym uruchomieniu
echo     ^(pobranie modelu AI ~500 MB, zapisywany w APPDATA\VoxFlow\^)
echo.
echo WAZNE:
echo   - NIE przenosic samego folderu voxflow\ bez reszty
echo   - Caly folder VoxFlow_Portable_v%VER%\ mozna przeniesc gdzie chcesz
echo   - Ustawienia zapisywane w: %%APPDATA%%\VoxFlow\
echo.
echo by AI Evolution Polska - https://github.com/aievolutionpl/VoxFlow
) > "%PORTABLE_DIR%\README_PORTABLE.txt"

echo.
echo [5/5] Gotowe!
echo.

REM --- Zapytaj czy zipowac ---
set /p DOZIP=Czy spakowac do ZIP? [T/n]: 
if /i "%DOZIP%"=="n" goto :done

echo.
echo Pakuje do ZIP...
powershell -Command "Compress-Archive -Path '%PORTABLE_DIR%' -DestinationPath 'portable\VoxFlow_Portable_v%VER%.zip' -Force"

if %errorlevel% equ 0 (
    echo [OK] ZIP stworzony: portable\VoxFlow_Portable_v%VER%.zip
) else (
    echo [UWAGA] Nie udalo sie stworzyc ZIP. Folder istnieje: %PORTABLE_DIR%
)

:done
echo.
echo ============================================================
echo   [OK] Wersja Portable gotowa!
echo.
echo   Folder:   %PORTABLE_DIR%
echo   Launcher: START_VOXFLOW.bat
echo   Skrot:    Pulpit\VoxFlow.lnk
echo ============================================================
echo.

start "" explorer "%PORTABLE_DIR%"
pause
