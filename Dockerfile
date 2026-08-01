# syntax=docker/dockerfile:1.7
FROM python:3.12-slim AS builder

ARG CORE_SOURCE=git+https://github.com/YutakaX17/advanced-hello-world-be-core.git@main
ENV PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /build
RUN apt-get update \
    && apt-get install --yes --no-install-recommends git \
    && rm -rf /var/lib/apt/lists/*
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN pip install --upgrade pip
COPY pyproject.toml README.md ./
COPY src ./src
RUN pip install "${CORE_SOURCE}" .

FROM python:3.12-slim
ENV PATH="/opt/venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    DJANGO_SETTINGS_MODULE=advanced_hello_world.settings.production
WORKDIR /app
RUN addgroup --system app && adduser --system --ingroup app app
COPY --from=builder /opt/venv /opt/venv
COPY manage.py ./
COPY scripts ./scripts
RUN chmod +x scripts/entrypoint.sh && chown -R app:app /app
USER app
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/api/v1/health/live')"
ENTRYPOINT ["./scripts/entrypoint.sh"]
CMD ["serve"]
