@echo off
setlocal

where python >nul 2>nul
if %errorlevel%==0 (
    echo menjalankan script executor.py
    python executor.py
    goto end
)

where python3 >nul 2>nul
if %errorlevel%==0 (
    echo menjalankan script executor.py
    python3 executor.py
    goto end
)