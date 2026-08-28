# Calibration (Phase 4)

> RQ4 / O5 / proposal §7.5. Implementation lives in `vaaniq.calibration` (unchanged API) plus `vaaniq.research.calibration_study`.

## Cells

| Cell | What it does |
|------|----------------|
| Raw | Softmax on unscaled logits |
| Temperature scaling | One T per (language × condition) (OQ-031), fit on val only (OQ-032) |
| Per-language | Named cell using the language-keyed T |
| Per-compression | Named cell using the condition-keyed T |

## Metrics and figures

- ECE (15 equal-width bins, OQ-017)
- Brier score
- Reliability diagram SVG
- Confidence histogram SVG
- Coverage–accuracy curve SVG (REQ-061)
- Reliability badge on the API/UI (OQ-010)

## UI

`/calibration` plots the live snapshot from `GET /api/v1/calibration`.

## Completeness

**RQ4 COMPLETE** on bounded V1. Production Baseline V1 strategy was selected on **validation only**
(per-language-and-condition; val ECE 0.0487). Held-out ECE moved 0.0245 → 0.026 (slightly
worsened). A standalone test-set comparison where global temperature scaling looked better
is exploratory and must not be used for strategy selection. Frozen XLS-R used
validation-selected global temperature scaling.
