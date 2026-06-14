#!/usr/bin/env python3
from __future__ import annotations

from tablediff import APP_NAME, APP_VERSION, DEFAULT_TABLE_MARKER, build_report, build_report_html
from tablediff.cli import main

__all__ = [
    "APP_NAME",
    "APP_VERSION",
    "DEFAULT_TABLE_MARKER",
    "build_report",
    "build_report_html",
    "main",
]


if __name__ == "__main__":
    raise SystemExit(main())
