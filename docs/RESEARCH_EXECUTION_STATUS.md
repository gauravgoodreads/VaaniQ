# Research execution status

Updated from `artifacts/final_results_manifest.json` (approved commit `084bd47`).

Statuses: **COMPLETE** = sufficient persisted evidence; **PARTIAL** = meaningful experiment
with a planned dimension incomplete; **PILOT** = pipeline evidence insufficient for a
research claim; **PENDING** = locally actionable work remains; **BLOCKED ON HUMAN DATA**
= protocol ready but N=0.

## Experiment matrix

| Experiment | Status | Canonical result | Artifact |
|------------|--------|------------------|----------|
| Baseline V1 (acoustic + AASIST-compatible head) | **COMPLETE** | 91.61% acc, 6.56% EER, ROC-AUC 0.9729 (n=584) | `artifacts/experiments/baseline_v1/` |
| Frozen XLS-R main | **COMPLETE** | 92.12% acc, 6.88% EER, ROC-AUC 0.9828 (n=584) | `artifacts/experiments/xlsr_main/` |
| RQ1 acoustic clean vs Opus | **COMPLETE** | Clean 93.84% / WhatsApp-style Opus simulation 89.38% (n=292) | `baseline_v1` per-condition |
| RQ1 frozen XLS-R clean vs Opus | **COMPLETE** | Clean 91.44% / Opus 92.81% (n=292) | `xlsr_main` per-condition |
| RQ2 English-only vs multilingual | **COMPLETE** | English-only 54.8% acc / 76.56% EER / 0.162 AUC; multilingual 91.61% / 6.56% / 0.9729 | `artifacts/experiments/rq2_english_control/` |
| RQ3 leave-one-language-out | **COMPLETE** | Hindi 78.83%; Marathi 93.29%; Tamil 93.94% accuracy | `artifacts/experiments/rq3_crosslingual/` |
| RQ4 calibration | **COMPLETE** | Val-selected per-language×condition; test ECE 0.0245→0.026 | `artifacts/experiments/rq4_calibration/` |
| LFCC-GMM baseline | **COMPLETE** | 54.79% acc, EER 23.48%, AUC 0.8195 | `artifacts/experiments/baseline_matrix/` |
| RawNet2-style approximate baseline | **COMPLETE** | 54.79% acc, EER 43.18%, AUC 0.5845 (not faithful RawNet2) | `baseline_matrix` |
| Source-shortcut analysis | **COMPLETE** | Label 84.8% / source 84.6% on V1 test | `artifacts/experiments/source_shortcut/` |
| Split diagnostics | **COMPLETE** | Val 87.4% vs test 91.6%; no proven leakage | `artifacts/experiments/split_diagnostics/` |
| Benchmark V2 | **PARTIAL** | External-source pilot; source probe 98.48%, label probe 85.83% | `artifacts/experiments/benchmark_v2/` |
| FLEURS unseen-real evaluation | **PILOT** | Frozen eval n=9 (55.6%); pipeline validation only | `artifacts/experiments/benchmark_v2/` |
| Generator-disjoint evaluation | **PENDING** | n=0; no result claimed | `artifacts/experiments/benchmark_v2/` |
| Faithful RawNet2 | **PENDING** | Not implemented | ROADMAP-032 |
| RQ5 human study | **BLOCKED ON HUMAN DATA** | Protocol + analysis path ready; N=0 | `scripts/analyze_human_study.py` |

## Dataset (Baseline V1)

| Field | Value |
|-------|-------|
| Clips | 2,346 evaluation instances (1,800 source + Opus twins) |
| Hours | ~4.11 |
| Languages | hi, mr, ta |
| Real source | Kathbath |
| Fake source | IndicSynth |
| Split | Speaker-disjoint 70/15/15 |
| Known limitation | Source correlates with label on V1 |

## Main model (Baseline V1)

- Front-end: deterministic **acoustic embedding 1024-D** (not frozen XLS-R)
- Head: **AASIST-compatible NumPy** anti-spoofing classifier (not canonical AASIST)
- Calibration: validation-selected per-language-and-condition strategy

## Remaining work

1. Complete the partial Benchmark V2 source×label design.
2. Re-evaluate FLEURS as a **new** experiment if the larger local ingest is used (see below). Frozen Round 3 claim stays n=9 PILOT.
3. Run generator-disjoint evaluation when a genuine held-out generator cell exists.
4. Implement faithful RawNet2.
5. Collect real human participants for RQ5; current N=0.

## Local disk vs frozen evaluation

`data/benchmark_v2/provenance.json` now records FLEURS=150 (50 hi / 50 mr / 50 ta)
and 3083 clips including Opus twins after the 2026-08-28 ingest job. That is
**ingest only**. `artifacts/final_results_manifest.json` still has
`independent_real_test` n=9 / 55.6% and V2 `fleurs.real`=50. Do not cite the
larger local corpus as a Round 3 result until a new evaluation is run and
approved.
