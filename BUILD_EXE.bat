@echo off
chcp 65001 >nul
cd /d "%~dp0"
title VoxFlow — Build Installer

echo.
echo  ╔══════════════════════════════════════════════════════════╗
echo  ║         VoxFlow — Build Setup.exe Installer              ║
echo  ║              by AI Evolution Polska                      ║
echo  ╚══════════════════════════════════════════════════════════╝
echo.

REM ─── Step 0: Check venv ─────────────────────────────────────────
if not exist "venv\Scripts\activate.bat" (
    echo  ❌ Środowisko venv nie istnieje. Uruchom najpierw install.bat
    pause & exit /b 1
)
call venv\Scripts\activate.bat

REM ─── Step 1: Install/update build tools ─────────────────────────
echo  [1/4]  Instalowanie narzędzi build...
pip install pyinstaller --quiet --disable-pip-version-check
if %errorlevel% neq 0 (
    echo  ❌ Błąd instalacji PyInstaller!
    pause & exit /b 1
)
echo  ✅ PyInstaller gotowy

REM ─── Step 2: Clean previous build ───────────────────────────────
echo.
echo  [2/4]  Czyszczenie poprzedniego buildu...
if exist "dist\VoxFlow" rmdir /s /q "dist\VoxFlow"
if exist "build"         rmdir /s /q "build"
echo  ✅ Wyczyszczono

REM ─── Step 3: Build EXE with PyInstaller ─────────────────────────
echo.
echo  [3/4]  Budowanie VoxFlow.exe przez PyInstaller...
echo         (To może potrwać 2-5 minut — proszę czekać)
echo.

pyinstaller VoxFlow.spec --noconfirm --clean

if %errorlevel% neq 0 (
    echo.
    echo  ❌ PyInstaller zakończył się błędem!
    echo     Sprawdź logi powyżej.
    pause & exit /b 1
)
if not exist "dist\VoxFlow\VoxFlow.exe" (
    echo  ❌ Nie znaleziono dist\VoxFlow\VoxFlow.exe!
    pause & exit /b 1
)

echo.
echo  ✅ VoxFlow.exe zbudowany pomyślnie

REM ─── Step 4: Build Installer with Inno Setup ────────────────────
echo.
echo  [4/4]  Tworzenie instalatora VoxFlow_Setup.exe...
echo.

REM Possible Inno Setup locations
set ISCC=""
if exist "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" (
    set ISCC="C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
)
if exist "C:\Program Files\Inno Setup 6\ISCC.exe" (
    set ISCC="C:\Program Files\Inno Setup 6\ISCC.exe"
)

if %ISCC%=="" (
    echo  ⚠️  Inno Setup nie jest zainstalowany!
    echo.
    echo  Pobierz Inno Setup 6 ze strony:
    echo     https://jrsoftware.org/isinfo.php
    echo.
    echo  Następnie uruchom ten skrypt ponownie, aby stworzyć
    echo  plik instalacyjny VoxFlow_Setup.exe
    echo.
    echo  Gotowy EXE znajduje się w: dist\VoxFlow\VoxFlow.exe
    pause
    start "" explorer "dist\VoxFlow"
    exit /b 0
)

if not exist "installer_output" mkdir installer_output

%ISCC% installer.iss /Q

if %errorlevel% neq 0 (
    echo.
    echo  ❌ Inno Setup zakończył się błędem!
    echo     Sprawdź plik installer.iss
    pause & exit /b 1
)

echo.
echo  ╔══════════════════════════════════════════════════════════╗
echo  ║                                                          ║
echo  ║   ✅  GOTOWE!  VoxFlow_Setup.exe zbudowany pomyślnie   ║
echo  ║                                                          ║
echo  ║   Lokalizacja:  installer_output\VoxFlow_Setup_v*.exe   ║
echo  ║                                                          ║
echo  ╚══════════════════════════════════════════════════════════╝
echo.

start "" explorer "installer_output"
pause
