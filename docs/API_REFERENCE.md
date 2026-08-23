# API reference (Phase 4)

> Generated types: `frontend/src/api/generated/`. Do not hand-edit. See also [`API.md`](API.md).

## Health

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/health` | Liveness |
| GET | `/health/ready` | DB probe |
| GET | `/api/v1/version` | Package / env |
| GET | `/api/v1/admin/status` | Hardware + git SHA monitoring hook |

## Inference and demo (O7)

| Method | Path |
|--------|------|
| POST | `/api/v1/uploads` |
| POST | `/api/v1/inference` |
| GET | `/api/v1/history` |
| POST | `/api/v1/live/session` |
| POST | `/api/v1/live/ingest` |
| GET | `/api/v1/explain` |
| GET | `/api/v1/calibration` |
| GET | `/api/v1/metrics` |

## Research catalogue

| Method | Path |
|--------|------|
| GET | `/api/v1/experiments` |
| GET | `/api/v1/experiments/compare?metric=eer` |
| GET | `/api/v1/experiments/search` |
| GET | `/api/v1/experiments/report` |
| GET | `/api/v1/datasets/explorer` |

## Human study (RQ5)

| Method | Path |
|--------|------|
| POST | `/api/v1/human-study/register` |
| POST | `/api/v1/human-study/response` |
| GET | `/api/v1/human-study/export` |
| GET | `/api/v1/human-study/report` |

Errors: RFC 7807 `application/problem+json`. CORS origins from config (never `*` in prod).
When `VAANIQ_ENV=prod`, `/docs`, `/redoc`, and `/openapi.json` are disabled.

## Examples (local)

Liveness:

```bash
curl -s http://127.0.0.1:8000/health
```

Upload then infer (WAV bytes):

```bash
curl -s -F "file=@clip.wav;type=audio/wav" http://127.0.0.1:8000/api/v1/uploads
curl -s -F "file=@clip.wav;type=audio/wav" -F "language=hi" -F "model_id=aasist-v1" \
  http://127.0.0.1:8000/api/v1/inference
```

Unsupported language returns 400 problem+json:

```bash
curl -s -F "language=xx" http://127.0.0.1:8000/api/v1/inference
```

Regenerate types:

```bash
powershell -File scripts/gen_api_types.ps1
```
