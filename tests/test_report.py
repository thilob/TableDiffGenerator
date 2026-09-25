import base64
import hashlib
from collections import Counter
from pathlib import Path
from unittest import TestCase

from tablediff.assets import REPORT_JS
from tablediff.report import build_report_html, render_summary_metrics


PROJECT_ROOT = Path(__file__).resolve().parents[1]


class RenderSummaryMetricsTests(TestCase):
    def test_diff_combines_different_and_missing_rows(self) -> None:
        metrics = render_summary_metrics(
            "table-1",
            Counter(same=4, different=2, missing=3),
        )

        self.assertIn("data-status='diff'", metrics)
        self.assertIn("5 Diff</button>", metrics)
        self.assertEqual(4, metrics.count("aria-pressed='false'"))

    def test_report_contains_pdf_and_csv_exports(self) -> None:
        report = build_report_html(
            [
                PROJECT_ROOT / "testdata" / "tablediff_ui5_a.html",
                PROJECT_ROOT / "testdata" / "tablediff_ui5_b.html",
            ],
            "Codeplug\\",
        )

        self.assertIn("data-action='export-pdf'", report)
        self.assertIn("data-action='export-csv'", report)
        self.assertIn("id='export-visible-only'", report)
        self.assertEqual(4, report.count("class='export-status-filter'"))
        self.assertIn("value='same' checked", report)
        self.assertIn("value='different' checked", report)
        self.assertIn("value='missing' checked", report)
        self.assertIn("value='diff'>Diff", report)
        self.assertNotIn("id='export-visible-only' type='checkbox' checked", report)
        self.assertIn("data-file-name='tablediff_ui5_a.html'", report)
        self.assertIn("function exportPdf()", report)
        self.assertIn("function exportCsv()", report)
        self.assertIn("function statusMatchesFilter", report)
        self.assertIn("activeStatuses.some", report)
        self.assertIn("function selectedExportStatuses", report)
        self.assertIn("function rowMatchesExport", report)
        self.assertIn("document.querySelectorAll('details.codeplug-table')", report)
        self.assertIn("filterStatus==='diff'", report)
        self.assertIn("@media print", report)
        self.assertIn("class='ui5-section ui5-panel toc-panel'", report)
        self.assertIn("if(/^[=+@-]/.test(text))", report)

    def test_embedded_script_matches_web_csp_hash(self) -> None:
        report = build_report_html(
            [PROJECT_ROOT / "testdata" / "tablediff_ui5_a.html"],
            "Codeplug\\",
        )
        embedded_script = report.partition("<script>")[2].partition("</script>")[0]

        expected_hash = base64.b64encode(
            hashlib.sha256(REPORT_JS.encode()).digest()
        ).decode()
        embedded_hash = base64.b64encode(
            hashlib.sha256(embedded_script.encode()).digest()
        ).decode()

        self.assertEqual(REPORT_JS, embedded_script)
        self.assertEqual(expected_hash, embedded_hash)
