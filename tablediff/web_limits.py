from __future__ import annotations

from .core import ParseLimits


DEFAULT_WEB_PARSE_LIMITS = ParseLimits(
    max_file_bytes=8 * 1024 * 1024,
    max_tables=1500,
    max_rows_per_table=50000,
    max_cells_per_table=100000,
    max_cell_chars=4096,
)
