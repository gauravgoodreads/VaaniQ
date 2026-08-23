# VaaniQ — Training Guide

## Prerequisites

- Python 3.11 + `uv`
- Backend: `cd backend && uv sync --extra dev`
- Optional GPU/real XLS-R: `uv sync --extra ml`
- Curated speaker-disjoint manifests under `data/` (gitignored)
- Embedding cache populated via `FrozenXLSRExtractor.extract_batch`

## Config entrypoints

| Profile | Path | Purpose |
|---------|------|---------|
| Default HI/MR/TA | `configs/train/default.yaml` | Primary run |
| CV | `configs/train/cv.yaml` | Folded eval |
| English-only | `configs/train/english_only.yaml` | RQ2 control (OQ-015) |
| Model | `configs/model/xlsr_aasist.yaml` | XLS-R + AASIST knobs (OQ-013/014) |

## Minimal training loop (embeddings in-memory)

```python
from pathlib import Path
import numpy as np
from vaaniq.models import AASISTClassifier
from vaaniq.training import FileExperimentTracker, Trainer

clf = AASISTClassifier()
tracker = FileExperimentTracker(root=Path("research/experiments"), experiment_id="demo")
trainer = Trainer(
    clf,
    tracker,
    seed=42,
    max_epochs=20,
    early_stopping_patience=5,
    use_amp=False,  # True when torch+[ml] available
    experiment_root=Path("research/experiments"),
    resume_from=None,  # or Path(".../checkpoints/last.npz")
)
exp_id = trainer.fit({
    "train_features": train_x,  # float32 [N, 1024]
    "train_labels": train_y,    # int64 0=real,1=fake
    "val_features": val_x,
    "val_labels": val_y,
})
```

## Baselines

- **LFCC+GMM:** `LfccGmmClassifier.fit(waveforms, labels)` then `predict_waveform`.
- **RawNet2:** `RawNet2Classifier.train_epoch` / `predict_waveform`.
- **English-only:** `EnglishOnlyXlsrAasistBaseline(train_config).run(dataset)`.

## Artefacts

Under `research/experiments/<id>/`:

- `manifest.json` — git SHA, seed, config, versions
- `metrics.jsonl` — train/val scalars
- `checkpoints/best.npz`, `last.npz`
- `tensorboard_scalars.csv` or `tb/` when torch TB available

## Determinism

`Trainer` calls `seed_everything(seed)` (random, numpy, torch + deterministic algorithms when present).
