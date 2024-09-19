@echo off
setlocal

where python >nul 2>nul
if %errorlevel%==0 (
    echo Python sudah terinstall.
    notepad "./.env"
    python -m pip install -r windows.txt >nul 2>nul
    echo menjalankan script main.py
    python main.py
    goto end
)

where python3 >nul 2>nul
if %errorlevel%==0 (
    echo Python sudah terinstall.
    notepad "./.env"
    python3 -m pip install -r windows.txt >nul 2>nul
    echo menjalankan script main.py
    python3 main.py
    goto end
)

echo Python tidak ditemukan. Mengunduh dan menginstal Python...

curl -o python-installer.exe https://www.python.org/ftp/python/3.12.6/python-3.12.6-amd64.exe

start /wait python-installer.exe /quiet InstallAllUsers=1 PrependPath=1 Include_test=0

del python-installer.exe

where python >nul 2>nul
if %errorlevel%==0 (
    echo Instalasi Python berhasil.
    notepad "./.env"
    python -m pip install -r windows.txt >nul 2>nul
    echo menjalankan script main.py
    python main.py
) else (
    echo Instalasi Python gagal.
)

:end
pause
