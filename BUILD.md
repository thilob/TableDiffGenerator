# Build-Anleitung

Diese Anleitung beschreibt, wie TableDiffGenerator aus dem Quellcode als
startbares Programm gebaut werden kann. Die Schritte sind bewusst ausführlich
gehalten.

## Was wird gebaut?

Der Build erzeugt ein PyInstaller-`onefile`-Programm. Das bedeutet:

- Es entsteht eine einzelne startbare Datei im Ordner `dist/`.
- Diese Datei kann ohne `_internal`-Ordner in ein anderes Verzeichnis kopiert werden.
- Python muss auf dem Zielrechner danach nicht mehr separat installiert sein.

## Allgemeine Voraussetzungen

Du brauchst:

- den Quellcode von TableDiffGenerator
- Internetzugang beim ersten Build, damit PyInstaller installiert werden kann
- ausreichend freien Speicherplatz für `.venv/`, `build/` und `dist/`

Die Ordner `.venv/`, `build/` und `dist/` werden automatisch erzeugt und sind
nicht für Git gedacht.

## Linux

### 1. Python prüfen

Öffne ein Terminal im Projektordner und prüfe Python:

```bash
python3 --version
```

Empfohlen ist Python 3.10 oder neuer.

Falls Python oder `venv` fehlt, installiere die Pakete über deine
Linux-Distribution. Beispiele:

```bash
sudo apt install python3 python3-venv
```

oder auf Arch/Manjaro:

```bash
sudo pacman -S python
```

### 2. Build starten

Im Projektordner:

```bash
./build-pyinstaller.sh
```

Das Skript erledigt automatisch:

- virtuelle Umgebung `.venv/` anlegen, falls sie fehlt
- `pip` aktualisieren
- PyInstaller installieren
- Programm bauen

### 3. Fertiges Programm starten

Nach erfolgreichem Build:

```bash
./dist/tablediffgenerator
```

Ohne Kommandozeilenparameter startet die GUI.

Versionsprüfung:

```bash
./dist/tablediffgenerator --version
```

## Windows

### 1. Python installieren

Installiere Python von:

<https://www.python.org/downloads/windows/>

Wichtig im Installer:

- Haken bei `Add python.exe to PATH` setzen
- danach Installation abschliessen

Öffne danach `cmd.exe` oder PowerShell und prüfe:

```bat
python --version
```

Empfohlen ist Python 3.10 oder neuer.

### 2. Projektordner öffnen

Wechsle in der Eingabeaufforderung in den Projektordner. Beispiel:

```bat
cd %USERPROFILE%\Downloads\TableDiffGenerator
```

Der genaue Pfad hängt davon ab, wohin du den Quellcode entpackt hast.

### 3. Build starten

In `cmd.exe`:

```bat
build-windows.bat
```

Das Skript erledigt automatisch:

- virtuelle Umgebung `.venv` anlegen, falls sie fehlt
- `pip` aktualisieren
- PyInstaller installieren
- Programm bauen

### 4. Fertiges Programm starten

Nach erfolgreichem Build:

```bat
dist\tablediffgenerator.exe
```

Ohne Kommandozeilenparameter startet die GUI.

Versionsprüfung:

```bat
dist\tablediffgenerator.exe --version
```

## Typische Probleme

### Python wird nicht gefunden

Linux:

```bash
python3 --version
```

Windows:

```bat
python --version
```

Falls der Befehl nicht funktioniert, Python installieren oder unter Windows
den PATH-Haken im Installer aktivieren.

### PyInstaller kann nicht installiert werden

Prüfe die Internetverbindung. PyInstaller wird beim Build mit `pip` aus PyPI
installiert.

### Das Programm startet mit GUI nicht

Auf Linux muss eine grafische Desktop-Sitzung laufen. Auf Servern ohne Desktop
kann die GUI nicht angezeigt werden. Die Kommandozeile funktioniert trotzdem:

```bash
./dist/tablediffgenerator input1.html input2.html -o vergleich.html
```

### Windows meldet Sicherheitswarnung

Selbst gebaute Programme sind nicht digital signiert. Windows SmartScreen kann
daher beim ersten Start warnen. Das ist bei lokal gebauten Programmen normal.

## Aufräumen

Wenn du neu bauen willst, kannst du diese Ordner löschen:

- `.venv/`
- `build/`
- `dist/`

Danach das Buildskript erneut starten.

## Release-Assets

Für GitHub-Releases gibt es zusätzlich den Workflow:

```text
.github/workflows/build-release-assets.yml
```

Dieser Workflow baut Linux-, Windows- und macOS-Archive automatisch auf GitHub.
