# Calibration Report

**RQ:** RQ4  
**Objective:** O5  
**Proposal:** §7.5

## Summary

Temperature scaling vs raw ECE/Brier on the logged cells.

## Tables

```json
{
  "ece": 0.021881306543946266
}
```

## Figures

- `..\research\figures\calibration\reliability_diagram.svg`
- `..\research\figures\compression\compression_degradation.svg`
- `..\research\figures\cross_lingual\cross_lingual_heatmap.svg`

## Research observations

- Per-language and per-condition T follow OQ-031.

## Limitations

- Fixture/offline scores unless curated manifests are present.
- NumPy AASIST-style head is not clovaai graph-parity (OQ-014).

## Future work

- Fit T on real val splits only (OQ-032).
