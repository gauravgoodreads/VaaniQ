#!/usr/bin/env python3
"""Generate docs/REQUIREMENTS.md for VaaniQ Phase 0 Step 1."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "REQUIREMENTS.md"

# Columns: id, requirement, type, source, rq, priority, phase, acceptance
# Types: FUNC | NFR | RESEARCH | DATA | UI | OPS | INFRA
# rq: RQ1..RQ5 | INFRA | MULTI

REQS: list[tuple[str, str, str, str, str, str, str, str]] = [
    # --- Identity / problem (p.1–3, slides 1–4) ---
    ("REQ-001", "System name is VaaniQ with the full research title covering cross-lingual, compression-robust detection and calibrated reliability for AI-generated voice in Indian languages with a human-perception baseline", "INFRA", "Proposal p.1 / Slide 1", "INFRA", "MUST", "P1", "README and package metadata use the exact title string"),
    ("REQ-002", "Detect real vs AI-generated speech in Hindi", "FUNC", "Proposal p.3 §3 / Slide 4", "RQ2", "MUST", "P5", "Held-out Hindi test metrics (EER, Acc) are produced and logged"),
    ("REQ-003", "Detect real vs AI-generated speech in Marathi", "FUNC", "Proposal p.3 §3 / Slide 4", "RQ2", "MUST", "P5", "Held-out Marathi test metrics are produced and logged"),
    ("REQ-004", "Detect real vs AI-generated speech in a third Indian language (Tamil per mockup)", "FUNC", "Proposal p.3 §3; p.14 Fig.2 / Slide 4", "RQ2", "MUST", "P5", "Language enum includes TA; Tamil test metrics produced"),
    ("REQ-005", "Evaluate detection under WhatsApp-style Opus compression", "RESEARCH", "Proposal p.3 §3 / Slide 4", "RQ1", "MUST", "P6", "Cross-condition matrix includes clean↔compressed cells for every language"),
    ("REQ-006", "Report a calibrated, trustworthy confidence rather than a raw uncalibrated score", "FUNC", "Proposal p.3 §3 / Slide 3", "RQ4", "MUST", "P7", "API and UI expose temperature-scaled confidence, not raw logits alone"),
    ("REQ-007", "Benchmark against established ML baselines", "RESEARCH", "Proposal p.3 §3 / Slide 4", "RQ2", "MUST", "P5", "LFCC-GMM, RawNet2, and English-only baseline results tables exist"),
    ("REQ-008", "Benchmark against a human-listener baseline on shared stimuli", "RESEARCH", "Proposal p.3 §3 / Slide 5", "RQ5", "MUST", "P9", "Human vs model accuracy table on identical clip IDs is published"),
    ("REQ-009", "Address the language gap (English/Mandarin-centric benchmarks)", "RESEARCH", "Proposal p.3 §2.2 / Slide 4", "RQ2", "MUST", "P6", "Evaluation uses Indic languages only for primary tables"),
    ("REQ-010", "Address the compression gap (no Indian language in RADAR 2026)", "RESEARCH", "Proposal p.3 §2.2 / Slide 4", "RQ1", "MUST", "P6", "Opus condition evaluation reported for all three languages"),
    ("REQ-011", "Address the trust/calibration gap under language and compression shift", "RESEARCH", "Proposal p.3 §2.2 / Slide 4", "RQ4", "MUST", "P7", "ECE reported per language × compression cell"),
    # --- Research questions ---
    ("REQ-012", "RQ1: quantify Opus compression degradation vs clean audio", "RESEARCH", "Proposal p.3 §4 / Slide 5", "RQ1", "MUST", "P6", "Clean vs compressed EER delta table exists with deciding metric EER"),
    ("REQ-013", "RQ2: compare multilingual training vs English-only baseline on Indic and compressed audio", "RESEARCH", "Proposal p.3 §4 / Slide 5", "RQ2", "MUST", "P6", "Side-by-side EER table multilingual vs English-only on same test sets"),
    ("REQ-014", "RQ3: measure zero-shot generalisation to a completely unseen Indian language", "RESEARCH", "Proposal p.3 §4 / Slide 5", "RQ3", "MUST", "P6", "Train-2/test-1 matrix completed for each held-out language"),
    ("REQ-015", "RQ4: measure whether compression degrades calibration (confidently wrong vs uncertain)", "RESEARCH", "Proposal p.3 §4 / Slide 5", "RQ4", "MUST", "P7", "Pre/post ECE and reliability diagrams per compression condition"),
    ("REQ-016", "RQ5: compare model detection and confidence-calibration to human listeners across languages and conditions", "RESEARCH", "Proposal p.3 §4 / Slide 5", "RQ5", "MUST", "P9", "Human vs model accuracy and calibration curves on shared stimuli"),
    # --- Objectives O1–O8 ---
    ("REQ-017", "O1: assemble labelled real + AI speech across 3 Indian languages", "DATA", "Proposal p.5 §6 / Slide 6", "RQ2", "MUST", "P2", "Manifest lists real/fake clips for HI, MR, TA with labels"),
    ("REQ-018", "O2: simulate WhatsApp-style delivery (Opus, resampling, noise) and evaluate under it", "DATA", "Proposal p.5 §6 / Slide 6", "RQ1", "MUST", "P3", "Every curated clip has a clean and Opus-compressed twin"),
    ("REQ-019", "O3: train and benchmark XLS-R + AASIST vs LFCC-GMM, RawNet2, English-only using EER and min-DCF", "RESEARCH", "Proposal p.5 §6 / Slide 6", "RQ2", "MUST", "P5", "Four-model comparison table with EER and min-DCF"),
    ("REQ-020", "O4: evaluate cross-lingual (train 2, test 1) and cross-condition (clean/compressed) generalisation", "RESEARCH", "Proposal p.5 §6 / Slide 6", "RQ3", "MUST", "P6", "Cross-lingual and cross-condition matrices both present in eval report"),
    ("REQ-021", "O5: measure and improve confidence calibration (ECE, reliability diagrams, Brier, temperature scaling)", "RESEARCH", "Proposal p.5 §6 / Slide 6", "RQ4", "MUST", "P7", "Post-calibration ECE ≤ pre-calibration ECE in majority of cells (success §17)"),
    ("REQ-022", "O6: run bounded listening-test comparing human and model accuracy/confidence", "RESEARCH", "Proposal p.5 §6 / Slide 6", "RQ5", "MUST", "P9", "≥12–15 responses collected and analysed (success floor §17)"),
    ("REQ-023", "O7: build live demo reporting calibrated confidence and reliability flag", "UI", "Proposal p.5 §6 / Slide 6", "RQ4", "MUST", "P9", "Demo accepts upload/record and returns confidence + reliability flag + ≥1 explainability view"),
    ("REQ-024", "O8: release dataset, code, and benchmark tables openly (arXiv / conference)", "OPS", "Proposal p.5 §6 / Slide 6", "INFRA", "SHOULD", "P9", "Public repo + arXiv preprint checklist completed"),
    # --- Dataset layers ---
    ("REQ-025", "Use curated Kathbath subsets as real (bonafide) speech", "DATA", "Proposal p.5 §7.1 / Slide 12", "RQ2", "MUST", "P2", "Kathbath clips appear in real-audio manifest with source=kathbath"),
    ("REQ-026", "Use curated IndicVoices-R subsets as real speech", "DATA", "Proposal p.5 §7.1 / Slide 12", "RQ2", "MUST", "P2", "IndicVoices-R clips in real-audio manifest with source=indicvoices_r"),
    ("REQ-027", "Use Common Voice v17 Hindi (hi) config as real speech", "DATA", "Proposal p.5 §7.1; p.11 / Slide 12", "RQ2", "MUST", "P2", "CV hi clips in manifest"),
    ("REQ-028", "Use Common Voice v17 Marathi (mr) config as real speech", "DATA", "Proposal p.5 §7.1; p.11 / Slide 12", "RQ2", "MUST", "P2", "CV mr clips in manifest"),
    ("REQ-029", "Include consenting team/classmate phone-mic recordings for realism", "DATA", "Proposal p.5 §7.1 / Slide 12", "RQ1", "SHOULD", "P2", "Team recordings present with consent flag and source=team_recording"),
    ("REQ-030", "Sample and curate IndicSynth as bulk fake-audio source", "DATA", "Proposal p.5–6 §7.1 / Slide 12", "RQ2", "MUST", "P2", "IndicSynth subset listed in fake-audio manifest"),
    ("REQ-031", "Generate targeted fraud-pattern fakes with Indic Parler-TTS", "DATA", "Proposal p.6 §7.1 / Slide 12", "RQ2", "SHOULD", "P2", "Parler-TTS clips tagged attack_type=tts_fraud_pattern"),
    ("REQ-032", "Generate targeted fraud-pattern voice clones with Coqui XTTS-v2", "DATA", "Proposal p.6 §7.1 / Slide 12", "RQ2", "SHOULD", "P2", "XTTS clips tagged attack_type=voice_clone_fraud_pattern"),
    ("REQ-033", "Model self-generated clips on family-in-trouble / digital-arrest fraud patterns (short, urgent, brief reference)", "DATA", "Proposal p.6 §7.1", "RQ2", "SHOULD", "P2", "Generation config documents pattern prompts and max duration"),
    ("REQ-034", "Target roughly 50–100 curated hours per language", "DATA", "Proposal p.6 §7.1 / Slide 11", "RQ2", "SHOULD", "P2", "Per-language hour totals logged in dataset report (OQ if exact split unspecified)"),
    ("REQ-035", "Produce every curated clip in both clean and Opus-compressed form via ffmpeg", "DATA", "Proposal p.6 §7.1 / Slide 12", "RQ1", "MUST", "P3", "Paired paths exist for 100% of curated clips"),
    # --- Model ---
    ("REQ-036", "Use pretrained Wav2Vec2-XLS-R as frozen front-end", "FUNC", "Proposal p.6 §7.2 / Slide 14", "RQ2", "MUST", "P4", "Training code freezes XLS-R parameters (requires_grad=False)"),
    ("REQ-037", "Run XLS-R forward pass once and cache embeddings", "FUNC", "Proposal p.6 §7.2 / Slide 11", "INFRA", "MUST", "P4", "Embedding cache hit avoids recompute; cache keyed by clip id + config hash"),
    ("REQ-038", "Train only the AASIST head on cached embeddings", "FUNC", "Proposal p.6 §7.2 / Slide 14", "RQ2", "MUST", "P5", "Trainable parameter count limited to AASIST head"),
    ("REQ-039", "Adapt AASIST from official clovaai/aasist repository", "FUNC", "Proposal p.6 §7.2 / Slide 12", "RQ2", "MUST", "P5", "Dependency or vendored attribution to clovaai/aasist documented"),
    ("REQ-040", "AASIST head sized ~1–5M parameters", "NFR", "Proposal p.3 §5.1 / Slide 7", "RQ2", "SHOULD", "P5", "Logged parameter count in [1e6, 5e6] or OQ deviation noted"),
    ("REQ-041", "Use HF facebook/wav2vec2-xls-r-300m as XLS-R checkpoint", "DATA", "Proposal p.11 §10", "RQ2", "MUST", "P4", "Config default model_id equals that HF path"),
    # --- Baselines ---
    ("REQ-042", "Implement LFCC + GMM classic non-deep baseline", "RESEARCH", "Proposal p.6 §7.3 / Slide 14", "RQ2", "MUST", "P5", "LFCC-GMM EER reported on same test splits"),
    ("REQ-043", "Implement RawNet2 baseline from AASIST repo", "RESEARCH", "Proposal p.6 §7.3 / Slide 14", "RQ2", "MUST", "P5", "RawNet2 EER reported on same test splits"),
    ("REQ-044", "Train English-only XLS-R + AASIST on ASVspoof as RQ2 control", "RESEARCH", "Proposal p.6 §7.3 / Slide 14", "RQ2", "MUST", "P5", "English-only model evaluated on Indic clean+compressed tests"),
    ("REQ-045", "Cite SATYAM/IndicSynth/Pascu published figures as contextual references without re-implementing them", "RESEARCH", "Proposal p.6 §7.3", "INFRA", "SHOULD", "P6", "Related-work tables cite published numbers with sources; no SATYAM reimplementation code"),
    # --- Detection metrics ---
    ("REQ-046", "Report Equal Error Rate (EER) as headline detection metric", "RESEARCH", "Proposal p.6 §7.4 / Slide 14", "RQ1", "MUST", "P6", "EER present in every primary results table"),
    ("REQ-047", "Report min-DCF alongside EER", "RESEARCH", "Proposal p.6 §7.4 / Slide 14", "RQ2", "MUST", "P6", "min-DCF column present alongside EER"),
    ("REQ-048", "Produce cross-lingual matrix (train 2 languages, test unseen 3rd)", "RESEARCH", "Proposal p.6 §7.4 / Slide 14", "RQ3", "MUST", "P6", "3× hold-out cells populated with EER/accuracy"),
    ("REQ-049", "Produce cross-condition matrix (train clean→test compressed and vice versa)", "RESEARCH", "Proposal p.6 §7.4 / Slide 14", "RQ1", "MUST", "P6", "Both transfer directions reported"),
    ("REQ-050", "Report Accuracy, Precision, Recall, F1 in evaluation suite", "RESEARCH", "Proposal p.6 §7.4; Phase-0 prompt eval list", "RQ2", "SHOULD", "P6", "Classification report generated per language/condition"),
    ("REQ-051", "Report ROC curves and AUC", "RESEARCH", "Phase-0 prompt eval list / Proposal §7.4 intent", "RQ2", "SHOULD", "P6", "ROC/AUC artefacts saved per primary experiment"),
    ("REQ-052", "Report confusion matrices (including language-wise)", "RESEARCH", "Proposal p.7 §7.7 / Slide 14", "RQ3", "MUST", "P6", "Language-wise confusion matrix figure in eval report"),
    ("REQ-053", "Report per-language, per-attack, and per-compression breakdowns", "RESEARCH", "Proposal p.7–8 §7.8", "RQ1", "MUST", "P6", "Error-analysis section contains all three slices"),
    # --- Calibration ---
    ("REQ-054", "Fit temperature scaling on held-out validation split", "FUNC", "Proposal p.6 §7.5 / Slide 14", "RQ4", "MUST", "P7", "Temperature scalar fitted with val split; train split unused for T"),
    ("REQ-055", "Fit temperature scaling per language", "FUNC", "Proposal p.6 §7.5 / Slide 14", "RQ4", "MUST", "P7", "Separate T parameter stored for HI, MR, TA"),
    ("REQ-056", "Fit temperature scaling per compression condition", "FUNC", "Proposal p.6 §7.5 / Slide 14", "RQ4", "MUST", "P7", "Separate T for clean and compressed (at least)"),
    ("REQ-057", "Compute Expected Calibration Error (ECE)", "RESEARCH", "Proposal p.6 §7.5 / Slide 6", "RQ4", "MUST", "P7", "ECE logged pre and post calibration"),
    ("REQ-058", "Produce reliability diagrams", "RESEARCH", "Proposal p.6 §7.5", "RQ4", "MUST", "P7", "Reliability diagram PNGs saved per language×condition"),
    ("REQ-059", "Compute Brier score alongside ECE", "RESEARCH", "Proposal p.6 §7.5 / Slide 6", "RQ4", "MUST", "P7", "Brier reported per language and condition, not aggregate-only"),
    ("REQ-060", "Compute entropy-based uncertainty", "RESEARCH", "Proposal p.6 §7.5", "RQ4", "MUST", "P7", "Per-prediction entropy available in prediction records"),
    ("REQ-061", "Produce reliability-threshold accuracy/coverage curve (Pascu et al. style)", "RESEARCH", "Proposal p.6–7 §7.5", "RQ4", "MUST", "P7", "Coverage curve figure and table exported"),
    ("REQ-062", "Surface reliability flag in demo when compression degrades trustworthiness", "UI", "Proposal p.2 §1 / Slide 3", "RQ4", "MUST", "P9", "UI shows reliability badge/flag with compression-aware state"),
    ("REQ-063", "Post-calibration ECE lower than pre-calibration in majority of language/condition cells", "RESEARCH", "Proposal p.15 §17", "RQ4", "MUST", "P7", "Success criterion boolean check passes on held-out test"),
    # --- Human study ---
    ("REQ-064", "Recruit ~20–30 volunteer listeners (classmates/peers)", "RESEARCH", "Proposal p.7 §7.6 / Slide 6", "RQ5", "SHOULD", "P9", "Participant count logged; floor ≥12–15 still valid per §17"),
    ("REQ-065", "Prefer Hindi/Marathi-fluent participants where possible", "RESEARCH", "Proposal p.7 §7.6", "RQ5", "SHOULD", "P9", "Language-fluency self-report field collected"),
    ("REQ-066", "Use fixed balanced stimulus subset spanning all 3 languages × clean/compressed", "RESEARCH", "Proposal p.7 §7.6", "RQ5", "MUST", "P9", "Stimulus manifest IDs match model eval subset"),
    ("REQ-067", "Forced-choice real vs AI-generated task per clip", "RESEARCH", "Proposal p.7 §7.6 / Slide 6", "RQ5", "MUST", "P9", "Each response stores binary choice"),
    ("REQ-068", "Collect self-reported confidence rating on 1–5 scale", "RESEARCH", "Proposal p.7 §7.6 / Slide 6", "RQ5", "MUST", "P9", "Confidence ∈ {1,2,3,4,5} validated"),
    ("REQ-069", "Deliver study via Google Forms or minimal static HTML", "OPS", "Proposal p.7 §7.6 / Slide 11", "RQ5", "SHOULD", "P9", "Hosting URL documented; no paid survey tooling required"),
    ("REQ-070", "Analyse human vs model accuracy per language × condition cell", "RESEARCH", "Proposal p.7 §7.6", "RQ5", "MUST", "P9", "Comparison table exists for each cell"),
    ("REQ-071", "Compare human vs model calibration curves", "RESEARCH", "Proposal p.7 §7.6", "RQ5", "MUST", "P9", "Human ECE-style plot exported"),
    ("REQ-072", "Include short qualitative question (what tipped you off)", "RESEARCH", "Proposal p.7 §7.6", "RQ5", "SHOULD", "P9", "Free-text field present in export"),
    ("REQ-073", "Collect only language-fluency self-report and answers; voluntary anonymous participation", "OPS", "Proposal p.7 §7.6; p.16 §20", "RQ5", "MUST", "P9", "No PII fields in schema; consent disclosure shown before start"),
    ("REQ-074", "Do not clone real public figures/celebrities without consent; use team/volunteer voices only", "OPS", "Proposal p.16 §20", "INFRA", "MUST", "P2", "Generation consent log exists for reference speakers"),
    # --- Explainability ---
    ("REQ-075", "Grad-CAM temporal attention heatmap for audio/spectrogram input", "FUNC", "Proposal p.7 §7.7 / Slide 13", "RQ1", "MUST", "P8", "Explain API returns Grad-CAM overlay artefact"),
    ("REQ-076", "Frequency-band importance via band-masking ablation", "FUNC", "Proposal p.7 §7.7 / Slide 13", "RQ1", "MUST", "P8", "Score-delta table per frequency band exported"),
    ("REQ-077", "Side-by-side clean vs compressed spectrogram comparison", "UI", "Proposal p.7 §7.7", "RQ1", "MUST", "P8", "Spectrogram pair view available in explainability panel"),
    ("REQ-078", "Compression-artifact visualisation (spectral energy cutoff, transient smearing)", "FUNC", "Proposal p.7 §7.7 / Slide 13", "RQ1", "MUST", "P8", "Artifact plot generated for representative clips"),
    ("REQ-079", "Present language-wise confusion matrix as explainability/failure-mode view", "RESEARCH", "Proposal p.7 §7.7", "RQ3", "MUST", "P6", "Confusion matrix included in dashboard or research metrics page"),
    # --- Error analysis ---
    ("REQ-080", "Per-language breakdown of headline metrics with hypothesis vs data hours", "RESEARCH", "Proposal p.7 §7.8", "RQ3", "MUST", "P6", "Error-analysis doc links hardest language to inventory hours"),
    ("REQ-081", "Per-condition breakdown: compression impact by attack type (TTS vs voice-cloning)", "RESEARCH", "Proposal p.7 §7.8", "RQ1", "MUST", "P6", "Attack-type × condition table exists"),
    ("REQ-082", "Per-frequency-band breakdown of lost cues under compression", "RESEARCH", "Proposal p.8 §7.8", "RQ1", "MUST", "P8", "Band-importance results referenced in error analysis"),
    ("REQ-083", "Calibration breakdown: locate overconfidence by language/condition", "RESEARCH", "Proposal p.8 §7.8", "RQ4", "MUST", "P7", "Overconfidence concentration analysis in calibration report"),
    # --- System implementation / UI ---
    ("REQ-084", "React frontend with clip upload", "UI", "Proposal p.8 §7.9 / Slide 13", "INFRA", "MUST", "P9", "Upload page accepts audio file and shows progress"),
    ("REQ-085", "React frontend with microphone recording", "UI", "Proposal p.8 §7.9", "INFRA", "MUST", "P9", "Record control captures audio via MediaRecorder"),
    ("REQ-086", "Waveform display for uploaded/recorded clip", "UI", "Proposal p.8 §7.9; p.14 Fig.2", "INFRA", "MUST", "P9", "Waveform component renders after load"),
    ("REQ-087", "Calibrated confidence display", "UI", "Proposal p.8 §7.9; p.14 Fig.2", "RQ4", "MUST", "P9", "Confidence percentage shown after inference"),
    ("REQ-088", "Reliability badge UI", "UI", "Proposal p.8 §7.9; p.14 Fig.2", "RQ4", "MUST", "P9", "Reliability state (e.g. MODERATE) visible"),
    ("REQ-089", "Explainability panel in dashboard", "UI", "Proposal p.8 §7.9; p.14 Fig.2", "RQ1", "MUST", "P9", "Panel lists Grad-CAM / frequency / artifact views"),
    ("REQ-090", "Language indicator in UI (Hindi/Marathi/Tamil)", "UI", "Proposal p.14 Fig.2", "RQ2", "MUST", "P9", "Language pill or selector shows active language"),
    ("REQ-091", "Verdict display (Real/Fake)", "UI", "Proposal p.14 Fig.2", "RQ2", "MUST", "P9", "Verdict text rendered from API response"),
    ("REQ-092", "Three-tier backend: Node.js request layer + FastAPI inference service", "FUNC", "Proposal p.8 §7.9; p.9", "INFRA", "MUST", "P9", "Architecture docs and deployment show separated request and inference tiers"),
    ("REQ-093", "Model can be retrained/swapped without changing the frontend", "NFR", "Proposal p.8 §7.9", "INFRA", "MUST", "P5", "Frontend depends only on versioned OpenAPI contract"),
    ("REQ-094", "Multi-stage audio decoding with primary library and fallback decoder", "FUNC", "Proposal p.8 §7.9", "INFRA", "MUST", "P3", "Unsupported format attempts fallback before typed error"),
    ("REQ-095", "Optional acoustic-feature ensemble ablation: jitter, shimmer, spectral entropy, temporal consistency", "RESEARCH", "Proposal p.8 §7.9; p.13 §12", "RQ2", "SHOULD", "P5", "Ablation toggle/config; results table with/without auxiliary features"),
    ("REQ-096", "Real-time streaming demo via MediaRecorder + sliding-window inference", "FUNC", "Proposal p.8 §7.9", "INFRA", "SHOULD", "P9", "Live page streams windows and updates verdict"),
    ("REQ-097", "Inference latency under roughly 2 seconds per clip on CPU", "NFR", "Proposal p.10 / Slide 13", "INFRA", "SHOULD", "P9", "p95 latency ≤ 2.0s measured in demo health/bench script"),
    # --- Pipeline stages (Fig.1) ---
    ("REQ-098", "Preprocessing: resample, silence trim, label, train/val/test split", "FUNC", "Proposal p.9 Fig.1 description", "INFRA", "MUST", "P3", "Preprocessor emits split-tagged clips; unit tests cover resample/trim"),
    ("REQ-099", "Speaker-disjoint versioned split manifests (never on-the-fly only)", "DATA", "vaaniq-core.mdc / Proposal §7.1 intent", "INFRA", "MUST", "P2", "Split JSON/CSV committed or versioned with checksums"),
    ("REQ-100", "Pipeline stages independently testable/modular", "NFR", "Proposal p.8 §8 / Slide 13", "INFRA", "MUST", "P1", "Each stage has ABC + unit tests"),
    # --- Datasets inventory exact paths ---
    ("REQ-101", "Access Kathbath via HF ai4bharat/Kathbath (CC0, gated)", "DATA", "Proposal p.11 §10", "INFRA", "MUST", "P2", "Dataset config stores exact HF path and licence note"),
    ("REQ-102", "Access IndicVoices-R via HF ai4bharat/indicvoices_r (research licence, gated)", "DATA", "Proposal p.11 §10", "INFRA", "MUST", "P2", "Config stores exact HF path"),
    ("REQ-103", "Access Common Voice v17 via mozilla-foundation/common_voice_17_0 or ungated mirror", "DATA", "Proposal p.11 §10", "INFRA", "MUST", "P2", "Config documents official and mirror paths"),
    ("REQ-104", "Access IndicSynth via HF vdivyasharma/IndicSynth (CC BY-NC 4.0)", "DATA", "Proposal p.11 §10", "INFRA", "MUST", "P2", "Non-commercial licence noted in DATASETS.md"),
    ("REQ-105", "Access Indic Parler-TTS via HF ai4bharat/indic-parler-tts (Apache-2.0, gated)", "DATA", "Proposal p.11 §10", "INFRA", "SHOULD", "P2", "Generation script documents gated access step"),
    ("REQ-106", "Access Coqui XTTS-v2 via HF coqui/XTTS-v2 / coqui-tts install", "DATA", "Proposal p.11 §10", "INFRA", "SHOULD", "P2", "Install instructions in DATASETS.md"),
    ("REQ-107", "Use AASIST code from GitHub clovaai/aasist including EER/t-DCF helpers", "FUNC", "Proposal p.11 §10", "RQ2", "MUST", "P5", "Metric module traces to AASIST repo helpers or equivalent tests"),
    # --- Compute / ops ---
    ("REQ-108", "Plan embedding extraction on Colab free T4; cache to Drive", "OPS", "Proposal p.11 §11 / Slide 11", "INFRA", "SHOULD", "P4", "Notebook/script documents Colab workflow"),
    ("REQ-109", "Train AASIST head on Colab free tier or laptop CPU", "OPS", "Proposal p.11 §11 / Slide 11", "INFRA", "SHOULD", "P5", "Training entrypoint runs without requiring paid GPU"),
    ("REQ-110", "Generate fraud-scenario supplement on Kaggle (≤30 GPU-hrs/week)", "OPS", "Proposal p.11 §11 / Slide 11", "INFRA", "COULD", "P2", "Kaggle notebook path documented"),
    ("REQ-111", "Store dataset (~50–80 GB) on Kaggle Datasets + pooled Google Drive", "OPS", "Proposal p.11 §11", "INFRA", "SHOULD", "P2", "Storage README lists locations; data/ gitignored"),
    ("REQ-112", "Host demo on Hugging Face Spaces (CPU) or local machine", "OPS", "Proposal p.11 §11 / Slide 11", "INFRA", "SHOULD", "P9", "Deployment guide covers HF Spaces or docker compose local"),
    ("REQ-113", "Compression pipeline uses ffmpeg for Opus re-encode, resample, and noise", "FUNC", "Proposal p.11 §11 / Slide 13", "RQ1", "MUST", "P3", "Compressor adapter shells out to ffmpeg with config-driven args"),
    # --- Expected results / targets ---
    ("REQ-114", "Target single-digit % EER on clean in-domain audio", "RESEARCH", "Proposal p.10 §9 / Slide 15", "RQ2", "SHOULD", "P6", "Clean EER logged; miss explained via §7.8 if outside range"),
    ("REQ-115", "Compressed EER measurably worse than clean but not collapsed", "RESEARCH", "Proposal p.10 §9 / Slide 15", "RQ1", "SHOULD", "P6", "Documented degradation delta; collapse flagged as risk"),
    ("REQ-116", "Unseen-language EER meaningfully better than ~45% SVDF-20 narrow-language reference", "RESEARCH", "Proposal p.10 §9 / Slide 15", "RQ3", "SHOULD", "P6", "Zero-shot EER compared numerically to 45% reference"),
    ("REQ-117", "Model accuracy vs human exceeds ~71–73% human range; calibrated confidence is headline", "RESEARCH", "Proposal p.10 §9 / Slide 15", "RQ5", "SHOULD", "P9", "Comparison table highlights confidence calibration, not only accuracy"),
    # --- Novelty / scope ---
    ("REQ-118", "Deliver combined Indic + Opus + calibration + human baseline benchmark (combined gap §5.7)", "RESEARCH", "Proposal p.5 §5.7 / Slide 9", "MULTI", "MUST", "P9", "Final report has sections answering RQ1–RQ5 with open artefacts"),
    ("REQ-119", "In scope: 3 languages, detection, calibration, human baseline, explainability, demo, open datasets", "INFRA", "Proposal p.15 §18 / Slide 10", "INFRA", "MUST", "P1", "Scope section in README matches; no out-of-scope modules required for success"),
    ("REQ-120", "Out of scope: WhatsApp plugin, call-centre/LE deployment, production-scale infra, languages beyond three, large demographic human study", "INFRA", "Proposal p.14 §14 / Slide 10", "INFRA", "MUST", "P1", "Roadmap marks these FUTURE; no Phase 1–9 tasks implement them as deliverables"),
    # --- Success criteria ---
    ("REQ-121", "Success: complete cross-lingual matrix including zero-shot cells", "RESEARCH", "Proposal p.15 §17", "RQ3", "MUST", "P6", "All matrix cells filled (honest underperformance allowed)"),
    ("REQ-122", "Success: clean and Opus evaluation for every language and every baseline", "RESEARCH", "Proposal p.15 §17", "RQ1", "MUST", "P6", "Baseline×language×condition coverage checklist complete"),
    ("REQ-123", "Success: human study ≥12–15 responses analysed on identical stimuli", "RESEARCH", "Proposal p.15 §17", "RQ5", "MUST", "P9", "Response count ≥12 with analysis notebook/report"),
    ("REQ-124", "Success: end-to-end demo without manual intervention", "UI", "Proposal p.15 §17 / Slide 6", "INFRA", "MUST", "P9", "Automated smoke test: upload → confidence + flag + explain view"),
    # --- Team / ethics / publication ---
    ("REQ-125", "Team roles: Model&Calibration (Gaurav), Evaluation&Human-Study (Eshaan), Data (Aarav), Systems&Explainability&Docs (Prajwal)", "OPS", "Proposal p.13 §13", "INFRA", "SHOULD", "P1", "CONTRIBUTING/roles doc lists primary ownership"),
    ("REQ-126", "Use datasets within stated licence terms", "OPS", "Proposal p.16 §20", "INFRA", "MUST", "P2", "Licence matrix in DATASETS.md; CI fails if commercial-only misuse flagged"),
    ("REQ-127", "Release for defensive research purposes only; state in publication", "OPS", "Proposal p.16 §20", "INFRA", "MUST", "P9", "README ethics statement present"),
    ("REQ-128", "Target Scopus regional/national conference (ICCCNT/ICACCS/INDICON) or workshop; stretch arXiv", "OPS", "Proposal p.17 §21 / Slide 6", "INFRA", "SHOULD", "P9", "Paper draft structured on RQ1–RQ5 exists"),
    ("REQ-129", "Track literature risk: SATYAM/IndicSynth/Pascu may narrow novelty", "OPS", "Proposal p.16 §19", "INFRA", "SHOULD", "P6", "Related-work refresh log before paper lock"),
    ("REQ-130", "Confirm gated dataset config/split names against each README on first load", "OPS", "Proposal p.16 §19", "INFRA", "MUST", "P2", "Loader fails fast listing valid configs"),
    # --- Metadata schema fields (prompt Step 2.6 → requirements) ---
    ("REQ-131", "Per-clip metadata includes speaker id (nullable for some sources)", "DATA", "Proposal p.5 §7.1; Phase-0 schema list", "INFRA", "MUST", "P2", "Pydantic ClipMetadata.speaker_id Optional[str]"),
    ("REQ-132", "Per-clip metadata includes language ∈ {hi, mr, ta}", "DATA", "Proposal p.3 §3; p.14 Fig.2", "INFRA", "MUST", "P2", "Language enum rejects other codes including te"),
    ("REQ-133", "Per-clip metadata includes source, label ∈ {real, fake}, compression status, sample rate, duration, split, attack type, generation model, dataset source", "DATA", "Phase-0 prompt §2.6 / Proposal §7.1", "INFRA", "MUST", "P2", "Schema validation unit tests cover required fields"),
    # --- Additional UI inventory from prompt / §15 ---
    ("REQ-134", "Dashboard pages cover landing, upload/inference, live, history, research metrics, experiments, calibration, explainability, admin, docs", "UI", "Phase-0 prompt UI inventory / Proposal §7.9–§15", "INFRA", "SHOULD", "P9", "Router lists all pages; stubs acceptable until implemented"),
    ("REQ-135", "Upload endpoints validate MIME type, magic bytes, duration, and file size before processing", "NFR", "vaaniq-core.mdc / Proposal §7.9 decode intent", "INFRA", "MUST", "P9", "Invalid uploads return typed 4xx problem+json"),
    ("REQ-136", "CORS origins loaded from config; no wildcard in non-dev profiles", "NFR", "vaaniq-core.mdc", "INFRA", "MUST", "P1", "Prod config test asserts origins ≠ ['*']"),
    ("REQ-137", "Experiment runs write reproducibility manifest (git SHA, dirty flag, config, seed, versions, hardware, checksums)", "OPS", "vaaniq-core.mdc / Proposal open-release intent", "INFRA", "MUST", "P5", "Manifest JSON written beside each run"),
    ("REQ-138", "Deterministic seeding via --seed for random, numpy, torch, cuda", "OPS", "vaaniq-core.mdc", "INFRA", "MUST", "P5", "Trainer accepts --seed; unit test checks seed plumbing"),
    ("REQ-139", "No Telugu (te) as a project language in code, config, or docs", "INFRA", "Proposal p.14 Fig.2 (Tamil); vaaniq-core.mdc", "INFRA", "MUST", "P1", "grep -rni telugu|'te' project language contexts returns empty; Language enum len==3"),
    ("REQ-140", "Confidence histograms and coverage curves available in calibration report UI", "UI", "Phase-0 prompt §10 / Proposal §7.5", "RQ4", "SHOULD", "P9", "Calibration page renders histogram + coverage curve"),
]

COVERAGE_PROPOSAL = {
    1: ("Title page", ["REQ-001"]),
    2: ("Executive summary + motivation §2.1", ["REQ-006", "REQ-062", "REQ-118"]),
    3: ("§2.2 gaps, §3 problem, §4 RQs, §5.1", ["REQ-002", "REQ-003", "REQ-004", "REQ-005", "REQ-007", "REQ-008", "REQ-009", "REQ-010", "REQ-011", "REQ-012", "REQ-013", "REQ-014", "REQ-015", "REQ-016", "REQ-040"]),
    4: ("Literature §5.2–5.6 start", ["REQ-045", "REQ-116"]),
    5: ("§5.6–5.7, §6 objectives, §7.1 start", ["REQ-017", "REQ-018", "REQ-019", "REQ-020", "REQ-021", "REQ-022", "REQ-023", "REQ-024", "REQ-025", "REQ-026", "REQ-027", "REQ-028", "REQ-029", "REQ-030", "REQ-118"]),
    6: ("§7.1–7.5", ["REQ-031", "REQ-032", "REQ-033", "REQ-034", "REQ-035", "REQ-036", "REQ-037", "REQ-038", "REQ-039", "REQ-042", "REQ-043", "REQ-044", "REQ-046", "REQ-047", "REQ-048", "REQ-049", "REQ-054", "REQ-055", "REQ-056", "REQ-057", "REQ-058", "REQ-059", "REQ-060"]),
    7: ("§7.5–7.8 start", ["REQ-061", "REQ-064", "REQ-065", "REQ-066", "REQ-067", "REQ-068", "REQ-069", "REQ-070", "REQ-071", "REQ-072", "REQ-073", "REQ-075", "REQ-076", "REQ-077", "REQ-078", "REQ-079", "REQ-080", "REQ-081"]),
    8: ("§7.8–7.9, §8", ["REQ-082", "REQ-083", "REQ-084", "REQ-085", "REQ-086", "REQ-087", "REQ-088", "REQ-089", "REQ-092", "REQ-093", "REQ-094", "REQ-095", "REQ-096", "REQ-100"]),
    9: ("Figure 1 + tech table", ["REQ-098", "REQ-092", "REQ-036", "REQ-038", "REQ-113"]),
    10: ("Latency + §9 expected results + §10 intro", ["REQ-097", "REQ-114", "REQ-115", "REQ-116", "REQ-117", "REQ-063"]),
    11: ("§10 inventory + §11 compute", ["REQ-101", "REQ-102", "REQ-103", "REQ-104", "REQ-105", "REQ-106", "REQ-107", "REQ-041", "REQ-108", "REQ-109", "REQ-110", "REQ-111", "REQ-112", "REQ-113"]),
    12: ("§12 novelty Fig.3", ["REQ-118", "REQ-095"]),
    13: ("§12 continued + §13 roles", ["REQ-125"]),
    14: ("§14 out of scope + §15 mockup Fig.2", ["REQ-120", "REQ-090", "REQ-091", "REQ-087", "REQ-088", "REQ-089", "REQ-004", "REQ-139"]),
    15: ("§16–18 deliverables, success, limitations", ["REQ-119", "REQ-121", "REQ-122", "REQ-123", "REQ-124", "REQ-034"]),
    16: ("§19 risks + §20 ethics", ["REQ-074", "REQ-073", "REQ-126", "REQ-127", "REQ-129", "REQ-130"]),
    17: ("§21 publication + §22 references", ["REQ-128"]),
}

COVERAGE_SLIDES = {
    1: ("Title", ["REQ-001"]),
    2: ("Agenda", []),  # structural only
    3: ("Introduction / threat", ["REQ-006", "REQ-062"]),
    4: ("Problem + three gaps", ["REQ-002", "REQ-003", "REQ-004", "REQ-005", "REQ-009", "REQ-010", "REQ-011"]),
    5: ("Aim + RQs", ["REQ-012", "REQ-013", "REQ-014", "REQ-015", "REQ-016"]),
    6: ("Objectives O1–O8", ["REQ-017", "REQ-018", "REQ-019", "REQ-020", "REQ-021", "REQ-022", "REQ-023", "REQ-024"]),
    7: ("Literature themes", ["REQ-040", "REQ-045"]),
    8: ("Closest works vs VaaniQ", ["REQ-118"]),
    9: ("Research gap / novelty", ["REQ-118", "REQ-075"]),
    10: ("Scope in/out", ["REQ-119", "REQ-120"]),
    11: ("Feasibility", ["REQ-034", "REQ-037", "REQ-108", "REQ-112", "REQ-064"]),
    12: ("Dataset inventory", ["REQ-025", "REQ-026", "REQ-027", "REQ-028", "REQ-030", "REQ-031", "REQ-032", "REQ-035"]),
    13: ("Pipeline stack", ["REQ-084", "REQ-092", "REQ-097", "REQ-113"]),
    14: ("Algorithm & evaluation", ["REQ-036", "REQ-038", "REQ-042", "REQ-043", "REQ-044", "REQ-046", "REQ-048", "REQ-049", "REQ-054"]),
    15: ("Expected results", ["REQ-114", "REQ-115", "REQ-116", "REQ-117"]),
    16: ("Timeline", ["REQ-128"]),  # process
    17: ("Conclusion", ["REQ-118"]),
    18: ("References [1–10]", []),  # bibliography
    19: ("References [11–19]", []),  # bibliography
}


def main() -> None:
    assert len(REQS) >= 80, len(REQS)
    lines: list[str] = [
        "# VaaniQ — Requirements Traceability Matrix",
        "",
        "> Phase 0 Step 1. Derived from `docs/source/Capstone_Project_Proposal.md` (authoritative)",
        "> and `docs/source/VaaniQ_Topic_Approval.md` (supplementary).",
        "> On conflict, Proposal wins — see `docs/OPEN_QUESTIONS.md`.",
        "",
        f"**Total requirements:** {len(REQS)}",
        "",
        "| ID | Requirement | Type | Source | RQ | Priority | Phase | Acceptance criterion |",
        "|----|-------------|------|--------|----|----------|-------|----------------------|",
    ]
    for row in REQS:
        rid, text, typ, src, rq, pri, phase, acc = row
        # escape pipes
        text = text.replace("|", "\\|")
        acc = acc.replace("|", "\\|")
        lines.append(f"| {rid} | {text} | {typ} | {src} | {rq} | {pri} | {phase} | {acc} |")

    lines += [
        "",
        "## RQ mapping summary",
        "",
        "| RQ | Requirement IDs (non-exhaustive primary) | Deciding metrics |",
        "|----|------------------------------------------|------------------|",
        "| RQ1 | REQ-005,012,018,035,049,076–078,081,113–115,122 | EER clean vs compressed; cross-condition matrix |",
        "| RQ2 | REQ-002–004,007,013,019,042–044,046–047 | Multilingual vs English-only EER/min-DCF |",
        "| RQ3 | REQ-014,020,048,052,116,121 | Zero-shot cross-lingual matrix EER |",
        "| RQ4 | REQ-006,015,021,054–063,083,087–088 | ECE, Brier, reliability diagrams, coverage curves |",
        "| RQ5 | REQ-008,016,022,064–073,117,123 | Human vs model accuracy + calibration on shared IDs |",
        "| INFRA | REQ-001,092–094,098–100,119–120,131–139 | Scaffold, schema, security, scope gates |",
        "",
        "## Coverage audit — Proposal pages",
        "",
    ]
    for page in range(1, 18):
        note, ids = COVERAGE_PROPOSAL[page]
        if ids:
            lines.append(f"- **p.{page}** ({note}): {', '.join(ids)}")
        else:
            lines.append(f"- **p.{page}** ({note}): _no direct REQ_ — justified as non-normative/layout")

    lines += ["", "## Coverage audit — Topic Approval slides", ""]
    for slide in range(1, 20):
        note, ids = COVERAGE_SLIDES[slide]
        if ids:
            lines.append(f"- **Slide {slide}** ({note}): {', '.join(ids)}")
        else:
            lines.append(
                f"- **Slide {slide}** ({note}): _zero requirements_ — justified "
                f"({'agenda/navigation' if slide == 2 else 'bibliography-only'})"
            )

    lines += [
        "",
        "## Notes",
        "",
        "1. Third language: body text says \"one additional Indian language\"; Fig.2 mockup names "
        "**Tamil**. REQ-004/REQ-132/REQ-139 encode Tamil (`ta`). Logged as OQ-001 if supervisor "
        "overrides.",
        "2. Telugu appears in Parler-TTS tool coverage (Proposal p.11) only — not a project language.",
        "3. Phase column maps to `docs/PROJECT_ROADMAP.md` phases P1–P9.",
        "",
    ]
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {OUT} with {len(REQS)} requirements")


if __name__ == "__main__":
    main()
