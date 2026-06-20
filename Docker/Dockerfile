FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PORT=8080

WORKDIR /app

COPY Docker/requirements-web.txt .
RUN pip install --no-cache-dir -r requirements-web.txt

COPY compare_codeplug_html.py ./
COPY tablediff ./tablediff
COPY Docker/web_app.py ./

RUN useradd --create-home --uid 1000 --shell /usr/sbin/nologin appuser \
    && chown -R appuser:appuser /app
USER appuser

EXPOSE 8080

CMD ["sh", "-c", "gunicorn --bind 0.0.0.0:${PORT:-8080} web_app:app"]
