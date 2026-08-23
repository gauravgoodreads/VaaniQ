# API guide

> HTTP surface for VaaniQ. Types are generated — never hand-edit
> `frontend/src/api/generated/`. Full table: [`API_REFERENCE.md`](API_REFERENCE.md).

## Live surface

Health, inference, live, calibration, explain, experiments (list/compare/search/report),
datasets explorer, human-study register/response/export/report, admin status.

Errors use RFC 7807 `application/problem+json` (ROADMAP-005).

## OpenAPI → TypeScript

```bash
./scripts/gen_api_types.sh
# Windows: powershell -File scripts/gen_api_types.ps1
# or: cd frontend && npm run gen:api-types
```

CI fails if regenerating produces a diff (`scripts/check_api_types_drift.sh`).

## Auth

Demo has no login. Human-study IDs are anonymous UUIDs (REQ-069).
Admin is a monitoring hook, not an authz system.

## Upload validation

MIME / magic / duration / size from config (REQ-135) on the ML upload path.

## Streaming

Sliding-window live session API (REQ-096, OQ-019): `POST /api/v1/live/session`, `POST /api/v1/live/ingest`.
