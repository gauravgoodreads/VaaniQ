# VaaniQ manuscript — approved Round 3 evidence

**Status:** RQ1–RQ4 complete; RQ5 blocked on human data (N=0).  
**Authoritative evidence:** `artifacts/final_results_manifest.json`  
**Approved baseline:** `084bd47ca6ca1b69a7cdbf424e2946f3794c2a95`

## 1. Abstract

VaaniQ studies multilingual audio-deepfake detection under language, codec, and
confidence-calibration shift in Hindi, Marathi, and Tamil. The bounded V1 benchmark
uses Kathbath real speech and IndicSynth fake speech with speaker-disjoint partitions.
On 584 held-out instances, an acoustic-embedding plus AASIST-compatible head achieved
91.61% accuracy and 6.56% EER. A frozen `facebook/wav2vec2-xls-r-300m` front-end with
mean pooling achieved 92.12% accuracy, 6.88% EER, and 0.9828 ROC-AUC. Compression,
leave-one-language-out transfer, and validation-selected calibration were evaluated.
Benchmark V2 remains a partial external-source pilot, and human data collection is
pending (N=0).

## 2. Introduction

AI voice cloning can be used in fraud delivered through compressed messaging audio.
VaaniQ studies detection of AI-generated speech in Hindi, Marathi, and Tamil, under
WhatsApp-style Opus simulation, with calibrated confidence and a human-study framework
(proposal §§1–4). The project evaluates a bounded benchmark rather than claiming
universal fake-voice detection.

## 3. Related Work

Literature (proposal §5): AASIST (Jung et al.); Wav2Vec2-XLS-R (Babu et al.);
Indic-CodecFake/SATYAM; IndicSynth; Pascu et al. on calibrated audio deepfake
detection; Müller et al. on human perception of audio deepfakes. This section
summarises prior work; it is not a VaaniQ result.

## 4. Research Gap

The contribution is the integrated evaluation of Indian-language synthetic speech,
WhatsApp-style Opus simulation, cross-language transfer, detector calibration, and
human-study infrastructure. It does not claim invention of XLS-R or AASIST.

## 5. Research Questions

- **RQ1 COMPLETE:** How does Opus compression affect detection performance?
- **RQ2 COMPLETE:** How does English-only anti-spoofing transfer to Hindi, Marathi,
  and Tamil relative to multilingual training?
- **RQ3 COMPLETE:** How well does the detector generalize to an unseen Indian language?
- **RQ4 COMPLETE:** Does validation-selected post-hoc calibration remain reliable
  under held-out language/condition shift?
- **RQ5 PENDING (N=0):** How does model performance compare with human listeners?

## 6. Dataset and Benchmark Construction

V1 contains 1,800 original source clips: 900 Kathbath real and 900 IndicSynth fake,
expanded to 2,346 train/validation/test instances by paired validation/test Opus twins.
The held-out test has n=584. Speaker-disjoint splitting prevents speaker overlap, but
does not remove the structural source-label association.

V2 is a partial pilot: Kathbath×real 1,177, IndicSynth×fake 1,169, and FLEURS×real 50.
Its 98.48% source-probe accuracy shows that source identity remains highly predictable.

## 7. Methodology

### 7.1 Dataset

The bounded V1 benchmark is the primary measured population. Benchmark V2 is reported
separately and is not presented as resolving source-domain confounding.

### 7.2 Preprocessing

16 kHz mono, peak normalisation, duration bounds (config YAML).

### 7.3 Opus compression

ffmpeg/libopus at 16 kbps provides a WhatsApp-style Opus simulation. It is not audio
transported through the WhatsApp service.

### 7.4 XLS-R

The main path uses frozen `facebook/wav2vec2-xls-r-300m`, last-layer mean pooling,
cached features, and a lightweight trainable anti-spoofing head.

### 7.5 AASIST

The measured head is AASIST-compatible NumPy code; it is not the canonical
clovaai/AASIST graph implementation.

### 7.6 Baselines

LFCC-GMM and a RawNet2-style approximate baseline were evaluated on V1. The latter
must not be called faithful RawNet2; faithful RawNet2 remains pending. An English-only
ASVspoof LA control was evaluated on the same Indic held-out test.

### 7.7 Calibration

Production calibration was selected using validation only. For Baseline V1,
per-language-and-condition scaling had validation ECE 0.0487 versus 0.0513 globally.
Held-out ECE nevertheless changed from 0.0245 to 0.026, a retained negative result.

### 7.8 Explainability

Grad-CAM proxy, band masking, compression artefacts (OQ-034). Demo artefacts only.

### 7.9 Human baseline

Protocol implemented (anonymous ID, 1-5 confidence, timing). N = 0.

## 8. Experimental Setup

The versioned manifest uses deterministic speaker-disjoint train/validation/test
partitions. Label 0 denotes REAL/bonafide, label 1 denotes FAKE/spoof, and higher
`score_fake` means greater probability of FAKE. The decision threshold is 0.5.
EER, ROC-AUC, and normalized min-DCF use the same score direction.

## 9. Results

### 9.1 RQ1 — Compression

For the acoustic baseline, clean accuracy was 93.84% (EER 5.63%, n=292) and
WhatsApp-style Opus simulation accuracy was 89.38% (EER 7.58%, n=292). For frozen
XLS-R, clean accuracy was 91.44% (EER 8.13%) and Opus accuracy was 92.81%
(EER 6.06%). Compression effects were model-dependent.

### 9.2 RQ2 — English-to-Indic Transfer

The English-only control achieved 54.8% accuracy, 76.56% EER, and 0.162 ROC-AUC,
predicting every instance as REAL at threshold 0.5. Negated scores produced 0.838
diagnostic AUC, but official scores were not flipped: the multilingual Baseline V1
validated the global score contract on the same test.

### 9.3 RQ3 — Leave-One-Language-Out

Held-out Hindi reached 78.83% accuracy and 21.83% EER; Marathi reached 93.29% and
7.14%; Tamil reached 93.94% and 6.35%. Transfer was strongly asymmetric.

### 9.4 RQ4 — Calibration

Baseline V1's validation-selected fine-grained calibration slightly worsened held-out
ECE from 0.0245 to 0.026. A standalone test comparison where global scaling looked
better is exploratory and was not used to select production calibration.

### 9.5 RQ5 — Human Study

Human-study protocol ready; participant data collection pending (N=0). No human
accuracy, confidence, calibration, or model-comparison result is claimed.

## 10. External Validity

Benchmark V2 remains PARTIAL. The held-out FLEURS result (n=9, accuracy 55.6%) is
a PILOT retained only as pipeline validation. Generator-disjoint evaluation has
n=0 and remains PENDING.

## 11. Discussion

Frozen XLS-R improved ranking performance while classification performance remained
broadly comparable with Baseline V1. The English-only control failed to transfer,
Hindi zero-shot transfer was substantially weaker, and validation-selected calibration
did not uniformly improve held-out reliability.

## 12. Limitations

Key threats are the V1 source-label confound, bounded corpus size, academic speech
rather than scam traffic, simulated rather than actual WhatsApp transport,
three-language scope, no faithful RawNet2, incomplete V2, source probe 98.48%,
FLEURS n=9, generator-disjoint n=0, RQ5 N=0, calibration-transfer uncertainty,
and unresolved validation/test heterogeneity.

## 13. Ethical Considerations

Dataset licences and IndicSynth non-commercial restrictions are respected. Audio and
model weights are excluded from version control. The human protocol is anonymous,
bounded, and has not yet collected participants.

## 14. Conclusion

VaaniQ establishes a reproducible multilingual framework for studying audio-deepfake
detection under language, codec, and confidence-calibration shift. Strong held-out V1
discrimination coexists with important cross-language, calibration, and source-domain
limitations. The evidence supports multilingual evaluation but does not establish
universal source- or generator-independent detection.

## 15. Future Work

See `docs/FUTURE_WORK.md`.

## References

As cited in `docs/source/Capstone_Project_Proposal.md` §5. Do not add unsourced
citations here.
