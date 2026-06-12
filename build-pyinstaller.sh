#!/usr/bin/env bash

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

cd "$ROOT_DIR"

if ! command -v python3 >/dev/null 2>&1; then
    echo "Fehler: python3 wurde nicht gefunden."
    echo "Bitte Python 3.10 oder neuer installieren."
    exit 1
fi

if [[ ! -d ".venv" ]]; then
    echo "Erzeuge virtuelle Umgebung .venv ..."
    python3 -m venv .venv
fi

echo "Installiere/aktualisiere Build-Werkzeuge ..."
".venv/bin/python" -m pip install --upgrade pip
".venv/bin/python" -m pip install -r requirements.txt pyinstaller

echo "Erzeuge Linux-Bundle ..."
".venv/bin/pyinstaller" --noconfirm --clean tablediffgenerator.spec

if [[ ! -x "dist/tablediffgenerator/tablediffgenerator" ]]; then
    echo "Fehler: Linux-Bundle wurde nicht erzeugt."
    exit 1
fi

echo
echo "Fertig."
echo "Startdatei: dist/tablediffgenerator/tablediffgenerator"
