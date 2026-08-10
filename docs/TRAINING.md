# Training guide

> Training loop, seeds, and baselines (P5 / ROADMAP-029–033). Bodies are stubs in
> Phase 1.

## Determinism

Every entrypoint must accept `--seed` and seed `random`, `numpy`, `torch`, and
`torch.cuda`; prefer `torch.use_deterministic_algorithms(True)` where feasible
(vaaniq-core.mdc).

Write a run manifest: git SHA, dirty flag, resolved config, seed, package versions,
hardware, dataset checksums (REQ-137).

## Config profiles

| Profile | Path | Purpose |
|---------|------|---------|
| default | `configs/train/default.yaml` | Primary XLS-R + AASIST |
| cv | `configs/train/cv.yaml` | Cross-validation |
| english_only | `configs/train/english_only.yaml` | ASVspoof control (REQ-044, OQ-015) |

## Models

| Model | Config | ROADMAP |
|-------|--------|---------|
| XLS-R 300m + AASIST | `configs/model/xlsr_aasist.yaml` | ROADMAP-025, 029 |
| LFCC + GMM | `configs/model/lfcc_gmm.yaml` | ROADMAP-031 |
| RawNet2 | `configs/model/rawnet2.yaml` | ROADMAP-032 |

Checkpoint: HF `facebook/wav2vec2-xls-r-300m` only (REQ-041, OQ-027).

## TODO

- TODO(ROADMAP-030): implement `Trainer` + `FileExperimentTracker`
- TODO(ROADMAP-014): document IndicSynth sampling for fakes
- TODO(ROADMAP-033): English-only ASVspoof protocol details (OQ-015)
