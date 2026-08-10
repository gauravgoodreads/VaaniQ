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

## CORS

Never `allow_origins=["*"]` outside a local-only profile (REQ-136). Compose sets
explicit localhost origins.

## Environments

| Env | Config overlay |
|-----|----------------|
| local | `configs/env/local.yaml` |
| dev | `configs/env/dev.yaml` |
| prod | `configs/env/prod.yaml` |

## TODO

- TODO(ROADMAP-062): HF Spaces Dockerfile / Space README
- TODO(ROADMAP-058): Node BFF reverse-proxy topology (OQ-026)
- TODO(ROADMAP-063): open release packaging + ethics statement
