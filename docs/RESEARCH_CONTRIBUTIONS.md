# Research contributions (traceability)

> Maps software to proposal §4 (RQ1–RQ5) and §6 (O1–O8). **Software ≠ published result.**

## Combined gap (proposal §5.7)

The citable contribution is the **combination** of Indic voice-cloning/TTS fraud audio, WhatsApp-style Opus, calibration/reliability, and a human baseline on the same stimuli — not “first Indic detector.”

## RQ / objective → code

| ID | Question / objective | Software | Result status |
|----|----------------------|----------|---------------|
| RQ1 | Opus degradation vs clean | Compression suite, Opus compressor, degrade ops, degradation SVG | **Partial** — fixture curves; real hours pending |
| RQ2 | Multilingual vs English-only | AASIST head, LFCC-GMM, RawNet2, English-only baseline, metrics | **Partial** — models exist; ASVspoof ingest pending (OQ-015) |
| RQ3 | Unseen-language generalisation | Leave-one-language-out runner + heatmap | **Partial** — folds implemented; real embeddings pending |
| RQ4 | Calibration under compression | Temperature scaling, ECE/Brier, reliability figures | **Partial** — suite on logits; val/test from manifests pending |
| RQ5 | Human vs model | Protocol, UI, export, stats | **Partial** — software done; N≥12–15 not collected |
| O1 | Dataset | Parsers, manifests, stats, explorer | **Partial** — pipeline; curated hours not ingested |
| O2 | WhatsApp simulation | ffmpeg Opus + resample/loss ladder | **Partial** — Windows spawn may skip ffmpeg |
| O3 | Benchmarked model | Four-model comparison table generator | **Partial** — NumPy AASIST-style, not clovaai graph |
| O4 | Generalisation study | Cross-lingual + cross-condition matrices | **Partial** — code; data pending |
| O5 | Calibrated reliability | Calibration module + UI badge | **Partial** — demo snapshot, not paper tables |
| O6 | Human baseline | Human-study module | **Partial** — no field sample yet |
| O7 | Live demo | FastAPI + React + compose | **Complete** as a demo (upload/live/confidence/flag/explain) |
| O8 | Publication | SVG/CSV/report bundle; arXiv not written | **Partial** — figures path; ROADMAP-064 paper not drafted |
