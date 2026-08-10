# VaaniQ deployment

Docker Compose brings up **Postgres**, the **FastAPI** API, and the **nginx** SPA
(ROADMAP-009 / REQ-112). ASSUMPTION: OQ-021 — Postgres in compose; SQLite remains
the local non-Docker default.

## Quick start

From the repository root:

```bash
docker compose -f deployment/docker-compose.yml up --build
```

| Service | URL |
|---------|-----|
| Web UI | http://localhost:8080 |
| API (direct) | http://localhost:8000 |
| API via nginx | http://localhost:8080/health , `/api/...` |
| Postgres | localhost:5432 (`vaaniq` / `vaaniq`) |

Dev overlay (bind-mount source, debug logs):

```bash
docker compose -f deployment/docker-compose.yml -f deployment/docker-compose.dev.yml up --build
```

## Healthchecks

Compose waits on `db` → `api` (`GET /health`) → `web` (`GET /healthz`).

## Notes

- Frontend image builds with `VITE_API_BASE_URL=""` so the browser uses same-origin
  requests; nginx proxies `/health` and `/api/` to the API container.
- Do not set `VAANIQ_CORS_ORIGINS=*` in prod (REQ-136).
