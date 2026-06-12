# Release-Checkliste

Aktuelle Version: `0.2.0`

## Versionsnummer erhoehen

Vor einem neuen Release die zentrale Versionsnummer in `compare_codeplug_html.py`
erhoehen:

```python
APP_VERSION = "0.2.0"
```

Danach dieselbe Version im GitHub-Actions-Workflow als Eingabe verwenden.
Empfohlenes Tag-Schema: `v0.2.0`.

## Lokaler Linux-Build

```bash
python3 -m venv .venv
.venv/bin/pip install --upgrade pip
.venv/bin/pip install -r requirements.txt pyinstaller
./build-pyinstaller.sh
./dist/tablediffgenerator/tablediffgenerator --version
```

Der Start ohne Kommandozeilenparameter oeffnet die GUI:

```bash
./dist/tablediffgenerator/tablediffgenerator
```

## Lokaler Windows-Build

```bat
python -m venv .venv
.venv\Scripts\pip install --upgrade pip
.venv\Scripts\pip install -r requirements.txt pyinstaller
build-windows.bat
dist\tablediffgenerator\tablediffgenerator.exe --version
```

## GitHub Actions

Workflow: `.github/workflows/build-release-assets.yml`

Der Workflow wird manuell gestartet und erwartet eine Version ohne fuehrendes
`v`, z. B. `0.2.0`. Er erzeugt:

- `tablediffgenerator-linux-v<VERSION>.tar.gz`
- `tablediffgenerator-linux-v<VERSION>.tar.gz.sha256`
- `tablediffgenerator-windows-v<VERSION>.zip`
- `tablediffgenerator-windows-v<VERSION>.zip.sha256`

Die HTML-Eingabedateien und erzeugten Reports werden nicht in Releases
mitverpackt.

