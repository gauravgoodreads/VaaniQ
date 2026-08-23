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

**Software complete.** Citing “ECE improved under Opus” as an RQ4 result still requires held-out val/test from curated manifests — not fixture logits.
