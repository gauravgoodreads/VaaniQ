# API guide

> HTTP surface for VaaniQ (ROADMAP-007 / REQ-134). Types are generated — never hand-edit
> `frontend/src/api/generated/`.

## Live surface (Phase 1)

| Method | Path | Status |
|--------|------|--------|
| GET | `/health` | 200 liveness |
| GET | `/health/ready` | 200 readiness (DB probe) |
| GET | `/api/v1/version` | 200 package/env metadata |
| GET | `/docs` | OpenAPI UI |
| * | `/api/v1/{inference,uploads,history,…}` | **501** + `roadmap_id` |

Errors use RFC 7807 `application/problem+json` (ROADMAP-005).

## OpenAPI → TypeScript

```bash
./scripts/gen_api_types.sh
# Windows: powershell -File scripts/gen_api_types.ps1
# or: cd frontend && npm run gen:api-types
```

CI fails if regenerating produces a diff (`scripts/check_api_types_drift.sh`).

Aliases for schemas live in `frontend/src/api/types.ts` (re-exports from generated
`schema.ts`).

## Auth

- TODO(ROADMAP-062): document admin auth model for demo deploy

## Upload validation

- TODO(ROADMAP-057): MIME / magic / duration / size limits from config (REQ-135)

## Streaming

- TODO(ROADMAP-055): sliding-window live session API (REQ-096, OQ-019)
