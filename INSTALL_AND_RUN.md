# VaaniQ — Install, understand, and run (any PC)

This is the **single onboarding doc** for moving the project to another machine.
Repo: https://github.com/notaarav999/broscapstone

If anything conflicts with the capstone proposal, **the proposal wins**:
`docs/source/Capstone_Project_Proposal.md`.

---

## 1. What this project is

**VaaniQ** = Cross-lingual, compression-robust detection and calibrated reliability
estimation for **AI-generated voice** in Indian languages, with a human-perception baseline.

| In scope | Out of scope |
|----------|----------------|
| Hindi (`hi`), Marathi (`mr`), Tamil (`ta`) | Telugu (`te`) — never a project language |
| WhatsApp-style Opus robustness (RQ1) | Auth / payments / mobile / production scaling |
| Multilingual vs English-only (RQ2) | Fabricating EER/ECE/human scores |
| Zero-shot cross-lingual (RQ3) | Fine-tuning XLS-R (must stay frozen) |
| Calibration (RQ4) | |
| Human vs model on same clips (RQ5) | |

**Current honesty rule:** software + demo are built; bounded V1 RQ1–RQ4 results are
frozen in `artifacts/final_results_manifest.json`. RQ5 is N=0. Benchmark V2 is
PARTIAL. FLEURS unseen-real eval is a PILOT (n=9). Do not treat demo/fixture
numbers as dissertation results. See `docs/RESEARCH_EXECUTION_STATUS.md`.

---

## 2. Repository map (what each folder is)

```text
broscapstone/
├── backend/                 # Python 3.11 package + FastAPI API
│   └── src/vaaniq/          # Core app (hexagonal architecture)
│       ├── api/             # HTTP routers (upload, inference, explain, human study…)
│       ├── audio/           # Load, preprocess, Opus compression
│       ├── calibration/     # Temperature scaling, ECE/Brier helpers
│       ├── core/            # Domain entities + ports (no FastAPI imports)
│       ├── datasets/        # Adapters: Kathbath, IndicVoices-R, CV, IndicSynth…
│       ├── evaluation/      # EER, min-DCF, metrics
│       ├── explainability/  # Grad-CAM proxy, bands, artefacts
│       ├── features/        # XLS-R embedding path (frozen front-end)
│       ├── human_study/     # RQ5 protocol + export
│       ├── models/          # AASIST-style head + baselines
│       ├── research/        # RQ runners, leakage audit, execute CLI
│       ├── training/        # Trainer, seeds, manifests
│       └── persistence/     # DB models / Alembic
├── frontend/                # React + Vite + TypeScript UI
├── configs/                 # All YAML knobs (no magic numbers in src)
├── data/                    # Local audio/embeddings (gitignored; create empty)
├── models/                  # Weight placeholders (gitignored bulk)
├── research/                # Results, reports, paper draft, experiment layout
│   ├── datasets/            # Manifests + dataset reports
│   ├── results/             # RQ tables; canonical metrics live in artifacts/
│   ├── reports/             # Findings (use research/reports/ + frozen manifest)
│   └── paper/               # Manuscript draft
├── docs/                    # Specs, architecture, RQs, limitations
│   └── source/              # Authoritative proposal + topic approval extracts
├── deployment/              # Docker Compose + nginx
├── scripts/                 # Gates, Telugu guard, helpers
├── notebooks/               # Optional notebooks
├── .env.example             # Copy to .env (never commit secrets)
├── INSTALL_AND_RUN.md       # This file
└── README.md                # Short quickstart
```

### Important docs to read on a new PC

| File | Why |
|------|-----|
| `INSTALL_AND_RUN.md` | This guide |
| `README.md` | 5-minute quickstart |
| `docs/SYSTEM_ARCHITECTURE.md` | How pieces connect |
| `docs/DEVELOPER_GUIDE.md` | Day-to-day engineering |
| `docs/DATASETS.md` | Corpora + licences |
| `docs/TRAINING.md` / `TRAINING_GUIDE.md` | How training is meant to run |
| `docs/RESEARCH.md` / `EXPERIMENTS.md` | RQ suites |
| `docs/KNOWN_LIMITATIONS.md` | Honest limitations (do not hide) |
| `docs/RESEARCH_EXECUTION_STATUS.md` | Measured vs PENDING |
| `docs/OPEN_QUESTIONS.md` | Assumptions (`OQ-###`) |
| `docs/source/Capstone_Project_Proposal.md` | Source of truth |

---

## 3. Prerequisites (new PC)

| Tool | Version | Purpose |
|------|---------|---------|
| Git | recent | clone |
| Python | **3.11** | backend |
| [uv](https://github.com/astral-sh/uv) | recent | Python envs / runner |
| Node.js | **22+** | frontend |
| npm | comes with Node | frontend install |
| ffmpeg | optional but recommended | Opus WhatsApp-style compression |
| Docker Desktop | optional | one-command stack |
| Hugging Face token | optional until data ingest | gated corpora |

### Windows notes (common failures)

1. **`uv` not found** — add to PATH for that terminal:
   ```powershell
   $env:Path = "$env:USERPROFILE\.local\bin;" + $env:Path
   ```
   Default install path: `%USERPROFILE%\.local\bin\uv.exe`

2. **Execution policy blocks `npm` / Activate.ps1**
   ```powershell
   Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
   ```
   Or call `npm.cmd` instead of `npm`.

3. **Application Control blocks `uvicorn.exe` (os error 4551)**
   Use:
   ```powershell
   uv run python -m uvicorn vaaniq.api.app:create_app --factory --reload --host 127.0.0.1 --port 8000
   ```
   instead of `uv run uvicorn ...`

---

## 4. Clone and configure

```powershell
git clone https://github.com/notaarav999/broscapstone.git
cd broscapstone
Copy-Item .env.example .env
Copy-Item frontend\.env.example frontend\.env
```

Linux/macOS:

```bash
git clone https://github.com/notaarav999/broscapstone.git
cd broscapstone
cp .env.example .env
cp frontend/.env.example frontend/.env
```

`.env` stays local (gitignored). Do not commit tokens.

Optional for gated datasets later:

```text
HF_TOKEN=hf_...
```

---

## 5. Run the full program (local — recommended)

You need **two terminals**.

### Terminal 1 — Backend API

```powershell
cd backend
uv venv
uv pip install -e ".[dev]"
uv run python -m uvicorn vaaniq.api.app:create_app --factory --reload --host 127.0.0.1 --port 8000
```

Checks:
- http://127.0.0.1:8000/health → `{"status":"ok"}`
- http://127.0.0.1:8000/docs → OpenAPI UI

### Terminal 2 — Frontend UI

```powershell
# if needed on Windows:
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass

cd frontend
npm.cmd ci
npm.cmd run dev
```

Open: **http://127.0.0.1:5173**  
Look for an **API ok** chip (frontend ↔ backend health).

### What the UI includes

| Area | Path idea |
|------|-----------|
| Upload / Inference | Detect real vs AI voice + confidence |
| Live | Mic recording path |
| Explainability | Attention / bands / artefacts views |
| Calibration / Dashboard | Reliability-facing views |
| Human Study | Listener protocol (Real/Fake + confidence 1–5) |
| Dataset / Experiments / Metrics | Research tooling surfaces |
| History | Past predictions |

---

## 6. Run with Docker (optional)

Requires Docker Desktop.

```powershell
docker compose -f deployment/docker-compose.yml up --build
```

| Service | URL |
|---------|-----|
| Web | http://localhost:8080 |
| API | http://localhost:8000/health |
| Postgres | localhost:5432 (`vaaniq` / `vaaniq`) |

Stop: `Ctrl+C` or `docker compose -f deployment/docker-compose.yml down`

---

## 7. Quality gates (optional)

Windows:

```powershell
powershell -File scripts\check_all.ps1
```

Or manually:

```powershell
cd backend
uv run ruff check src tests
uv run mypy --strict src
uv run python -m pytest

cd ..\frontend
npm.cmd run typecheck
npm.cmd run lint
npm.cmd run test
```

Telugu language guard:

```powershell
uv run python scripts\check_no_telugu.py
```

---

## 8. Research execution CLI (not the web UI)

Inventory + quality audit + **PENDING** RQ tables (does **not** invent metrics):

```powershell
cd backend
uv run python -m vaaniq.research.cli --mode execute --repo-root .. --root ..\research
```

CI/demo fixture suites (software path only — **not** dissertation results):

```powershell
uv run python -m vaaniq.research.cli --mode fixtures --root ..\research --seed 42
```

---

## 9. How the system works (pipeline)

```text
Upload / live audio
  → validate MIME, size, duration, language
  → preprocess (mono, 16 kHz, normalize)
  → optional Opus WhatsApp-style twin (ffmpeg)
  → frozen XLS-R embeddings (cacheable)
  → AASIST-style head → score / logits
  → temperature calibration → confidence + reliability badge
  → explainability + API + React UI
```

**Research path (already run on bounded V1):** speaker-disjoint Kathbath +
IndicSynth subset → acoustic / frozen XLS-R heads → RQ1–RQ4. RQ5 still needs
listeners. Further V2/FLEURS work is a new experiment, not the frozen baseline.

---

## 10. What is already done vs still PENDING

| Layer | Status |
|-------|--------|
| Architecture, API, React demo | Done |
| Dataset adapters + Opus pipeline | Done (software) |
| Metrics / calibration / explain / human-study UI | Done (software) |
| Bounded V1 corpus + RQ1–RQ4 tables | Frozen in `artifacts/final_results_manifest.json` |
| RQ5 human study | **BLOCKED ON HUMAN DATA** (N=0) |
| Benchmark V2 / FLEURS eval | **PARTIAL** / **PILOT** (frozen n=9); larger local ingest is unevaluated |
| Human-study UI | Done (software); N=0 |
| Paper / master docs | Generated from frozen manifest; not a new experiment |

Never copy proposal target numbers into result CSVs.

---

## 11. What never gets committed

Already enforced by `.gitignore`:

- `.env` and secrets
- `*.wav` / `*.mp3` / `*.opus` / model weights (`*.pt`, `*.onnx`, …)
- `/data/**` audio and caches
- `backend/data/**` local object store / embedding cache
- `node_modules/`, `.venv/`, DBs, logs

On a new PC you recreate empty local dirs as needed; downloads are operator-side.

---

## 12. Pushing updates back to GitHub

```powershell
git status
git add <files>
git commit -m "describe why"
git push origin main
```

Use a Personal Access Token or GitHub CLI login if HTTPS asks for credentials.

---

## 13. Quick troubleshooting

| Symptom | Fix |
|---------|-----|
| `uv` not recognized | Add `%USERPROFILE%\.local\bin` to PATH |
| `npm` script disabled | `Set-ExecutionPolicy -Scope Process Bypass` or `npm.cmd` |
| `uvicorn` blocked (4551) | `uv run python -m uvicorn ...` |
| Frontend no API | Backend on :8000; `frontend/.env` has `VITE_API_BASE_URL=http://127.0.0.1:8000` |
| Port in use | Free 8000 / 5173 or change ports |
| Gated dataset download fails | Set `HF_TOKEN` after accepting dataset licences on Hugging Face |

---

## 14. Next research steps (after the app runs)

1. Obtain HF token; ingest Kathbath / IndicVoices-R / Common Voice hi-mr / IndicSynth.
2. Verify **Tamil audio files** exist (not labels only).
3. Write speaker-disjoint, pair-safe `dataset_manifest_v*`.
4. Freeze XLS-R on Colab T4 / Kaggle; cache embeddings.
5. Train AASIST head; fill RQ1–RQ4 CSVs from real eval.
6. Recruit ≥12–15 listeners on the **same** test clip IDs (RQ5).
7. Update `research/reports/RESEARCH_FINDINGS.md` and the paper Results sections.

---

## 15. Contact points inside the repo

- Requirements: `docs/REQUIREMENTS.md`
- Roadmap IDs: `docs/PROJECT_ROADMAP.md`
- Limitations: `docs/KNOWN_LIMITATIONS.md`
- Future work: `docs/FUTURE_WORK.md`
- Completion checklist: `docs/PROJECT_COMPLETION_CHECKLIST.md`
