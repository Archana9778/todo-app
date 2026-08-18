# ---------- Builder ----------
FROM python:3.12-slim AS builder

WORKDIR /build

COPY app/requirements.txt .

RUN pip install --no-cache-dir --prefix=/install -r requirements.txt


# ---------- Production ----------
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY --from=builder /install /usr/local

COPY app/ .

RUN useradd \
    --create-home \
    --uid 1000 \
    appuser

RUN chown -R appuser:appuser /app

USER appuser

EXPOSE 5000

HEALTHCHECK \
    --interval=30s \
    --timeout=5s \
    --start-period=10s \
    --retries=3 \
    CMD python -c \
    "import urllib.request; urllib.request.urlopen('http://localhost:5000/health')" \
    || exit 1

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
