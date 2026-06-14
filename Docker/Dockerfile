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

EXPOSE 8080

CMD ["python", "web_app.py"]
