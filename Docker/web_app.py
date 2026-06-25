#!/usr/bin/env python3
from __future__ import annotations

import base64
import hashlib
import hmac
import os
import sys
import tempfile
from http import HTTPStatus
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if (PROJECT_ROOT / "compare_codeplug_html.py").is_file() and str(
    PROJECT_ROOT
) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from flask import Flask, Response, render_template_string, request  # noqa: E402
from werkzeug.exceptions import RequestEntityTooLarge  # noqa: E402
from werkzeug.utils import secure_filename  # noqa: E402

from tablediff import APP_NAME, APP_VERSION, DEFAULT_TABLE_MARKER, build_report_html  # noqa: E402
from tablediff.assets import REPORT_JS  # noqa: E402
from tablediff.core import DEFAULT_PARSE_LIMITS, ParseLimitError, ParseLimits  # noqa: E402


MAX_FILES = 4
MAX_TABLE_MARKER_CHARS = 128
ALLOWED_EXTENSIONS = {".html", ".htm"}
REPORT_JS_HASH = base64.b64encode(hashlib.sha256(REPORT_JS.encode()).digest()).decode()
AUTH_USERNAME = os.environ.get("WEB_USERNAME")
AUTH_PASSWORD = os.environ.get("WEB_PASSWORD")
if bool(AUTH_USERNAME) != bool(AUTH_PASSWORD):
    raise RuntimeError("WEB_USERNAME und WEB_PASSWORD muessen gemeinsam gesetzt sein.")


def get_int_env(name: str, default: int, minimum: int = 1) -> int:
    raw_value = os.environ.get(name)
    if raw_value is None:
        return default
    try:
        value = int(raw_value)
    except ValueError as error:
        raise RuntimeError(f"{name} muss eine ganze Zahl sein.") from error
    if value < minimum:
        raise RuntimeError(f"{name} muss mindestens {minimum} sein.")
    return value


UPLOAD_LIMITS = ParseLimits(
    max_file_bytes=get_int_env(
        "MAX_FILE_SIZE", DEFAULT_PARSE_LIMITS.max_file_bytes
    ),
    max_tables=get_int_env("MAX_TABLES_PER_FILE", DEFAULT_PARSE_LIMITS.max_tables),
    max_rows_per_table=get_int_env(
        "MAX_ROWS_PER_TABLE", DEFAULT_PARSE_LIMITS.max_rows_per_table
    ),
    max_cells_per_table=get_int_env(
        "MAX_CELLS_PER_TABLE", DEFAULT_PARSE_LIMITS.max_cells_per_table
    ),
    max_cell_chars=get_int_env("MAX_CELL_CHARS", DEFAULT_PARSE_LIMITS.max_cell_chars),
)


app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = get_int_env(
    "MAX_UPLOAD_SIZE", MAX_FILES * UPLOAD_LIMITS.max_file_bytes
)


PORTAL_TEMPLATE = """
<!doctype html>
<html lang="de">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>{{ app_name }} Web</title>
    <style>
        :root{
            --sapBackgroundColor:#f5f6f7;
            --sapShellColor:#354a5f;
            --sapShell_TextColor:#fff;
            --sapGroup_ContentBackground:#fff;
            --sapList_BorderColor:#d9d9d9;
            --sapTextColor:#1d2d3e;
            --sapContent_LabelColor:#556b82;
            --sapLinkColor:#0a6ed1;
            --sapButton_Hover_Background:#ebf5fe;
            --sapErrorBackground:#ffb8b8;
            --sapErrorBorderColor:#bb0000;
        }
        *{box-sizing:border-box}
        body{
            margin:0;
            background:var(--sapBackgroundColor);
            color:var(--sapTextColor);
            font-family:"72","72full",Arial,Helvetica,sans-serif;
            font-size:14px;
        }
        .shellbar{
            min-height:48px;
            display:flex;
            align-items:center;
            gap:12px;
            padding:0 24px;
            background:var(--sapShellColor);
            color:var(--sapShell_TextColor);
            box-shadow:0 2px 4px rgba(0,0,0,.18);
        }
        .shell-title{font-weight:700;font-size:16px}
        .shell-subtitle{color:#d3dce6;font-size:13px}
        main{max-width:1120px;margin:0 auto;padding:24px}
        .object-header{
            background:#fff;
            border:1px solid var(--sapList_BorderColor);
            border-radius:4px;
            padding:20px 24px;
            box-shadow:0 1px 2px rgba(0,0,0,.06);
        }
        h1{font-weight:400;font-size:26px;margin:0}
        .subtitle{margin:6px 0 0;color:var(--sapContent_LabelColor)}
        .panel{
            margin-top:16px;
            background:var(--sapGroup_ContentBackground);
            border:1px solid var(--sapList_BorderColor);
            border-radius:4px;
        }
        .panel-header{
            min-height:44px;
            display:flex;
            align-items:center;
            padding:0 16px;
            background:#f7f7f7;
            border-bottom:1px solid var(--sapList_BorderColor);
            font-weight:700;
        }
        form{padding:16px}
        .grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:16px}
        label{display:block;margin-bottom:6px;color:var(--sapContent_LabelColor);font-size:12px}
        input[type="file"],input[type="text"]{
            width:100%;
            min-height:36px;
            border:1px solid #89919a;
            border-radius:4px;
            background:#fff;
            color:var(--sapTextColor);
            padding:7px 10px;
            font:inherit;
        }
        .actions{display:flex;gap:8px;flex-wrap:wrap;margin-top:18px}
        button{
            min-height:36px;
            border:1px solid var(--sapLinkColor);
            border-radius:4px;
            background:#fff;
            color:var(--sapLinkColor);
            padding:7px 14px;
            font:inherit;
            font-weight:700;
            cursor:pointer;
        }
        button.primary{background:var(--sapLinkColor);color:#fff}
        button:hover{background:var(--sapButton_Hover_Background)}
        button.primary:hover{background:#0854a0}
        .message{
            margin:16px 16px 0;
            padding:10px 12px;
            border:1px solid var(--sapErrorBorderColor);
            border-radius:4px;
            background:var(--sapErrorBackground);
            color:#8f0000;
            font-weight:700;
        }
        .file-row{margin-bottom:12px}
        @media (max-width:700px){
            main{padding:12px}
            .object-header{padding:16px}
            .actions button{width:100%}
        }
    </style>
</head>
<body>
    <header class="shellbar">
        <span class="shell-title">{{ app_name }}</span>
        <span class="shell-subtitle">Webportal {{ app_version }}</span>
    </header>
    <main>
        <section class="object-header">
            <h1>Codeplug Vergleich</h1>
            <p class="subtitle">HTML-Dateien auswählen und Vergleichsreport erzeugen</p>
        </section>

        <section class="panel">
            <div class="panel-header">Vergleichsparameter</div>
            {% if error %}
                <div class="message">{{ error }}</div>
            {% endif %}
            <form action="/compare" method="post" enctype="multipart/form-data">
                <div class="grid">
                    <div>
                        {% for index in range(1, max_files + 1) %}
                            <div class="file-row">
                                <label for="file-{{ index }}">Datei {{ index }}</label>
                                <input id="file-{{ index }}" name="files" type="file" accept=".html,.htm">
                            </div>
                        {% endfor %}
                    </div>
                    <div>
                        <label for="table-marker">Tabellen-Suchbegriff</label>
                        <input id="table-marker" name="table_marker" type="text" value="{{ table_marker }}">
                    </div>
                </div>
                <div class="actions">
                    <button class="primary" type="submit">Vergleich starten</button>
                    <button type="reset">Zurücksetzen</button>
                </div>
            </form>
        </section>
    </main>
</body>
</html>
"""


def render_portal(error: str | None = None) -> str:
    return render_template_string(
        PORTAL_TEMPLATE,
        app_name=APP_NAME,
        app_version=APP_VERSION,
        table_marker=DEFAULT_TABLE_MARKER,
        max_files=MAX_FILES,
        error=error,
    )


def auth_required_response() -> Response:
    response = Response("Authentifizierung erforderlich.", HTTPStatus.UNAUTHORIZED)
    response.headers["WWW-Authenticate"] = 'Basic realm="TableDiffGenerator"'
    return response


@app.before_request
def require_basic_auth() -> Response | None:
    if not AUTH_USERNAME:
        return None
    if request.endpoint == "healthz":
        return None

    authorization = request.authorization
    if not authorization:
        return auth_required_response()
    if not hmac.compare_digest(authorization.username or "", AUTH_USERNAME):
        return auth_required_response()
    if not hmac.compare_digest(authorization.password or "", AUTH_PASSWORD or ""):
        return auth_required_response()
    return None


@app.after_request
def add_security_headers(response: Response) -> Response:
    response.headers.setdefault("X-Content-Type-Options", "nosniff")
    response.headers.setdefault("X-Frame-Options", "DENY")
    response.headers.setdefault("Referrer-Policy", "no-referrer")
    response.headers.setdefault(
        "Permissions-Policy",
        "camera=(), microphone=(), geolocation=(), payment=(), usb=()",
    )
    if response.mimetype == "text/html":
        response.headers.setdefault(
            "Content-Security-Policy",
            "default-src 'none'; "
            "base-uri 'none'; "
            "form-action 'self'; "
            "frame-ancestors 'none'; "
            "img-src 'self' data:; "
            "style-src 'self' 'unsafe-inline'; "
            f"script-src 'self' 'sha256-{REPORT_JS_HASH}'",
        )
        response.headers.setdefault("Cache-Control", "no-store")
    return response


@app.errorhandler(RequestEntityTooLarge)
def handle_too_large(_: RequestEntityTooLarge) -> tuple[str, int]:
    return (
        render_portal("Die hochgeladenen Dateien sind zu gross."),
        HTTPStatus.REQUEST_ENTITY_TOO_LARGE,
    )


@app.errorhandler(ParseLimitError)
def handle_parse_limit(error: ParseLimitError) -> tuple[str, int]:
    return render_portal(str(error)), HTTPStatus.BAD_REQUEST


@app.errorhandler(ValueError)
def handle_value_error(error: ValueError) -> tuple[str, int]:
    return render_portal(str(error)), HTTPStatus.BAD_REQUEST


@app.get("/")
def index() -> str:
    return render_portal()


@app.get("/healthz")
def healthz() -> dict[str, str]:
    return {"status": "ok", "version": APP_VERSION}


@app.post("/compare")
def compare() -> Response | tuple[str, int]:
    table_marker = request.form.get("table_marker", DEFAULT_TABLE_MARKER).strip()
    uploads = [
        upload
        for upload in request.files.getlist("files")
        if upload and upload.filename
    ]

    if not 1 <= len(uploads) <= MAX_FILES:
        return render_portal(f"Bitte 1 bis {MAX_FILES} HTML-Dateien auswählen."), 400

    if not table_marker:
        return render_portal("Der Tabellen-Suchbegriff darf nicht leer sein."), 400
    if len(table_marker) > MAX_TABLE_MARKER_CHARS:
        return (
            render_portal(
                f"Der Tabellen-Suchbegriff darf maximal {MAX_TABLE_MARKER_CHARS} Zeichen lang sein."
            ),
            400,
        )

    invalid_files = [
        upload.filename
        for upload in uploads
        if Path(upload.filename).suffix.lower() not in ALLOWED_EXTENSIONS
    ]
    if invalid_files:
        return render_portal(
            "Nur HTML-Dateien sind erlaubt: " + ", ".join(invalid_files)
        ), 400

    with tempfile.TemporaryDirectory(prefix="tablediff-web-") as temp_dir:
        input_files: list[Path] = []
        for index, upload in enumerate(uploads, start=1):
            original_suffix = Path(upload.filename).suffix.lower()
            safe_stem = secure_filename(Path(upload.filename).stem) or f"upload-{index}"
            filename = f"{index:02d}-{safe_stem}{original_suffix}"
            target = Path(temp_dir) / filename
            upload.save(target)
            if target.stat().st_size > UPLOAD_LIMITS.max_file_bytes:
                raise ParseLimitError("Eine hochgeladene Datei ist zu gross.")
            input_files.append(target)

        report = build_report_html(input_files, table_marker, UPLOAD_LIMITS)

    return Response(report, mimetype="text/html")


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "8080"))
    app.run(host="0.0.0.0", port=port)
