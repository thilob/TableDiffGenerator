from __future__ import annotations

import html
from collections import Counter, OrderedDict
from pathlib import Path

from .assets import REPORT_CSS, REPORT_JS
from .core import make_anchor, ordered_union, parse_codeplug_tables, row_status, status_counts, value_class
from .metadata import APP_NAME


def build_report_html(input_files: list[Path], table_marker: str) -> str:
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
    return "\n".join(report_parts)


def build_report(input_files: list[Path], output_file: Path, table_marker: str) -> None:
    output_file.write_text(build_report_html(input_files, table_marker), encoding="utf-8")


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
