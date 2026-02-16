@echo off
title VoxFlow - Building .exe + Installer (AI Evolution Polska)
echo.
echo  ╔═══════════════════════════════════════════════════╗
echo  ║  🔨 Building VoxFlow .exe + Installer             ║
echo  ║     by AI Evolution Polska                        ║
echo  ╚═══════════════════════════════════════════════════╝
echo.

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Install PyInstaller if needed
pip install pyinstaller --quiet --disable-pip-version-check 2>nul

echo.
echo ═══════════════════════════════════════════
echo  STEP 1: Building VoxFlow .exe
echo ═══════════════════════════════════════════
echo.

pyinstaller ^
    --name "VoxFlow" ^
    --icon "assets\voxflow.ico" ^
    --onedir ^
    --windowed ^
    --noconfirm ^
    --clean ^
    --add-data "voxflow;voxflow" ^
    --add-data "assets;assets" ^
    --hidden-import "faster_whisper" ^
    --hidden-import "ctranslate2" ^
    --hidden-import "huggingface_hub" ^
    --hidden-import "tokenizers" ^
    --hidden-import "sounddevice" ^
    --hidden-import "customtkinter" ^
    --hidden-import "pystray" ^
    --hidden-import "keyboard" ^
    --hidden-import "pyperclip" ^
    --hidden-import "_sounddevice_data" ^
    --hidden-import "scipy" ^
    --collect-all "customtkinter" ^
    --collect-all "faster_whisper" ^
    --collect-all "ctranslate2" ^
    voxflow/main.py

if %errorlevel% neq 0 (
    echo.
    echo  ❌ PyInstaller build failed!
    deactivate
    pause
    exit /b 1
)

echo.
echo  ✅ .exe built successfully at: dist\VoxFlow\VoxFlow.exe
echo.

echo ═══════════════════════════════════════════
echo  STEP 2: Creating Installer (optional)
echo ═══════════════════════════════════════════
echo.

REM Check if Inno Setup is installed
if exist "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" (
    echo  📦 Inno Setup found! Building installer...
    "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" installer.iss
    if %errorlevel% equ 0 (
        echo.
        echo  ✅ Installer created at: installer_output\VoxFlow_Setup_v1.0.0.exe
    ) else (
        echo  ⚠️ Installer build failed. You can still use the portable .exe.
    )
) else (
    echo  ℹ️ Inno Setup not found. Skipping installer creation.
    echo     Install from: https://jrsoftware.org/isinfo.php
    echo     Then re-run this script to create an installer.
    echo.
    echo  💡 You can still use the portable .exe at: dist\VoxFlow\VoxFlow.exe
)

echo.
echo ══════════════════════════════════════
echo  📂 Output files:
echo    dist\VoxFlow\VoxFlow.exe  (portable)
if exist "installer_output\VoxFlow_Setup_v1.0.0.exe" echo    installer_output\VoxFlow_Setup_v1.0.0.exe  (installer)
echo ══════════════════════════════════════
echo.

deactivate
pause
