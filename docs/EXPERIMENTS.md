# Experiments guide

> Layout under `research/experiments/` (REQ-137–138 / ROADMAP-030).

## Directory convention

```
research/experiments/
  <experiment_id>/
    config.resolved.yaml
    manifest.json          # git SHA, seed, versions, checksums
    metrics.jsonl
    artefacts/
```

Never commit audio, weights, or large binaries (see `.gitignore`).

## Creating a run (when Trainer lands)

```bash
# Pseudocode — TODO(ROADMAP-030)
uv run python -m vaaniq.training.cli --config configs/train/default.yaml --seed 42
```

## Tracking

`FileExperimentTracker` stub logs metrics + manifests (ROADMAP-030). Swap for
external trackers only via the `ExperimentTracker` port.

## TODO

- TODO(ROADMAP-030): CLI entrypoint + manifest writer
- TODO(ROADMAP-035): model registry linkage to experiment IDs
- TODO(ROADMAP-041): copy final tables into `research/figures/`
