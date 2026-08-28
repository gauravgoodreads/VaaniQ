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
> **Measured Baseline V1** exists on a speaker-disjoint Kathbath + IndicSynth subset (~4.11 h).
> All headline metrics live in `artifacts/experiments/baseline_v1/metrics.json` (synced from `train_report.json`).

## Research status (measured vs pending)

| Item | Status | Artifact |
|------|--------|----------|
| Baseline V1 (acoustic + AASIST head) | **Measured** | `artifacts/experiments/baseline_v1/` |
| RQ1 clean vs Opus | **Measured** | `baseline_v1` per-condition metrics |
| RQ3 leave-one-language-out | **Measured** | `artifacts/experiments/rq3_crosslingual/` |
| RQ4 calibration audit | **Measured** | `artifacts/experiments/rq4_calibration/` |
| LFCC-GMM / RawNet2 baselines | **Measured** | `artifacts/experiments/baseline_matrix/` |
| Source-shortcut analysis | **Measured** | `artifacts/experiments/source_shortcut/` |
| Frozen XLS-R main model | **Pending** | run `extract_xlsr_embeddings.py` + `train_demo_detector.py --front-end xlsr` |
| Benchmark V2 (multi-source) | **Pending** | `prepare_benchmark_v2.py` (needs HF_TOKEN) |
| RQ2 English-only ASVspoof | **Pending** | OQ-015 |
| RQ5 human study | **Protocol ready, N=0** | `/api/v1/human-study/*` |

### Reproduce main results

```bash
cd backend
uv pip install -e ".[dev,data,docs]"
uv run python ../scripts/sync_experiment_artifacts.py
uv run python ../scripts/export_predictions.py
uv run python ../scripts/evaluate_baselines.py
uv run python ../scripts/sync_research_results.py
uv run python ../scripts/verify_research_integrity.py   # must exit 0
```

Regenerate documents from artifacts: `uv run python ../scripts/generate_master_docx.py` (see `docs/TRAINING_GUIDE.md`).

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

## Full install on a new PC

Step-by-step for another machine (folder map, Windows fixes, Docker, research CLI):
**[`INSTALL_AND_RUN.md`](./INSTALL_AND_RUN.md)**.

## 5-minute quickstart

Prerequisites: **Python 3.11**, [**uv**](https://github.com/astral-sh/uv), **Node.js 22+**.

On Windows, if `uvicorn.exe` is blocked by Application Control, use:
`uv run python -m uvicorn ...` (see `INSTALL_AND_RUN.md`).

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
