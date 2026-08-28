# VaaniQ manuscript (research execution snapshot)

**Status of experimental results: NOT RUN.**
Generated: 2026-08-27T17:59:43.353502+00:00. Git `8f439439a32f6ae9111ffeb5da367f7c7b4eb1d2`.

This draft records methods and questions from the capstone proposal. It does **not**
contain measured EER, min-DCF, ECE, Brier, hours, or human accuracy.

## 1. Abstract

NOT RUN: abstract with numbers will be written after RQ1-RQ5 execute on curated data.

## 2. Introduction

AI voice cloning is used in fraud delivered as compressed WhatsApp-style voice notes.
VaaniQ studies detection of AI-generated speech in Hindi, Marathi, and Tamil, under
WhatsApp-style Opus, with calibrated confidence and a human-listener baseline
(proposal §§1-4). Tamil is the third language. Telugu is not in scope.

## 3. Related Work

Literature (proposal §5): AASIST (Jung et al.); Wav2Vec2-XLS-R (Babu et al.);
Indic-CodecFake/SATYAM; IndicSynth; Pascu et al. on calibrated audio deepfake
detection; Müller et al. on human perception of audio deepfakes. This section
summarises prior work; it is not a VaaniQ result.

## 4. Research Gap

No published combination of (a) Indian-language cloning/TTS fraud audio, (b)
WhatsApp-style Opus as a named condition, (c) detector calibration, and (d) a
human baseline on the same stimuli (proposal §5.7).

## 5. Research Questions

- RQ1: Opus degradation vs clean.
- RQ2: Multilingual vs English-only robustness.
- RQ3: Zero-shot transfer among HI, MR, TA (train-2 / test-1).
- RQ4: Calibration under compression (ECE, Brier, reliability, coverage).
- RQ5: Human vs model on identical clip IDs.

## 6. Dataset and Benchmark Construction

PENDING. Measured research hours: Hindi 0, Marathi 0, Tamil 0.
See `research/reports/DATASET_REPORT.md`.

## 7. Methodology

### 7.1 Dataset

Adapters exist for Kathbath, IndicVoices-R, Common Voice, IndicSynth, generated
audio, and team recordings. Ingest is blocked without an HF token (REQ-130).

### 7.2 Preprocessing

16 kHz mono, peak normalisation, duration bounds (config YAML).

### 7.3 Opus compression

ffmpeg WhatsApp-style simulation (OQ-007). Not byte-identical WhatsApp.

### 7.4 XLS-R

Frozen feature extractor. Must not be fine-tuned.

### 7.5 AASIST

AASIST-style head on cached embeddings in this repository; not claimed as
clovaai graph-attention parity (see `docs/KNOWN_LIMITATIONS.md`).

### 7.6 Baselines

LFCC-GMM, RawNet2, English-only XLS-R+AASIST. Not yet evaluated on curated hours.

### 7.7 Calibration

Temperature scaling on validation only (OQ-032). Not yet fit on real val logits.

### 7.8 Explainability

Grad-CAM proxy, band masking, compression artefacts (OQ-034). Demo artefacts only.

### 7.9 Human baseline

Protocol implemented (anonymous ID, 1-5 confidence, timing). N = 0.

## 8. Experimental Setup

Speaker-disjoint 70/15/15 is the required split (OQ-008). **Not written** for a
research corpus because no audio is on disk. Training on fixtures is forbidden
as an RQ result.

## 9. Results

### 9.1 RQ1

NOT RUN.

### 9.2 RQ2

NOT RUN.

### 9.3 RQ3

NOT RUN.

### 9.4 RQ4

NOT RUN.

### 9.5 RQ5

NOT RUN. Human n = 0.

## 10. Error Analysis

NOT RUN.

## 11. Discussion

WITHHELD until §9 has measured values.

## 12. Limitations

Incorporated from `docs/KNOWN_LIMITATIONS.md` (authoritative). Additional
execution fact: research corpus hours are zero in this environment.

## 13. Ethical Considerations

Gated licences (REQ-130). IndicSynth CC BY-NC may block full audio release (OQ-035).
Human study is anonymous and bounded.

## 14. Conclusion

NOT WRITTEN as a results claim. Software apparatus exists; evidence does not.

## 15. Future Work

See `docs/FUTURE_WORK.md`.

## References

As cited in `docs/source/Capstone_Project_Proposal.md` §5. Do not add unsourced
citations here.
