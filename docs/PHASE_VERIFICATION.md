# Phase verification (Phases 1–5)

This file answers: **are all Cursor phases done?**  
**Software: yes, as an implementable research platform.**  
**Empirical dissertation results: no.** Do not treat fixture EER or empty-history metrics as paper numbers.

Status key:

- **Software complete** — module exists, unit-tested, documented, importable.
- **Partial** — software exists; real data, GPU, ffmpeg, or field collection still required.
- **Missing** — not in the repo (called out explicitly).

Languages in code: Hindi (`hi`), Marathi (`mr`), Tamil (`ta`) only.

---

## Phase 1 — Architecture + scaffolding

| Deliverable | Status | Evidence |
|-------------|--------|----------|
| Proposal extracts | Software complete | `docs/source/` |
| REQ / OQ / roadmap | Software complete | `REQUIREMENTS.md`, `OPEN_QUESTIONS.md`, `PROJECT_ROADMAP.md` |
| Hexagonal ports | Software complete | `backend/src/vaaniq/core/ports/` |
| FastAPI factory + health | Software complete | `api/app.py`, `/health`, `/health/ready` |
| React + Vite shell | Software complete | `frontend/src/app/` |
| Config YAML + Pydantic | Software complete | `configs/`, `vaaniq/config/` |
| Compose skeleton | Software complete | `deployment/docker-compose.yml` |
| Telugu guard | Software complete | `scripts/check_no_telugu.py` |

Phase 1 is **done**. Architecture docs were not regenerated in later phases.

---

## Phase 2 — Data pipeline (no AASIST training in this phase)

### Dataset adapters (common `DatasetSourcePort`)

| Source | Adapter | Parser | Config |
|--------|---------|--------|--------|
| Kathbath | `KathbathSource` | `kathbath.py` | `configs/data/kathbath.yaml` |
| IndicVoices-R | `IndicVoicesRSource` | `indicvoices_r.py` | `configs/data/indicvoices_r.yaml` |
| Common Voice | `CommonVoiceSource` | `common_voice.py` | `configs/data/common_voice.yaml` |
| IndicSynth | `IndicSynthSource` | `indicsynth.py` | `configs/data/indicsynth.yaml` |
| Generated audio | `GeneratedAudioSource` | `generated_audio.py` | `configs/data/generated_audio.yaml` |
| Team recordings | `TeamRecordingsSource` | `team_recordings.py` | `configs/data/team_recordings.yaml` |

Shared: download manager + mock + local cache, corpus cache, validators, manifest loader, ID normalizer, statistics, preview, speaker-disjoint splits.

**Partial:** gated Hugging Face downloads and 50–100 h/lang curation (OQ-002) are operator-side. Offline fixtures prove the pipeline.

### Metadata schema (`ClipMetadata` / `audio_clips`)

Required proposal fields are present: id, speaker_id, language (hi/mr/ta), dataset source, real/fake, generation model, compression, sample rate, duration, file size, speaker age, emotion, attack type, recording medium, split, quality, checksum. Optional enrichments: `# ASSUMPTION: OQ-036`.

### Audio processing

Loaders (soundfile + ffmpeg fallback), resample, mono, silence trim, noise floor, peak norm, duration trim, validation, STFT, mel spectrogram, light augmentation. Hypothesis tests on resample/peak.

### Compression

`FFmpegOpusCompressor`, pairing, bitrate metadata. **Partial** on this Windows host if ffmpeg spawn is blocked.

### Embeddings

Frozen XLS-R extractor (inference-only), filesystem cache, batch/resume APIs, mock backend in CI.

### Database

SQLAlchemy models: users, uploads, predictions, experiments, metrics, models, calibration, human study, datasets, audio_clips. Alembic `0001`–`0004`. **Partial:** inference path does not yet persist ORM rows (in-memory demo state).

### Config

Languages, datasets, paths, train/eval/compression/calibration YAML. UI theme is CSS variables, not YAML (acceptable).

### Tests / docs

Unit tests per pipeline; mock manifest fixture. Integration vertical slice added in `tests/integration/test_inference_e2e.py`. Phase 2 progress: `IMPLEMENTATION_PROGRESS.md`.

Phase 2 is **software complete**. It is **not** “production-ready data” until curated hours exist.

---

## Phase 3 — ML pipeline + demo app

| Prompt item | Status | Module |
|-------------|--------|--------|
| Frozen XLS-R | Software complete (CI mock / optional HF) | `features/xlsr` |
| Embedding cache | Software complete | `features/cache` |
| AASIST-style head | Partial vs clovaai graph | `models/aasist` |
| Train / val / ckpt / early stop / resume | Software complete (NumPy) | `training/` |
| Mixed precision / TensorBoard | Software complete when `[ml]` + torch | `trainer.py`, `tracker.py` |
| LFCC-GMM, RawNet2, English-only | Software complete | `models/baselines/` |
| EER, min-DCF, ROC, PR, confusion | Software complete (class-conditional EER) | `evaluation/metrics` |
| Cross-language / condition matrices | Software complete | `evaluation/matrices` |
| Per-language / per-attack reports | Software complete | `evaluation/` |
| Temperature, ECE, Brier, entropy, coverage, badge | Software complete | `calibration/` |
| Grad-CAM proxy, spectrogram, bands, artifacts, attention | Software complete as proxy (OQ-034) | `explainability/` |
| Upload, live, waveform, spectrogram, confidence, badge, history, dashboard | Software complete | API + React pages |

Docs: `ML_IMPLEMENTATION.md`, `TRAINING_GUIDE.md`, `EVALUATION_GUIDE.md`, `NEXT_STEPS.md`.

Phase 3 is **software complete**. Training on real embeddings/GPU is **not** done here.

---

## Phase 4 — Research, experiments, publication support

| Step | Status |
|------|--------|
| 1 Experiment store (id, git, seed, hardware, metrics, RQ tags, compare/search) | Software complete |
| 2 Leave-one-lang-out HI/MR/TA + CSV/SVG | Software complete; real scores Partial |
| 3 Compression ladder, packet loss, resample, degradation curves | Software complete; ffmpeg Partial |
| 4 Calibration suite (fit≠eval for n≥4) | Software complete |
| 5 Human study protocol/UI/CSV/stats | Software complete; N Missing |
| 6 Explainability expansion + explorer | Software complete (proxy) |
| 7 Error analysis markdown | Software complete |
| 8 Seven report types | Software complete |
| 9 Dashboard / gauges / explorer / dark mode | Software complete |
| 10 Docker Compose + Spaces Dockerfile | Software complete; unpublished Partial |
| 11 Coverage ≥80% | Software complete |
| 12 Vector SVG/CSV publication bundle | Software complete; paper Missing |
| 13 Final docs listed in the Phase 4 prompt | Software complete |

`PROJECT_COMPLETION_CHECKLIST.md` maps RQ/O/proposal sections honestly as Partial except O7.

---

## Phase 5 — Audit and hardening

| Deliverable | Status |
|-------------|--------|
| `CODE_REVIEW.md` | Present |
| `PROPOSAL_COMPLIANCE.md` | Present |
| `ML_REVIEW.md` | Present |
| `PERFORMANCE_REPORT.md` | Present (CPU; no GPU profile) |
| `SECURITY_REVIEW.md` | Present |
| `PROJECT_SCORECARD.md` | Present |
| `FINAL_REFACTOR_SUMMARY.md` | Present (this verification pass) |
| `PHASE_VERIFICATION.md` | This file |

Hardening applied: class-conditional EER, calibration split, upload UUID keys, duration/language 400s, prod OpenAPI off, DB indexes, localhost Postgres bind, frontend loading/error/a11y.

---

## End-to-end testing (what exists vs what does not)

| Layer | What runs in default CI | Gap |
|-------|-------------------------|-----|
| Unit | `backend/tests/unit/` (audio, datasets, ML, research, persistence, config) | None material |
| API | `backend/tests/api/test_app.py` | — |
| Integration vertical slice | `backend/tests/integration/test_inference_e2e.py` (upload→infer→history→research GETs) | No real corpus bytes |
| Frontend | Vitest: shell, all 14 routes, languages, skip-link | No Playwright browser e2e |
| Compose | Documented; previously verified healthy on this machine | Not re-run every commit |
| GPU / HF download / human N | Marked integration / operator | Intentionally out of default CI |

---

## What is still not “complete” for a conference paper

1. Curated hours per language (OQ-002).
2. GPU train of frozen-XLS-R + head (and graph AASIST if claiming clovaai parity).
3. RQ1–RQ4 tables from held-out speakers, not fixtures.
4. Human study N ≥ 12–15 on the same clip IDs (RQ5).
5. arXiv / conference draft (O8 / ROADMAP-064).
6. Node BFF (proposal §7.9; OQ-026 — documented, not blocking O7 demo).

Marking Phases 1–5 **software-complete** is correct.  
Marking the **capstone research questions answered** is not.
