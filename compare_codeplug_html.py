#!/usr/bin/env python3
from __future__ import annotations

import argparse
import html
import re
import sys
import tkinter as tk
import webbrowser
from collections import Counter, OrderedDict
from dataclasses import dataclass
from html.parser import HTMLParser
from tkinter import filedialog, messagebox, ttk
from pathlib import Path
from typing import Iterable


APP_NAME = "TableDiffGenerator"
APP_VERSION = "0.4.0"
DEFAULT_TABLE_MARKER = "Codeplug\\"


class HelpOnErrorParser(argparse.ArgumentParser):
    def error(self, message: str) -> None:
        self.print_help(sys.stderr)
        self.exit(2, f"\nFehler: {message}\n")


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


REPORT_CSS = """
:root{
    --sapBackgroundColor:#f5f6f7;
    --sapShellColor:#354a5f;
    --sapShell_TextColor:#fff;
    --sapPageHeader_Background:#fff;
    --sapObjectHeader_Background:#fff;
    --sapGroup_ContentBackground:#fff;
    --sapList_HeaderBackground:#f7f7f7;
    --sapList_BorderColor:#d9d9d9;
    --sapList_TableGroupHeaderBackground:#f2f2f2;
    --sapTextColor:#1d2d3e;
    --sapContent_LabelColor:#556b82;
    --sapLinkColor:#0a6ed1;
    --sapButton_BorderColor:#0a6ed1;
    --sapButton_TextColor:#0a6ed1;
    --sapButton_Hover_Background:#ebf5fe;
    --sapHighlightColor:#0854a0;
    --sapInformationBackground:#e5f2ff;
    --sapSuccessBackground:#f1fdf6;
    --sapSuccessBorderColor:#188918;
    --sapWarningBackground:#fff8d6;
    --sapWarningBorderColor:#e76500;
    --sapErrorBackground:#ffb8b8;
    --sapErrorBorderColor:#bb0000;
    --sapContent_Shadow0:0 0 0 1px rgba(0,0,0,.08),0 2px 8px rgba(0,0,0,.08);
}
*{box-sizing:border-box}
html{scroll-behavior:smooth}
body{
    margin:0;
    background:var(--sapBackgroundColor);
    color:var(--sapTextColor);
    font-family:"72","72full",Arial,Helvetica,sans-serif;
    font-size:14px;
    line-height:1.4;
}
a{color:var(--sapLinkColor);text-decoration:none}
a:hover{text-decoration:underline}
.ui5-shellbar{
    position:sticky;
    top:0;
    z-index:10;
    display:flex;
    align-items:center;
    min-height:48px;
    padding:0 24px;
    background:var(--sapShellColor);
    color:var(--sapShell_TextColor);
    box-shadow:0 2px 4px rgba(0,0,0,.18);
}
.ui5-product-switch{font-size:18px;margin-right:12px}
.ui5-shell-title{font-size:16px;font-weight:700}
.ui5-shell-subtitle{margin-left:12px;color:#d3dce6;font-size:13px}
.ui5-page{max-width:1440px;margin:0 auto;padding:24px}
.ui5-object-page-header{
    background:var(--sapObjectHeader_Background);
    border-bottom:1px solid var(--sapList_BorderColor);
    box-shadow:var(--sapContent_Shadow0);
    padding:20px 24px;
}
h1{margin:0;color:var(--sapTextColor);font-size:26px;font-weight:400;letter-spacing:0}
.ui5-title-row{display:flex;align-items:flex-start;justify-content:space-between;gap:16px;flex-wrap:wrap}
.ui5-subtitle{margin:6px 0 0;color:var(--sapContent_LabelColor);font-size:14px}
.ui5-kpis{display:flex;gap:12px;flex-wrap:wrap;margin-top:18px}
.ui5-kpi{
    min-width:132px;
    padding:10px 12px;
    background:#f7f7f7;
    border:1px solid var(--sapList_BorderColor);
    border-radius:4px;
}
.ui5-kpi-value{display:block;font-size:22px;font-weight:700;color:var(--sapHighlightColor)}
.ui5-kpi-label{display:block;margin-top:2px;color:var(--sapContent_LabelColor);font-size:12px}
.ui5-section{margin-top:16px}
.ui5-panel{
    background:var(--sapGroup_ContentBackground);
    border:1px solid var(--sapList_BorderColor);
    border-radius:4px;
    box-shadow:0 1px 2px rgba(0,0,0,.04);
}
.ui5-panel-header{
    display:flex;
    align-items:center;
    justify-content:space-between;
    gap:16px;
    min-height:44px;
    padding:0 16px;
    background:var(--sapList_HeaderBackground);
    border-bottom:1px solid var(--sapList_BorderColor);
}
.ui5-panel-title{font-size:16px;font-weight:700}
.ui5-toolbar{display:flex;align-items:center;gap:8px;flex-wrap:wrap;padding:12px 16px}
.ui5-button{
    min-height:32px;
    border:1px solid var(--sapButton_BorderColor);
    border-radius:4px;
    background:#fff;
    color:var(--sapButton_TextColor);
    padding:6px 12px;
    font:inherit;
    font-weight:700;
    cursor:pointer;
}
.ui5-button:hover{background:var(--sapButton_Hover_Background)}
.ui5-button:focus-visible,.ui5-input:focus-visible{outline:2px solid var(--sapHighlightColor);outline-offset:1px}
.ui5-button-icon{padding:5px 10px}
.ui5-input{
    min-height:32px;
    width:min(420px,100%);
    border:1px solid #89919a;
    border-radius:4px;
    background:#fff;
    color:var(--sapTextColor);
    padding:6px 10px;
    font:inherit;
}
.ui5-meta-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:12px;padding:16px}
.ui5-label{color:var(--sapContent_LabelColor);font-size:12px}
.ui5-token-list{display:flex;gap:8px;flex-wrap:wrap;margin-top:6px}
.ui5-token{
    display:inline-flex;
    align-items:center;
    min-height:26px;
    max-width:100%;
    border:1px solid #b3d4f5;
    border-radius:4px;
    background:var(--sapInformationBackground);
    color:#174a7c;
    padding:3px 8px;
    overflow-wrap:anywhere;
}
.toc-details{overflow:hidden}
.toc-details>summary,.codeplug-table>summary{
    display:flex;
    align-items:center;
    justify-content:space-between;
    gap:12px;
    min-height:44px;
    padding:0 16px;
    background:var(--sapList_HeaderBackground);
    border-bottom:1px solid var(--sapList_BorderColor);
    cursor:pointer;
    font-weight:700;
    list-style:none;
}
.toc-details>summary::-webkit-details-marker,.codeplug-table>summary::-webkit-details-marker{display:none}
.toc-details>summary::before,.codeplug-table>summary::before{content:"\\25B8";color:var(--sapContent_LabelColor);margin-right:2px}
.toc-details[open]>summary::before,.codeplug-table[open]>summary::before{content:"\\25BE"}
.summary-title{flex:1;min-width:0;overflow-wrap:anywhere}
.summary-metrics{display:flex;align-items:center;gap:6px;flex-wrap:wrap}
.summary-label{
    display:inline-flex;
    align-items:center;
    min-height:24px;
    border-radius:4px;
    padding:2px 8px;
    font-size:12px;
    font-weight:700;
    white-space:nowrap;
    cursor:pointer;
    font-family:inherit;
}
.summary-label-same{background:var(--sapSuccessBackground);border:1px solid var(--sapSuccessBorderColor);color:#107e3e}
.summary-label-different{background:var(--sapWarningBackground);border:1px solid var(--sapWarningBorderColor);color:#8a4100}
.summary-label-missing{background:#ffcaca;border:1px solid var(--sapErrorBorderColor);color:#8f0000}
.summary-label-active{box-shadow:0 0 0 2px var(--sapHighlightColor)}
.top-link{
    flex:0 0 auto;
    border:1px solid transparent;
    border-radius:4px;
    padding:5px 8px;
    font-size:12px;
    font-weight:700;
}
.top-link:hover{background:var(--sapButton_Hover_Background);text-decoration:none}
.toc-search{display:flex;gap:8px;flex-wrap:wrap;padding:12px 16px;border-bottom:1px solid var(--sapList_BorderColor)}
.toc{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:0;margin:0;padding:0;list-style:none}
.toc li{border-bottom:1px solid var(--sapList_BorderColor)}
.toc a{display:block;padding:10px 16px;overflow-wrap:anywhere}
.toc a:hover{background:#f0f7ff;text-decoration:none}
.toc-empty{display:none;margin:0;padding:14px 16px;color:var(--sapContent_LabelColor)}
.codeplug-table{margin-top:12px;overflow:hidden}
.table-wrap{overflow:auto;background:#fff}
table{width:100%;border-collapse:collapse;background:#fff;table-layout:auto}
th,td{
    border-bottom:1px solid var(--sapList_BorderColor);
    border-right:1px solid var(--sapList_BorderColor);
    padding:8px 10px;
    text-align:left;
    vertical-align:top;
    overflow-wrap:anywhere;
}
th:last-child,td:last-child{border-right:0}
th{
    background:var(--sapList_TableGroupHeaderBackground);
    color:var(--sapContent_LabelColor);
    font-weight:700;
}
td:first-child{font-weight:700;background:#fafafa}
.same{background:var(--sapSuccessBackground);box-shadow:inset 4px 0 0 var(--sapSuccessBorderColor)}
.different{background:var(--sapWarningBackground);box-shadow:inset 4px 0 0 var(--sapWarningBorderColor)}
.missing{background:var(--sapErrorBackground);box-shadow:inset 4px 0 0 var(--sapErrorBorderColor)}
.empty{color:var(--sapContent_LabelColor)}
@media (max-width:700px){
    .ui5-shellbar{padding:0 16px}
    .ui5-shell-subtitle{display:none}
    .ui5-page{padding:12px}
    .ui5-object-page-header{padding:16px}
    h1{font-size:22px}
    .ui5-toolbar,.toc-search{align-items:stretch}
    .ui5-button,.ui5-input{width:100%}
    .summary-metrics{width:100%;order:3}
}
"""


REPORT_JS = """
function setAllDetails(open){
    document.querySelectorAll('details.codeplug-table').forEach(function(item){item.open=open;});
}
function openAndJump(id){
    var item=document.getElementById(id);
    if(item){item.open=true;item.scrollIntoView({behavior:'smooth',block:'start'});}
}
function filterToc(){
    var term=document.getElementById('toc-search').value.toLowerCase();
    var shown=0;
    document.querySelectorAll('#toc-list li').forEach(function(item){
        var match=item.textContent.toLowerCase().indexOf(term)!==-1;
        item.style.display=match?'':'none';
        if(match){shown++;}
    });
    document.getElementById('toc-empty').style.display=shown?'none':'block';
}
function clearTocSearch(){
    document.getElementById('toc-search').value='';
    filterToc();
    document.getElementById('toc-search').focus();
}
function filterTable(id,status,trigger){
    var table=document.getElementById(id);
    if(!table){return;}
    var nextStatus=status;
    if(trigger&&trigger.classList.contains('summary-label-active')){nextStatus='all';}
    table.open=true;
    table.querySelectorAll('tbody tr').forEach(function(row){
        row.style.display=nextStatus==='all'||row.dataset.status===nextStatus?'':'none';
    });
    table.querySelectorAll('.summary-label').forEach(function(label){
        label.classList.toggle('summary-label-active', nextStatus!=='all'&&label.dataset.status===nextStatus);
    });
}
"""


GUI_COLORS = {
    "background": "#f5f6f7",
    "shell": "#354a5f",
    "shell_text": "#ffffff",
    "panel": "#ffffff",
    "panel_header": "#f7f7f7",
    "border": "#d9d9d9",
    "text": "#1d2d3e",
    "label": "#556b82",
    "link": "#0a6ed1",
    "button_hover": "#ebf5fe",
}


def build_report(input_files: list[Path], output_file: Path, table_marker: str) -> None:
    parsed_files = [parse_codeplug_tables(path, table_marker) for path in input_files]
    table_titles = ordered_union(parsed_files)
    anchors = {title: make_anchor(title, index) for index, title in enumerate(table_titles, start=1)}
    total_rows = sum(len(parsed_file[title].rows) for parsed_file in parsed_files for title in parsed_file)
    report_parts = [
        "<!doctype html>",
        "<html lang='de'>",
        "<head>",
        "<meta charset='utf-8'>",
        "<meta name='viewport' content='width=device-width, initial-scale=1'>",
        "<title>Codeplug Vergleich</title>",
        "<style>",
        REPORT_CSS,
        "</style>",
        "<script>",
        REPORT_JS,
        "</script>",
        "</head>",
        "<body>",
        "<div id='top'></div>",
        "<header class='ui5-shellbar'>",
        "<span class='ui5-product-switch' aria-hidden='true'>&#9638;</span>",
        f"<span class='ui5-shell-title'>{html.escape(APP_NAME)}</span>",
        "<span class='ui5-shell-subtitle'>Codeplug Vergleichsreport</span>",
        "</header>",
        "<main class='ui5-page'>",
        "<section class='ui5-object-page-header'>",
        "<div class='ui5-title-row'>",
        "<div>",
        "<h1>Codeplug Vergleich</h1>",
        "<p class='ui5-subtitle'>HTML-Vergleichsreport im UI5/Fiori-Stil</p>",
        "</div>",
        "<div class='ui5-toolbar' aria-label='Tabellenaktionen'>",
        "<button class='ui5-button' type='button' onclick='setAllDetails(true)'>Alle Tabellen aufklappen</button>",
        "<button class='ui5-button' type='button' onclick='setAllDetails(false)'>Alle Tabellen zuklappen</button>",
        "</div>",
        "</div>",
        "<div class='ui5-kpis'>",
        f"<div class='ui5-kpi'><span class='ui5-kpi-value'>{len(input_files)}</span><span class='ui5-kpi-label'>Dateien</span></div>",
        f"<div class='ui5-kpi'><span class='ui5-kpi-value'>{len(table_titles)}</span><span class='ui5-kpi-label'>Tabellen</span></div>",
        f"<div class='ui5-kpi'><span class='ui5-kpi-value'>{total_rows}</span><span class='ui5-kpi-label'>Werte</span></div>",
        "</div>",
        "</section>",
        "<section class='ui5-section ui5-panel'>",
        "<div class='ui5-panel-header'><span class='ui5-panel-title'>Vergleichsparameter</span></div>",
        "<div class='ui5-meta-grid'>",
        "<div>",
        "<div class='ui5-label'>Tabellen-Suchbegriff</div>",
        f"<div class='ui5-token-list'><span class='ui5-token'>{html.escape(table_marker)}</span></div>",
        "</div>",
        "<div>",
        "<div class='ui5-label'>Eingabedateien</div>",
        "<div class='ui5-token-list'>",
    ]

    for path in input_files:
        report_parts.append(f"<span class='ui5-token'>{html.escape(str(path))}</span>")
    report_parts.append("</div>")
    report_parts.append("</div>")
    report_parts.append("</div>")
    report_parts.append("</section>")
    report_parts.append("<section class='ui5-section ui5-panel'>")
    report_parts.append("<details class='toc-details' open>")
    report_parts.append("<summary>Inhaltsverzeichnis</summary>")
    report_parts.append("<div class='toc-search'>")
    report_parts.append(
        "<input id='toc-search' class='ui5-input' type='search' placeholder='Tabellen suchen' "
        "oninput='filterToc()' aria-label='Inhaltsverzeichnis durchsuchen'>"
    )
    report_parts.append("<button class='ui5-button' type='button' onclick='clearTocSearch()'>Suche leeren</button>")
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
    report_parts.append("</section>")

    for title in table_titles:
        anchor = html.escape(anchors[title], quote=True)
        per_file_rows = [
            parsed_file[title].rows if title in parsed_file else OrderedDict()
            for parsed_file in parsed_files
        ]
        keys = ordered_union(per_file_rows)
        counts = status_counts(per_file_rows)
        report_parts.append(f"<details class='codeplug-table ui5-panel' id='{anchor}'>")
        report_parts.append(
            f"<summary><span class='summary-title'>{html.escape(title)}</span>"
            f"{render_summary_metrics(anchor, counts)}"
            "<a class='top-link' href='#top' onclick='event.stopPropagation()'>Nach oben</a></summary>"
        )
        report_parts.append("<div class='table-wrap'>")
        report_parts.append("<table>")
        report_parts.append("<thead><tr><th>Key</th>")
        for path in input_files:
            report_parts.append(f"<th>{html.escape(path.name)}</th>")
        report_parts.append("</tr></thead><tbody>")
        if not keys:
            report_parts.append(render_row("Tabelle fehlt oder leer", [None] * len(input_files), "missing"))
        else:
            for key in keys:
                values = [rows.get(key) if key in rows else None for rows in per_file_rows]
                report_parts.append(render_row(key, values, row_status(values)))

        report_parts.append("</tbody></table>")
        report_parts.append("</div>")
        report_parts.append("</details>")

    report_parts.extend(["</main>", "</body>", "</html>"])
    output_file.write_text("\n".join(report_parts), encoding="utf-8")


def render_summary_metrics(anchor: str, counts: Counter[str]) -> str:
    escaped_anchor = html.escape(anchor, quote=True)
    return (
        "<span class='summary-metrics'>"
        f"<button type='button' class='summary-label summary-label-same' data-status='same' "
        f"onclick=\"event.stopPropagation();filterTable('{escaped_anchor}','same',this);\">"
        f"{counts['same']} Übereinstimmungen</button>"
        f"<button type='button' class='summary-label summary-label-different' data-status='different' "
        f"onclick=\"event.stopPropagation();filterTable('{escaped_anchor}','different',this);\">"
        f"{counts['different']} Abweichungen</button>"
        f"<button type='button' class='summary-label summary-label-missing' data-status='missing' "
        f"onclick=\"event.stopPropagation();filterTable('{escaped_anchor}','missing',this);\">"
        f"{counts['missing']} Fehlende</button>"
        "</span>"
    )


def render_row(key: str, values: list[str | None], status: str) -> str:
    cells = [f"<tr data-status='{html.escape(status, quote=True)}'><td>{html.escape(key)}</td>"]
    for value in values:
        css_class = value_class(values, value)
        display_value = "" if value is None else value
        if display_value == "":
            cells.append(f"<td class='{css_class} empty'>&nbsp;</td>")
        else:
            cells.append(f"<td class='{css_class}'>{html.escape(display_value)}</td>")
    cells.append("</tr>")
    return "".join(cells)


def create_parser() -> argparse.ArgumentParser:
    parser = HelpOnErrorParser(
        description="Vergleicht bis zu vier HTML-Dateien mit Key/Value-Tabellen.",
        epilog=(
            "Ohne Kommandozeilenparameter startet die GUI.\n"
            "Beispiel CLI: python3 compare_codeplug_html.py file1.html file2.html -o vergleich.html"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--version", action="version", version=f"{APP_NAME} {APP_VERSION}")
    parser.add_argument("files", nargs="*", type=Path, help="HTML-Dateien, die verglichen werden sollen")
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


class TableDiffGui:
    GUI_MIN_WIDTH = 780
    GUI_PREFERRED_WIDTH = 900
    GUI_SCREEN_MARGIN_X = 80
    GUI_SCREEN_MARGIN_Y = 120
    GUI_CONTENT_PADDING_Y = 32

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title(f"{APP_NAME} {APP_VERSION}")
        self.file_vars = [tk.StringVar() for _ in range(4)]
        self.marker_var = tk.StringVar(value=DEFAULT_TABLE_MARKER)
        self.output_var = tk.StringVar(value=str(Path.cwd() / "tablediff_report.html"))
        self.open_report_var = tk.BooleanVar(value=True)
        self.status_var = tk.StringVar(value="Bitte 1 bis 4 HTML-Dateien auswählen.")
        self._configure_style()
        self._build()
        self._fit_window_to_content()

    def _configure_style(self) -> None:
        self.root.configure(background=GUI_COLORS["background"])
        style = ttk.Style(self.root)
        if "clam" in style.theme_names():
            style.theme_use("clam")

        default_font = ("Arial", 10)
        title_font = ("Arial", 16)
        section_font = ("Arial", 11, "bold")

        style.configure(".", font=default_font, background=GUI_COLORS["background"], foreground=GUI_COLORS["text"])
        style.configure("Ui5Page.TFrame", background=GUI_COLORS["background"])
        style.configure("Ui5Panel.TFrame", background=GUI_COLORS["panel"], relief="solid", borderwidth=1)
        style.configure("Ui5PanelHeader.TFrame", background=GUI_COLORS["panel_header"])
        style.configure("Ui5Toolbar.TFrame", background=GUI_COLORS["panel"])
        style.configure("Ui5Label.TLabel", background=GUI_COLORS["panel"], foreground=GUI_COLORS["label"])
        style.configure("Ui5Text.TLabel", background=GUI_COLORS["panel"], foreground=GUI_COLORS["text"])
        style.configure("Ui5Title.TLabel", background=GUI_COLORS["panel"], foreground=GUI_COLORS["text"], font=title_font)
        style.configure(
            "Ui5Section.TLabel",
            background=GUI_COLORS["panel_header"],
            foreground=GUI_COLORS["text"],
            font=section_font,
        )
        style.configure("Ui5Status.TLabel", background=GUI_COLORS["background"], foreground=GUI_COLORS["label"])
        style.configure("Ui5.TEntry", fieldbackground="#ffffff", foreground=GUI_COLORS["text"], padding=5)
        style.configure(
            "Ui5.TButton",
            background="#ffffff",
            foreground=GUI_COLORS["link"],
            bordercolor=GUI_COLORS["link"],
            lightcolor="#ffffff",
            darkcolor="#ffffff",
            padding=(10, 6),
        )
        style.map("Ui5.TButton", background=[("active", GUI_COLORS["button_hover"])])
        style.configure(
            "Ui5Primary.TButton",
            background=GUI_COLORS["link"],
            foreground="#ffffff",
            bordercolor=GUI_COLORS["link"],
            lightcolor=GUI_COLORS["link"],
            darkcolor=GUI_COLORS["link"],
            padding=(14, 7),
        )
        style.map("Ui5Primary.TButton", background=[("active", "#0854a0")], foreground=[("active", "#ffffff")])
        style.configure("Ui5.TCheckbutton", background=GUI_COLORS["panel"], foreground=GUI_COLORS["text"])

    def _build(self) -> None:
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(1, weight=1)

        shellbar = tk.Frame(self.root, background=GUI_COLORS["shell"], height=48)
        shellbar.grid(row=0, column=0, sticky="ew")
        shellbar.grid_propagate(False)
        shellbar.columnconfigure(1, weight=1)
        tk.Label(
            shellbar,
            text=APP_NAME,
            background=GUI_COLORS["shell"],
            foreground=GUI_COLORS["shell_text"],
            font=("Arial", 11, "bold"),
            padx=20,
        ).grid(row=0, column=0, sticky="w")
        tk.Label(
            shellbar,
            text="Codeplug Vergleich",
            background=GUI_COLORS["shell"],
            foreground="#d3dce6",
            font=("Arial", 10),
        ).grid(row=0, column=1, sticky="w")

        page = ttk.Frame(self.root, padding=16, style="Ui5Page.TFrame")
        page.grid(row=1, column=0, sticky="nsew")
        page.columnconfigure(0, weight=1)
        page.rowconfigure(1, weight=1)

        header = ttk.Frame(page, padding=(18, 14), style="Ui5Panel.TFrame")
        header.grid(row=0, column=0, sticky="ew", pady=(0, 12))
        header.columnconfigure(0, weight=1)
        ttk.Label(header, text="Codeplug Vergleich", style="Ui5Title.TLabel").grid(row=0, column=0, sticky="w")
        ttk.Label(
            header,
            text="HTML-Dateien auswählen und einen UI5-ähnlichen Vergleichsreport erzeugen.",
            style="Ui5Label.TLabel",
        ).grid(row=1, column=0, sticky="w", pady=(4, 0))

        panel = ttk.Frame(page, style="Ui5Panel.TFrame")
        panel.grid(row=1, column=0, sticky="nsew")
        panel.columnconfigure(0, weight=1)

        panel_header = ttk.Frame(panel, padding=(14, 10), style="Ui5PanelHeader.TFrame")
        panel_header.grid(row=0, column=0, sticky="ew")
        ttk.Label(panel_header, text="Vergleichsparameter", style="Ui5Section.TLabel").grid(row=0, column=0, sticky="w")

        frame = ttk.Frame(panel, padding=14, style="Ui5Toolbar.TFrame")
        frame.grid(row=1, column=0, sticky="nsew")
        frame.columnconfigure(1, weight=1)

        ttk.Label(frame, text="HTML-Dateien", style="Ui5Text.TLabel").grid(row=0, column=0, columnspan=3, sticky="w")
        for index, file_var in enumerate(self.file_vars, start=1):
            row = index
            ttk.Label(frame, text=f"Datei {index}", style="Ui5Label.TLabel").grid(row=row, column=0, sticky="w", pady=4)
            ttk.Entry(frame, textvariable=file_var, style="Ui5.TEntry").grid(
                row=row, column=1, sticky="ew", padx=10, pady=4
            )
            ttk.Button(
                frame,
                text="Auswählen",
                style="Ui5.TButton",
                command=lambda i=index - 1: self._select_input(i),
            ).grid(
                row=row, column=2, sticky="ew", pady=3
            )

        marker_row = 5
        ttk.Label(frame, text="Tabellen-Suchbegriff", style="Ui5Label.TLabel").grid(
            row=marker_row, column=0, sticky="w", pady=(14, 4)
        )
        ttk.Entry(frame, textvariable=self.marker_var, style="Ui5.TEntry").grid(
            row=marker_row, column=1, columnspan=2, sticky="ew", padx=(10, 0), pady=(14, 4)
        )

        output_row = 6
        ttk.Label(frame, text="Ausgabedatei", style="Ui5Label.TLabel").grid(row=output_row, column=0, sticky="w", pady=4)
        ttk.Entry(frame, textvariable=self.output_var, style="Ui5.TEntry").grid(
            row=output_row, column=1, sticky="ew", padx=10, pady=4
        )
        ttk.Button(frame, text="Speichern unter", style="Ui5.TButton", command=self._select_output).grid(
            row=output_row, column=2, sticky="ew", pady=4
        )

        ttk.Checkbutton(
            frame,
            text="Report nach dem Erzeugen öffnen",
            variable=self.open_report_var,
            style="Ui5.TCheckbutton",
        ).grid(row=7, column=0, columnspan=3, sticky="w", pady=(10, 4))

        action_frame = ttk.Frame(frame, style="Ui5Toolbar.TFrame")
        action_frame.grid(row=8, column=0, columnspan=3, sticky="ew", pady=(14, 4))
        action_frame.columnconfigure(0, weight=1)
        ttk.Button(action_frame, text="Vergleich starten", style="Ui5Primary.TButton", command=self._run_compare).grid(
            row=0, column=1
        )
        ttk.Button(action_frame, text="Beenden", style="Ui5.TButton", command=self.root.destroy).grid(
            row=0, column=2, padx=(8, 0)
        )

        ttk.Label(page, textvariable=self.status_var, style="Ui5Status.TLabel").grid(
            row=2, column=0, sticky="w", pady=(10, 0)
        )

    def _fit_window_to_content(self) -> None:
        self.root.update_idletasks()

        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        max_width = max(self.GUI_MIN_WIDTH, screen_width - self.GUI_SCREEN_MARGIN_X)
        max_height = max(480, screen_height - self.GUI_SCREEN_MARGIN_Y)

        requested_width = self.root.winfo_reqwidth()
        requested_height = self.root.winfo_reqheight() + self.GUI_CONTENT_PADDING_Y
        window_width = min(max(self.GUI_PREFERRED_WIDTH, requested_width), max_width)
        window_height = min(requested_height, max_height)

        min_width = min(self.GUI_MIN_WIDTH, window_width)
        min_height = min(requested_height, window_height)
        self.root.minsize(min_width, min_height)

        position_x = max(0, (screen_width - window_width) // 2)
        position_y = max(0, (screen_height - window_height) // 3)
        self.root.geometry(f"{window_width}x{window_height}+{position_x}+{position_y}")

    def _select_input(self, index: int) -> None:
        filename = filedialog.askopenfilename(
            title="HTML-Datei auswählen",
            filetypes=[("HTML-Dateien", "*.html *.htm"), ("Alle Dateien", "*.*")],
        )
        if filename:
            self.file_vars[index].set(filename)
            if index == 0:
                self.output_var.set(str(Path(filename).with_name("tablediff_report.html")))

    def _select_output(self) -> None:
        filename = filedialog.asksaveasfilename(
            title="Vergleichsreport speichern",
            defaultextension=".html",
            initialfile=Path(self.output_var.get()).name,
            filetypes=[("HTML-Dateien", "*.html"), ("Alle Dateien", "*.*")],
        )
        if filename:
            self.output_var.set(filename)

    def _run_compare(self) -> None:
        input_files = [Path(file_var.get()) for file_var in self.file_vars if file_var.get().strip()]
        table_marker = self.marker_var.get()
        output_file = Path(self.output_var.get())

        if not 1 <= len(input_files) <= 4:
            messagebox.showerror("Fehler", "Bitte 1 bis 4 HTML-Dateien auswählen.")
            return

        if not table_marker:
            messagebox.showerror("Fehler", "Der Tabellen-Suchbegriff darf nicht leer sein.")
            return

        missing_files = [path for path in input_files if not path.is_file()]
        if missing_files:
            messagebox.showerror("Fehler", "Datei nicht gefunden:\n" + "\n".join(str(path) for path in missing_files))
            return

        try:
            self.status_var.set("Vergleich wird erzeugt ...")
            self.root.update_idletasks()
            output_file.parent.mkdir(parents=True, exist_ok=True)
            build_report(input_files, output_file, table_marker)
        except Exception as error:
            self.status_var.set("Fehler beim Erzeugen des Reports.")
            messagebox.showerror("Fehler", str(error))
            return

        self.status_var.set(f"Report geschrieben: {output_file}")
        if self.open_report_var.get():
            opened = webbrowser.open(output_file.resolve().as_uri())
            if not opened:
                messagebox.showinfo("Report erzeugt", f"Report wurde erzeugt:\n{output_file}")


def run_gui() -> int:
    root = tk.Tk()
    TableDiffGui(root)
    root.mainloop()
    return 0


def main(argv: list[str] | None = None) -> int:
    if argv is None:
        argv = sys.argv[1:]

    if not argv:
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


if __name__ == "__main__":
    raise SystemExit(main())
