from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .metadata import APP_NAME, APP_VERSION, DEFAULT_TABLE_MARKER
from .report import build_report


class HelpOnErrorParser(argparse.ArgumentParser):
    def error(self, message: str) -> None:
        self.print_help(sys.stderr)
        self.exit(2, f"\nFehler: {message}\n")


def create_parser() -> argparse.ArgumentParser:
    parser = HelpOnErrorParser(
        description="Vergleicht bis zu vier HTML-Dateien mit Key/Value-Tabellen.",
        epilog=(
            "Ohne Kommandozeilenparameter startet die GUI.\n"
            "Beispiel CLI: python3 compare_codeplug_html.py file1.html file2.html -o vergleich.html"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--version", action="version", version=f"{APP_NAME} {APP_VERSION}"
    )
    parser.add_argument(
        "files", nargs="*", type=Path, help="HTML-Dateien, die verglichen werden sollen"
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=Path("codeplug_vergleich.html"),
        help="Zieldatei für den HTML-Report (Standard: codeplug_vergleich.html)",
    )
    parser.add_argument(
        "-m",
        "--table-marker",
        default=DEFAULT_TABLE_MARKER,
        help=r"Suchbegriff für relevante Tabellenüberschriften (Standard: Codeplug\)",
    )
    return parser


def parse_args(argv: list[str]) -> argparse.Namespace:
    return create_parser().parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    if argv is None:
        argv = sys.argv[1:]

    if not argv:
        from .gui import run_gui

        return run_gui()

    parser = create_parser()
    args = parser.parse_args(argv)

    if not 1 <= len(args.files) <= 4:
        parser.error("Bitte 1 bis 4 HTML-Dateien angeben.")

    missing_files = [path for path in args.files if not path.is_file()]
    if missing_files:
        missing = ", ".join(str(path) for path in missing_files)
        parser.error(f"Datei nicht gefunden: {missing}")

    if not args.table_marker:
        parser.error("Der Tabellen-Suchbegriff darf nicht leer sein.")

    build_report(args.files, args.output, args.table_marker)
    print(f"Report geschrieben: {args.output}")
    return 0
