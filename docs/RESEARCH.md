# Research guide

> Research questions, metrics, and paper track (REQ-118, REQ-128 / ROADMAP-064).
> **Measured results** live in `artifacts/final_results_manifest.json` (approved commit
> `084bd47ca6ca1b69a7cdbf424e2946f3794c2a95`). Proposal wording below is **planned**.

## Research questions

| RQ | Planned question | Status | Measured result |
|----|------------------|--------|-----------------|
| RQ1 | How does Opus compression affect detection? | **COMPLETE** | Acoustic 93.84%→89.38%; frozen XLS-R 91.44%→92.81% under WhatsApp-style Opus simulation |
| RQ2 | How does English-only anti-spoofing transfer to Indic languages? | **COMPLETE** | English-only 54.8% acc / 76.56% EER / 0.162 AUC vs multilingual Baseline V1 91.61% / 6.56% / 0.9729 |
| RQ3 | How well does the detector generalize to an unseen Indian language? | **COMPLETE** | Hindi 78.83%; Marathi 93.29%; Tamil 93.94% (asymmetric) |
| RQ4 | Does validation-selected calibration remain reliable under shift? | **COMPLETE** | Baseline V1 test ECE 0.0245→0.026; not uniformly improved |
| RQ5 | How does model performance compare with human listeners? | **BLOCKED ON HUMAN DATA** | Human-study protocol ready; participant data collection pending (N=0) |

Authoritative planned wording: `docs/source/Capstone_Project_Proposal.md`.
Authoritative measured numbers: `artifacts/final_results_manifest.json`.

## Metrics (measured on bounded V1 unless noted)

- EER, normalized min-DCF (P_target=0.05, C_miss=C_fa=1)
- Accuracy / precision / recall / F1, ROC-AUC
- Cross-lingual leave-one-language-out matrix
- ECE, Brier, reliability diagrams
- Score contract: label 0=REAL, 1=FAKE; higher `score_fake` = more fake; threshold 0.5

## Human baseline

Forced-choice listening study software is implemented (`make analyze-human-study`).
Human-study protocol ready; participant data collection pending (N=0). There are no
human accuracy or model-versus-human results.

## Paper track

IEEE-style paper: `docs/VaaniQ_IEEE_Research_Paper_Final.docx`  
Manuscript notes: `research/paper/manuscript/VaaniQ_manuscript.md`
