# Research contributions (traceability)

> Maps software to proposal §4 (RQ1–RQ5) and §6 (O1–O8). **Software ≠ published result.**

## Combined gap (proposal §5.7)

The citable contribution is the **combination** of Indic voice-cloning/TTS fraud audio, WhatsApp-style Opus, calibration/reliability, and a human baseline on the same stimuli — not “first Indic detector.”

## RQ / objective → code

| ID | Question / objective | Software | Result status |
|----|----------------------|----------|---------------|
| RQ1 | Opus degradation vs clean | Paired 16 kbps Opus evaluation | **Complete** — model-dependent acoustic and XLS-R results |
| RQ2 | Multilingual vs English-only | English-only ASVspoof control and multilingual comparator | **Complete** — catastrophic English→Indic transfer documented |
| RQ3 | Unseen-language generalisation | Three leave-one-language-out folds | **Complete** — asymmetric transfer; Hindi weakest |
| RQ4 | Calibration under shift | Validation-selected temperature scaling and held-out audit | **Complete** — Baseline V1 ECE slightly worsened on test |
| RQ5 | Human vs model | Protocol, UI, export, stats | **Blocked on human data** — N=0; no human result |
| O1 | Dataset | Parsers, manifests, stats, explorer | **Complete for bounded V1; V2 partial** |
| O2 | WhatsApp simulation | ffmpeg/libopus paired twins | **Complete for 16 kbps simulation** |
| O3 | Benchmarked model | Acoustic, frozen XLS-R, LFCC-GMM, approximate RawNet2-style, English control | **Complete except faithful RawNet2 pending** |
| O4 | Generalisation study | Cross-lingual matrix and V2 pilot | **Partial externally** — generator-disjoint n=0 |
| O5 | Calibrated reliability | Calibration module, held-out metrics, UI | **Complete with negative transfer result retained** |
| O6 | Human baseline | Human-study module | **Blocked on human data** — N=0 |
| O7 | Live demo | FastAPI + React + compose | **Complete** as a demo (upload/live/confidence/flag/explain) |
| O8 | Publication | Frozen manifest, figures, CSVs, IEEE and master documents | **Complete for capstone documentation** |
