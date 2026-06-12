# TableDiffGenerator

TableDiffGenerator vergleicht bis zu vier HTML-Dateien, die Key/Value-Tabellen enthalten, und erzeugt daraus einen HTML-Vergleichsreport.

Das Tool ist fuer exportierte Tabellenberichte gedacht, bei denen relevante Tabellen an einer gemeinsamen Ueberschrift erkannt werden. Standardmaessig sucht es nach Tabellenueberschriften mit `Codeplug\\`.

Aktuelle Programmversion: `0.2.0`

## Funktionen

- Vergleich von 1 bis 4 HTML-Dateien
- automatische Erkennung relevanter Tabellen per Suchbegriff
- gemeinsame Darstellung gleicher Tabellen nebeneinander
- farbliche Markierung:
  - hellgruen fuer gleiche Werte
  - orange fuer abweichende Werte
  - rot fuer fehlende Tabellen oder Keys
- einklappbare Tabellen im Report
- Inhaltsverzeichnis mit Suchfunktion
- Schaltflaechen zum Auf- und Zuklappen aller Tabellen
- Navigation zurueck zum Dateianfang pro Tabelle
- einfache GUI fuer Linux und Windows
- keine externen Python-Abhaengigkeiten

## Nutzung

Ohne Kommandozeilenargumente startet die GUI:

```bash
python3 compare_codeplug_html.py
```

In der GUI koennen bis zu vier HTML-Dateien ausgewaehlt werden. Der Tabellen-Suchbegriff ist mit `Codeplug\\` vorbelegt und kann angepasst werden. Nach dem Start des Vergleichs wird der Report erzeugt und, wenn moeglich, ueber die Betriebssystemfunktionen im Standardbrowser geoeffnet.

Die Kommandozeile bleibt weiterhin nutzbar:

```bash
python3 compare_codeplug_html.py file1.html file2.html -o vergleich.html
```

Sobald Kommandozeilenparameter uebergeben werden, wird die GUI nicht gestartet.
Fehlerhafte oder unvollstaendige Parameter geben eine Hilfeseite mit
Fehlermeldung aus.

Bis zu vier Dateien sind moeglich:

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

## Release-Builds

Die Release-Builds werden mit PyInstaller als `--onedir`-Bundle gebaut.

### Linux

```bash
python3 -m venv .venv
.venv/bin/pip install --upgrade pip
.venv/bin/pip install -r requirements.txt pyinstaller
./build-pyinstaller.sh
./dist/tablediffgenerator/tablediffgenerator --version
```

### Windows

```bat
python -m venv .venv
.venv\Scripts\pip install --upgrade pip
.venv\Scripts\pip install -r requirements.txt pyinstaller
build-windows.bat
dist\tablediffgenerator\tablediffgenerator.exe --version
```

### GitHub Actions

Der Workflow `.github/workflows/build-release-assets.yml` kann manuell gestartet
werden und erzeugt Linux- und Windows-Archive inklusive SHA256-Dateien.

Neue Releases sollen die Versionsnummer in `compare_codeplug_html.py` erhoehen:

```python
APP_VERSION = "0.2.0"
```

Weitere Details stehen in `RELEASE.md`.

## Hinweise

Die Eingabe-HTML-Dateien und erzeugten Reports werden nicht versioniert. Die `.gitignore` schliesst `*.html` und `*.htm` aus. Build-Artefakte wie `dist/`, `build/`, `*.zip` und `*.tar.gz` werden ebenfalls ignoriert.

## Lizenz

Dieses Projekt steht unter der CC0-1.0-Lizenz. Details stehen in `LICENSE`.
