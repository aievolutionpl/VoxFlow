@echo off
chcp 65001 >nul
cd /d "%~dp0"
title VoxFlow — Tworzenie wersji Portable

echo.
echo  ╔══════════════════════════════════════════════════════════╗
echo  ║       VoxFlow — Tworzenie wersji Portable                ║
echo  ║            by AI Evolution Polska                        ║
echo  ╚══════════════════════════════════════════════════════════╝
echo.

REM ─── Ustal wersję ──────────────────────────────────────────────
set VER=1.1.0
set PORTABLE_DIR=dist\VoxFlow_Portable_v%VER%
set PORTABLE_APP=%PORTABLE_DIR%\VoxFlow

REM ─── Krok 0: Sprawdź venv ──────────────────────────────────────
if not exist "venv\Scripts\activate.bat" (
    echo  ❌ Nie znaleziono środowiska venv.
    echo     Uruchom najpierw install.bat
    echo.
    pause & exit /b 1
)
call venv\Scripts\activate.bat

REM ─── Krok 1: Zbuduj EXE jeśli nie istnieje ────────────────────
echo  [1/4]  Sprawdzam czy VoxFlow.exe jest zbudowany...
if exist "dist\VoxFlow\VoxFlow.exe" (
    echo  ✅ VoxFlow.exe już istnieje — pomijam build
) else (
    echo  ⏳ Buduję VoxFlow.exe przez PyInstaller...
    echo     (To może potrwać 3-6 minut)
    pip install pyinstaller --quiet --disable-pip-version-check
    pyinstaller VoxFlow.spec --noconfirm --clean
    if %errorlevel% neq 0 (
        echo  ❌ Build nie powiódł się!
        pause & exit /b 1
    )
    if not exist "dist\VoxFlow\VoxFlow.exe" (
        echo  ❌ Nie znaleziono dist\VoxFlow\VoxFlow.exe
        pause & exit /b 1
    )
    echo  ✅ VoxFlow.exe zbudowany
)

REM ─── Krok 2: Wyczyść stary portable folder ────────────────────
echo.
echo  [2/4]  Przygotowanie katalogu portable...
if exist "%PORTABLE_DIR%" (
    echo  🗑  Usuwam stary folder %PORTABLE_DIR%...
    rmdir /s /q "%PORTABLE_DIR%"
)
mkdir "%PORTABLE_DIR%"

REM ─── Krok 3: Kopiuj pliki ─────────────────────────────────────
echo.
echo  [3/4]  Kopiowanie plików VoxFlow...
xcopy "dist\VoxFlow\*" "%PORTABLE_APP%\" /E /I /Q
if %errorlevel% neq 0 (
    echo  ❌ Błąd kopiowania plików!
    pause & exit /b 1
)

REM ─── Stwórz launcher START_VOXFLOW.bat ────────────────────────
echo @echo off > "%PORTABLE_DIR%\START_VOXFLOW.bat"
echo chcp 65001 ^>nul >> "%PORTABLE_DIR%\START_VOXFLOW.bat"
echo cd /d "%%~dp0VoxFlow" >> "%PORTABLE_DIR%\START_VOXFLOW.bat"
echo start "" "VoxFlow.exe" >> "%PORTABLE_DIR%\START_VOXFLOW.bat"

REM ─── Stwórz README_PORTABLE.txt ───────────────────────────────
(
echo VoxFlow %VER% — Wersja Portable
echo ================================
echo.
echo JAK URUCHOMIĆ:
echo   1. Kliknij dwukrotnie START_VOXFLOW.bat
echo      (lub uruchom VoxFlow\VoxFlow.exe bezpośrednio)
echo.
echo JAK DZIAŁA:
echo   - Przytrzymaj F2 i mów - pojawi sie animacja nagrywania na dole ekranu
echo   - Zwolnij F2 - tekst zostanie wklejony w aktywnym oknie
echo   - Kliknij przycisk klawisza w UI zeby zmienić skrót klawiszowy
echo   - Ikona w zasobniku - kliknij prawym przyciskiem dla opcji
echo.
echo WYMAGANIA:
echo   - Windows 10/11 (64-bit)
echo   - Mikrofon
echo   - Połączenie z internetem (TYLKO przy pierwszym uruchomieniu
echo     - do pobrania modelu AI ~500 MB)
echo.
echo WAŻNE:
echo   - NIE przenoś samego VoxFlow.exe bez całego folderu VoxFlow\
echo   - Możesz przenieść cały folder VoxFlow_Portable_v%VER% gdzie chcesz
echo   - Ustawienia są zapisywane w: %%APPDATA%%\VoxFlow\
echo.
echo by AI Evolution Polska - https://github.com/aievolutionpl/VoxFlow
) > "%PORTABLE_DIR%\README_PORTABLE.txt"

echo.
echo  [4/4]  Gotowe!
echo.

REM ─── Zapytaj czy zipować ──────────────────────────────────────
set /p DOZIP="Czy spakować do ZIP? [T/n]: "
if /i "%DOZIP%"=="n" goto :done

echo.
echo  📦 Pakuję do ZIP...

REM Użyj PowerShell do zipowania
powershell -Command "Compress-Archive -Path '%PORTABLE_DIR%' -DestinationPath 'dist\VoxFlow_Portable_v%VER%.zip' -Force"

if %errorlevel% equ 0 (
    echo  ✅ ZIP stworzony: dist\VoxFlow_Portable_v%VER%.zip
) else (
    echo  ⚠️ Nie udało się stworzyć ZIP. Folder istnieje: %PORTABLE_DIR%
)

:done
echo.
echo  ╔══════════════════════════════════════════════════════════╗
echo  ║                                                          ║
echo  ║   ✅  Wersja Portable gotowa!                           ║
echo  ║                                                          ║
echo  ║   Folder:  %PORTABLE_DIR%           ║
echo  ║   Launcher: START_VOXFLOW.bat                           ║
echo  ║                                                          ║
echo  ╚══════════════════════════════════════════════════════════╝
echo.

start "" explorer "%PORTABLE_DIR%"
pause
