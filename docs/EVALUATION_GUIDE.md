# VaaniQ — Evaluation Guide

## Metrics (REQ-046–053)

```python
from vaaniq.evaluation import (
    equal_error_rate,
    min_dcf,
    classification_report_scores,
    roc_curve,
    pr_curve,
    confusion_matrix,
    cross_lingual_matrix,
    cross_condition_matrix,
    per_language_report,
    per_attack_report,
    EvalReportGenerator,
)

eer = equal_error_rate(scores, labels)          # higher score = more fake
mdcf = min_dcf(scores, labels)                  # ASSUMPTION: OQ-018
clf = classification_report_scores(scores, labels)
fpr, tpr, auc = roc_curve(scores, labels)
prec, rec = pr_curve(scores, labels)
cm = confusion_matrix(scores, labels)

xl = cross_lingual_matrix([{
    "train_lang": "hi", "test_lang": "ta", "scores": scores, "labels": labels
}])
xc = cross_condition_matrix([{
    "train_condition": "clean",
    "test_condition": "opus_whatsapp_sim",
    "scores": scores,
    "labels": labels,
}])
```

## Calibration (REQ-054–062)

```python
from vaaniq.calibration import (
    TemperatureScaler,
    expected_calibration_error,
    reliability_diagram,
    brier_score,
    predictive_entropy,
    coverage_accuracy_curve,
    reliability_badge,
)
```

Fit `TemperatureScaler` **per (language × condition)** on val logits only (OQ-031, OQ-032).

## Explainability (REQ-075–078)

```python
from vaaniq.explainability import CompositeExplainer
arts = CompositeExplainer().explain(clip, wav, model_id="aasist-v1")
```

Artefacts land under `research/explain/` as JSON (Grad-CAM temporal, attention, bands, spectrogram, compression ratio).

## Reports

```python
EvalReportGenerator().write("exp_id", Path("research/experiments/reports/exp_id.md"),
    metrics=..., matrices=..., slices=...)
```

API: `GET /api/v1/metrics`, `GET /api/v1/calibration`, `GET /api/v1/experiments/report`.
