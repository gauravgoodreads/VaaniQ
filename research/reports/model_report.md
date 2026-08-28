# Model Report

**RQ:** RQ2  
**Objective:** O3  
**Proposal:** §7.3 / §8

## Summary

XLS-R frozen + AASIST head vs LFCC-GMM, RawNet2, English-only.

## Tables

```json
{
  "name": "aasist-v1"
}
```

## Figures

- `..\research\figures\calibration\reliability_diagram.svg`
- `..\research\figures\compression\compression_degradation.svg`
- `..\research\figures\cross_lingual\cross_lingual_heatmap.svg`

## Research observations

- English-only control uses ASVspoof 2019 LA (OQ-015).

## Limitations

- Fixture/offline scores unless curated manifests are present.
- NumPy AASIST-style head is not clovaai graph-parity (OQ-014).

## Future work

- Swap NumPy head for clovaai/aasist on GPU.
