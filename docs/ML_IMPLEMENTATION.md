# VaaniQ — ML Implementation

> Research ML stack for ROADMAP-029–057 (models → train → eval → calibration → explain → app).
> Human-study tooling, publication packaging, and HF Spaces deploy are **out of scope** here.

## Completed components

| Area | Modules | ROADMAP |
|------|---------|---------|
| Frozen XLS-R + cache | `features/xlsr`, `features/cache` | 025–028 |
| AASIST head | `models/aasist` | 029 |
| Trainer (seed, val, early stop, ckpt, resume, AMP probe, TB/CSV) | `training/*` | 030 |
| LFCC+GMM, RawNet2, English-only control | `models/baselines/*` | 031–033 |
| Registry | `models/registry` | 035 |
| EER, minDCF, ROC/PR, confusion, matrices, reports | `evaluation/*` | 036–041 |
| Temperature, ECE, Brier, entropy, coverage, badge | `calibration/*` | 043–047 |
| Grad-CAM proxy, bands, spectrogram, compression artifacts | `explainability/*` | 049–052 |
| Upload / infer / live / history / metrics API | `api/v1/routers/ml.py` | 054–057 |
| React pages | `frontend/src/pages/*` | 054–056 |

## Design notes

- CI uses **NumPy** paths (no torch required). Optional `[ml]` enables real XLS-R HF weights, torch AMP, and TensorBoard.
- AASIST is an **AASIST-style residual attention head** on pooled XLS-R embeddings (proposal REQ-038–041). Hyperparameters marked `# ASSUMPTION: OQ-014`.
- min-DCF costs: `# ASSUMPTION: OQ-018`. Badge policy: `# ASSUMPTION: OQ-010`. Streaming window: `# ASSUMPTION: OQ-019`.
- English-only baseline: `# ASSUMPTION: OQ-015` (ASVspoof 2019 LA).

## Explicitly deferred

- ROADMAP-059 human-study export / hosting
- ROADMAP-062–064 deployment / ethics packaging / paper draft
- ROADMAP-027 Colab/Kaggle notebooks
- Full clovaai/aasist graph parity on GPU hosts (swap NumPy head for torch AASIST when reproducing paper numbers)
