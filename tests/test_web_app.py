from io import BytesIO
from pathlib import Path
from unittest import TestCase

from Docker.web_app import MAX_FILES, app
from tablediff import APP_VERSION


PROJECT_ROOT = Path(__file__).resolve().parents[1]


class WebAppTests(TestCase):
    def setUp(self) -> None:
        app.config.update(TESTING=True)
        self.client = app.test_client()

    def test_portal_offers_four_file_inputs(self) -> None:
        response = self.client.get("/")
        page = response.get_data(as_text=True)

        self.assertEqual(4, MAX_FILES)
        self.assertEqual(4, page.count('name="files"'))
        self.assertIn(f"Webportal {APP_VERSION}", page)

    def test_compare_accepts_four_files(self) -> None:
        source = (PROJECT_ROOT / "testdata" / "tablediff_ui5_a.html").read_bytes()
        uploads = [(BytesIO(source), f"input-{index}.html") for index in range(4)]

        response = self.client.post(
            "/compare",
            data={"files": uploads, "table_marker": "Codeplug\\"},
            content_type="multipart/form-data",
        )

        self.assertEqual(200, response.status_code)
        self.assertIn("4</span><span class='ui5-kpi-label'>Dateien", response.get_data(as_text=True))

    def test_compare_rejects_more_than_four_files(self) -> None:
        uploads = [(BytesIO(b"<html></html>"), f"input-{index}.html") for index in range(5)]

        response = self.client.post(
            "/compare",
            data={"files": uploads, "table_marker": "Codeplug\\"},
            content_type="multipart/form-data",
        )

        self.assertEqual(400, response.status_code)
        self.assertIn("Bitte 1 bis 4 HTML-Dateien auswählen.", response.get_data(as_text=True))
