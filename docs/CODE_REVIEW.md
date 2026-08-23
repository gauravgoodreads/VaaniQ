# Code review (Phase 5)

Principal-engineer audit of VaaniQ as implemented. Findings are from the current tree, not from intent. Severity: **P0** must-fix for correctness or safety, **P1** high, **P2** maintainability.

## Verdict

The repository is a genuine research **system** (ports, config, tests, experiment store), not a notebook demo. It is not a production multi-tenant service and must not be described as having answered RQ1–RQ5 on curated hours. After this audit pass, the worst metric bug (joint vs class-conditional EER) and the upload path-traversal store key are fixed.

## Architecture

| Area | Assessment |
|------|------------|
| Hexagonal / ports | Domain in `core/` has no FastAPI/SQLAlchemy imports. Ports exist for extractors, classifiers, compressors, store, calibrator, explainer, tracker. |
| Composition root | `container.build_container` wires adapters. API deps inject `AppContainer`. |
| Violations | `MlApiService` / `ResearchApiService` keep **process-global** `_STATE`. That is a hidden singleton: tests can leak, workers cannot scale, DI is incomplete. |
| Config | Typed Pydantic `AppConfig` plus domain YAML. Runtime `create_app()` uses `load_config()` (defaults/env). Compose injects `VAANIQ_*`. Operators must not assume YAML files load unless the loader is given those files. |
| Circular imports | None found in `core/` vs `api/`. |

## Code smells and coupling

| Smell | Where | Severity |
|-------|-------|----------|
| God service | `api/services/ml_demo.py` (upload, infer, metrics, live, reports) | P2 |
| Duplicate JSON fetch | Frontend pages each reimplemented `fetch` (consolidated onto `getJson` this pass) | P2, mitigated |
| Dead UI | `PageStub` unused after Phase 4 (removed) | P2, mitigated |
| Magic fallback embedding | `except Exception` then pad waveform into a 1024-D vector (`ml_demo._predict_waveform`) | P1 — silent quality drop; now logged |
| Trainer val leak | Missing `val_features` used a **train prefix** (`trainer.py`). Now warns; still a leakage footgun if callers omit val | P1 |
| Orphan speakers | Missing `speaker_id` → singleton buckets (`speaker_disjoint.py`). Now warned | P1 for RQ validity |
| Demo metrics | `/api/v1/metrics` fabricates scores when history is empty | P1 for examiner honesty — the UI can look like results |
| Calibration cells | Per-language / per-condition named cells reused the same scaler (OQ-031 documented) | P2 |

## Large functions

`MlApiService._predict_waveform`, `Trainer.fit`, `run_calibration_suite`, and several research runners exceed a comfortable review size. Split only if behaviour is preserved; do not rewrite AASIST.

## Duplicate / unused

- Dual docs: `docs/API.md` vs `docs/API_REFERENCE.md`, `DATASETS.md` vs `DATASET.md` — complementary, easy to drift.
- ORM tables exist; **API inference does not persist** `UploadRow` / `PredictionRow`. Schema is ahead of the serving path.
- `frontend/src/api/generated/` is the OpenAPI contract; some UI types remain hand-written in `api/types.ts`.

## Concurrency / async

- FastAPI upload handlers are `async` and `await file.read()`, then call **sync** NumPy inference on the event loop. Fine for local demo; stalls under concurrent uploads.
- `_STATE.sessions` is not locked. Single-process uvicorn is assumed.
- No background job queue for embedding extraction.

## Naming

Languages are consistently `hi` / `mr` / `ta`. `check_no_telugu.py` previously used brace globs that **pathlib does not expand** (`*.{ts,tsx}`), so frontend TS could skip the guard. Globs are now split.

## Dependencies

Backend is `uv`-locked; frontend is npm. Unused Python extras are gated behind `[ml]`. Default CI does not run `pip-audit` / `npm audit` (see `SECURITY_REVIEW.md`).

## Residual P1 list (not rewritten this pass)

1. Move `_STATE` into `AppContainer` or a request-scoped store.
2. Persist uploads/predictions through the ORM, or stop implying the ER diagram is on the live path.
3. Replace empty-history **synthetic metrics** with an explicit empty payload.
4. Decode MediaRecorder WebM to PCM before live ingest (currently documented, not faked).
5. Fit temperature on **manifest val**, not an in-memory half-split of caller logits.

## Fixed in this audit

- Class-conditional EER / min-DCF.
- Calibration suite fit/eval split when `n >= 4`.
- Upload object key `uploads/{uuid}` (no filename concatenation).
- Duration and language validation → HTTP 400.
- Magic-byte validator bound to `max_upload_bytes`.
- Prod OpenAPI/Swagger disabled; nginx no longer steals SPA `/docs`.
- Additive DB indexes (Alembic `0004`).
- Postgres compose port bound to `127.0.0.1`.
- Trainer / splitter leakage warnings.
- Frontend loading/error/empty states, skip link, favicon, shared `getJson`.
