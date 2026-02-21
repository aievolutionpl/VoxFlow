@echo off
cd /d "%~dp0"
title VoxFlow - Build Setup.exe Installer

echo.
echo ============================================================
echo   VoxFlow - Build Setup.exe Installer
echo   by AI Evolution Polska
echo ============================================================
echo.

REM --- Sprawdz venv ---
if not exist "venv\Scripts\activate.bat" (
    echo [BLAD] Srodowisko venv nie istnieje. Uruchom najpierw install.bat
    pause & exit /b 1
)
call venv\Scripts\activate.bat

REM --- Krok 1: Narzedzia build ---
echo [1/4] Instalowanie PyInstaller...
pip install pyinstaller --quiet --disable-pip-version-check
if %errorlevel% neq 0 (
    echo [BLAD] Instalacja PyInstaller nie powiodla sie!
    pause & exit /b 1
)
echo [OK] PyInstaller gotowy

REM --- Krok 2: Czyszczenie ---
echo.
echo [2/4] Czyszczenie poprzedniego buildu...
if exist "dist\VoxFlow" rmdir /s /q "dist\VoxFlow"
if exist "build"         rmdir /s /q "build"
echo [OK] Wyczyszczono

REM --- Krok 3: Build EXE ---
echo.
echo [3/4] Budowanie VoxFlow.exe przez PyInstaller...
echo       (To moze potrwac 3-6 minut - prosze czekac)
echo.

pyinstaller VoxFlow.spec --noconfirm --clean

if %errorlevel% neq 0 (
    echo.
    echo [BLAD] PyInstaller zakonczyl sie bledem!
    pause & exit /b 1
)
if not exist "dist\VoxFlow\VoxFlow.exe" (
    echo [BLAD] Nie znaleziono dist\VoxFlow\VoxFlow.exe!
    pause & exit /b 1
)

echo.
echo [OK] VoxFlow.exe zbudowany pomyslnie

REM --- Krok 4: Inno Setup ---
echo.
echo [4/4] Tworzenie instalatora VoxFlow_Setup.exe...
echo.

set ISCC=""
if exist "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" (
    set ISCC="C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
)
if exist "C:\Program Files\Inno Setup 6\ISCC.exe" (
    set ISCC="C:\Program Files\Inno Setup 6\ISCC.exe"
)

if %ISCC%=="" (
    echo [UWAGA] Inno Setup nie jest zainstalowany!
    echo.
    echo Pobierz Inno Setup 6 ze strony:
    echo   https://jrsoftware.org/isinfo.php
    echo.
    echo Gotowy EXE znajduje sie w: dist\VoxFlow\VoxFlow.exe
    pause
    start "" explorer "dist\VoxFlow"
    exit /b 0
)

if not exist "installer_output" mkdir installer_output
%ISCC% installer.iss /Q

if %errorlevel% neq 0 (
    echo [BLAD] Inno Setup zakonczyl sie bledem!
    pause & exit /b 1
)

echo.
echo ============================================================
echo   [OK] GOTOWE! VoxFlow_Setup.exe zbudowany pomyslnie
echo   Lokalizacja: installer_output\VoxFlow_Setup_v*.exe
echo ============================================================
echo.

start "" explorer "installer_output"
pause
