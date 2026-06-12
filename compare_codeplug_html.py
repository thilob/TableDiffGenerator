#!/usr/bin/env python3
from __future__ import annotations

import argparse
import html
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
        if tag in {"td", "th"} and self._table_depth == 1 and self._current_cell_parts is not None:
            if self._current_row is not None:
                self._current_row.append(normalize_text("".join(self._current_cell_parts)))
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


def parse_codeplug_tables(path: Path, table_marker: str) -> OrderedDict[str, CodeplugTable]:
    html_tables = parse_tables(path)
    result: OrderedDict[str, CodeplugTable] = OrderedDict()

    index = 0
    while index < len(html_tables):
        table = html_tables[index]
        title = normalize_text(table.text)
        if table_marker in title:
            rows = extract_key_value_rows(html_tables[index + 1] if index + 1 < len(html_tables) else None)
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
    if counts[current] == most_common_count and list(counts.values()).count(most_common_count) == 1:
        return "same"

    return "different"


def make_anchor(title: str, index: int) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", title).strip("-").lower()
    return f"table-{index}-{slug or 'codeplug'}"


def build_report(input_files: list[Path], output_file: Path, table_marker: str) -> None:
    parsed_files = [parse_codeplug_tables(path, table_marker) for path in input_files]
    table_titles = ordered_union(parsed_files)
    anchors = {title: make_anchor(title, index) for index, title in enumerate(table_titles, start=1)}
    report_parts = [
        "<!doctype html>",
        "<html lang='de'>",
        "<head>",
        "<meta charset='utf-8'>",
        "<title>Codeplug Vergleich</title>",
        "<style>",
        "body{font-family:Arial,sans-serif;margin:24px;background:#f7f7f7;color:#222}",
        "h1{font-size:24px;margin:0 0 16px}",
        "h2{font-size:18px;margin:24px 0 10px}",
        "table{border-collapse:collapse;width:100%;background:white}",
        "th,td{border:1px solid #bbb;padding:6px 8px;text-align:left;vertical-align:top}",
        "th{background:#d8e8ff}",
        "button{border:1px solid #888;background:white;border-radius:4px;padding:7px 10px;cursor:pointer}",
        "button:hover{background:#eef4ff}",
        "details{margin:0 0 12px;background:white;border:1px solid #ccc}",
        "summary{font-size:16px;font-weight:bold;padding:10px 12px;cursor:pointer;background:#e9eef5}",
        "summary:hover{background:#dde8f5}",
        ".summary-title{display:inline-block;margin-right:10px}",
        ".top-link{float:right;font-size:12px;font-weight:normal;border:1px solid #8fa3ba;background:white;border-radius:4px;padding:3px 7px;color:#17456d;text-decoration:none}",
        ".top-link:hover{background:#eef4ff}",
        "input[type='search']{border:1px solid #aaa;border-radius:4px;padding:7px 9px;min-width:280px}",
        ".marker-field{display:flex;gap:8px;align-items:center;flex-wrap:wrap;margin:0 0 16px}",
        ".marker-field input{border:1px solid #aaa;border-radius:4px;padding:7px 9px;min-width:220px;background:white}",
        ".table-wrap{padding:12px;overflow:auto}",
        ".same{background:#c9f7c9}",
        ".different{background:#ffd58a}",
        ".missing{background:#ffb3b3}",
        ".empty{color:#777}",
        ".files,.toc{margin:0 0 20px;padding-left:18px}",
        ".actions{display:flex;gap:8px;flex-wrap:wrap;margin:0 0 18px}",
        ".toc-search{display:flex;gap:8px;flex-wrap:wrap;margin:12px}",
        ".toc li{margin:3px 0}",
        ".toc-empty{display:none;margin:0 12px 12px;color:#666}",
        "</style>",
        "<script>",
        "function setAllDetails(open){document.querySelectorAll('details.codeplug-table').forEach(function(item){item.open=open;});}",
        "function openAndJump(id){var item=document.getElementById(id);if(item){item.open=true;item.scrollIntoView({behavior:'smooth',block:'start'});}}",
        "function filterToc(){var term=document.getElementById('toc-search').value.toLowerCase();var shown=0;document.querySelectorAll('#toc-list li').forEach(function(item){var match=item.textContent.toLowerCase().indexOf(term)!==-1;item.style.display=match?'':'none';if(match){shown++;}});document.getElementById('toc-empty').style.display=shown?'none':'block';}",
        "function clearTocSearch(){document.getElementById('toc-search').value='';filterToc();document.getElementById('toc-search').focus();}",
        "</script>",
        "</head>",
        "<body>",
        "<div id='top'></div>",
        "<h1>Codeplug Vergleich</h1>",
        "<ul class='files'>",
    ]

    for path in input_files:
        report_parts.append(f"<li>{html.escape(str(path))}</li>")
    report_parts.append("</ul>")
    report_parts.append("<div class='marker-field'>")
    report_parts.append("<label for='table-marker'>Tabellen-Suchbegriff</label>")
    report_parts.append(
        f"<input id='table-marker' type='text' value='{html.escape(table_marker, quote=True)}' readonly>"
    )
    report_parts.append("</div>")
    report_parts.append("<div class='actions'>")
    report_parts.append("<button type='button' onclick='setAllDetails(true)'>Alle Tabellen aufklappen</button>")
    report_parts.append("<button type='button' onclick='setAllDetails(false)'>Alle Tabellen zuklappen</button>")
    report_parts.append("</div>")
    report_parts.append("<details class='toc-details'>")
    report_parts.append("<summary>Inhaltsverzeichnis</summary>")
    report_parts.append("<div class='toc-search'>")
    report_parts.append(
        "<input id='toc-search' type='search' placeholder='Tabellen suchen' "
        "oninput='filterToc()' aria-label='Inhaltsverzeichnis durchsuchen'>"
    )
    report_parts.append("<button type='button' onclick='clearTocSearch()'>Suche leeren</button>")
    report_parts.append("</div>")
    report_parts.append("<p id='toc-empty' class='toc-empty'>Keine passende Tabelle gefunden.</p>")
    report_parts.append("<ul id='toc-list' class='toc'>")
    for title in table_titles:
        anchor = anchors[title]
        escaped_anchor = html.escape(anchor, quote=True)
        report_parts.append(
            f"<li><a href='#{escaped_anchor}' onclick=\"openAndJump('{escaped_anchor}');return false;\">"
            f"{html.escape(title)}</a></li>"
        )
    report_parts.append("</ul>")
    report_parts.append("</details>")

    for title in table_titles:
        anchor = html.escape(anchors[title], quote=True)
        report_parts.append(f"<details class='codeplug-table' id='{anchor}'>")
        report_parts.append(
            f"<summary><span class='summary-title'>{html.escape(title)}</span>"
            "<a class='top-link' href='#top' onclick='event.stopPropagation()'>Nach oben</a></summary>"
        )
        report_parts.append("<div class='table-wrap'>")
        report_parts.append("<table>")
        report_parts.append("<thead><tr><th>Key</th>")
        for path in input_files:
            report_parts.append(f"<th>{html.escape(path.name)}</th>")
        report_parts.append("</tr></thead><tbody>")

        per_file_rows = [
            parsed_file[title].rows if title in parsed_file else OrderedDict()
            for parsed_file in parsed_files
        ]
        keys = ordered_union(per_file_rows)
        if not keys:
            report_parts.append(render_row("Tabelle fehlt oder leer", [None] * len(input_files)))
        else:
            for key in keys:
                values = [rows.get(key) if key in rows else None for rows in per_file_rows]
                report_parts.append(render_row(key, values))

        report_parts.append("</tbody></table>")
        report_parts.append("</div>")
        report_parts.append("</details>")

    report_parts.extend(["</body>", "</html>"])
    output_file.write_text("\n".join(report_parts), encoding="utf-8")


def render_row(key: str, values: list[str | None]) -> str:
    cells = [f"<tr><td>{html.escape(key)}</td>"]
    for value in values:
        css_class = value_class(values, value)
        display_value = "" if value is None else value
        if display_value == "":
            cells.append(f"<td class='{css_class} empty'>&nbsp;</td>")
        else:
            cells.append(f"<td class='{css_class}'>{html.escape(display_value)}</td>")
    cells.append("</tr>")
    return "".join(cells)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Vergleicht bis zu vier HTML-Dateien mit Codeplug-Key/Value-Tabellen."
    )
    parser.add_argument("files", nargs="+", type=Path, help="HTML-Dateien, die verglichen werden sollen")
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=Path("codeplug_vergleich.html"),
        help="Zieldatei fuer den HTML-Report (Standard: codeplug_vergleich.html)",
    )
    parser.add_argument(
        "-m",
        "--table-marker",
        default="Codeplug\\",
        help=r"Suchbegriff fuer relevante Tabellenueberschriften (Standard: Codeplug\)",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if not 1 <= len(args.files) <= 4:
        raise SystemExit("Bitte 1 bis 4 HTML-Dateien angeben.")

    missing_files = [path for path in args.files if not path.is_file()]
    if missing_files:
        missing = ", ".join(str(path) for path in missing_files)
        raise SystemExit(f"Datei nicht gefunden: {missing}")

    if not args.table_marker:
        raise SystemExit("Der Tabellen-Suchbegriff darf nicht leer sein.")

    build_report(args.files, args.output, args.table_marker)
    print(f"Report geschrieben: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
