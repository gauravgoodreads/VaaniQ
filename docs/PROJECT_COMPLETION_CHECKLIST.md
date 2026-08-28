# Project completion checklist (Phase 4)

> Maps implemented software to research questions (proposal §4), objectives (proposal §6),
> proposal sections, and dissertation chapter analogues.
>
> **Complete** means a meaningful experiment has sufficient data, valid protocol,
> persisted evidence, and final metrics. The frozen source is
> `artifacts/final_results_manifest.json`.

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
| RQ1 | Opus degradation vs clean | **Complete** | Acoustic and frozen XLS-R clean/Opus cells | — |
| RQ2 | Multilingual vs English-only | **Complete** | English-only ASVspoof control on Indic test | — |
| RQ3 | Unseen Indian language | **Complete** | Three leave-one-language-out folds | — |
| RQ4 | Calibration under shift | **Complete** | Validation selection plus held-out ECE | — |
| RQ5 | Human vs model | **Blocked on human data** | Protocol, UI, export, stats | Real participants; N=0 |

## Objectives

| ID | Item | Status | Evidence | Remaining |
|----|------|--------|----------|-----------|
| O1 | Dataset | **Complete for bounded V1; V2 partial** | Versioned speaker-disjoint manifests | Balance V2 source×label |
| O2 | WhatsApp simulation | **Complete** | Paired 16 kbps libopus twins | — |
| O3 | Benchmarked model | **Complete except faithful RawNet2** | Acoustic, XLS-R, LFCC-GMM, approximate RawNet2-style, English control | Faithful RawNet2 |
| O4 | Generalisation study | **Partial externally** | RQ3 complete; FLEURS pilot | Generator-disjoint n=0 |
| O5 | Calibrated reliability | **Complete** | Validation-selected strategy and held-out negative result | — |
| O6 | Human baseline | **Blocked on human data** | Software complete | Field collection; N=0 |
| O7 | Live demo | **Complete** | Upload/live/confidence/badge/explain + compose | Node BFF optional |
| O8 | Publication | **Complete for capstone** | Frozen manifest, IEEE paper, master document, reports | External submission optional |

## Proposal sections (software coverage)

| Section | Topic | Status |
|---------|-------|--------|
| §7.1 Dataset | Manifest/pipeline | V1 complete (bounded); V2 partial |
| §7.2 Compression | WhatsApp-style Opus simulation | RQ1 complete |
| §7.3 Model | Acoustic / frozen XLS-R + AASIST-compatible head | Complete; not canonical AASIST |
| §7.4 Eval matrices | Cross-lingual / condition | RQ1 and RQ3 complete |
| §7.5 Calibration | ECE, T-scaling, badge | RQ4 complete (val-selected; test ECE slightly worsened) |
| §7.6 Human study | Listening test | Protocol complete; N=0 |
| §7.7 Explainability | Grad-CAM / bands / artifacts | Complete as proxy (OQ-034) |
| §7.9 Web app | Three-tier | Complete (FastAPI+React; no Node BFF) |
| §8 Pipeline | End-to-end | Complete on bounded V1 |
| §10 Inventory | Sources | Complete as configs/adapters |
| §11 Compute | Colab/Kaggle | Remaining (no local GPU assumed) |
| §17 Success criteria | Binary gates | See below |
| §18 Limitations | Documented | Complete as `KNOWN_LIMITATIONS.md` |
| §20 Open release | Licence | Remaining (OQ-035) |
| §21 Venue | ICCCNT/ICACCS/INDICON | Remaining (OQ-029) |

## Success criteria (proposal §17 / REQ-121–124)

| Criterion | Status |
|-----------|--------|
| Detector better than chance on held-out Indic test | **Complete** on bounded V1 |
| Calibration improves ECE in majority of cells | **Not supported**; Baseline V1 held-out ECE slightly worsened |
| ≥12–15 human responses analysed | **Remaining** |
| Demo returns confidence + reliability flag + ≥1 explain view | **Complete** (software) |

## Phase 4 prompt steps

| Step | Status | Notes |
|------|--------|-------|
| 1 Experiment framework | **Complete** | JSONL store + compare/search |
| 2 Cross-lingual experiments | **Complete** | RQ3 measured |
| 3 Compression robustness | **Complete** | RQ1 measured |
| 4 Calibration studies | **Complete** | RQ4 measured |
| 5 Human baseline module | **Complete** (software) | Collection remaining |
| 6 Explainability expansion | **Complete** (proxy) | Graph CAM remaining |
| 7 Error analysis | **Complete** | Markdown reports |
| 8 Report generation | **Complete** | Seven report types |
| 9 Frontend enhancements | **Complete** | Dark mode already present; gauges/explorer added |
| 10 Deployment | **Partial** | Compose+health; Spaces Dockerfile added, not published |
| 11 Code quality | **Partial** | Gates run this phase; 80% coverage target |
| 12 Publication support | **Complete for capstone** | IEEE paper regenerated from frozen metrics |
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

1. Complete and balance Benchmark V2.
2. Run generator-disjoint evaluation; current n=0.
3. Implement faithful RawNet2.
4. Collect human-study responses; current N=0.
5. Resolve licensing/ethics requirements for any open audio release.

## Recommended next steps for publication and capstone submission

1. Freeze configs (`configs/eval/research_conditions.yaml`, train YAML) and git SHA on every table.
2. Produce RQ1–RQ4 tables from the experiment store; paste SVGs into the dissertation.
3. Run the human study on the **same clip IDs** used for model scores.
4. Copy `KNOWN_LIMITATIONS.md` into dissertation Ch.7.
5. Keep RQ5, V2, generator-disjoint, and faithful RawNet2 labelled as blocked/partial/pending. Do not invent human results.
