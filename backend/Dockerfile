# syntax=docker/dockerfile:1
# VaaniQ API — multi-stage (deps → runtime), non-root (ROADMAP-009 / REQ-112)

FROM python:3.11-slim-bookworm AS deps

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_LINK_MODE=copy \
    UV_COMPILE_BYTECODE=1

WORKDIR /build

COPY --from=ghcr.io/astral-sh/uv:0.8.4 /uv /usr/local/bin/uv

COPY backend/pyproject.toml backend/README.md ./
COPY backend/src ./src

# ASSUMPTION: OQ-021 — include psycopg for compose Postgres.
RUN uv pip install --system --no-cache ".[postgres]"

# --- runtime ---
FROM python:3.11-slim-bookworm AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    VAANIQ_ENV=prod \
    VAANIQ_LOG_LEVEL=INFO \
    VAANIQ_API_HOST=0.0.0.0 \
    VAANIQ_API_PORT=8000

RUN apt-get update \
    && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/* \
    && groupadd --system --gid 10001 vaaniq \
    && useradd --system --uid 10001 --gid vaaniq --home-dir /app --shell /usr/sbin/nologin vaaniq

WORKDIR /app

COPY --from=deps /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=deps /usr/local/bin /usr/local/bin
COPY backend/alembic.ini ./alembic.ini
COPY configs ./configs

RUN mkdir -p /app/data/object_store /app/data/embedding_cache \
    && chown -R vaaniq:vaaniq /app

USER vaaniq

EXPOSE 8000

HEALTHCHECK --interval=15s --timeout=5s --start-period=20s --retries=5 \
  CMD curl -fsS "http://127.0.0.1:8000/health" || exit 1

CMD ["uvicorn", "vaaniq.api.app:create_app", "--factory", "--host", "0.0.0.0", "--port", "8000"]
