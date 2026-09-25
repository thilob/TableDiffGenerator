FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PORT=8080
ENV GUNICORN_WORKERS=1
ENV GUNICORN_THREADS=4
ENV GUNICORN_TIMEOUT=120
ENV GUNICORN_GRACEFUL_TIMEOUT=30
ENV GUNICORN_KEEP_ALIVE=5

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

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import os, urllib.request; urllib.request.urlopen('http://127.0.0.1:' + os.environ.get('PORT', '8080') + '/healthz', timeout=3).read()" || exit 1

CMD ["sh", "-c", "exec gunicorn --bind 0.0.0.0:${PORT:-8080} --worker-class gthread --workers ${GUNICORN_WORKERS:-1} --threads ${GUNICORN_THREADS:-4} --timeout ${GUNICORN_TIMEOUT:-120} --graceful-timeout ${GUNICORN_GRACEFUL_TIMEOUT:-30} --keep-alive ${GUNICORN_KEEP_ALIVE:-5} --worker-tmp-dir /tmp --access-logfile - --error-logfile - web_app:app"]
