# Proposal compliance

Source of truth for **scope**: `docs/source/Capstone_Project_Proposal.md`.
Source of truth for **measured results**: `artifacts/final_results_manifest.json`
(approved commit `084bd47ca6ca1b69a7cdbf424e2946f3794c2a95`).

Proposal-scale targets (50–100 h/lang, clovaai AASIST, N≈20 listeners) were **not**
met. Bounded V1 experiments **were** run. Fixture/demo numbers are not dissertation
results.

Status key: **COMPLETE** = frozen evidence on bounded V1 · **PARTIAL** = software plus
incomplete planned dimension · **PILOT** = pipeline evidence, not a claim ·
**BLOCKED** = protocol ready, no field data · **Implemented** = software exists.

## Research questions (proposal §4)

| ID | Question | Status | Evidence | Gap vs proposal scale |
|----|----------|--------|----------|------------------------|
| RQ1 | Opus vs clean degradation | **COMPLETE** (bounded V1) | Acoustic 93.84%→89.38%; XLS-R 91.44%→92.81% under WhatsApp-style Opus simulation | Not 50–100 h/lang |
| RQ2 | Multilingual vs English-only | **COMPLETE** (bounded V1) | English-only 54.8% / 76.56% EER / 0.162 AUC vs multilingual 91.61% / 6.56% / 0.9729 | Not full ASVspoof-hours ingest |
| RQ3 | Unseen Indian language | **COMPLETE** (bounded V1) | Leave-one-language-out: hi 78.83%, mr 93.29%, ta 93.94% | Same bounded subset |
| RQ4 | Calibration under compression | **COMPLETE** (bounded V1) | Val-selected per-language×condition; test ECE 0.0245→0.026 | Proposal-scale cells not filled |
| RQ5 | Human vs model | **BLOCKED ON HUMAN DATA** | Protocol, UI, analysis path | N=0; proposal ~20–30 listeners |

Tamil is the third language. Telugu is not in scope (REQ-139).

## Objectives (proposal §6)

| ID | Objective | Status | Notes |
|----|-----------|--------|-------|
| O1 | Dataset | **Partial** | Bounded Kathbath + IndicSynth V1; V2 ingest larger locally. Not 50–100 h/lang. |
| O2 | Compression robustness | **COMPLETE** on bounded V1 | WhatsApp-style Opus simulation (OQ-007). Packet-loss SHOULD (OQ-037). |
| O3 | Benchmarked model | **Partial** | Frozen XLS-R + AASIST-compatible NumPy vs LFCC-GMM and approximate RawNet2. Not clovaai graph AASIST. |
| O4 | Generalisation study | **Partial** | RQ3 COMPLETE on V1. FLEURS frozen eval n=9 PILOT. Generator-disjoint n=0. |
| O5 | Calibrated reliability | **COMPLETE** on bounded V1 | ECE, reliability diagrams, Brier, T-scaling. |
| O6 | Human baseline | **BLOCKED** | Software complete. Collection remaining (N=0). |
| O7 | Demo | **Implemented** | Upload, live session, confidence, reliability flag, explain views. |
| O8 | Publication | **Partial** | IEEE/master docs generated from the frozen manifest. |

## Methodology mapping (proposal §7)

| Section | Topic | Status |
|---------|-------|--------|
| §7.1 | Dataset layers | Partial — bounded V1 + local V2 FLEURS ingest; not full gated hours |
| §7.2 | Architecture: frozen XLS-R + AASIST on cache | Partial — frozen XLS-R path + NumPy AASIST-compatible head |
| §7.3 | Baselines LFCC-GMM, RawNet2, English-only | LFCC-GMM and English-only COMPLETE; RawNet2 is approximate only |
| §7.4 | EER, min-DCF, cross-lingual, cross-condition | COMPLETE on bounded V1 |
| §7.5 | T-scaling, ECE, Brier | COMPLETE on bounded V1 |
| §7.6 | Human study | BLOCKED (N=0) |
| §7.7 | Grad-CAM / bands / artifacts | Implemented as proxy (OQ-034) |
| §7.9 | Web app three-tier | Partial — FastAPI + React + nginx; **no Node BFF** (OQ-026) |

## Datasets (proposal §10)

V1 evaluation subset: Kathbath real + IndicSynth fake, speaker-disjoint 1254/508/584
(n_test=584). Gated full-hour downloads vs 50–100 h/lang were not executed (OQ-002).

## Success criteria (proposal §17)

| Criterion | Status |
|-----------|--------|
| Detector better than chance on held-out Indic test | COMPLETE on bounded V1 (91.61% / 92.12%, n=584) |
| Calibration improves ECE in majority of cells | COMPLETE on bounded V1 (val-selected; see RQ4) |
| ≥12–15 human responses analysed | Missing (N=0) |
| Demo returns confidence + reliability + ≥1 explain view | Implemented |

## Examiner note

RQ1–RQ4 are **COMPLETE on the bounded V1 benchmark**, not at proposal hour scale.
Marking RQ5 complete, or treating FLEURS n=9 / local 150-clip ingest as a finished
external benchmark, would be a defect.
