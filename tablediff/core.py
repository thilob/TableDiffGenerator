from __future__ import annotations

import re
from collections import Counter, OrderedDict
from dataclasses import dataclass
from html.parser import HTMLParser
from pathlib import Path
from typing import Iterable


@dataclass
class HtmlTable:
    rows: list[list[str]]

    @property
    def text(self) -> str:
        return " ".join(cell for row in self.rows for cell in row)


@dataclass
class CodeplugTable:
    title: str
    rows: OrderedDict[str, str]


class TableParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.tables: list[HtmlTable] = []
        self._table_depth = 0
        self._rows: list[list[str]] = []
        self._current_row: list[str] | None = None
        self._current_cell_parts: list[str] | None = None

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        tag = tag.lower()
        if tag == "table":
            self._table_depth += 1
            if self._table_depth == 1:
                self._rows = []
        elif self._table_depth == 1 and tag == "tr":
            self._current_row = []
        elif self._table_depth == 1 and tag in {"td", "th"}:
            self._current_cell_parts = []

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()
        if (
            tag in {"td", "th"}
            and self._table_depth == 1
            and self._current_cell_parts is not None
        ):
            if self._current_row is not None:
                self._current_row.append(
                    normalize_text("".join(self._current_cell_parts))
                )
            self._current_cell_parts = None
        elif tag == "tr" and self._table_depth == 1 and self._current_row is not None:
            if self._current_row:
                self._rows.append(self._current_row)
            self._current_row = None
        elif tag == "table" and self._table_depth > 0:
            if self._table_depth == 1:
                self.tables.append(HtmlTable(self._rows))
                self._rows = []
            self._table_depth -= 1

    def handle_data(self, data: str) -> None:
        if self._table_depth == 1 and self._current_cell_parts is not None:
            self._current_cell_parts.append(data)


def normalize_text(value: str) -> str:
    return " ".join(value.replace("\xa0", " ").split())


def read_text(path: Path) -> str:
    data = path.read_bytes()
    for encoding in ("utf-8-sig", "utf-16", "cp1252", "latin-1"):
        try:
            return data.decode(encoding)
        except UnicodeDecodeError:
            pass
    return data.decode("utf-8", errors="replace")


def parse_tables(path: Path) -> list[HtmlTable]:
    parser = TableParser()
    parser.feed(read_text(path))
    parser.close()
    return parser.tables


def parse_codeplug_tables(
    path: Path, table_marker: str
) -> OrderedDict[str, CodeplugTable]:
    html_tables = parse_tables(path)
    result: OrderedDict[str, CodeplugTable] = OrderedDict()

    index = 0
    while index < len(html_tables):
        table = html_tables[index]
        title = normalize_text(table.text)
        if table_marker in title:
            rows = extract_key_value_rows(
                html_tables[index + 1] if index + 1 < len(html_tables) else None
            )
            result[title] = CodeplugTable(title=title, rows=rows)
            index += 2
        else:
            index += 1

    return result


def extract_key_value_rows(table: HtmlTable | None) -> OrderedDict[str, str]:
    rows: OrderedDict[str, str] = OrderedDict()
    if table is None:
        return rows

    for row in table.rows:
        if len(row) < 3:
            continue
        key = normalize_text(row[1])
        value = normalize_text(row[2])
        if not key or key.lower() == "field":
            continue
        rows[key] = value

    return rows


def ordered_union(groups: Iterable[OrderedDict[str, object]]) -> list[str]:
    seen: OrderedDict[str, None] = OrderedDict()
    for group in groups:
        for key in group:
            seen.setdefault(key, None)
    return list(seen)


def value_class(values: list[str | None], current: str | None) -> str:
    if current is None:
        return "missing"

    present_values = [value for value in values if value is not None]
    if len(present_values) == len(values) and len(set(present_values)) == 1:
        return "same"

    counts = Counter(present_values)
    most_common_count = max(counts.values(), default=0)
    if (
        counts[current] == most_common_count
        and list(counts.values()).count(most_common_count) == 1
    ):
        return "same"

    return "different"


def row_status(values: list[str | None]) -> str:
    if any(value is None for value in values):
        return "missing"

    if len(set(values)) == 1:
        return "same"

    return "different"


def status_counts(rows_per_file: list[OrderedDict[str, str]]) -> Counter[str]:
    counts: Counter[str] = Counter()
    keys = ordered_union(rows_per_file)
    if not keys:
        counts["missing"] = 1
        return counts

    for key in keys:
        values = [rows.get(key) if key in rows else None for rows in rows_per_file]
        counts[row_status(values)] += 1
    return counts


def make_anchor(title: str, index: int) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", title).strip("-").lower()
    return f"table-{index}-{slug or 'codeplug'}"
