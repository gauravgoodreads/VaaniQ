# Research execution status

Updated: 2026-08-28 (synced from `artifacts/experiments/`)

Statuses: **COMPLETE** = measured on persisted speaker-disjoint publication subset unless noted.

## Experiment matrix

| Experiment | Status | Key result | Artifact |
|------------|--------|------------|----------|
| Baseline V1 (Kathbath-real / IndicSynth-fake) | **COMPLETE** | 91.6% acc, 6.56% EER, ROC-AUC 0.973 (n=584 test) | `artifacts/experiments/baseline_v1/` |
| RQ1 clean vs Opus | **COMPLETE** | Clean 93.8% / Opus 89.4% acc | `baseline_v1` per-condition |
| RQ2 English-only vs multilingual | **COMPLETE** | English-only 54.8% acc; multilingual 93.7% | `artifacts/experiments/rq2_english_control/` |
| RQ3 leave-one-language-out | **COMPLETE** | LOO folds measured | `artifacts/experiments/rq3_crosslingual/` |
| RQ4 calibration audit | **COMPLETE** | Val-selected per-language×condition TS | `artifacts/experiments/rq4_calibration/` |
| LFCC-GMM baseline | **COMPLETE** | 54.8% acc, EER 23.5% | `artifacts/experiments/baseline_matrix/` |
| RawNet2-style approximate baseline | **COMPLETE** | 54.8% acc, EER 43.2% (not canonical RawNet2) | `baseline_matrix` |
| Source-shortcut analysis | **COMPLETE** | Label 84.8% / source 84.6% on V1 test | `artifacts/experiments/source_shortcut/` |
| Split diagnostics | **COMPLETE** | Val/test gap analyzed | `artifacts/experiments/split_diagnostics/` |
| Frozen XLS-R main | **COMPLETE** | 92.1% acc, 6.88% EER, ROC-AUC 0.983 | `artifacts/experiments/xlsr_main/` |
| Benchmark V2 (multi-source) | **PARTIAL** | 50 FLEURS hi + generator metadata; `artifacts/experiments/benchmark_v2/` |
| Faithful RawNet2 (AASIST repo) | **PENDING** | Not implemented | ROADMAP-032 |
| RQ5 human study | **PENDING (N=0)** | Protocol + analysis path ready | `scripts/analyze_human_study.py` |

## Dataset (Baseline V1)

| Field | Value |
|-------|-------|
| Clips | 2,346 |
| Hours | ~4.11 |
| Languages | hi, mr, ta |
| Real source | Kathbath |
| Fake source | IndicSynth |
| Split | Speaker-disjoint 70/15/15 |
| Known limitation | Source correlates with label on V1 |

## Main model (Baseline V1)

- Front-end: deterministic **acoustic embedding 1024-D** (not frozen XLS-R for V1 metrics)
- Head: **AASIST-compatible NumPy** anti-spoofing classifier
- Calibration: validation-selected strategy (see `train_report.json`)

## Reproducibility

```bash
cd backend
uv pip install -e ".[dev,data,docs]"
uv run python ../scripts/sync_experiment_artifacts.py
uv run python ../scripts/verify_research_integrity.py
```

## Remaining work

1. Complete frozen XLS-R main experiment and sync `artifacts/experiments/xlsr_main/`
2. Complete Benchmark V2 build (FLEURS real + generator-disjoint eval)
3. Implement faithful RawNet2 baseline (optional stretch)
4. Collect real human participants for RQ5 (N>0)
