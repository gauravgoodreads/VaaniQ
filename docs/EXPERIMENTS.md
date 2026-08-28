# Experiments (Phase 4)

> Layout, catalogue, and automated RQ runners. Serves REQ-137–138 / ROADMAP-030.

## Catalogue

Each run is a `ResearchRunRecord` written under `research/experiments/<id>/record.json` and appended to `index.jsonl`.

Recorded fields: experiment ID, timestamp, git SHA, model version, dataset version, languages, compression settings, hyperparameters, metrics, calibration results, hardware, seed, training duration, RQ IDs.

Search: `GET /api/v1/experiments/search?language=ta&rq_id=RQ3`  
Compare: `GET /api/v1/experiments/compare?metric=eer`

## Automated suites (software path)

```bash
# from repo root, with backend env
uv run python -m vaaniq.research.cli --root ./research --seed 42
```

| Suite | Folds / cells | Tables | Figures |
|-------|---------------|--------|---------|
| Cross-lingual | train HI+MR→TA; HI+TA→MR; MR+TA→HI | `cross_lingual.csv` | heatmap SVG |
| Compression | clean, Opus 8/16/24 kbps, resample, packet loss | `compression_robustness.csv` | degradation SVG |
| Calibration | raw, temperature, per-language, per-condition | `calibration_cells.csv` | reliability, coverage, histogram SVG |

CI runs the same functions on **synthetic embeddings** (no network, no GPU). Those numbers are **not** RQ answers.

## Real RQ tables (measured)

Canonical numbers are frozen in `artifacts/final_results_manifest.json`. CI still runs
synthetic embeddings; those numbers are **not** RQ answers. Dissertation citations must
use the frozen Round 3 artifacts, not fixture logits.

## Primary WhatsApp cell

Opus 16 kbps, 16 kHz mono (OQ-007). Bitrate ladder and packet-loss are SHOULD ablations (OQ-012, OQ-037, OQ-038).
