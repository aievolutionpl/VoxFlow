@echo off
cd /d "%~dp0"
title VoxFlow - Tworzenie wersji Portable

echo.
echo ============================================================
echo   VoxFlow - Tworzenie wersji Portable
echo   by AI Evolution Polska
echo ============================================================
echo.

set VER=1.1.0
set PORTABLE_DIR=dist\VoxFlow_Portable_v%VER%
set PORTABLE_APP=%PORTABLE_DIR%\VoxFlow

REM --- Sprawdz venv ---
if not exist "venv\Scripts\activate.bat" (
    echo [BLAD] Nie znaleziono srodowiska venv.
    echo        Uruchom najpierw install.bat
    echo.
    pause & exit /b 1
)
call venv\Scripts\activate.bat

REM --- Krok 1: Zbuduj EXE jesli nie istnieje ---
echo [1/4] Sprawdzam czy VoxFlow.exe jest zbudowany...
if exist "dist\VoxFlow\VoxFlow.exe" (
    echo [OK] VoxFlow.exe juz istnieje - pomijam build
) else (
    echo Budowanie VoxFlow.exe przez PyInstaller...
    echo (To moze potrwac 3-6 minut)
    pip install pyinstaller --quiet --disable-pip-version-check
    pyinstaller VoxFlow.spec --noconfirm --clean
    if %errorlevel% neq 0 (
        echo [BLAD] Build nie powiodl sie!
        pause & exit /b 1
    )
    if not exist "dist\VoxFlow\VoxFlow.exe" (
        echo [BLAD] Nie znaleziono dist\VoxFlow\VoxFlow.exe
        pause & exit /b 1
    )
    echo [OK] VoxFlow.exe zbudowany
)

REM --- Krok 2: Wyczysc stary portable folder ---
echo.
echo [2/4] Przygotowanie katalogu portable...
if exist "%PORTABLE_DIR%" (
    echo Usuwam stary folder %PORTABLE_DIR%...
    rmdir /s /q "%PORTABLE_DIR%"
)
mkdir "%PORTABLE_DIR%"

REM --- Krok 3: Kopiuj pliki ---
echo.
echo [3/4] Kopiowanie plikow VoxFlow...
xcopy "dist\VoxFlow\*" "%PORTABLE_APP%\" /E /I /Q
if %errorlevel% neq 0 (
    echo [BLAD] Blad kopiowania plikow!
    pause & exit /b 1
)

REM --- Stworz launcher START_VOXFLOW.bat ---
(
echo @echo off
echo cd /d "%%~dp0VoxFlow"
echo start "" "VoxFlow.exe"
) > "%PORTABLE_DIR%\START_VOXFLOW.bat"

REM --- Stworz README_PORTABLE.txt ---
(
echo VoxFlow %VER% - Wersja Portable
echo ================================
echo.
echo JAK URUCHOMIC:
echo   Kliknij dwukrotnie START_VOXFLOW.bat
echo   (lub uruchom VoxFlow\VoxFlow.exe bezposrednio)
echo.
echo JAK DZIALA:
echo   - Przytrzymaj F2 i mow - pojawi sie animacja nagrywania na dole ekranu
echo   - Zwolnij F2 - tekst zostanie wklejony w aktywnym oknie
echo   - Kliknij przycisk klawisza w UI aby zmienic skrot klawiszowy
echo   - Ikona w zasobniku - kliknij prawym przyciskiem dla opcji
echo.
echo WYMAGANIA:
echo   - Windows 10/11 (64-bit)
echo   - Mikrofon
echo   - Internet TYLKO przy pierwszym uruchomieniu
echo     (pobranie modelu AI ~500 MB)
echo.
echo WAZNE:
echo   - NIE przenosic samego VoxFlow.exe bez calego folderu VoxFlow\
echo   - Caly folder VoxFlow_Portable_v%VER% mozna przeniesc gdzie chcesz
echo   - Ustawienia zapisywane w: %%APPDATA%%\VoxFlow\
echo.
echo by AI Evolution Polska - https://github.com/aievolutionpl/VoxFlow
) > "%PORTABLE_DIR%\README_PORTABLE.txt"

echo.
echo [4/4] Gotowe!
echo.

REM --- Zapytaj czy zipowac ---
set /p DOZIP=Czy spakowac do ZIP? [T/n]: 
if /i "%DOZIP%"=="n" goto :done

echo.
echo Pakuje do ZIP...
powershell -Command "Compress-Archive -Path '%PORTABLE_DIR%' -DestinationPath 'dist\VoxFlow_Portable_v%VER%.zip' -Force"

if %errorlevel% equ 0 (
    echo [OK] ZIP stworzony: dist\VoxFlow_Portable_v%VER%.zip
) else (
    echo [UWAGA] Nie udalo sie stworzyc ZIP. Folder istnieje: %PORTABLE_DIR%
)

:done
echo.
echo ============================================================
echo   [OK] Wersja Portable gotowa!
echo.
echo   Folder:  %PORTABLE_DIR%
echo   Launcher: START_VOXFLOW.bat
echo ============================================================
echo.

start "" explorer "%PORTABLE_DIR%"
pause
