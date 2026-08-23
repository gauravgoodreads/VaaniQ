# VaaniQ — Next Steps

Phase 4 research-platform software is in place. Remaining for dissertation **results**:

1. **Operator data** — Curate HI/MR/TA hours, generate Opus twins (needs working ffmpeg), fill embedding cache with real XLS-R (`uv sync --extra ml` + HF token).
2. **Paper-faithful AASIST** — Swap NumPy head for clovaai/aasist torch graph on Colab/Kaggle T4; keep the same Trainer/manifest contract.
3. **Fill RQ tables** — `python -m vaaniq.research.cli` on real embeddings; paste SVG/CSV into the dissertation.
4. **Human study collection** — ≥12–15 responses on shared clip IDs (ROADMAP-060). Software/UI is ready.
5. **Paper draft (ROADMAP-064)** — Structure on RQ1–RQ5.
6. **Open release (ROADMAP-063)** — Licence matrix (OQ-035).
7. **Optional** — Node BFF (ROADMAP-058); publish HF Spaces (`deployment/spaces/`).

Do **not** claim success criteria REQ-063 / 121–124 until real curated eval numbers and human N exist.

See [`PROJECT_COMPLETION_CHECKLIST.md`](PROJECT_COMPLETION_CHECKLIST.md).
