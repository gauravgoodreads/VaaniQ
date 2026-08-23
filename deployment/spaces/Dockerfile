# syntax=docker/dockerfile:1
# Optional Hugging Face Spaces image — API on port 7860 (OQ-020 / ROADMAP-062).
# Primary local demo remains deployment/docker-compose.yml.

FROM python:3.11-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    VAANIQ_ENV=prod \
    VAANIQ_LOG_LEVEL=INFO \
    VAANIQ_API_HOST=0.0.0.0 \
    VAANIQ_API_PORT=7860 \
    VAANIQ_CORS_ORIGINS=http://localhost,http://127.0.0.1

WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:0.8.4 /uv /usr/local/bin/uv
COPY backend/pyproject.toml backend/README.md ./
COPY backend/src ./src
COPY configs ./configs
COPY backend/alembic.ini ./alembic.ini

RUN uv pip install --system --no-cache "." \
    && apt-get update \
    && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

EXPOSE 7860

HEALTHCHECK --interval=15s --timeout=5s --start-period=25s --retries=5 \
  CMD curl -fsS "http://127.0.0.1:7860/health" || exit 1

CMD ["uvicorn", "vaaniq.api.app:create_app", "--factory", "--host", "0.0.0.0", "--port", "7860"]
