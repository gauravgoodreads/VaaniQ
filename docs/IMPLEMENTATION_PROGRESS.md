# VaaniQ — Implementation Progress

> **Historical data-pipeline snapshot (ROADMAP-011–028).** Current measured results
> are in `artifacts/final_results_manifest.json`. This file does not replace
> `docs/PROJECT_ROADMAP.md` or the Round 3 experiment matrix.

## What was completed

### Phase 1 closeout
- Docker Desktop installed (CLI 29.7.2 / Desktop 4.86 / Compose v5.3.1).
- Compose **verified**: `docker compose -f deployment/docker-compose.yml up --build -d`
  → `db`, `api`, `web` healthy; `curl http://127.0.0.1:8000/health` and
  `curl http://127.0.0.1:8080/health` both `{"status":"ok"}`; nginx `/healthz` → `ok`.

### Dataset management (ROADMAP-011, 013–016)
- Shared pipeline under `backend/src/vaaniq/datasets/`:
  download (ABC + LocalCache + Mock), corpus cache, validators, parsers,
  manifest loader, normalizers, statistics, preview.
- Adapters (offline manifest/rows): Kathbath, IndicVoices-R, Common Voice,
  IndicSynth, Team Recordings, GeneratedAudio (Parler-TTS / XTTS).
- Config: `configs/data/generated_audio.yaml` registered in domain loader.
- Fixtures: `backend/tests/fixtures/datasets/mock_manifest.jsonl`.

### Metadata (ROADMAP-012, 017–018)
- Extended `ClipMetadata` optional enrichment fields (`# ASSUMPTION: OQ-036`).
- Pydantic `ClipMetadataModel` + `parse_clip_metadata`.
- ORM: `datasets` + `audio_clips` + Alembic `0002_datasets_audio_clips`.
- Speaker-disjoint splitter (70/15/15, `# ASSUMPTION: OQ-008`) writing versioned JSONL.
- Dataset statistics + preview helpers.

### Audio processing (ROADMAP-019–020, 024)
- SoundFile loader, ffmpeg fallback loader, DefaultPreprocessor, magic-byte validator.
- Pure ops: mono, resample, peak norm, silence trim, duration trim, noise floor.
- Spectrogram / mel utilities; light gain/noise augmentations.
- Hypothesis property tests for resample / peak normalize.

### Compression (ROADMAP-021–023)
- `FFmpegOpusCompressor` from `configs/audio/compression.yaml` (`# ASSUMPTION: OQ-007`).
- Pair id helpers + `CompressionMetadata` (codec, bitrate, ratio, signal loss).
- Bitrate ladder support when enabled in config (`# ASSUMPTION: OQ-012`).
- Unit tests skip when `ffmpeg` is not on PATH.

### Embeddings (ROADMAP-025–028)
- Frozen XLS-R extractor (inference-only; mock backend for unit tests; HF path under `[ml]`).
- Filesystem embedding cache with SHA-256 checksum validation + resume/batch APIs.
- `LocalObjectStore` implemented for blob persistence.

### Other
- `soundfile` added to backend core dependencies.
- Open question **OQ-036** logged for optional metadata enrichment fields.

## Remaining tasks

| Area | Status |
|------|--------|
| Docker compose healthchecks | **Verified** (stack left running) |
| Real gated HF downloads / curated hours | Needs HF token + OQ-001/003 supervisor confirm |
| ffmpeg on Windows PATH for Opus CI | Installed (`Gyan.FFmpeg` 9.0); **spawn blocked** by Application Control on this host — tests skip via usability probe |
| Real XLS-R weights in CI | Optional `[ml]`; integration mark only |
| Colab/Kaggle extraction notebooks (ROADMAP-027) | Not started |
| AASIST training / baselines (ROADMAP-029+) | **Explicitly deferred** |
| Calibration, explainability, human study, live UI | Later phases |

## Testing status

Backend (`backend/`):

```text
ruff check — pass
mypy --strict — pass (137 source files)
pytest tests/unit — 127 passed, 3 skipped (ffmpeg blocked by OS policy), 23 xfailed (P5+ stubs)
coverage ≈ 89% (gate ≥ 80%)
Re-verified after Docker Desktop healthy (2026-08-13).
```

Compression tests skip when ffmpeg is missing **or** on PATH but unusable (WDAC/Application
Control). XLS-R unit tests use a mock backend (no network/GPU).

Docker compose (2026-08-13): `db`/`api`/`web` healthy; `/health` OK on `:8000` and `:8080`.
ffmpeg documented in `docs/DEPLOYMENT.md`.

## Known issues

1. **ffmpeg spawn blocked** on this Windows host by Application Control even after
   `winget install Gyan.FFmpeg` — Opus unit tests skip via usability probe. Unblock
   the binary (or run Opus twins in Linux/Docker/CI) for live compression.
2. **No real corpus bytes in repo** — offline manifests/fixtures prove the pipeline;
   curation is operator-side (gated HF + OQ-001/003).
3. Enrichment field name is `recording_medium` (not `recording_device`) in code/schema;
   documented under OQ-036.

## Recommended next phase

See [`NEXT_STEPS.md`](NEXT_STEPS.md), [`PROJECT_COMPLETION_CHECKLIST.md`](PROJECT_COMPLETION_CHECKLIST.md), and [`PHASE_VERIFICATION.md`](PHASE_VERIFICATION.md).

### Phases 1–5 (software)

| Phase | Software | Empirical / field |
|-------|----------|-------------------|
| 1 Architecture | Complete | n/a |
| 2 Data pipeline | Complete (fixtures/offline) | Curated hours remaining |
| 3 ML + demo app | Complete (NumPy/CI path) | GPU train remaining |
| 4 Research platform | Complete (runners/UI/reports) | RQ tables + human N remaining |
| 5 Audit + hardening | Complete | n/a |

Do not mark RQ1–RQ5 complete until curated audio and listeners are run.

