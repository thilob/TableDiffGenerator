from collections import Counter
from pathlib import Path
from unittest import TestCase

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
        self.assertIn("data-file-name='tablediff_ui5_a.html'", report)
        self.assertIn("function exportPdf()", report)
        self.assertIn("function exportCsv()", report)
        self.assertIn("@media print", report)
        self.assertIn("class='ui5-section ui5-panel toc-panel'", report)
        self.assertIn("if(/^[=+@-]/.test(text))", report)
