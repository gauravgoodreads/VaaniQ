# Project completion checklist (Phase 4)

> Maps implemented software to research questions (proposal §4), objectives (proposal §6),
> proposal sections, and dissertation chapter analogues.
>
> **Complete** means implemented, unit-tested, and documented.
> Fixture/demo numbers are **not** treated as dissertation results.

Dissertation chapter analogues (proposal has numbered sections, not named chapters):

| Chapter analogue | Proposal sections |
|------------------|-------------------|
| Ch.1 Introduction | §1–§3 |
| Ch.2 Literature | §5 |
| Ch.3 Methodology | §7–§8 |
| Ch.4 Data | §10 |
| Ch.5 Experimental design | §11–§12 |
| Ch.6 Results | §4 questions + §17 success criteria |
| Ch.7 Limitations | §18 |
| Ch.8 Conclusion / publication | §19–§21 |

---

## Research questions

| ID | Item | Status | Evidence | Remaining |
|----|------|--------|----------|-----------|
| RQ1 | Opus degradation vs clean | **Partial** | Compression suite, Opus compressor, SVG/CSV | Curated-hour EER deltas |
| RQ2 | Multilingual vs English-only | **Partial** | Four classifiers + metrics module | ASVspoof ingest + GPU train |
| RQ3 | Unseen Indian language | **Partial** | Leave-one-lang-out folds HI/MR/TA | Real embeddings / hours |
| RQ4 | Calibration under compression | **Partial** | T-scaling, ECE, diagrams | Val/test from manifests |
| RQ5 | Human vs model | **Partial** | Protocol, UI, export, stats | N≥12–15 on shared audio |

## Objectives

| ID | Item | Status | Evidence | Remaining |
|----|------|--------|----------|-----------|
| O1 | Dataset | **Partial** | Parsers, manifests, explorer | Gated downloads / hour report |
| O2 | WhatsApp simulation | **Partial** | Opus + resample + loss ladder | Reliable ffmpeg on all hosts |
| O3 | Benchmarked model | **Partial** | XLS-R freeze path + NumPy AASIST-style + baselines | clovaai graph AASIST |
| O4 | Generalisation study | **Partial** | Cross-lingual + cross-condition runners | Paper tables |
| O5 | Calibrated reliability | **Partial** | Calibration module + UI | RQ4 result cells |
| O6 | Human baseline | **Partial** | Software complete | Field collection |
| O7 | Live demo | **Complete** | Upload/live/confidence/badge/explain + compose | Node BFF optional |
| O8 | Publication | **Partial** | Vector SVG/CSV/reports | arXiv draft (ROADMAP-064) |

## Proposal sections (software coverage)

| Section | Topic | Status |
|---------|-------|--------|
| §7.1 Dataset | Manifest/pipeline | Partial (no full hours) |
| §7.2 Compression | Opus WhatsApp-style | Partial (ffmpeg host-dependent) |
| §7.3 Model | XLS-R + AASIST vs baselines | Partial (NumPy head) |
| §7.4 Eval matrices | Cross-lingual / condition | Partial (code) |
| §7.5 Calibration | ECE, T-scaling, badge | Partial (demo) |
| §7.6 Human study | Listening test | Partial (no N) |
| §7.7 Explainability | Grad-CAM / bands / artifacts | Complete as proxy (OQ-034) |
| §7.9 Web app | Three-tier | Partial (FastAPI+React+nginx; no Node) |
| §8 Pipeline | End-to-end | Partial without curated data |
| §10 Inventory | Sources | Complete as configs/adapters |
| §11 Compute | Colab/Kaggle | Remaining (no local GPU assumed) |
| §17 Success criteria | Binary gates | See below |
| §18 Limitations | Documented | Complete as `KNOWN_LIMITATIONS.md` |
| §20 Open release | Licence | Remaining (OQ-035) |
| §21 Venue | ICCCNT/ICACCS/INDICON | Remaining (OQ-029) |

## Success criteria (proposal §17 / REQ-121–124)

| Criterion | Status |
|-----------|--------|
| Detector better than chance on held-out Indic test | **Partial** (demo path only) |
| Calibration improves ECE in majority of cells | **Partial** (suite exists; not on real cells) |
| ≥12–15 human responses analysed | **Remaining** |
| Demo returns confidence + reliability flag + ≥1 explain view | **Complete** (software) |

## Phase 4 prompt steps

| Step | Status | Notes |
|------|--------|-------|
| 1 Experiment framework | **Complete** | JSONL store + compare/search |
| 2 Cross-lingual experiments | **Complete** (software) | Real data remaining |
| 3 Compression robustness | **Complete** (software) | ffmpeg remaining on some hosts |
| 4 Calibration studies | **Complete** (software) | |
| 5 Human baseline module | **Complete** (software) | Collection remaining |
| 6 Explainability expansion | **Complete** (proxy) | Graph CAM remaining |
| 7 Error analysis | **Complete** | Markdown reports |
| 8 Report generation | **Complete** | Seven report types |
| 9 Frontend enhancements | **Complete** | Dark mode already present; gauges/explorer added |
| 10 Deployment | **Partial** | Compose+health; Spaces Dockerfile added, not published |
| 11 Code quality | **Partial** | Gates run this phase; 80% coverage target |
| 12 Publication support | **Complete** (path) | SVG/CSV; paper not written |
| 13 Final documentation | **Complete** | This file + companion docs |

## Phase 5 audit (hardening)

| Item | Status |
|------|--------|
| Class-conditional EER / min-DCF | **Complete** |
| Calibration fit ≠ eval (`n ≥ 4`) | **Complete** |
| Upload key / duration / language 400s | **Complete** |
| Prod OpenAPI hidden | **Complete** |
| DB lookup indexes (`0004`) | **Complete** |
| Frontend loading/error/a11y polish | **Complete** |
| Audit docs + scorecard | **Complete** (`CODE_REVIEW.md` … `PROJECT_SCORECARD.md`) |
| `FINAL_REFACTOR_SUMMARY.md` | **Complete** |
| `PHASE_VERIFICATION.md` | **Complete** (software vs empirical split) |
| Integration vertical slice | **Complete** (`tests/integration/test_inference_e2e.py`) |

## Remaining work (do not skip)

1. Ingest real datasets and write the hour report (OQ-002).
2. Train/evaluate on GPU; replace fixture EER.
3. Collect human-study responses (ROADMAP-060).
4. Draft paper (ROADMAP-064).
5. Licence/ethics for open release (ROADMAP-063).
6. Optional Node BFF (ROADMAP-058).

## Recommended next steps for publication and capstone submission

1. Freeze configs (`configs/eval/research_conditions.yaml`, train YAML) and git SHA on every table.
2. Produce RQ1–RQ4 tables from the experiment store; paste SVGs into the dissertation.
3. Run the human study on the **same clip IDs** used for model scores.
4. Copy `KNOWN_LIMITATIONS.md` into dissertation Ch.7.
5. Submit Review 3 with this checklist attached; do not claim RQ answers until the remaining column is empty.
