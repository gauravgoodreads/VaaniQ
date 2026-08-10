# persistence

SQLAlchemy 2.0 models and Alembic migrations (ROADMAP-006).

**Tables:** users, uploads, predictions, experiments, experiment_metrics, models,
calibration_runs, human_study_participants, human_study_responses.

**Commands** (from `backend/`):

```bash
alembic upgrade head
alembic downgrade base
```

SQLite by default (OQ-021); types are PostgreSQL-compatible.
