# Hugging Face Spaces (optional publish)

ASSUMPTION: OQ-020 — docker-compose is the primary local demo; Spaces is optional.

## Docker SDK Space

1. Create a Space with **SDK = Docker**.
2. Set the Dockerfile path to `deployment/spaces/Dockerfile` (or copy it to the Space root if the Space is not the full monorepo).
3. HF exposes port **7860**. The image runs uvicorn on that port.
4. Set secrets: `HF_TOKEN` only if gated models/datasets are needed. Never commit tokens.

This image serves the **API** (OpenAPI at `/docs`, health at `/health`). The full nginx SPA is the compose `web` service; for a browser demo on Spaces, use compose on a VM or build the frontend with `VITE_API_BASE_URL` pointing at the Space URL.

## Health / logging

- Liveness: `GET /health`
- Ready: `GET /health/ready`
- Monitoring: `GET /api/v1/admin/status` (hardware + git SHA)
- Logs: JSON `structlog` on stdout (HF log viewer)

## Cloud abstraction

The same `VAANIQ_*` variables in `.env.example` are the contract for local, compose, Spaces, or any VM. Swap `VAANIQ_DATABASE_URL` and `VAANIQ_CORS_ORIGINS`; do not hard-code hosts in application code.
