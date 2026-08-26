@echo off
title DroidDoctor Pro - Diagnostic Launcher
cd /d "%~dp0"
cls
color 0B
echo ===============================================================
echo      DROIDDOCTOR - Android Health ^& Diagnostics Suite
echo                     v1.0.0 Pro Edition
echo ===============================================================
echo  [*] Memeriksa Engine Python ^& Dependensi...
echo  [*] Menyiapkan High-DPI ClearType Antarmuka...
echo  [*] Menjalankan DroidDoctor Desktop GUI...
echo ---------------------------------------------------------------
echo  [OK] Aplikasi aktif di layar Anda.
echo  [INFO] Tutup jendela aplikasi DroidDoctor untuk keluar.
echo ===============================================================
echo.

where python >nul 2>&1
if %errorlevel% equ 0 (
    python main.py
    goto end
)

if exist "C:\Program Files\Python314\python.exe" (
    "C:\Program Files\Python314\python.exe" main.py
    goto end
)

if exist "C:\laragon\bin\python\python-3.10\python.exe" (
    "C:\laragon\bin\python\python-3.10\python.exe" main.py
    goto end
)

echo [ERROR] Python tidak ditemukan di sistem. Pastikan Python telah terpasang.
pause

:end
