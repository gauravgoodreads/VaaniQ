# VaaniQ

[![CI](https://github.com/local/vaaniq/actions/workflows/ci.yml/badge.svg)](https://github.com/local/vaaniq/actions/workflows/ci.yml)
[![Docs](https://github.com/local/vaaniq/actions/workflows/docs.yml/badge.svg)](https://github.com/local/vaaniq/actions/workflows/docs.yml)
[![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)](./backend/pyproject.toml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)

**Cross-Lingual, Compression-Robust Detection and Calibrated Reliability Estimation for
AI-Generated Voice in Indian Languages, with a Human-Perception Baseline.**

Languages in scope: **Hindi (`hi`)**, **Marathi (`mr`)**, **Tamil (`ta`)**.
Telugu is **not** a project language (REQ-139).

> Research-grade system (dataset → train → eval → calibrate → explain → web app).
> Phase 1 is scaffold only — ML bodies are deferred behind `ROADMAP-###` stubs.

## Architecture (C4 container sketch)

```mermaid
flowchart LR
  User([User]) --> Web[React SPA]
  Web --> API[FastAPI]
  API --> DB[(SQLite / Postgres)]
  API --> Store[(Object store)]
  Worker[Experiment worker] --> DB
  Worker --> Store
```

Full design: [`docs/SYSTEM_ARCHITECTURE.md`](./docs/SYSTEM_ARCHITECTURE.md).
Roadmap: [`docs/PROJECT_ROADMAP.md`](./docs/PROJECT_ROADMAP.md).

## 5-minute quickstart

Prerequisites: **Python 3.11**, [**uv**](https://github.com/astral-sh/uv), **Node.js 22+**.

### 1. Clone and env

```bash
git clone <this-repo> broscapstone
cd broscapstone
cp .env.example .env
cp frontend/.env.example frontend/.env
```

### 2. Backend API

```bash
cd backend
uv venv
uv pip install -e ".[dev]"
uv run uvicorn vaaniq.api.app:create_app --factory --reload --host 127.0.0.1 --port 8000
```

Check: open [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health) → `{"status":"ok"}`.
OpenAPI: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs).

### 3. Frontend (second terminal)

```bash
cd frontend
npm ci
npm run dev
```

Open [http://127.0.0.1:5173](http://127.0.0.1:5173). The shell shows an **API ok** chip when
`GET /health` succeeds (frontend↔backend loop).

### 4. Gates (optional)

```bash
# GNU make (Linux/macOS/Git Bash)
make check

# Windows PowerShell
powershell -File scripts/check_all.ps1

# Or manually:
cd backend && uv run ruff check src tests && uv run mypy --strict src && uv run pytest
cd frontend && npm run typecheck && npm run lint && npm run test
```

### Docker (optional)

Requires Docker Desktop. See [`deployment/README.md`](./deployment/README.md).

```bash
docker compose -f deployment/docker-compose.yml up --build
# Web http://localhost:8080  ·  API http://localhost:8000/health
```

## Documentation

| Doc | Contents |
|-----|----------|
| [DEVELOPER_GUIDE](./docs/DEVELOPER_GUIDE.md) | Tooling, layout, conventions |
| [API](./docs/API.md) | HTTP surface & OpenAPI types |
| [DATASETS](./docs/DATASETS.md) | Corpora, licences, manifests |
| [TRAINING](./docs/TRAINING.md) | Seeds, manifests, baselines |
| [DEPLOYMENT](./docs/DEPLOYMENT.md) | Compose, Spaces, ops |
| [RESEARCH](./docs/RESEARCH.md) | RQs, metrics, paper track |
| [EXPERIMENTS](./docs/EXPERIMENTS.md) | Run layout under `research/` |
| [CONTRIBUTING](./docs/CONTRIBUTING.md) | PRs, commits, gates |
| [REQUIREMENTS](./docs/REQUIREMENTS.md) | REQ catalogue (Phase 0) |
| [OPEN_QUESTIONS](./docs/OPEN_QUESTIONS.md) | OQ tracker |

## Project languages

Iterate `Language` / `LANGUAGES` in code — never hardcode language lists.
Guard: `python scripts/check_no_telugu.py`.

## License

MIT — see [`LICENSE`](./LICENSE). Dataset redistributions must honour upstream licences
(see OQ-035 / `docs/DATASETS.md`).
