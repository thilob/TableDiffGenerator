# TableDiffGenerator

TableDiffGenerator vergleicht bis zu vier HTML-Dateien, die Key/Value-Tabellen enthalten, und erzeugt daraus einen HTML-Vergleichsreport.

Das Tool ist für exportierte Tabellenberichte gedacht, bei denen relevante Tabellen an einer gemeinsamen Überschrift erkannt werden. Standardmaessig sucht es nach Tabellenüberschriften mit `Codeplug\\`.

Als Vergleichgrundlage für iTM-Codeplugs ist ein Export als Benutzerbericht aus CPS Plus heraus notwendig (Codeplug in CPS Plus öffnen -> Datei -> Export -> Benutzerbericht Strg+J).

Aktuelle Programmversion: `1.0`

## Funktionen

- Vergleich von 1 bis 4 HTML-Dateien
- automatische Erkennung relevanter Tabellen per Suchbegriff
- gemeinsame Darstellung gleicher Tabellen nebeneinander
- farbliche Markierung:
  - hellgrün für gleiche Werte
  - orange für abweichende Werte
  - rot für fehlende Tabellen oder Keys
- Tabellenfilter für gleiche, abweichende, fehlende und alle unterschiedlichen (`Diff`) Werte
- PDF-Export über das Drucklayout des Browsers
- CSV-Export für Excel und andere Tabellenprogramme
- einklappbare Tabellen im Report
- Inhaltsverzeichnis mit Suchfunktion
- Schaltflächen zum Auf- und Zuklappen aller Tabellen
- Navigation zurück zum Dateianfang pro Tabelle
- einfache GUI für Linux, Windows und macOS
- Web-Limits für Uploads und Parser-Komplexität
- Security-Header und optionale Basic-Auth in der Webversion
- keine externen Python-Abhängigkeiten für CLI und GUI

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

### Ergebnis exportieren

Der erzeugte HTML-Report enthält Schaltflächen für den PDF- und CSV-Export.
Der PDF-Export öffnet das Druckfenster des Browsers, in dem der Report als PDF
gespeichert werden kann. Der CSV-Export erzeugt eine UTF-8-Datei mit
Semikolon-Trennung, die sich unter anderem mit Excel öffnen lässt.

Die Option `Nur sichtbare Zeilen` ist standardmäßig aktiviert. Dadurch werden
gesetzte Tabellenfilter einschließlich des kombinierten `Diff`-Filters bei
beiden Exporten berücksichtigt. Wird die Option deaktiviert, enthalten PDF und
CSV unabhängig von den Filtern alle Ergebniszeilen.

Versionsausgabe:

```bash
python3 compare_codeplug_html.py --version
```

## Webportal

Die Webversion stellt ein Upload-Portal bereit, in dem 1 bis 2 HTML-Dateien
ausgewählt und direkt im Browser verglichen werden können.

```bash
python3 -m venv .venv
.venv/bin/pip install -r Docker/requirements-web.txt
.venv/bin/python Docker/web_app.py
```

Danach ist das Portal unter `http://127.0.0.1:8080` erreichbar.

Für eine geschützte Webinstanz können Benutzername und Passwort per
Umgebungsvariablen gesetzt werden:

```bash
WEB_USERNAME=tablediff WEB_PASSWORD='ein-langes-passwort' .venv/bin/python Docker/web_app.py
```

Die Webversion setzt Upload- und Parser-Limits, damit öffentliche Instanzen
gegen übergroße Eingaben geschützt sind. CLI, GUI und daraus gebaute
Einzelprogramme verwenden diese Web-Limits nicht. Die wichtigsten Web-Limits
sind in `tablediff/web_limits.py` gebündelt und per Umgebungsvariablen
konfigurierbar:

```text
MAX_UPLOAD_SIZE      gesamter Request, direkt gestartet 16777216 Bytes,
                     in Docker Compose und Helm 33554432 Bytes
MAX_FILE_SIZE        einzelne Datei, Standard 8388608 Bytes
MAX_TABLES_PER_FILE  Tabellen pro Datei, Standard 1500
MAX_ROWS_PER_TABLE   Zeilen pro Tabelle, Standard 50000
MAX_CELLS_PER_TABLE  Zellen pro Tabelle, Standard 100000
MAX_CELL_CHARS       Zeichen pro Tabellenzelle, Standard 4096
```

### Docker

Die Webversion ist für den Betrieb im Container vorbereitet:

```bash
docker build -f Docker/Dockerfile -t tablediffgenerator-web .
docker run --rm -p 8080:8080 tablediffgenerator-web
```

Für öffentlich erreichbare Installationen sollte die Webversion nur hinter TLS
und mit Authentifizierung betrieben werden.

Alternativ mit Docker Compose:

```bash
docker compose -f Docker/docker-compose.yaml up --build
```

Für Dockhand oder andere Deployment-Werkzeuge, die ein bereits veröffentlichtes
Image aus GHCR ziehen sollen, ist eine separate Compose-Datei vorbereitet:

```bash
docker compose -f Docker/docker-compose.ghcr.yaml up
```

Diese Variante nutzt `ghcr.io/thilob/tablediffgenerator-web:latest`. Der Tag
wird bei erfolgreichen Builds von `main` aktualisiert, damit Docker- und
Dockhand-Installationen neue Image-Digests erkennen können.

Ein reiner Container-Neustart lädt einen geänderten Image-Tag nicht zwingend
erneut herunter. Das veröffentlichte Image wird mit folgenden Befehlen
aktualisiert und der Container anschließend neu erzeugt:

```bash
docker compose -f Docker/docker-compose.ghcr.yaml pull
docker compose -f Docker/docker-compose.ghcr.yaml up -d --force-recreate
```

Für reproduzierbare Installationen kann der `image`-Eintrag der Compose-Datei
auf den festen Release-Tag
`ghcr.io/thilob/tablediffgenerator-web:1.0` gesetzt werden.

Für private GHCR-Images muss der Docker-Host vorher angemeldet sein:

```bash
echo "DEIN_TOKEN" | docker login ghcr.io -u thilob --password-stdin
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
APP_VERSION = "1.0"
```

Weitere Details stehen in `RELEASE.md`.

Eine ausführliche Anleitung für lokale Builds unter Linux und Windows steht
in `BUILD.md`.

## Hinweise

Die Eingabe-HTML-Dateien und erzeugten Reports werden nicht versioniert. Die `.gitignore` schließt `*.html` und `*.htm` aus. Build-Artefakte wie `dist/`, `build/`, `*.zip` und `*.tar.gz` werden ebenfalls ignoriert.

Eine kompakte Sicherheitsbewertung für die Kundenauslieferung steht in
`SECURITY_REVIEW.md`.

## Lizenz

Dieses Projekt steht unter der CC0-1.0-Lizenz. Details stehen in `LICENSE`.
