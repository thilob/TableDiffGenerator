# Release-Checkliste

Aktuelle Version: `0.4.0`

## Versionsnummer erhöhen

Vor einem neuen Release die zentrale Versionsnummer in `compare_codeplug_html.py`
erhöhen:

```python
APP_VERSION = "0.4.0"
```

Danach dieselbe Version im GitHub-Actions-Workflow als Eingabe verwenden.
Empfohlenes Tag-Schema: `v0.4.0`.

## Lokaler Linux-Build

Eine ausführliche Anleitung für ungeübte Nutzer steht in `BUILD.md`.

```bash
./build-pyinstaller.sh
./dist/tablediffgenerator --version
```

Der Start ohne Kommandozeilenparameter öffnet die GUI:

```bash
./dist/tablediffgenerator
```

## Lokaler Windows-Build

```bat
build-windows.bat
dist\tablediffgenerator.exe --version
```

## GitHub Actions

Workflow: `.github/workflows/build-release-assets.yml`

Der Workflow wird manuell gestartet und erwartet eine Version ohne führendes
`v`, z. B. `0.4.0`. Er erzeugt:

- `tablediffgenerator-linux-v<VERSION>.tar.gz`
- `tablediffgenerator-linux-v<VERSION>.tar.gz.sha256`
- `tablediffgenerator-windows-v<VERSION>.zip`
- `tablediffgenerator-windows-v<VERSION>.zip.sha256`
- `tablediffgenerator-macos-v<VERSION>.tar.gz`
- `tablediffgenerator-macos-v<VERSION>.tar.gz.sha256`

Die HTML-Eingabedateien und erzeugten Reports werden nicht in Releases
mitverpackt.
