from __future__ import annotations

from .metadata import APP_NAME, APP_VERSION, DEFAULT_TABLE_MARKER
from .report import build_report, build_report_html

__all__ = [
    "APP_NAME",
    "APP_VERSION",
    "DEFAULT_TABLE_MARKER",
    "build_report",
    "build_report_html",
]
