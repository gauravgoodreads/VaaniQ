# VaaniQ — Training Guide

## Prerequisites

- Python 3.11 + `uv`
- Backend: `cd backend && uv sync --extra dev`
- Optional GPU/real XLS-R: `uv sync --extra ml`
- Hugging Face streaming ingest: `uv sync --extra data`
- Curated speaker-disjoint manifests under `data/` (gitignored)
- Embedding cache populated via `FrozenXLSRExtractor.extract_batch`

## Config entrypoints

| Profile | Path | Purpose |
|---------|------|---------|
| Default HI/MR/TA | `configs/train/default.yaml` | Primary run |
| CV | `configs/train/cv.yaml` | Folded eval |
| English-only | `configs/train/english_only.yaml` | RQ2 control (OQ-015) |
| Model | `configs/model/xlsr_aasist.yaml` | Frozen XLS-R + AASIST-compatible head (OQ-013/014) |

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

## Kathbath + IndicSynth publication subset

Kathbath is gated. Accept its Hugging Face terms, create a read token, and set
`HF_TOKEN` in the gitignored project `.env`. Never paste or commit the token.

The complete Hindi/Marathi/Tamil cells exceed 303 GB across both repositories.
The default command therefore creates a deterministic balanced subset: 300
Kathbath real and 300 IndicSynth fake clips per language (1,800 source clips).

```powershell
cd backend
$env:PYTHONPATH = "src"
$env:HF_TOKEN = "<load from the project .env>"

uv run --extra data python ..\scripts\prepare_publication_corpus.py
uv run --extra data python ..\scripts\prepare_publication_corpus.py --augment-existing-opus
uv run python ..\scripts\train_demo_detector.py `
  --corpus ..\data\publication_corpus `
  --output ..\models\checkpoints\xlsr_aasist\aasist-v1.npz
```

The importer:

- streams only Hindi, Marathi, and Tamil;
- normalizes audio to mono 16 kHz FLAC;
- preserves source, licence, model, speaker, gender, and checksum provenance;
- assigns shared Kathbath/IndicSynth speaker IDs to deterministic 70/15/15 splits;
- creates actual 16 kbps libopus twins for validation and test;
- writes `data/publication_corpus/provenance.json` and `manifest.jsonl`.

All paper and DOCX values must be read from the resulting persisted
`train_report.json`; never copy values from console output or fixtures.

## Baselines

- **LFCC+GMM:** `LfccGmmClassifier.fit(waveforms, labels)` then `predict_waveform`.
- **RawNet2-style approximate baseline:** `RawNet2Classifier.train_epoch` / `predict_waveform`. Faithful RawNet2 is PENDING.
- **English-only:** `EnglishOnlyXlsrAasistBaseline(train_config).run(dataset)`.

## Artefacts

Under `research/experiments/<id>/`:

- `manifest.json` — git SHA, seed, config, versions
- `metrics.jsonl` — train/val scalars
- `checkpoints/best.npz`, `last.npz`
- `tensorboard_scalars.csv` or `tb/` when torch TB available

## Determinism

`Trainer` calls `seed_everything(seed)` (random, numpy, torch + deterministic algorithms when present).
