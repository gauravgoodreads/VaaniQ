# VaaniQ — Cursor Agent Prompt Pack

This file contains **three separate blocks**. Use them differently:

| Block | Where it goes | Why |
|---|---|---|
| **A. Project Rules** | `.cursor/rules/vaaniq-core.mdc` (alwaysApply) | Cursor re-injects this on *every* request. Constraints stay alive for the whole project. |
| **B. Phase 0 Prompt** | Paste into Composer/Agent chat | Document ingestion + requirements extraction only. No code. |
| **C. Phase 1 Prompt** | Paste into a *new* chat after Phase 0 is approved | Scaffold only. No ML. |

> **Do not paste all three at once.** Long single prompts degrade agent adherence. The rules file handles persistence; the task prompts handle the current milestone.

---
---

# BLOCK A — `.cursor/rules/vaaniq-core.mdc`

```markdown
---
description: VaaniQ core engineering constraints. Applies to all files.
alwaysApply: true
---

# VaaniQ — Core Engineering Rules

## Project identity
- **Name:** VaaniQ
- **Full title:** Cross-Lingual, Compression-Robust Detection and Calibrated Reliability
  Estimation for AI-Generated Voice in Indian Languages, with a Human-Perception Baseline
- **Type:** Research-grade system (dataset → training → evaluation → calibration →
  explainability → web app). Not an inference demo.
- **Languages:** Hindi (`hi`), Marathi (`mr`), Tamil (`ta`).
  **Tamil is the third language. Telugu is NOT in this project.** If you ever emit
  `te`, `telugu`, or `Telugu` in code, config, docs, or comments, that is a defect —
  stop and correct it.

## Source of truth
1. `docs/source/Capstone_Project_Proposal.md` (extracted from the proposal PDF) — **authoritative**
2. `docs/source/VaaniQ_Topic_Approval.md` (extracted from the PPT) — **supplementary**
3. `docs/PROJECT_ANALYSIS.md` — derived; must cite (1) and (2) by page/slide

On conflict: **Proposal wins.** Log the conflict in `docs/OPEN_QUESTIONS.md` with both
citations rather than silently resolving it.

## Ambiguity protocol — the single most important rule
You are forbidden from inventing project facts. This includes dataset sizes, sample
counts, model hyperparameters, target metric values, hardware specs, timelines,
citations, author names, and evaluation thresholds.

When the source documents do not specify something you need:
1. Write the gap to `docs/OPEN_QUESTIONS.md` using the template in that file.
2. Choose a defensible default, mark it `# ASSUMPTION: OQ-###` at the point of use.
3. Continue. Do **not** halt the whole task for one gap; do **not** hide the gap either.

If a number appears in code or docs and cannot be traced to a proposal page or an
`OQ-###`, it is a defect.

## Architectural constraints
- Clean/hexagonal architecture. Domain logic must not import framework code
  (no FastAPI/SQLAlchemy imports inside `core/domain/`).
- Every swappable concern is defined as an ABC (Python) or interface (TS) **first**,
  concrete implementation second: feature extractors, classifiers, compressors,
  storage backends, dataset sources, calibrators, explainers, experiment trackers.
- Dependency injection via constructor args + a composition root. No global singletons,
  no import-time side effects, no service locators.
- Config-driven. `grep` for a literal number in `src/` should return almost nothing.
  Constants live in `configs/*.yaml` or typed config dataclasses.

## Scope discipline
- **Never** drop a research component because it is hard. If it cannot be implemented
  now, ship: the ABC, the config schema, the `NotImplementedError` stub, the unit test
  marked `@pytest.mark.xfail(reason="ROADMAP-###")`, the docstring, and the roadmap entry.
- **Never** expand beyond the current phase. If you notice needed work outside scope,
  append it to `docs/PROJECT_ROADMAP.md` and move on.
- A `TODO` without a `ROADMAP-###` reference is a defect. Format:
  `# TODO(ROADMAP-042): swap in ONNX runtime for CPU inference`

## Code standards — Python
- Python 3.11. `from __future__ import annotations` in every module.
- Full type annotations on every public function, method, and dataclass field.
  `mypy --strict` must pass. No bare `Any` without an inline justification comment.
- `ruff` (lint + format) and `mypy` are gates, not suggestions.
- Pydantic v2 for all I/O boundaries (API schemas, config files, metadata records).
- `structlog` JSON logging. No `print()` outside `scripts/`. No f-strings inside log calls —
  use structured kwargs: `log.info("clip_loaded", path=p, sr=sr)`.
- Errors: define a project exception hierarchy rooted at `VaaniQError`. Never `except:`
  or bare `except Exception:` without re-raise or explicit structured logging.
- Docstrings: Google style, on every public symbol. Include the RQ or REQ ID it serves.

## Code standards — TypeScript / React
- TS `strict: true`, `noUncheckedIndexedAccess: true`. **Zero `any`.**
- Function components + hooks only. No class components.
- Server state → TanStack Query. Local UI state → `useState`/`useReducer`. No Redux.
- API types are **generated** from the FastAPI OpenAPI schema into
  `frontend/src/api/generated/` — never hand-written, never edited.
- Every component ≤ 200 lines. Extract hooks and subcomponents past that.
- Tailwind + shadcn/ui. No inline `style={{}}` except for computed dynamic values
  (e.g. waveform canvas dimensions).
- Accessibility: keyboard-navigable, ARIA labels on all icon-only buttons, visible focus rings.

## Testing
- Every new module ships with tests in the same commit. No exceptions.
- `pytest` + `pytest-cov`, coverage gate ≥ 80% on `backend/src/` (excluding stubs).
- Property-based tests (`hypothesis`) for audio transforms: resampling, normalization,
  trimming, length padding.
- Frontend: Vitest + React Testing Library. Test behaviour, not implementation.
- No network, no GPU, no dataset downloads in unit tests. Mark anything heavier
  `@pytest.mark.integration` and exclude it from the default run.

## Determinism & reproducibility
- Every experiment entrypoint takes `--seed` and seeds `random`, `numpy`, `torch`,
  and `torch.cuda`; sets `torch.use_deterministic_algorithms(True)` where feasible.
- Every run writes a manifest: git SHA, dirty-flag, resolved config, seed, package
  versions, hardware, dataset checksums.
- Data splits are speaker-disjoint and written to versioned manifest files, never
  computed on the fly.

## Security & hygiene
- No secrets in the repo. `.env.example` only, with every key documented.
- No committed audio, model weights, or `.pt` files. `.gitignore` and Git LFS config
  must cover `*.wav *.mp3 *.opus *.flac *.pt *.pth *.onnx *.ckpt`.
- All upload endpoints validate MIME type, magic bytes, duration, and file size before
  touching the file. Reject, log, return a typed error.
- CORS origins from config. Never `allow_origins=["*"]` in anything but a local dev profile.

## Working protocol
- Work in **small, verifiable increments**. After each increment: run the gates
  (`ruff`, `mypy`, `pytest`, `tsc`, `vitest`), report pass/fail, then continue.
- **Stop and ask** if: the proposal is genuinely contradictory, a task requires
  downloading a gated dataset, or you would need to delete/rewrite >100 lines of
  existing work.
- Never create a file without adding it to the relevant index/`__init__`/docs.
- Conventional Commits. One logical change per commit.

## Response format for every turn
1. **Plan** — numbered steps you are about to take (≤10 lines)
2. **Changes** — table: `file | action (new/edit/delete) | why`
3. **Verification** — the exact commands run and their real output
4. **Open questions** — new `OQ-###` entries created this turn, or "none"
5. **Next** — the single next increment

Never claim a command passed without having actually run it.
```

---
---

# BLOCK B — Phase 0 Prompt (paste into Agent chat)

```
# PHASE 0 — Document Ingestion & Requirements Extraction

You are the technical lead for VaaniQ. This phase produces **zero application code**.
Deliverables are documents only. Read `.cursor/rules/vaaniq-core.mdc` first; it governs
everything below.

## Attached sources
@Capstone_Project_Proposal.pdf
@VaaniQ_Topic_Approval.pptx

## Step 0 — Make the sources machine-checkable
PDFs and PPTX are unreliable to reason over directly. First, convert them to text you
can cite:

1. Create `scripts/ingest_sources.py` using `pymupdf` (fitz) and `python-pptx`.
2. It must emit:
   - `docs/source/Capstone_Project_Proposal.md` — full text, with `<!-- page: N -->`
     markers before each page's content, tables preserved as markdown tables,
     and `<!-- figure: page N, caption -->` markers for every image/diagram.
   - `docs/source/VaaniQ_Topic_Approval.md` — same, with `<!-- slide: N -->` markers
     and speaker notes under `### Notes`.
   - `docs/source/ingest_report.json` — page count, slide count, extracted char count
     per page, and a list of pages where extraction yielded < 50 chars (likely
     image-only pages needing manual review).
3. Run it. Report the ingest_report contents.
4. For any page flagged as image-only, render it to PNG under
   `docs/source/figures/page_NNN.png` and read it visually. Describe the figure content
   in the markdown at the correct position. **Do not guess** what a diagram shows — if
   it is illegible, log an `OQ-###`.

Confirm total pages and slides ingested before proceeding.

## Step 1 — Requirements Traceability Matrix
Produce `docs/REQUIREMENTS.md`. This is the core artifact of Phase 0.

Every requirement gets a row:

| ID | Requirement (verbatim or close paraphrase) | Type | Source | RQ | Priority | Phase | Acceptance criterion |
|----|---|---|---|---|---|---|---|
| REQ-001 | ... | FUNC / NFR / RESEARCH / DATA / UI / OPS | Proposal p.4 / Slide 7 | RQ1 | MUST/SHOULD/COULD | P2 | Testable, observable statement |

Rules:
- **Every** requirement must have a `Source` citation with a page or slide number.
  A row without a citation is invalid.
- Decompose compound sentences into atomic requirements. "Train on Hindi, Marathi and
  Tamil with compression augmentation" is at least four requirements.
- Acceptance criteria must be *checkable by a machine or a reviewer*. "Good accuracy"
  is invalid; "EER reported per-language on the held-out test split" is valid.
- Target ≥ 120 requirements. If you have fewer than 80, you skimmed — go back.
- Include a final section: **Coverage audit** — walk every page/slide number in order
  and state which REQ IDs came from it. Any page contributing zero requirements must be
  explicitly justified (e.g. "p.1 title page").

## Step 2 — `docs/PROJECT_ANALYSIS.md`
Organised synthesis, every claim citing REQ IDs:

1. Problem statement & motivation
2. Research questions RQ1–RQ5 — full statement, the hypothesis, the experiment that
   answers it, the metric that decides it, the failure condition
3. Objectives, each mapped to RQ IDs and REQ IDs
4. Scope: in-scope / explicitly out-of-scope / deferred
5. Datasets — one subsection each (Kathbath, IndicVoices-R, Common Voice, IndicSynth,
   team recordings, generated audio): licence, access route, languages, real/fake,
   approx size, known caveats. Mark anything not stated in the proposal as `OQ-###`.
6. Required per-clip metadata schema (speaker, language, source, label, compression
   status, sample rate, duration, split, attack type, generation model, dataset source)
   — as a typed schema sketch, with nullability and allowed values per field
7. Model architecture as specified: frozen Wav2Vec2 XLS-R → cached embeddings → AASIST
   classifier. Note every hyperparameter the proposal states and every one it does not.
8. Baselines: LFCC+GMM, RawNet2, English-only, main model — what each isolates
9. Evaluation protocol: every metric (Accuracy, Precision, Recall, F1, ROC, AUC, EER,
   minDCF, confusion matrix, cross-language matrix, cross-condition matrix, per-language,
   per-attack, per-compression), plus split policy and statistical tests
10. Calibration: temperature scaling, ECE, reliability diagrams, Brier, entropy,
    confidence histograms, coverage curves, reliability badge thresholds
11. Explainability: GradCAM, frequency importance, spectrogram comparison, compression
    artifact visualisation, attention visualisation
12. Human study protocol: participants, randomisation, confidence scale, anonymisation,
    export format, model-vs-human statistical comparison
13. Compression conditions: clean, WhatsApp-style Opus, bitrate ladder, quality levels —
    exact codec/bitrate/container values where stated
14. Complete UI inventory: every page, every widget on it, and the REQ it satisfies
15. Backend / API / data / deployment requirements
16. Deliverables the proposal promises (demo, paper, artefacts) and their acceptance bar

## Step 3 — `docs/OPEN_QUESTIONS.md`
Every gap, ambiguity, and proposal-vs-PPT conflict:

| ID | Question | Why it matters | Blocking? | Proposed default | Source |
|----|---|---|---|---|---|
| OQ-001 | ... | ... | Yes/No | ... | Proposal p.9 vs Slide 12 |

Be aggressive here — an honest 30-row OQ list is worth more than a confident fabrication.

## Step 4 — `docs/SYSTEM_ARCHITECTURE.md`
- C4 Level 1 (context) and Level 2 (containers) as Mermaid diagrams
- Component diagram per layer
- The canonical pipeline as a Mermaid flowchart:
  `raw audio → validation → normalization → compression variants → XLS-R embedding
   (cached) → AASIST → calibration → explainability → API → dashboard`
- Sequence diagrams: single-file upload inference; real-time streaming inference;
  training run; evaluation sweep
- ER diagram for the database
- Every ABC/port in the system: name, responsibility, method signatures, known implementations
- Directory layout with a one-line purpose for every top-level folder
- Technology decision table: choice | alternatives considered | rationale | REQ IDs
- Non-functional targets: latency budget, throughput, model size, memory ceiling
  (cite proposal or mark as `OQ-###`)

## Step 5 — `docs/PROJECT_ROADMAP.md`
Phases P1–P9, each with: goal, ROADMAP-### task IDs, REQ IDs covered, dependencies,
exit criteria, and risks.
- P1 Foundation & scaffold
- P2 Dataset pipeline & metadata store
- P3 Audio + compression pipeline
- P4 Embedding extraction & caching
- P5 Model, training loop, baselines
- P6 Evaluation engine & research metrics
- P7 Calibration engine
- P8 Explainability engine
- P9 Web app, real-time mode, human study module, deployment

Add a **Risk register**: risk | likelihood | impact | mitigation | trigger.

## Phase 0 exit criteria — all must be true
- [ ] Every page and slide accounted for in the REQUIREMENTS coverage audit
- [ ] ≥ 80 requirements, each with a page/slide citation
- [ ] Every REQ maps to ≥ 1 RQ or is marked `INFRA`
- [ ] Every RQ1–RQ5 has ≥ 1 experiment and ≥ 1 deciding metric
- [ ] Zero occurrences of "Telugu"/"te" as a project language
- [ ] `grep -c "OQ-" docs/OPEN_QUESTIONS.md` > 0
- [ ] All five documents exist and cross-reference each other by ID
- [ ] No application code written

## Output now
Start with Step 0 only. Show me `ingest_report.json` and the page/slide counts, then
**stop and wait for my confirmation** before Step 1.
```

---
---

# BLOCK C — Phase 1 Prompt (new chat, after Phase 0 is approved)

```
# PHASE 1 — Foundation & Scaffold

Read `.cursor/rules/vaaniq-core.mdc`, `docs/REQUIREMENTS.md`, `docs/SYSTEM_ARCHITECTURE.md`,
and `docs/PROJECT_ROADMAP.md` before touching anything.

## Scope
**IN:** repo structure, tooling, config system, logging, DI composition root, typed
schemas shared between backend and frontend, empty-but-typed module skeletons, Docker,
CI, test harness, docs skeleton, initial commits.

**OUT (do not write):** model code, training loops, dataset downloads, audio DSP
implementations, calibration math, GradCAM. Their *interfaces* are in scope; their
*bodies* raise `NotImplementedError` with a `ROADMAP-###` reference.

## Target structure
Create exactly this. Every Python package gets `__init__.py`; every directory gets a
`README.md` stating its purpose and the REQ IDs it serves.

```
vaaniq/
├── .cursor/rules/
├── .github/workflows/          # ci.yml, docs.yml
├── backend/
│   ├── src/vaaniq/
│   │   ├── core/
│   │   │   ├── domain/         # entities, value objects — zero framework imports
│   │   │   ├── ports/          # ABCs: AudioLoader, FeatureExtractor, Classifier,
│   │   │   │                   #   Compressor, Calibrator, Explainer, Repository,
│   │   │   │                   #   ExperimentTracker, ObjectStore
│   │   │   ├── errors.py
│   │   │   └── types.py        # Language enum {HI, MR, TA}, Label, AttackType, ...
│   │   ├── config/             # pydantic-settings, hydra-compatible loaders
│   │   ├── datasets/           # sources/, manifests/, splits/  (interfaces only)
│   │   ├── audio/              # io/, transforms/, compression/, cache/ (interfaces only)
│   │   ├── features/           # xlsr/, cache/ (interfaces only)
│   │   ├── models/             # aasist/, baselines/{lfcc_gmm,rawnet2}/, registry.py
│   │   ├── training/           # trainer, callbacks, schedulers (interfaces only)
│   │   ├── evaluation/         # metrics/, matrices/, reports/ (interfaces only)
│   │   ├── calibration/        # temperature, ece, reliability (interfaces only)
│   │   ├── explainability/     # gradcam, freq_importance (interfaces only)
│   │   ├── human_study/        # participants, sessions, export (interfaces only)
│   │   ├── streaming/          # window buffer, session manager (interfaces only)
│   │   ├── persistence/        # sqlalchemy models, repositories, alembic/
│   │   ├── storage/            # local + object-store adapters
│   │   ├── observability/      # structlog config, request ids, metrics
│   │   ├── api/
│   │   │   ├── v1/routers/     # health, inference, uploads, history, experiments,
│   │   │   │                   #   metrics, calibration, explain, human_study, admin
│   │   │   ├── schemas/        # pydantic request/response models
│   │   │   ├── deps.py         # DI providers
│   │   │   └── app.py          # factory: create_app(settings)
│   │   └── container.py        # composition root
│   ├── tests/{unit,integration,api,fixtures}/
│   ├── pyproject.toml
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── app/                # router, providers, error boundary
│   │   ├── pages/              # landing, dashboard, upload, live, inference, history,
│   │   │                       #   research-metrics, experiments, calibration,
│   │   │                       #   explainability, admin, docs
│   │   ├── components/{ui,charts,audio,layout}/
│   │   ├── hooks/
│   │   ├── api/{client.ts,generated/}
│   │   ├── lib/
│   │   ├── types/
│   │   └── styles/
│   ├── tests/
│   ├── package.json  tsconfig.json  vite.config.ts  tailwind.config.ts
│   └── Dockerfile
├── configs/
│   ├── base.yaml
│   ├── data/{kathbath,indicvoices_r,common_voice,indicsynth,team_recordings}.yaml
│   ├── audio/{preprocessing,compression}.yaml
│   ├── model/{xlsr_aasist,lfcc_gmm,rawnet2}.yaml
│   ├── train/{default,cv,english_only}.yaml
│   ├── eval/{full,zero_shot,cross_condition}.yaml
│   ├── calibration/temperature.yaml
│   └── env/{local,dev,prod}.yaml
├── scripts/                    # ingest_sources.py, bootstrap_dev.sh, gen_api_types.sh
├── deployment/
│   ├── docker-compose.yml  docker-compose.dev.yml
│   └── nginx/
├── docs/                       # from Phase 0 + guides added here
├── notebooks/                  # numbered, output-stripped via nbstripout
├── research/{experiments,figures,paper}/
├── data/                       # gitignored; .gitkeep + README only
├── models/                     # gitignored; registry manifest only
├── .env.example  .gitignore  .gitattributes  .pre-commit-config.yaml
├── Makefile  LICENSE  README.md  CONTRIBUTING.md
```

## Required implementations (these are real, not stubs)
1. **`core/types.py`** — `Language` enum with exactly `HI`, `MR`, `TA`; `Label`
   {`REAL`,`FAKE`}; `CompressionCondition`; `AttackType`; `DatasetSource`; `Split`.
   Language must be iterated from the enum everywhere — no hardcoded lists, no string
   literals. Add a test that asserts `len(Language) == 3` and that no member equals `"te"`.
2. **`core/ports/*.py`** — every ABC from `SYSTEM_ARCHITECTURE.md`, fully typed,
   fully docstringed, with the REQ IDs each satisfies.
3. **`config/`** — layered loading: defaults → yaml → env → CLI override. Fully typed
   pydantic-settings models. Fail loudly on unknown keys.
4. **`observability/`** — structlog JSON, request-ID middleware, exception handler
   returning RFC-7807 problem details.
5. **`api/app.py`** — working FastAPI app: `/health`, `/health/ready`, `/api/v1/version`,
   OpenAPI at `/docs`, CORS from config, all routers mounted with typed stub handlers
   returning `501 Not Implemented` plus a roadmap reference.
6. **`persistence/`** — SQLAlchemy 2.0 models + Alembic initial migration for:
   `uploads`, `predictions`, `experiments`, `experiment_metrics`, `models`,
   `calibration_runs`, `human_study_participants`, `human_study_responses`, `users`.
   SQLite by default, PostgreSQL-compatible types only.
7. **Frontend shell** — Vite + React 18 + TS strict + Tailwind + shadcn init, routing
   for all 12 pages, layout with nav, dark/light theme, TanStack Query provider,
   API client reading `VITE_API_BASE_URL`, one live call to `/health` proving the
   frontend↔backend loop works end to end.
8. **Type generation** — `scripts/gen_api_types.sh` runs
   `openapi-typescript` against the live schema into `frontend/src/api/generated/`.
   CI fails if regenerating produces a diff.
9. **Docker** — multi-stage backend (deps → build → runtime, non-root user) and
   frontend (build → nginx). `docker compose up` brings up both plus the DB and passes
   healthchecks.
10. **CI** (`.github/workflows/ci.yml`) — matrix job running ruff, mypy --strict,
    pytest with coverage gate, tsc --noEmit, eslint, vitest, docker build, and the
    API-type drift check.
11. **`Makefile`** — `setup install dev test lint format typecheck check docker-up
    docker-down clean gen-types migrate`. `make check` runs every gate.
12. **Docs skeleton** — `README.md` (badges, architecture image, 5-minute quickstart
    that actually works), plus `docs/{DEVELOPER_GUIDE,API,TRAINING,DATASETS,DEPLOYMENT,
    RESEARCH,EXPERIMENTS,CONTRIBUTING}.md` with real structure and TODO markers tied
    to roadmap IDs.

## Execution order — one commit per step, gates green before moving on
1. Repo init, `.gitignore`, `.gitattributes`, LICENSE, pre-commit
2. Backend package skeleton + `pyproject.toml` + tooling config
3. `core/` — types, errors, domain, ports (+ tests)
4. `config/` (+ tests)
5. `observability/`
6. `persistence/` + Alembic initial migration (+ tests)
7. `api/` app factory, health, versioned routers (+ API tests)
8. Remaining backend module skeletons with ABCs and xfail tests
9. `configs/*.yaml` tree
10. Frontend scaffold + routing + theme + API client (+ tests)
11. `scripts/gen_api_types.sh` and generated types committed
12. Dockerfiles + compose, verified `docker compose up`
13. CI workflow, verified locally where possible
14. Docs skeleton + README quickstart
15. Final `make check`, then the scaffold commit

## Phase 1 exit criteria — I will verify each of these
- [ ] `make check` exits 0
- [ ] `mypy --strict backend/src` — zero errors
- [ ] `tsc --noEmit` — zero errors; `grep -rn ": any" frontend/src` returns nothing
- [ ] `docker compose up` → both healthchecks green, frontend renders backend `/health`
- [ ] `alembic upgrade head` then `downgrade base` both succeed
- [ ] `grep -rni "telugu\|'te'" --include=*.py --include=*.ts --include=*.yaml .`
      returns nothing
- [ ] Every ABC in `core/ports/` has a docstring naming its REQ IDs
- [ ] Every `TODO`/`NotImplementedError` cites a `ROADMAP-###` that exists in the roadmap
- [ ] Zero ML algorithm implementations
- [ ] `git log --oneline` shows ≥ 15 conventional commits, each independently building

## Start
Post your plan for steps 1–3 only, then execute step 1 and stop for review.
```

---
---

# What changed, and why

| Problem in the original | Fix |
|---|---|
| "You are NOT an AI assistant" + 8 job titles | Dropped. Role-play framing costs tokens and doesn't improve output; concrete constraints do. |
| "Read line by line, do NOT skim" | Unenforceable. Replaced with a **traceability matrix requiring page citations** — the agent cannot produce it without reading. |
| PDF/PPTX handed straight to the agent | Step 0 converts them to cited markdown + renders image-only pages. Extraction failure now surfaces instead of silently becoming hallucination. |
| One mega-prompt | Split into persistent rules file + per-phase prompts. Cursor's rules system keeps constraints alive across the whole project. |
| No anti-hallucination rule | Explicit ban on inventing facts + `OPEN_QUESTIONS.md` as the pressure-release valve, so gaps get logged rather than filled in. |
| Bare lists ("Accuracy, Precision, Recall…") | Kept, but each must land in REQUIREMENTS with an acceptance criterion. |
| No definition of done | Machine-checkable exit criteria per phase, including the literal grep commands. |
| Telugu warning repeated as prose | Converted to a grep-able test and a CI-checkable criterion. |
| "Work iteratively" | Concrete: numbered execution order, one commit per step, gates green before advancing, mandatory stop points. |
| No response format | Fixed 5-section turn format so you can audit progress at a glance. |

## Two things to do before pasting

**1. Confirm the Telugu constraint direction.** Your prompt says "Tamil, not Telugu" four times — that intensity usually means the source documents say Telugu somewhere. If the proposal actually specifies Telugu, the rules file will fight the source of truth. Check page-by-page during Phase 0 and, if there's a real conflict, resolve it with your supervisor before Phase 1.

**2. Fill in your environment.** Append this to Block A before saving it, replacing the placeholders — otherwise the agent will assume a GPU you may not have:

```
## Environment
- OS: <Windows 11 / macOS 14 / Ubuntu 22.04>
- Python: 3.11 via <uv / conda / venv>
- Node: <20 LTS> via <nvm / volta>
- GPU: <none / RTX 4060 8GB / Colab T4 / university cluster>
- Package manager: <uv / poetry / pip-tools>
- Existing repo state: <empty / has commits>
- Assume no internet during test runs.
```
