# Project scorecard (Phase 5)

> **Historical Phase 5 audit — not the approved Round 3 assessment.** Scores and
> statements below intentionally preserve the pre-experiment review state. They must
> not be used as current research results or ratings. Current metrics are frozen in
> `artifacts/final_results_manifest.json`; this documentation pass does not rerate them.

Grades are **1–10** against what an ICSE reviewer, a FAANG hiring manager, and a university examiner would actually inspect. 10 means publication-grade empirical science **and** production-grade engineering. This repo is stronger as software than as completed research.

| Category | Score | Why |
|----------|------:|-----|
| Architecture | **8** | Hexagonal ports, composition root, typed config, no domain→FastAPI imports. Deducted for process-global `_STATE` and ORM unused on the live path. |
| Scalability | **5** | Single-process NumPy inference, in-memory sessions/history, no queue. Compose + Postgres is a start, not horizontal scale. |
| Research quality | **6** | RQ1–RQ5 apparatus exists (suites, metrics, human protocol, figures). Empirical cells on curated hours and listeners are **not** filled. Honest docs (`KNOWN_LIMITATIONS.md`) raise the score vs typical student overclaim. |
| Code quality | **7** | `ruff` + `mypy --strict`, Google-ish docstrings on public modules, conventional layout. God services and `except Exception` embedding fallback remain. |
| ML quality | **7** | Class-conditional EER/min-DCF, speaker-disjoint splitter, T-scaling with a fit/eval split, seeds/manifests. Deducted for NumPy AASIST-not-graph, trainer train-prefix val, synthetic demo metrics. |
| UI/UX | **7** | Distinct research palette, gauges, skip link, loading/error states, reduced-motion, no Telugu, no leftover `PageStub`. Dense 14-item nav and live-PCM limitation keep it off 8–9. |
| Documentation | **8** | Proposal extracts, REQ/OQ/roadmap, architecture, API, limitations, this audit set. Dual overlapping files can drift. |
| Testing | **8** | Unit+API coverage gated ≥80% on `backend/src/`; hypothesis on audio ops; Vitest on shell. No Playwright e2e; no GPU integration in default CI. |
| Deployment | **7** | Docker Compose (API, Postgres, nginx), Spaces Dockerfile, health/ready. Default DB password (now localhost-bound). No Node BFF (OQ-026). |
| Maintainability | **7** | Clear packages and ROADMAP ids. Global demo state and unused ORM confuse the next engineer. |
| Security | **6** | Real upload validation, prod Swagger off, store-key hardening. No auth; open admin; lab Postgres defaults. Appropriate for a closed demo, not the public internet. |
| Performance | **6** | Sensible downsample/JSON bounds and DB indexes. No GPU profile, event-loop blocking inference, unbounded `_STATE`. |
| Reproducibility | **7** | Seeds, manifests, JSONL experiment store, versioned splits. Real audio checksums/hours not yet in the artefact. |
| Publication readiness | **4** | Cannot submit RQ answers without data+listeners+GPU tables. Software + protocol can support a methods appendix today. |

**Mean (unweighted): 6.6 / 10.**

## How to raise the score without bloat

1. Fill O1 hours and run RQ1–RQ4 on cached embeddings (research + ML + publication).
2. Collect RQ5 N≥12–15 on the same clips (research + publication).
3. Delete or clearly flag synthetic `/metrics` when history is empty (integrity).
4. Containerise `_STATE` and persist predictions (architecture + security DoS).
5. Swap NumPy head for official AASIST on a T4 when training (proposal §7.2–7.3).

Do **not** add chatbots, extra languages, or a custom auth product. Those would lower proposal alignment.
