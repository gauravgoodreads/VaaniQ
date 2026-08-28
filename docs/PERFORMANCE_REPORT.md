# Performance report (Phase 5)

> **Historical engineering-performance snapshot.** This report predates the approved
> Round 3 research baseline and is retained only for CPU/UI performance traceability.
> Its statements about dataset or experiment readiness are not current research claims;
> use `artifacts/final_results_manifest.json` for measured results.

No GPU is assumed on this workstation (proposal §11: Colab T4 / Kaggle). This report is **evidence from local CPU gates**, not a CUDA Nsight profile. Optimisations were applied only where they were correctness-adjacent (indexes, upload key, avoiding extra copies of unsafe filenames).

## What was measured

| Surface | Method | Result |
|---------|--------|--------|
| Backend unit+API tests | `pytest` default suite (171 tests) | **171 passed** in **20.81 s**; coverage **88.90%** of `backend/src` |
| Type/lint | `ruff`, `mypy --strict` | Gate, not a profiler. |
| Frontend | `tsc`, `eslint`, `vitest` | Gate. |
| Bundle | `npm run build` | `dist/assets/index-*.js` **278.77 kB** (gzip **87.86 kB**); CSS **18.28 kB** (gzip **4.61 kB**) |
| GPU utilisation | Not measured | No local GPU. |
| Training throughput | Not measured on curated hours | NumPy toy epochs only. |

## Frontend

- Route-level code splitting is **not** used (`AppRouter` static-imports every page). Acceptable for a 14-page research UI; a FAANG SPA would lazy-load.
- Charts are lightweight SVG (`LineChart`), not a heavy charting library.
- Google Fonts are loaded from the network in `index.html` (Figtree, Literata). Offline/air-gapped exam machines will fall back to system fonts.
- Animations respect `prefers-reduced-motion`.
- Duplicate `fetch` wrappers were removed in favour of one `getJson` (less client work, not a measurable FPS win).

## Backend / inference

- Inference is **synchronous NumPy** on the FastAPI event loop. Under concurrent uploads this becomes the bottleneck.
- Feature extractor may hit Hugging Face weights; CI uses a stats embedding backend.
- Waveform/spectrogram previews downsample in `ml_demo` (stride) before JSON serialisation — necessary to keep payloads small.
- Embedding cache is filesystem-backed; good for repeated clips, useless until freeze-XLS-R runs.

## Training / datasets

- Dataset parsers are streaming/JSONL-oriented. Full Kathbath-scale IO was not profiled (no downloads).
- Speaker-disjoint split is in-memory group-by; fine for tens of thousands of clip rows, not for millions without a DB scan.

## Memory / disk

- Process-global `_STATE` retains history, uploads paths, live sessions, and last report in RAM. Unbounded history is a leak under a public demo.
- Object store writes whole files. `max_upload_bytes` (ASSUMPTION: 26_214_400) and `max_audio_duration_sec` (120) bound disk/CPU.
- Postgres is used in compose; SQLite is the local default (OQ-021).

## Startup

- API imports numpy/soundfile/sqlalchemy. Cold start is dominated by those imports, not route count.
- Frontend Vite dev server is separate from the API (typical 5173 / 8000).

## Caching

| Cache | Role |
|-------|------|
| XLS-R embedding cache | Designed for freeze-once (proposal §7.2) |
| Experiment JSONL store | Research catalogue |
| HTTP | No CDN, no ETag strategy |

## Justified optimisations (this pass)

- Alembic `0004` secondary indexes on `audio_clips.clip_id` (unique), language, split, speaker, FKs — cheap and correct for explorer/study queries **when** the ORM is used.
- Stop concatenating user filenames into store paths (security; also avoids extra directory stats).

## Not done (would be feature-bloat or unjustified without a profile)

- Rewriting AASIST in C++/ONNX.
- Redis, Celery, or embedding microservices.
- Frontend virtual lists (tables are tiny).
- GPU graphs without hardware.

## Recommendation

Profile **after** the first freeze-XLS-R pass on a T4: embedding extract time/clip, cache hit rate, head-train epoch time, and p95 `/api/v1/inference`. Until then, treat this file as a risk register, not a benchmark paper.
