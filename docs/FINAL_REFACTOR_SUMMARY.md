# Final refactor summary (Phase 5)

Safe refactors and defect fixes after the principal-engineer audit. Public HTTP paths were not renamed. No AASIST/trainer rewrite. No extra languages.

## Correctness

| Change | Why |
|--------|-----|
| Class-conditional FPR/FNR in `equal_error_rate` / `min_dcf` | Joint `mean(pred & y==0)` is not FPR; a 6-real/2-fake equal-score case would have reported 0.75 instead of 1.0. |
| Calibration suite fit/eval split (`n ≥ 4`) | Temperature must not be fit on the logits it is scored on (proposal §7.5 / OQ-032 spirit). |
| Known-answer unit tests for EER and `n_fit`/`n_eval` | Prevents regression of the two metric bugs. |

## Security / API

| Change | Why |
|--------|-----|
| Object-store key `uploads/{uuid}` | User filenames must not enter filesystem paths. |
| Duration and `Language` → HTTP 400 | Avoid 500s and unbounded decode. |
| Validator `max_bytes` from `AppConfig` | Size limit was previously a disconnected default. |
| Prod OpenAPI/Swagger disabled | Lab demo must not ship Swagger on `VAANIQ_ENV=prod`. |
| nginx no longer proxies `/docs` to FastAPI | SPA docs route must work. |
| Compose Postgres bound to `127.0.0.1` | Default `vaaniq/vaaniq` must not listen on all interfaces. |

## Data / ML leakage footguns (warn, do not break callers)

| Change | Why |
|--------|-----|
| Trainer logs when val is omitted (train prefix) | Silent leakage. |
| Splitter logs missing `speaker_id` singleton buckets | Speaker-disjoint splits become clip-disjoint. |

## Database

| Change | Why |
|--------|-----|
| Alembic `0004_query_indexes` | Additive indexes on clip_id (unique), language, split, speaker, FKs. |
| ORM `index=True` aligned with migration | Schema and models stay consistent. |

## Frontend (production polish, no new product surface)

| Change | Why |
|--------|-----|
| Shared `getJson` | Duplicate fetch wrappers. |
| `QueryStatus` loading/error/empty | Raw JSON dumps and blank pages. |
| Skip-to-content, favicon, reduced-motion already present | a11y. |
| Live-page PCM disclaimer | Do not fake WebM decode. |
| Vitest cleanup + all-route heading smoke | Leftover DOM and untested pages. |

## Tests added this hardening window

- EER class-conditional known answer
- Calibration half-split counts
- Upload oversize / traversal filename / long audio / bad language / prod docs 404
- Index presence after `alembic upgrade head`
- Integration vertical slice: upload → infer → history → research GETs
- Frontend: 14 route headings, skip link

## Deliberately not refactored

- NumPy AASIST-style head → official graph AASIST (needs GPU; proposal §11)
- Process-global `_STATE` in demo services (would be a behavioural rewrite of the demo process)
- Synthetic empty-history metrics payload (flagged in `ML_REVIEW.md` / `KNOWN_LIMITATIONS.md`)
- Adding JWT/auth (not in the proposal)
- Playwright or Node BFF (OQ-026)

## Residual risk (unchanged by design)

See `CODE_REVIEW.md` residual P1 list and `KNOWN_LIMITATIONS.md`.
