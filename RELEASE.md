# Release-Checkliste

Aktuelle Version: `1.0.1`

## Versionsnummer erhöhen

Vor einem neuen Release die zentrale Versionsnummer in `tablediff/metadata.py`
erhöhen:

```python
APP_VERSION = "1.0.1"
```

Danach dieselbe Version im GitHub-Actions-Workflow als Eingabe verwenden.
Empfohlenes Tag-Schema: `v1.0.1`.

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
`v`, z. B. `1.0.1`. Er erzeugt:

- `tablediffgenerator-linux-v<VERSION>.tar.gz`
- `tablediffgenerator-linux-v<VERSION>.tar.gz.sha256`
- `tablediffgenerator-windows-v<VERSION>.zip`
- `tablediffgenerator-windows-v<VERSION>.zip.sha256`
- `tablediffgenerator-macos-v<VERSION>.tar.gz`
- `tablediffgenerator-macos-v<VERSION>.tar.gz.sha256`

Die HTML-Eingabedateien und erzeugten Reports werden nicht in Releases
mitverpackt.

## Container Package / GHCR

Die Webversion wird als Container-Image über GitHub Packages / GHCR
veröffentlicht.

Workflow: `.github/workflows/publish-container-package.yml`

Image:

```text
ghcr.io/thilob/tablediffgenerator-web
```

Der Workflow läuft automatisch bei Pushes auf `main`, wenn sich relevante
Dateien ändern:

- `.github/workflows/publish-container-package.yml`
- `Docker/**`
- `Kubernetes/**`
- `compare_codeplug_html.py`
- `tablediff/**`

Ein Push nach `main` veröffentlicht folgende fortlaufend aktualisierte Tags:

```text
latest
kubernetes-latest
```

Der Workflow veröffentlicht außerdem einen Commit-bezogenen Tag:

```text
kubernetes-<kurzer-commit-sha>
```

Beim manuellen Start kann über die Eingabe `image_tag` zusätzlich ein fester
Versions-Tag wie `1.0.1` veröffentlicht werden. Ein Push nach `main` erzeugt
`latest`, `kubernetes-latest` und den Commit-bezogenen Tag. Für ein Release wird
der Container-Workflow zusätzlich manuell mit derselben Versionsnummer wie der
GitHub-Release gestartet.

Für Kubernetes/Rancher ist die GHCR-Variante vorbereitet in:

```text
Kubernetes/helm/tablediffgenerator/values-ghcr.yaml
```

Beispiel:

```bash
helm upgrade --install tablediffgenerator Kubernetes/helm/tablediffgenerator \
  --namespace tablediff \
  --create-namespace \
  -f Kubernetes/helm/tablediffgenerator/values-ghcr.yaml
```
