# Developer guide

> Scaffold guide (ROADMAP-010). Update as phases land.

## Prerequisites

| Tool | Version | Notes |
|------|---------|-------|
| Python | 3.11 | via `uv` |
| Node.js | 22+ (LTS OK) | frontend |
| Docker | optional | compose stack |
| GNU make | optional | `make check` |

## Repository layout

```
backend/src/vaaniq/   # Python package (hexagonal core + adapters)
frontend/src/        # React 18 + Vite + Tailwind
configs/             # App + experiment YAMLs
deployment/          # compose + nginx
docs/                # Phase 0 + guides
scripts/             # ingest, OpenAPI gen, guards
```

## Conventions

- **Languages:** `hi` / `mr` / `ta` only. Never add `te` (REQ-139).
- **Ambiguity:** log `OQ-###` in `docs/OPEN_QUESTIONS.md`; mark `# ASSUMPTION: OQ-###`.
- **Deferred work:** `TODO(ROADMAP-###): …` or `NotImplementedInPhaseError`.
- **Domain purity:** `core/domain/` must not import FastAPI/SQLAlchemy.
- **Config:** no magic numbers in `src/` — use `configs/*.yaml`.

## Daily loop

```bash
# Backend gates
cd backend && uv run ruff check src tests && uv run mypy --strict src && uv run pytest

# Frontend gates
cd frontend && npm run typecheck && npm run lint && npm run test

# All (GNU make)
make check
```

## Composition root

Wire adapters in `vaaniq.container.build_container` — no global singletons
(vaaniq-core.mdc).

## Related

- Architecture: `SYSTEM_ARCHITECTURE.md`
- Contributing: `CONTRIBUTING.md`
- API: `API.md`

## TODO

- TODO(ROADMAP-010): expand IDE setup (Cursor rules already in `.cursor/rules/`)
- TODO(ROADMAP-058): document Node BFF when added (OQ-026)
