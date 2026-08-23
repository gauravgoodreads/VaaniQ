# Final architecture (Phase 4)

> Additive view of the implemented system. Does **not** replace
> [`SYSTEM_ARCHITECTURE.md`](SYSTEM_ARCHITECTURE.md). Proposal §7–§8 / §7.9 win on conflict.

## Containers

| Container | Implementation | Notes |
|-----------|----------------|-------|
| Web | React + TypeScript (Vite) | Upload, live, dashboard, human study, experiments |
| API | FastAPI (`vaaniq.api`) | Inference, research catalogue, human-study protocol |
| Persistence | SQLAlchemy + Alembic | SQLite local; Postgres in compose (OQ-021) |
| Object store | Local filesystem | Uploads / artefacts |
| Experiment store | JSONL under `research/experiments/` | Searchable `ResearchRunRecord` |
| Worker | Offline `python -m vaaniq.research.cli` | Fixture RQ suites; GPU train remains Colab/Kaggle per proposal §11 |

Node BFF is still deferred (OQ-026 / ROADMAP-058). FastAPI serves the React app in local/dev; nginx reverse-proxies in compose.

## Research package (new in Phase 4)

`backend/src/vaaniq/research/` extends the existing tracker; it does not replace `training.FileExperimentTracker` or `evaluation/`.

- `ExperimentStore` — git SHA, seed, hardware, metrics, calibration, languages, compression
- `run_cross_lingual_suite` — train HI+MR / HI+TA / MR+TA, test held-out (RQ3)
- `run_compression_suite` — clean / Opus ladder / resample / packet loss (RQ1)
- `run_calibration_suite` — raw / temperature / per-language / per-condition (RQ4)
- `analyze_errors` — worst language/condition/attack, over/under-confidence
- `ResearchReportBundle` — seven markdown reports
- `write_publication_bundle` — ROC / confusion SVG + CSV

## Ports that remain swappable

Feature extractors, classifiers, compressors, storage, dataset sources, calibrators, explainers, experiment trackers — ABC first, as in Phase 1.

## Languages

`hi`, `mr`, `ta` only. Telugu is a defect (REQ-139).
