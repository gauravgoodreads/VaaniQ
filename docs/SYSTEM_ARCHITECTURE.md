# VaaniQ — System Architecture

> Phase 0 Step 4. Cites REQ IDs. Engineering style: clean/hexagonal architecture per `vaaniq-core.mdc`.

---

## 1. C4 Level 1 — System Context

```mermaid
C4Context
title VaaniQ System Context
Person(researcher, "Researcher / Reviewer", "Trains, evaluates, views metrics")
Person(listener, "Human-study volunteer", "Forced-choice listening test")
Person(demoUser, "Demo user", "Uploads or records a clip")
System(vaaniq, "VaaniQ", "Cross-lingual Opus-robust deepfake detection with calibrated confidence")
System_Ext(hf, "Hugging Face datasets/models", "Kathbath, IndicVoices-R, CV, IndicSynth, XLS-R")
System_Ext(ffmpeg, "ffmpeg", "Opus compression / decode")
System_Ext(forms, "Google Forms / static study page", "Human baseline collection")
System_Ext(spaces, "HF Spaces / local host", "Demo hosting")
Rel(demoUser, vaaniq, "Upload / record audio")
Rel(researcher, vaaniq, "Train, eval, calibrate")
Rel(listener, forms, "Judgements + confidence 1-5")
Rel(forms, vaaniq, "Export responses")
Rel(vaaniq, hf, "Download corpora / weights")
Rel(vaaniq, ffmpeg, "Compress / decode")
Rel(vaaniq, spaces, "Serve demo")
```

---

## 2. C4 Level 2 — Containers

```mermaid
C4Container
title VaaniQ Containers
Person(user, "User")
Container(web, "Web App", "React + TS", "Upload, live, metrics, explainability")
Container(bff, "Request layer", "Node.js", "Auth-light routing, upload validation proxy")
Container(api, "Inference & Research API", "FastAPI", "Inference, eval jobs, calibration, explain")
Container(worker, "Experiment worker", "Python", "Train, embed, eval sweeps")
ContainerDb(db, "Metadata DB", "SQLite/Postgres", "uploads, predictions, experiments")
ContainerDb(obj, "Object store", "Local/S3/Drive", "audio, embeddings, artefacts")
Rel(user, web, "HTTPS")
Rel(web, bff, "REST")
Rel(bff, api, "REST")
Rel(api, db, "SQL")
Rel(api, obj, "Read/Write")
Rel(worker, db, "SQL")
Rel(worker, obj, "Read/Write")
Rel(api, worker, "Enqueue jobs")
```

**Assumption OQ-026:** Phase 1 may wire React → FastAPI directly; Node BFF lands before final demo (**REQ-092**).

---

## 3. Canonical pipeline

```mermaid
flowchart LR
  raw[Raw audio] --> val[Validation]
  val --> norm[Normalize / resample / trim]
  norm --> comp[Compression variants]
  comp --> xlsr[XLS-R embedding cached]
  xlsr --> aasist[AASIST head]
  aasist --> cal[Temperature calibration]
  cal --> xai[Explainability]
  xai --> api[API]
  api --> dash[Dashboard]
```

Maps to Proposal Fig.1 (**REQ-098**, **REQ-035–038**, **REQ-054**, **REQ-075**, **REQ-084**).

---

## 4. Sequence — single-file upload inference

```mermaid
sequenceDiagram
  actor U as User
  participant FE as React
  participant API as FastAPI
  participant Store as ObjectStore
  participant Emb as FeatureExtractor
  participant Clf as Classifier
  participant Cal as Calibrator
  participant Xai as Explainer
  U->>FE: Upload clip
  FE->>API: POST /api/v1/uploads
  API->>API: MIME/magic/duration/size checks
  API->>Store: Put audio
  API->>Emb: Extract or cache lookup
  Emb->>Clf: Embedding
  Clf->>Cal: Logits
  Cal->>Xai: Calibrated probs + optional explain
  Xai-->>API: Artefacts
  API-->>FE: Verdict, confidence, reliability, explain refs
  FE-->>U: Dashboard update
```

Latency budget: ~≤2 s CPU (**REQ-097**) — **OQ** if XLS-R not cached at request time.

---

## 5. Sequence — real-time streaming inference

```mermaid
sequenceDiagram
  actor U as User
  participant FE as React MediaRecorder
  participant API as FastAPI StreamingSession
  U->>FE: Start mic
  loop every hop (OQ-019)
    FE->>API: POST window bytes
    API->>API: Buffer + infer
    API-->>FE: Partial verdict + confidence
  end
  U->>FE: Stop
  FE->>API: Finalize session
```

---

## 6. Sequence — training run

```mermaid
sequenceDiagram
  participant CLI as Train entrypoint
  participant Cfg as Config
  participant Emb as Embedding cache
  participant Tr as Trainer
  participant Man as Manifest writer
  CLI->>Cfg: Load yaml + --seed
  CLI->>Emb: Ensure embeddings for split
  CLI->>Tr: Fit AASIST head only
  Tr->>Man: Write metrics + git SHA + checksums
```

---

## 7. Sequence — evaluation sweep

```mermaid
sequenceDiagram
  participant Ev as Eval engine
  participant M as Model registry
  participant Met as Metrics
  Ev->>M: Load model + baselines
  loop language × condition × attack
    Ev->>Met: Score batch
  end
  Ev->>Ev: Build cross-lingual & cross-condition matrices
  Ev->>Ev: Export tables/figures
```

---

## 8. ER diagram (persistence)

```mermaid
erDiagram
  users ||--o{ uploads : creates
  uploads ||--o{ predictions : yields
  experiments ||--o{ experiment_metrics : has
  experiments ||--o{ models : produces
  calibration_runs }o--|| models : calibrates
  human_study_participants ||--o{ human_study_responses : gives
  uploads {
    uuid id PK
    string language
    string compression_status
    string storage_uri
    float duration_sec
  }
  predictions {
    uuid id PK
    uuid upload_id FK
    string label
    float confidence
    string reliability
    json extras
  }
  experiments {
    uuid id PK
    string name
    string git_sha
    json config
    int seed
  }
  experiment_metrics {
    uuid id PK
    uuid experiment_id FK
    string metric_name
    float value
    json dims
  }
  models {
    uuid id PK
    string name
    string uri
    json card
  }
  calibration_runs {
    uuid id PK
    uuid model_id FK
    json temperatures
    float ece_pre
    float ece_post
  }
  human_study_participants {
    uuid id PK
    string fluency_self_report
  }
  human_study_responses {
    uuid id PK
    uuid participant_id FK
    string clip_id
    string choice
    int confidence_1_5
  }
  users {
    uuid id PK
    string role
  }
```

---

## 9. Ports (ABCs)

| Port | Responsibility | Key methods | Known implementations |
|------|----------------|-------------|------------------------|
| `AudioLoader` | Load bytes/path → waveform | `load(uri) -> Waveform` | SoundFileLoader, FallbackDecoderLoader (**REQ-094**) |
| `AudioValidator` | MIME/magic/duration/size | `validate(upload) -> None` | MagicByteValidator (**REQ-135**) |
| `Preprocessor` | Resample, trim, normalize | `transform(wav) -> Waveform` | FFmpegPreprocessor (**REQ-098**) |
| `Compressor` | Clean→Opus twin | `compress(wav, cfg) -> Waveform` | FFmpegOpusCompressor (**REQ-113**) |
| `FeatureExtractor` | XLS-R embeddings | `extract(wav) -> Embedding` | FrozenXLSRExtractor (**REQ-036**) |
| `EmbeddingCache` | Persist embeddings | `get/put(key)` | FilesystemEmbeddingCache (**REQ-037**) |
| `Classifier` | Logits / scores | `predict(emb) -> Logits` | AASISTClassifier, RawNet2, LFCCGMM (**REQ-038**, **042–043**) |
| `Calibrator` | Temperature / probs | `fit`, `transform` | TemperatureScaler (**REQ-054**) |
| `Explainer` | XAI artefacts | `explain(clip, model)` | GradCAMExplainer, BandImportanceExplainer (**REQ-075–076**) |
| `DatasetSource` | Pull/iterate corpora | `iter_clips()` | KathbathSource, … (**REQ-101–104**) |
| `Repository` | Persistence | CRUD | SqlAlchemyRepositories |
| `ObjectStore` | Blob storage | `put/get` | LocalObjectStore, S3ObjectStore |
| `ExperimentTracker` | Metrics/manifests | `log_metric`, `write_manifest` | FileExperimentTracker (**REQ-137**) |
| `HumanStudyExporter` | Export responses | `export(format)` | CsvExporter (**REQ-069**) |

---

## 10. Directory layout (target)

```text
vaaniq/
  backend/src/vaaniq/   # domain, ports, adapters, api
  frontend/            # React app
  configs/             # yaml constants (no magic numbers in src)
  scripts/             # ingest, bootstrap, gen-types
  docs/                # Phase 0 + guides
  data/                # gitignored audio
  models/              # gitignored weights
  research/            # experiments, figures, paper
  deployment/          # compose, nginx
```

Each top-level folder purpose matches Phase-1 scaffold prompt; created in Phase 1, not Phase 0.

---

## 11. Technology decisions

| Choice | Alternatives | Rationale | REQs |
|--------|--------------|-----------|------|
| Frozen XLS-R + AASIST | Train full SSL; Whisper encoder | Proposal architecture; cheap iteration on cache | REQ-036–038 |
| ffmpeg Opus | torchaudio codecs only | Proposal §11; WhatsApp-like control | REQ-113 |
| FastAPI inference | Flask, pure Node inference | Typed OpenAPI; research Python stack | REQ-092 |
| Node request layer | FastAPI-only | Proposal three-tier; swap model without FE change | REQ-092–093 |
| React + TS | Vue, plain HTML | Proposal frontend; strict FE standards | REQ-084 |
| Temperature scaling | Vector scaling, ensembles | Pascu-style; low cost | REQ-054 |
| SQLite default | Postgres-only | Laptop-friendly; PG-compatible types | OQ-021 |
| uv + Python 3.11 | conda | Environment rule | INFRA |

---

## 12. Non-functional targets

| Target | Value | Source |
|--------|-------|--------|
| Clip inference latency | ~≤2 s CPU | Proposal p.10; REQ-097 |
| AASIST head size | ~1–5M params | Proposal §5.1; REQ-040 |
| Dataset storage | ~50–80 GB | Proposal §11; REQ-111 |
| Throughput | Not stated | **OQ-020** / leave unset |
| Memory ceiling | Not stated | **OQ** — assume Colab T4 16 GB for embedding |
| Live window | Not stated | **OQ-019** default 2.0/0.5 s |

---

## 13. Component diagram (logical layers)

```mermaid
flowchart TB
  subgraph presentation
    UI[React pages]
  end
  subgraph application
    API[API routers]
    APP[Use-cases / services]
  end
  subgraph domain
    ENT[Entities / value objects]
    PORTS[Ports ABCs]
  end
  subgraph adapters
    INF[FastAPI / SQL / ffmpeg / HF]
  end
  UI --> API --> APP --> PORTS
  APP --> ENT
  INF --> PORTS
```

Domain must not import FastAPI/SQLAlchemy (`vaaniq-core.mdc`).

---

## Cross-references

- REQs: especially **REQ-036–038**, **REQ-084–096**, **REQ-092**, **REQ-113**, **REQ-135–137**
- Open questions: **OQ-007**, **OQ-013**, **OQ-016**, **OQ-019–021**, **OQ-026**
- Implementation order: `docs/PROJECT_ROADMAP.md` (**ROADMAP-001+**)
