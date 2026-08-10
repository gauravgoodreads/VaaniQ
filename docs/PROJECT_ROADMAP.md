# VaaniQ — Project Roadmap

> Phase 0 Step 5. Phases P1–P9 with ROADMAP task IDs, REQ coverage, dependencies, exit criteria, risks.
> Cross-refs: `REQUIREMENTS.md`, `SYSTEM_ARCHITECTURE.md`, `OPEN_QUESTIONS.md`, `PROJECT_ANALYSIS.md`.

---

## Phase overview

| Phase | Goal | Depends on |
|-------|------|------------|
| P1 | Foundation & scaffold | Phase 0 docs approved |
| P2 | Dataset pipeline & metadata store | P1; OQ-001, OQ-003 resolved |
| P3 | Audio + compression pipeline | P2; OQ-007 |
| P4 | Embedding extraction & caching | P3; OQ-013 |
| P5 | Model, training loop, baselines | P4; OQ-014, OQ-015 |
| P6 | Evaluation engine & research metrics | P5 |
| P7 | Calibration engine | P6 |
| P8 | Explainability engine | P5 (model), P6 (eval hooks) |
| P9 | Web app, real-time, human study, deployment | P7, P8 |

---

## P1 — Foundation & scaffold

**Goal:** Repo structure, tooling, config, logging, DI, typed schemas, Docker/CI skeletons, zero ML bodies.

| ID | Task | REQs |
|----|------|------|
| ROADMAP-001 | Repo init, gitignore/gitattributes, LICENSE, pre-commit | REQ-001, 139 |
| ROADMAP-002 | Backend package + pyproject (ruff, mypy, pytest) | INFRA |
| ROADMAP-003 | `core/types` Language={HI,MR,TA}, ports ABCs | REQ-132, 139; Architecture §9 |
| ROADMAP-004 | Config system (yaml→env→CLI) | INFRA |
| ROADMAP-005 | Observability (structlog, request IDs) | INFRA |
| ROADMAP-006 | Persistence models + Alembic | Architecture §8 |
| ROADMAP-007 | FastAPI app factory, health, 501 stubs | REQ-134 |
| ROADMAP-008 | Frontend Vite/React/TS shell + routing | REQ-134 |
| ROADMAP-009 | Docker compose + CI + Makefile | REQ-112 |
| ROADMAP-010 | Docs skeleton + README quickstart | REQ-001, 119–120 |

**Exit:** `make check` green; no Telugu language codes; no ML algorithms.

---

## P2 — Dataset pipeline & metadata store

**Goal:** Sources, manifests, speaker-disjoint splits, consent log.

| ID | Task | REQs |
|----|------|------|
| ROADMAP-011 | DatasetSource adapters + gated access docs | REQ-101–106, 130 |
| ROADMAP-012 | ClipMetadata Pydantic schema + validators | REQ-131–133 |
| ROADMAP-013 | Curate HI/MR/TA real subsets (Kathbath, IV-R, CV) | REQ-025–028, 003 |
| ROADMAP-014 | Sample IndicSynth fakes | REQ-030, OQ-004 |
| ROADMAP-015 | Team recordings + consent refs | REQ-029, 074 |
| ROADMAP-016 | Parler-TTS / XTTS fraud-pattern supplement | REQ-031–033, OQ-006 |
| ROADMAP-017 | Versioned speaker-disjoint split manifests | REQ-099, OQ-008 |
| ROADMAP-018 | Dataset report (hours/lang) | REQ-034, OQ-002 |

**Exit:** Manifests for all three languages with real+fake labels; licence matrix published.

**Risks:** Gated HF access delays; Tamil real-data gap (OQ-003).

---

## P3 — Audio + compression pipeline

**Goal:** Decode, preprocess, Opus twins.

| ID | Task | REQs |
|----|------|------|
| ROADMAP-019 | AudioLoader + fallback decoder | REQ-094 |
| ROADMAP-020 | Preprocessor (resample, trim, normalize) | REQ-098 |
| ROADMAP-021 | FFmpegOpusCompressor (config-driven) | REQ-113, 018, OQ-007 |
| ROADMAP-022 | Pair clean↔compressed (`pair_id`) | REQ-035, OQ-028 |
| ROADMAP-023 | Optional noise / bitrate ladder | REQ-018, OQ-012, OQ-023 |
| ROADMAP-024 | Property tests for audio transforms | INFRA |

**Exit:** 100% curated clips have Opus twins; compressor unit/integration tests pass.

---

## P4 — Embedding extraction & caching

**Goal:** Frozen XLS-R once; durable cache.

| ID | Task | REQs |
|----|------|------|
| ROADMAP-025 | FrozenXLSRExtractor (300m) | REQ-036, 041, OQ-013 |
| ROADMAP-026 | Filesystem embedding cache + keys | REQ-037 |
| ROADMAP-027 | Colab/Kaggle extraction notebooks | REQ-108 |
| ROADMAP-028 | Cache checksum verification | REQ-137 |

**Exit:** Embeddings for train/val/test recoverable without GPU on subsequent runs.

---

## P5 — Model, training loop, baselines

**Goal:** AASIST head + baselines + English-only control.

| ID | Task | REQs |
|----|------|------|
| ROADMAP-029 | AASISTClassifier on cached embeddings | REQ-038–040, 107 |
| ROADMAP-030 | Trainer, seed, run manifest | REQ-137–138, OQ-014 |
| ROADMAP-031 | LFCC+GMM baseline | REQ-042 |
| ROADMAP-032 | RawNet2 baseline | REQ-043 |
| ROADMAP-033 | English-only ASVspoof control | REQ-044, OQ-015 |
| ROADMAP-034 | Optional acoustic aux ablation | REQ-095, OQ-033 |
| ROADMAP-035 | Model registry entries | Architecture §8 |

**Exit:** Four comparable models train end-to-end on cached features; manifests written.

---

## P6 — Evaluation engine & research metrics

**Goal:** Answer RQ1–RQ3 tables.

| ID | Task | REQs |
|----|------|------|
| ROADMAP-036 | EER + min-DCF metrics | REQ-046–047, OQ-018 |
| ROADMAP-037 | Acc/P/R/F1, ROC/AUC | REQ-050–051 |
| ROADMAP-038 | Cross-lingual matrix | REQ-048, 121 |
| ROADMAP-039 | Cross-condition matrix | REQ-049, 122 |
| ROADMAP-040 | Confusion + per-language/attack/compression slices | REQ-052–053, 080–081 |
| ROADMAP-041 | Eval report generator | REQ-118 |
| ROADMAP-042 | Bootstrap CIs / stats helpers | OQ-009 |

**Exit:** Success criteria REQ-121–122 satisfied (honest numbers OK).

---

## P7 — Calibration engine

**Goal:** Answer RQ4.

| ID | Task | REQs |
|----|------|------|
| ROADMAP-043 | TemperatureScaler per language×condition | REQ-054–056, OQ-031 |
| ROADMAP-044 | ECE + reliability diagrams | REQ-057–058, OQ-017 |
| ROADMAP-045 | Brier score | REQ-059 |
| ROADMAP-046 | Entropy + coverage curves | REQ-060–061 |
| ROADMAP-047 | Reliability badge policy | REQ-062, OQ-010 |
| ROADMAP-048 | Majority-cell ECE improvement check | REQ-063 |

**Exit:** Calibration report published; REQ-063 boolean evaluated.

---

## P8 — Explainability engine

**Goal:** Mechanistic views for RQ1/RQ4 story.

| ID | Task | REQs |
|----|------|------|
| ROADMAP-049 | Grad-CAM temporal heatmap | REQ-075, OQ-034 |
| ROADMAP-050 | Frequency-band importance ablation | REQ-076, 082 |
| ROADMAP-051 | Spectrogram clean vs compressed view | REQ-077 |
| ROADMAP-052 | Compression-artifact visualisation | REQ-078 |
| ROADMAP-053 | Wire explain artefacts into API | REQ-089 |

**Exit:** At least one explain view per demo inference (feeds REQ-124).

---

## P9 — Web app, real-time, human study, deployment

**Goal:** O7 demo + O6 human baseline + O8 release path.

| ID | Task | REQs |
|----|------|------|
| ROADMAP-054 | Upload/inference UI (waveform, verdict, confidence, badge) | REQ-084–091 |
| ROADMAP-055 | Live MediaRecorder sliding-window mode | REQ-096, OQ-019 |
| ROADMAP-056 | Research metrics / calibration / explain pages | REQ-134, 140 |
| ROADMAP-057 | Upload validation + CORS hardening | REQ-135–136 |
| ROADMAP-058 | Node BFF (if deferred in P1) | REQ-092, OQ-026 |
| ROADMAP-059 | Human-study hosting + export schema | REQ-064–073 |
| ROADMAP-060 | Collect ≥12–15 responses; analyse vs model | REQ-123, 070–071 |
| ROADMAP-061 | E2E smoke: upload→confidence+flag+explain | REQ-023, 124 |
| ROADMAP-062 | HF Spaces / compose deploy docs | REQ-112, OQ-020 |
| ROADMAP-063 | Open release packaging + ethics statement | REQ-024, 127, OQ-035 |
| ROADMAP-064 | Paper draft structured on RQ1–RQ5 | REQ-128 |

**Exit:** All five binary success criteria (REQ-063, 121–124) true; demo smoke green.

---

## Risk register

| Risk | Likelihood | Impact | Mitigation | Trigger |
|------|------------|--------|------------|---------|
| Gated dataset config mismatch | Med | High | Fail-fast loader; early README confirm (REQ-130) | First download errors |
| Tamil real/fake data thin | Med | High | OQ-003/004; Parler-TTS TA supplement | Hour report < floor |
| TTS quality varies by language | Med | Med | Manual QC; document limitation | QC fail rate > threshold |
| Novelty narrowed by new papers | Med | Med | Literature refresh log (REQ-129) | New ACL/IS arXiv hit |
| Baseline reproduction overrun | Med | High | Start from clovaai/aasist | >1 week blocked on RawNet2 |
| Human-study N < 20 | Med | Med | Recruit early; floor 12–15 (REQ-123) | <12 one week before Review 3 |
| Calibration/human scope creep | Med | High | Fixed module boundaries in roadmap | New OQ without ROADMAP id |
| Free-tier GPU exhaustion | Med | Med | Cache embeddings; reserve GPU for extract/gen only | Colab quota errors |
| Opus params unrepresentative of WhatsApp | Med | Med | Document simulation limit (§18); OQ-007 sensitivity | Reviewer challenge |
| Node+FastAPI split delays demo | Low | Med | OQ-026 FastAPI-first; BFF later | P9 schedule slip |
| IndicSynth NC licence blocks full open dump | Med | High | OQ-035 dual release strategy | Pre-arXiv legal review |
| English-only baseline unfair mismatch | Low | Med | Matched eval protocol; disclose ASVspoof domain shift | RQ2 table disputed |

---

## Review timeline alignment (Topic Approval Slide 16)

| Review | Expected phase progress |
|--------|-------------------------|
| Review 1 | Topic + lit + verified tools (Phase 0 done) |
| Review 2 | Dataset + baselines + 50–70% modules (≈ P2–P5) |
| Review 3 | Full eval, calibration, human study, explainability (≈ P6–P9) |
| Final | RQ1–RQ5 dissertation + open release |

---

## ID index

`ROADMAP-001` … `ROADMAP-064` are the only legal references for `TODO(ROADMAP-###)` / `NotImplementedError` / `@pytest.mark.xfail` in later phases.
