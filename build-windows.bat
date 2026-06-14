@echo off
setlocal

cd /d %~dp0

where python >nul 2>nul
if errorlevel 1 (
    echo Fehler: python wurde nicht gefunden.
    echo Bitte Python 3.10 oder neuer installieren und "Add python.exe to PATH" aktivieren.
    exit /b 1
)

if not exist .venv (
    echo Erzeuge virtuelle Umgebung .venv ...
    python -m venv .venv
    if errorlevel 1 exit /b 1
)

echo Installiere/aktualisiere Build-Werkzeuge ...
.venv\Scripts\python.exe -m pip install --upgrade pip
if errorlevel 1 exit /b 1
.venv\Scripts\python.exe -m pip install -r requirements.txt pyinstaller
if errorlevel 1 exit /b 1

echo Erzeuge Windows-Bundle ...
.venv\Scripts\pyinstaller.exe --noconfirm --clean tablediffgenerator.spec
if errorlevel 1 exit /b 1

if not exist dist\tablediffgenerator.exe (
    echo Fehler: Windows-Bundle wurde nicht erzeugt.
    exit /b 1
)

echo.
echo Fertig.
echo Startdatei: dist\tablediffgenerator.exe
