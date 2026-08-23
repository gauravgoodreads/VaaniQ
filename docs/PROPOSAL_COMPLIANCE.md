# Proposal compliance (Phase 5)

Source of truth: `docs/source/Capstone_Project_Proposal.md`. PPT is supplementary. **Complete** means implemented, tested, and (for RQs) runnable on real curated data. Fixture/demo numbers are not dissertation results.

Status key: **Implemented** (software + intended data path exists) · **Partial** (software exists; real experiment incomplete) · **Missing**.

## Research questions (proposal §4)

| ID | Question | Status | Evidence | Gap |
|----|----------|--------|----------|-----|
| RQ1 | Opus vs clean degradation | **Partial** | Opus compressor, compression suite, cross-condition matrix, SVG/CSV | No curated-hour EER deltas |
| RQ2 | Multilingual vs English-only | **Partial** | AASIST-style head, LFCC-GMM, RawNet2, English-only baseline class, EER/min-DCF | No ASVspoof ingest + GPU train on real hours |
| RQ3 | Unseen Indian language (HI+MR→TA and permutations) | **Partial** | `leave_one_language_folds`, cross-lingual suite | Real embeddings / hours |
| RQ4 | Calibration under compression | **Partial** | Temperature scaling, ECE, Brier, diagrams; fit/eval split in suite | Manifest val/test cells on real logits (OQ-032) |
| RQ5 | Human vs model | **Partial** | Protocol, anonymous UUID, 36 clips, 1–5 confidence, timing, CSV, McNemar helper, UI | Field N ≥ 12–15 (proposal ~20–30 listeners) |

Tamil is the third language. Telugu is not in scope (REQ-139).

## Objectives (proposal §6)

| ID | Objective | Status | Notes |
|----|-----------|--------|-------|
| O1 | Dataset | **Partial** | Parsers, manifests, explorer, clip schema. Gated downloads and 50–100 h/lang not executed here. |
| O2 | Compression robustness | **Partial** | WhatsApp-style Opus sim, resample ladder (OQ-038), packet-loss SHOULD (OQ-037). ffmpeg host-dependent. |
| O3 | Benchmarked model | **Partial** | Frozen XLS-R path + NumPy AASIST-style vs three baselines. Not clovaai graph AASIST. |
| O4 | Generalisation study | **Partial** | Cross-lingual and cross-condition runners exist. Paper tables need real scores. |
| O5 | Calibrated reliability | **Partial** | ECE, reliability diagrams, Brier, T-scaling, reliability badge. Demo can show fitted T=1. |
| O6 | Human baseline | **Partial** | Software complete. Collection remaining. |
| O7 | Demo | **Implemented** | Upload, live session, confidence, reliability flag, explain views, compose stack. |
| O8 | Publication | **Partial** | SVG/CSV/report generators. No arXiv draft (ROADMAP-064). |

## Methodology mapping (proposal §7)

| Section | Topic | Status |
|---------|-------|--------|
| §7.1 | Dataset layers (Kathbath, IndicVoices-R, Common Voice, team, IndicSynth, Parler/XTTS) | Partial — adapters/configs; no full hours |
| §7.2 | Architecture: frozen XLS-R + AASIST on cache | Partial — cache + NumPy head |
| §7.3 | Baselines LFCC-GMM, RawNet2, English-only | Partial — modules exist |
| §7.4 | EER, min-DCF, cross-lingual, cross-condition | Partial — **EER now class-conditional** (was joint; fixed this audit) |
| §7.5 | T-scaling, ECE, Brier, entropy/coverage | Partial |
| §7.6 | Human study | Partial (no N) |
| §7.7 | Grad-CAM / bands / artifacts | Implemented as proxy (OQ-034) |
| §7.9 | Web app three-tier | Partial — FastAPI + React + nginx; **no Node BFF** (OQ-026) |

## Datasets (proposal §10)

Configs and parsers: Kathbath, IndicVoices-R, Common Voice (hi/mr), IndicSynth, generated audio, team recordings. **Missing in this environment:** gated downloads, hour report vs 50–100 h/lang (OQ-002).

## Metrics

| Metric | Status |
|--------|--------|
| EER | Implemented (class-conditional FPR/FNR) |
| min-DCF | Implemented (OQ-018 ASVspoof-style costs) |
| Accuracy / P / R / F1 | Implemented |
| ROC-AUC / PR | Implemented |
| Confusion | Implemented |
| Bootstrap CI | Implemented (OQ-009) |
| ECE / Brier / reliability diagram / coverage curve | Implemented |

## Dashboard / deployment

| Item | Status |
|------|--------|
| Research dashboard | Implemented (verdict, ECE, clip counts) |
| docker-compose API + Postgres + nginx | Implemented |
| HF Spaces Dockerfile | Implemented (`deployment/spaces/`) |
| Node request layer | Missing (documented OQ-026) |

## Success criteria (proposal §17)

| Criterion | Status |
|-----------|--------|
| Detector better than chance on held-out Indic test | Partial (demo path only) |
| Calibration improves ECE in majority of cells | Partial (suite exists) |
| ≥12–15 human responses analysed | Missing |
| Demo returns confidence + reliability + ≥1 explain view | Implemented |

## Examiner note

Marking RQ1–RQ5 **complete** would be a defect. The honest claim is: the **experimental apparatus** exists; **empirical answers** do not, until curated audio and listeners are run through it.
