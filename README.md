# TableDiffGenerator

TableDiffGenerator vergleicht bis zu vier HTML-Dateien, die Key/Value-Tabellen enthalten, und erzeugt daraus einen HTML-Vergleichsreport.

Das Tool ist für exportierte Tabellenberichte gedacht, bei denen relevante Tabellen an einer gemeinsamen Überschrift erkannt werden. Standardmaessig sucht es nach Tabellenüberschriften mit `Codeplug\\`.

Als Vergleich von iTM-Codeplugs ist ein Export als Benutzerbericht aus CPS Plus heraus notwendig.

Aktuelle Programmversion: `0.4.0`

## Funktionen

- Vergleich von 1 bis 4 HTML-Dateien
- automatische Erkennung relevanter Tabellen per Suchbegriff
- gemeinsame Darstellung gleicher Tabellen nebeneinander
- farbliche Markierung:
  - hellgrün für gleiche Werte
  - orange für abweichende Werte
  - rot für fehlende Tabellen oder Keys
- einklappbare Tabellen im Report
- Inhaltsverzeichnis mit Suchfunktion
- Schaltflächen zum Auf- und Zuklappen aller Tabellen
- Navigation zurück zum Dateianfang pro Tabelle
- einfache GUI für Linux und Windows
- keine externen Python-Abhängigkeiten

## Projektstruktur

Die gemeinsame Vergleichs- und Reportlogik liegt im Paket `tablediff/`.
Der bisherige Einstiegspunkt `compare_codeplug_html.py` bleibt für CLI, GUI
und bestehende Build-Skripte erhalten.

- `tablediff/core.py`: HTML-Parsing und Tabellenvergleich
- `tablediff/report.py`: HTML-Report-Erzeugung
- `tablediff/gui.py`: Tkinter-GUI
- `tablediff/cli.py`: Kommandozeilenstart
- `Docker/`: Webportal, Dockerfile und Compose-Konfiguration

## Nutzung

Ohne Kommandozeilenargumente startet die GUI:

```bash
python3 compare_codeplug_html.py
```

In der GUI können bis zu vier HTML-Dateien ausgewählt werden. Der Tabellen-Suchbegriff ist mit `Codeplug\\` vorbelegt und kann angepasst werden. Nach dem Start des Vergleichs wird der Report erzeugt und, wenn möglich, über die Betriebssystemfunktionen im Standardbrowser geöffnet.

Die Kommandozeile bleibt weiterhin nutzbar:

```bash
python3 compare_codeplug_html.py file1.html file2.html -o vergleich.html
```

Sobald Kommandozeilenparameter übergeben werden, wird die GUI nicht gestartet.
Fehlerhafte oder unvollständige Parameter geben eine Hilfeseite mit
Fehlermeldung aus.

Bis zu vier Dateien sind möglich:

```bash
python3 compare_codeplug_html.py file1.html file2.html file3.html file4.html -o vergleich.html
```

Der Tabellen-Suchbegriff ist variabel. Standard ist `Codeplug\\`.

```bash
python3 compare_codeplug_html.py file1.html file2.html --table-marker "Codeplug\\" -o vergleich.html
```

Kurzform:

```bash
python3 compare_codeplug_html.py file1.html file2.html -m "Codeplug\\" -o vergleich.html
```

Versionsausgabe:

```bash
python3 compare_codeplug_html.py --version
```

## Webportal

Die Webversion stellt ein Upload-Portal bereit, in dem 1 bis 4 HTML-Dateien
ausgewählt und direkt im Browser verglichen werden können.

```bash
python3 -m venv .venv
.venv/bin/pip install -r Docker/requirements-web.txt
.venv/bin/python Docker/web_app.py
```

Danach ist das Portal unter `http://127.0.0.1:8080` erreichbar.

### Docker

Die Webversion ist für den Betrieb im Container vorbereitet:

```bash
docker build -f Docker/Dockerfile -t tablediffgenerator-web .
docker run --rm -p 8080:8080 tablediffgenerator-web
```

Alternativ mit Docker Compose:

```bash
docker compose -f Docker/docker-compose.yaml up --build
```

### Kubernetes

Ein Helm Chart und eine Schritt-für-Schritt-Anleitung für Rancher Desktop und
Rancher Server liegen unter [Kubernetes](Kubernetes/README.md).

## Release-Builds

Die Release-Builds werden mit PyInstaller als einzelne `--onefile`-Programme gebaut.

### Linux

```bash
python3 -m venv .venv
.venv/bin/pip install --upgrade pip
.venv/bin/pip install -r requirements.txt pyinstaller
./build-pyinstaller.sh
./dist/tablediffgenerator --version
```

### Windows

```bat
python -m venv .venv
.venv\Scripts\pip install --upgrade pip
.venv\Scripts\pip install -r requirements.txt pyinstaller
build-windows.bat
dist\tablediffgenerator.exe --version
```

### GitHub Actions

Der Workflow `.github/workflows/build-release-assets.yml` kann manuell gestartet
werden und erzeugt Linux-, Windows- und macOS-Archive inklusive SHA256-Dateien.

Neue Releases sollen die Versionsnummer in `tablediff/metadata.py` erhöhen:

```python
APP_VERSION = "0.4.0"
```

Weitere Details stehen in `RELEASE.md`.

Eine ausführliche Anleitung für lokale Builds unter Linux und Windows steht
in `BUILD.md`.

## Hinweise

Die Eingabe-HTML-Dateien und erzeugten Reports werden nicht versioniert. Die `.gitignore` schließt `*.html` und `*.htm` aus. Build-Artefakte wie `dist/`, `build/`, `*.zip` und `*.tar.gz` werden ebenfalls ignoriert.

## Lizenz

Dieses Projekt steht unter der CC0-1.0-Lizenz. Details stehen in `LICENSE`.
