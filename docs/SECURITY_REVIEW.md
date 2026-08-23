# Security review (Phase 5)

Scope: API, uploads, audio parsing, secrets, auth abstraction, dependencies. This is a **research demo**, not a multi-tenant SaaS. Findings assume an examiner laptop and `docker compose` on a trusted host.

## Summary

Upload validation is real (MIME allow-list, magic bytes, size, duration). Several high-severity issues from the audit are **fixed**. Authentication is **intentionally absent** (no proposal requirement for login). Treat compose Postgres credentials and `/api/v1/admin/status` as lab-only.

## Uploads and audio

| Control | Status |
|---------|--------|
| Size | `MagicByteValidator(max_bytes=config.api.max_upload_bytes)` |
| MIME allow-list | wav / ogg / opus / flac / mpeg / octet-stream |
| Magic bytes | RIFF, OggS, fLaC, ID3, MPEG sync |
| Duration | Rejected if `duration > max_audio_duration_sec` **before** preprocess |
| Path traversal | Object key is `uploads/{uuid}`; `LocalObjectStore` rejects `..` and absolute keys |
| Filename | User filename is metadata only; no longer concatenated onto the store path |

`application/octet-stream` is allowed so some clients can upload without a proper MIME. Magic bytes still must match. Empty files are rejected.

## API

| Issue | Status |
|-------|--------|
| Invalid `Language` | HTTP 400 (`ValidationError`) |
| Unknown `upload_id` | HTTP 400 (was `FileNotFoundError` → 500) |
| RFC 7807 problems | `observability/exception_handlers.py` |
| CORS | From config; prod forbids `*` |
| OpenAPI in prod | `docs_url` / `redoc_url` / `openapi_url` disabled when `env=prod` |
| nginx `/docs` | Proxied to SPA (Swagger stays on API `:8000` in non-prod) |
| `/api/v1/admin/status` | **Unauthenticated** hardware + git SHA. Lab-only. Do not expose on a public IP without a reverse-proxy ACL. |
| Human-study register | Anonymous UUID, no PII fields in the protocol. Export CSV is filesystem path disclosure to the caller. |

## Secrets and environment

- `.env.example` is the documented template; no committed `.env` with live secrets was used in this review.
- Compose Postgres user/password `vaaniq`/`vaaniq` are **defaults**. Port is now bound to `127.0.0.1:5432` so the database is not published on all interfaces.
- Change the password before any shared-host deploy. Do not invent a secret manager this phase.

## Authentication

No user login, no API keys, no CSRF tokens (JSON POST + CORS). `users` table exists in the ER diagram and is unused by inference. Adding JWT now would be scope expansion.

## Dependencies

CI does not run `pip-audit` or `npm audit` by default. Before public deploy: audit `backend/uv.lock` and `frontend/package-lock.json`. Hugging Face / dataset tokens must stay in env, never in git.

## Residual risks

1. Unauthenticated admin and human-study mutation endpoints.
2. Unbounded in-memory history (`_STATE`) — disk/RAM DoS if the demo is public.
3. Sync inference on the event loop — easy to stall.
4. Live ingest accepts raw chunks with little type checking beyond session id.
5. Default DB password if operators republish `5432` on `0.0.0.0`.

## Tests added this pass

- Oversized upload → 400
- Traversal-style filename still infers via UUID key
- Long audio → 400
- Unsupported language → 400
- Prod OpenAPI hidden
