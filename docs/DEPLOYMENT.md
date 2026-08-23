# Deployment guide

> Ops & demo hosting (ROADMAP-009, ROADMAP-062 / REQ-112). ASSUMPTION: OQ-020 —
> docker-compose for development; HF Spaces optional publish.

## Local compose

See [`../deployment/README.md`](../deployment/README.md).

```bash
docker compose -f deployment/docker-compose.yml up --build
```

| Service | Port | Health |
|---------|------|--------|
| web (nginx) | 8080 | `/healthz` |
| api | 8000 | `/health` |
| db (Postgres) | 5432 | `pg_isready` |

ASSUMPTION: OQ-021 — Postgres in compose; SQLite remains non-Docker local default.

## Host dependencies (audio pipeline)

| Tool | Why | Notes |
|------|-----|-------|
| `ffmpeg` | Opus twin generation (ROADMAP-021–023) | Required on training hosts. Unit tests **skip** when missing or when the OS blocks spawn (e.g. Windows Application Control). Install: `winget install Gyan.FFmpeg` (or distro package). Compose API image does not currently embed ffmpeg for twin generation. |

## CORS

Never `allow_origins=["*"]` outside a local-only profile (REQ-136). Compose sets
explicit localhost origins.

## Environments

| Env | Config overlay |
|-----|----------------|
| local | `configs/env/local.yaml` |
| dev | `configs/env/dev.yaml` |
| prod | `configs/env/prod.yaml` |

## Hugging Face Spaces (optional)

See [`../deployment/spaces/README.md`](../deployment/spaces/README.md). ASSUMPTION: OQ-020.

```bash
# API-only image on port 7860
docker build -f deployment/spaces/Dockerfile -t vaaniq-spaces .
docker run --rm -p 7860:7860 vaaniq-spaces
```

## Production environment variables

Copy `.env.example`. Required in compose/prod:

| Variable | Role |
|----------|------|
| `VAANIQ_ENV` | `local` / `dev` / `prod` |
| `VAANIQ_LOG_LEVEL` | JSON structlog level |
| `VAANIQ_DATABASE_URL` | SQLite or Postgres |
| `VAANIQ_CORS_ORIGINS` | Comma-separated; never `*` in prod |
| `VAANIQ_OBJECT_STORE_ROOT` | Uploads |
| `VAANIQ_EMBEDDING_CACHE_ROOT` | XLS-R cache |
| `VAANIQ_SEED` | Default experiment seed |

## Monitoring hooks

- `GET /health` liveness (compose + Docker HEALTHCHECK)
- `GET /health/ready` database
- `GET /api/v1/admin/status` hardware + git SHA
- stdout JSON logs (`structlog`)

## Cloud abstraction

Same `VAANIQ_*` contract on a VM, compose, or Spaces. Do not hard-code hosts.

## TODO

- TODO(ROADMAP-058): Node BFF reverse-proxy topology (OQ-026)
- TODO(ROADMAP-063): open release packaging + ethics statement
- TODO(ROADMAP-062): publish a live Space (Dockerfile exists; not deployed from CI)

