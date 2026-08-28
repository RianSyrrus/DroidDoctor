@echo off
setlocal enabledelayedexpansion
title DroidDoctor Standalone Build Tool - RianSyrrus
color 0B

echo ================================================================================
echo           DROIDDOCTOR v1.1.1 PRO - STANDALONE COMPILER (PYINSTALLER)
echo                           Developer: RianSyrrus
echo ================================================================================
echo.

cd /d "%~dp0"

echo [1/4] Checking Python Environment...
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] Python not found in system PATH. Please ensure Python 3.10+ is installed.
    pause
    exit /b 1
)

echo [2/4] Installing Required Build Dependencies...
python -m pip install --upgrade pip
python -m pip install pyinstaller customtkinter pillow

echo.
echo [3/4] Compiling DroidDoctor into Standalone Application...
if exist "build" rd /s /q "build"
if exist "dist\DroidDoctor" rd /s /q "dist\DroidDoctor"

python -m PyInstaller ^
    --name="DroidDoctor" ^
    --icon="assets\app_icon.ico" ^
    --noconsole ^
    --onedir ^
    --clean ^
    --collect-all customtkinter ^
    --add-data "bin;bin" ^
    --add-data "assets;assets" ^
    --add-data "data;data" ^
    --add-data "config.json;." ^
    main.py

if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Compilation failed. Please inspect the error log above.
    pause
    exit /b 1
)

echo.
echo [4/4] Finalizing Portable Distribution Folder...
xcopy /E /I /Y "bin" "dist\DroidDoctor\bin" >nul 2>&1
xcopy /E /I /Y "data" "dist\DroidDoctor\data" >nul 2>&1
copy /Y "LICENSE" "dist\DroidDoctor\LICENSE" >nul 2>&1
copy /Y "README.md" "dist\DroidDoctor\README.md" >nul 2>&1
copy /Y "README_ID.md" "dist\DroidDoctor\README_ID.md" >nul 2>&1

echo.
echo ================================================================================
echo [SUCCESS] DroidDoctor Standalone Portable Build Completed!
echo Application Folder: dist\DroidDoctor\DroidDoctor.exe
echo ================================================================================
echo.
echo To build the Setup Installer (DroidDoctor-Setup-v1.1.1.exe):
echo Open installer.iss in Inno Setup and click 'Compile'.
echo.
pause
