# VaaniQ: Cross-Lingual, Compression-Robust Detection and Calibrated Reliability Estimation for AI-Generated Voice in Indian Languages

**Venue target:** IEEE conference / journal short paper (capstone archival draft)  
**Status:** RQ1–RQ4 COMPLETE on the bounded machine-evaluated V1 benchmark  
**Authoritative evidence:** `artifacts/final_results_manifest.json`  
**Frozen commit:** `084bd47ca6ca1b69a7cdbf424e2946f3794c2a95`

**Authors:** Gaurav Phadale, Eshaan Sarkhawas, Aarav Phutane, Prajwal Patil  
**Affiliation:** Mukesh Patel School of Technology Management & Engineering, NMIMS  
**Faculty Guide:** Prof. Rama Bharti Varshney

---

## Abstract

Voice cloning and neural TTS enable scalable audio fraud, yet anti-spoofing evidence remains concentrated in English/Mandarin and rarely couples Indian-language stimuli with messaging-style compression, confidence calibration, and cross-lingual transfer. VaaniQ constructs a bounded speaker-disjoint benchmark for Hindi (hi), Marathi (mr), and Tamil (ta) using Kathbath real speech and IndicSynth synthetic speech, then evaluates detection under clean audio and WhatsApp-style 16 kbps Opus simulation. On 584 held-out instances, an acoustic-embedding AASIST-compatible head achieves 91.61% accuracy and 6.56% EER; frozen `facebook/wav2vec2-xls-r-300m` with mean pooling achieves 92.12% accuracy, 6.88% EER, and 0.9828 ROC-AUC. Compression effects are model-dependent; English-only ASVspoof transfer collapses on Indic test audio; leave-one-language-out transfer is strongly asymmetric (Hindi weakest); validation-selected calibration does not uniformly improve held-out ECE. Benchmark V2 remains a partial external-source pilot. VaaniQ is a reproducible machine-evaluation framework for multilingual audio-deepfake study under language, codec, and calibration shift—not a claim of universal fake-voice detection.

**Index Terms**—audio deepfake detection, Indian languages, Kathbath, IndicSynth, Opus compression, calibration, XLS-R, speaker-disjoint evaluation, cross-lingual transfer

---

## I. Introduction

Neural voice cloning can imitate a speaker from short enrollments and can be delivered as compressed chat audio. Established anti-spoofing campaigns (e.g., ASVspoof) remain dominated by English or Mandarin conditions. Indian-language telephony and messaging fraud therefore sits outside the best-supported evaluation regimes.

VaaniQ addresses a **combined** gap rather than inventing a new backbone: (a) Indic synthetic/real speech under a controlled benchmark, (b) WhatsApp-style Opus simulation, (c) post-hoc confidence calibration under language/condition shift, and (d) leave-one-language-out transfer analysis. Languages in scope are Hindi, Marathi, and Tamil only; Telugu is out of scope.

### Contributions

1. A speaker-disjoint V1 publication corpus (1,800 source clips → 2,346 train/val/test instances with paired Opus twins; held-out **n=584**) with frozen manifests and checksums.
2. Complete empirical answers to RQ1–RQ4 on that benchmark for acoustic and frozen XLS-R pipelines, including negative calibration-transfer and catastrophic English→Indic transfer results retained honestly.
3. An end-to-end research software stack (training, evaluation, calibration, explainability proxies, API, UI) with integrity verification against the frozen Round-3 manifest.

Non-claims: VaaniQ does not claim to be the first Indic detector, the first calibrated detector, or a production fraud system. Source-label confounding on V1 is disclosed.

---

## II. Related Work and Comparative Study

### A. Anti-spoofing and multilingual speech

AASIST integrates spectro-temporal graph attention for logical-access anti-spoofing [1]. RawNet2-style end-to-end and LFCC-GMM pipelines remain standard baselines in ASVspoof-style protocols. XLS-R provides cross-lingual SSL features at scale [2]; frozen SSL front-ends with lightweight trainable heads are practical under limited GPU budgets.

### B. Indian-language and compression-adjacent benchmarks

IndicSUPERB / Kathbath supply large human-labelled Indian-language speech [3],[6]. IndicSynth supplies multilingual synthetic speech for Indian ADD research [4],[7]. Indic-CodecFake / SATYAM (proposal §5.4) targets neural-audio-codec synthesis—a related but different attack surface than lossy messaging transport of cloning/TTS fraud audio—and does not isolate WhatsApp-style Opus with confidence calibration. RADAR-style robustness challenges evaluate codec/noise/reverb across several languages but, per proposal §5.3, do not represent Indian languages. FLEURS supports cross-lingual evaluation [8]. Bengali-only deepfake benchmarks confirm per-language Indic detection remains active but fragmented.

### C. Confidence calibration

Pascu et al. study calibrated SSL-based audio deepfake detection [5] without Indian languages or an isolated WhatsApp-Opus cell. VaaniQ tests whether validation-selected calibration transfers to a held-out multilingual codec-shift benchmark and retains negative calibration results rather than assuming post-hoc scaling always helps.

### D. Positioning table (feature comparison — not a scoreboard of EER across mismatched test sets)

Cross-paper EER comparison is invalid when corpora, generators, and codecs differ. Table below compares **evaluation axes**, not absolute metric superiority.

| Work / axis | Indic langs | WhatsApp-style Opus cell | Calibration (ECE/Brier) | Cross-lingual LOLO | Notes |
|-------------|-------------|--------------------------|-------------------------|--------------------|-------|
| ASVspoof LA + AASIST [1] | No (EN-centric) | No | Rarely primary | N/A | Architecture baseline |
| XLS-R SSL [2] | Pretrain multilingual | N/A | N/A | Representation | Front-end used frozen here |
| Kathbath / IndicSUPERB [3] | Yes | No | No | ASR-oriented | REAL source in V1 |
| IndicSynth [4] | Yes | No | No | Dataset baselines | FAKE source in V1 |
| Pascu et al. [5] | No | Not isolated Opus | Yes | Multi-dataset | Closest calibration prior |
| Indic-CodecFake/SATYAM (lit.) | Yes | Codec synth ≠ Opus transport | No | Cross-Indic codecs | Different attack surface |
| **VaaniQ (this work)** | **hi, mr, ta** | **Yes (16 kbps sim.)** | **Yes (RQ4)** | **Yes (RQ3)** | Combined gap; V1 confound disclosed |

### E. Empirical comparative study on the **same** VaaniQ V1 held-out test (n=584)

All systems below share identical clips, labels, threshold 0.5, and score contract. This is the only fair numeric comparison in this paper.

| Model | Accuracy | EER | ROC-AUC | min-DCF | Role |
|-------|----------|-----|---------|---------|------|
| LFCC-GMM | 54.79% | 23.48% | 0.8195 | 0.4962 | Classical weak baseline |
| RawNet2-style approx. | 54.79% | 43.18% | 0.5845 | 0.9621 | Approximate end-to-end control (**not** faithful RawNet2) |
| Acoustic AASIST-compatible V1 | **91.61%** | **6.56%** | 0.9729 | 0.7841 | Primary acoustic system |
| Frozen XLS-R + head | **92.12%** | 6.88% | **0.9828** | **0.3144** | Primary SSL system |
| English-only ASVspoof control | 54.8% | 76.56% | 0.162 | — | RQ2 transfer failure |

Note: LFCC and RawNet2-style matching 54.79% accuracy at threshold 0.5 is a documented coincidence; EER/ROC-AUC differ materially (`baseline_matrix.identical_accuracy_check`). Faithful RawNet2 remains **PENDING**.

### F. In-domain language cells vs LOLO (comparative view)

| Language | In-domain Baseline V1 acc / EER | LOLO held-out acc / EER |
|----------|----------------------------------|-------------------------|
| Hindi | 90.99% / 7.04% | **78.83% / 21.83%** |
| Marathi | 93.29% / 6.25% | 93.29% / 7.14% |
| Tamil | 90.91% / 7.14% | 93.94% / 6.35% |

Hindi zero-shot collapse is the standout comparative finding for RQ3.

### G. Precise gap claim (proposal §5.7)

VaaniQ does **not** claim to be first at Indic detection or first at calibration. The defensible contribution is the **combination**: Indic cloning/TTS-style fraud audio + WhatsApp-style Opus + calibration audit + cross-lingual transfer under one frozen evaluation protocol.

---

## III. Research Questions

| ID | Question | Status |
|----|----------|--------|
| RQ1 | How does Opus compression affect detection? | **COMPLETE** |
| RQ2 | How does English-only anti-spoofing transfer to hi/mr/ta vs multilingual training? | **COMPLETE** |
| RQ3 | How well does the detector generalize to an unseen Indian language (LOLO)? | **COMPLETE** |
| RQ4 | Does validation-selected post-hoc calibration remain reliable under held-out shift? | **COMPLETE** |

---

## IV. Dataset and Benchmark

### A. Bounded V1 (primary measured population)

- **Sources:** Kathbath REAL (900) + IndicSynth FAKE (900); balanced across hi/mr/ta.
- **Expansion:** paired validation/test 16 kbps libopus twins → 2,346 instances.
- **Held-out test:** n=584.
- **Splits:** speaker-disjoint; manifests versioned with checksums.
- **Structural confound (disclosed):** REAL≈Kathbath and FAKE≈IndicSynth, so source identity correlates with class. Speaker-disjoint splits block speaker leakage but do **not** remove source-domain shortcuts.

### B. Benchmark V2 (partial pilot)

Kathbath×real 1,177; IndicSynth×fake 1,169; FLEURS×real 50. Source-probe accuracy **98.48%** shows source identity remains highly predictable. Generator-disjoint evaluation: **n=0 (PENDING)**. Held-out FLEURS independent-real pilot: **n=9**, accuracy 55.6% retained only as pipeline validation—not a statistical claim.

### C. Score contract

Label 0 = REAL, label 1 = FAKE; higher `score_fake` = more fake; decision threshold **0.5**. EER, ROC-AUC, and normalized min-DCF share this orientation (`P_target=0.05`, `C_miss=C_fa=1`).

---

## V. Methodology

### A. Preprocessing

16 kHz mono; peak normalisation; duration bounds from config YAML.

### B. Compression (RQ1 condition)

ffmpeg/libopus at **16 kbps** as a WhatsApp-**style** Opus simulation (RFC 6716 [10]). Not actual WhatsApp transport.

### C. Acoustic Baseline V1

Deterministic 1024-D acoustic embedding + AASIST-**compatible** NumPy head (not canonical clovaai/AASIST graphs).

### D. Frozen XLS-R main

Frozen `facebook/wav2vec2-xls-r-300m`, last-layer mean pooling, cached features, lightweight trainable head. Backbone not updated.

### E. Baselines and controls

LFCC-GMM (complete weak baseline). RawNet2-**style approximate** baseline (not faithful RawNet2; faithful RawNet2 **PENDING**). English-only ASVspoof LA control [10] on the same Indic held-out test (RQ2).

### F. Calibration (RQ4)

Production strategy selected on **validation only**. Baseline V1 selected fine-grained per-language-and-condition temperature scaling (val ECE 0.0487 vs global 0.0513). Held-out ECE moved **0.0245 → 0.026** (negative transfer retained). XLS-R uses global temperature scaling selected on validation.

### G. Explainability (supporting)

Grad-CAM spectrogram-energy proxy, frequency-band masking, compression-artefact views. Demo/analysis aids—not backpropagation through canonical AASIST.

---

## VI. Experimental Setup

Deterministic speaker-disjoint partitions; seed-controlled training where applicable; frozen checkpoint and prediction SHA-256 recorded in the Round-3 manifest. Integrity gate: `scripts/verify_research_integrity.py`. Metrics consume `artifacts/final_results_manifest.json` only.

---

## VII. Results

### A. Primary held-out performance (n=584)

| System | Accuracy | F1 | EER | ROC-AUC | min-DCF |
|--------|----------|-----|-----|---------|---------|
| Acoustic Baseline V1 | 91.61% | 91.36% | 6.56% | 0.9729 | 0.7841 |
| Frozen XLS-R main | 92.12% | — | 6.88% | 0.9828 | 0.3144 |

Frozen XLS-R improves ranking (AUC/min-DCF) while thresholded accuracy remains comparable.

### B. RQ1 — Compression

| Model | Clean acc / EER | Opus 16 kbps acc / EER |
|-------|-----------------|-------------------------|
| Acoustic | 93.84% / 5.63% (n=292) | 89.38% / 7.58% (n=292) |
| Frozen XLS-R | 91.44% / 8.13% | 92.81% / 6.06% |

Compression effects are **model-dependent**.

### C. RQ2 — English→Indic transfer

English-only control: **54.8%** accuracy, **76.56%** EER, **0.162** ROC-AUC; all predictions REAL at threshold 0.5. Negated scores yield 0.838 diagnostic AUC, but official scores are **not** flipped. Multilingual Baseline V1 validates the global score contract on the same test.

### D. RQ3 — Leave-one-language-out

| Held-out language | Accuracy | EER |
|-------------------|----------|-----|
| Hindi | 78.83% | 21.83% |
| Marathi | 93.29% | 7.14% |
| Tamil | 93.94% | 6.35% |

Transfer is strongly asymmetric; Hindi is the weakest zero-shot cell.

### E. RQ4 — Calibration

Baseline V1 validation-selected fine-grained calibration: held-out ECE **0.0245 → 0.026**. Validation-selected calibration did **not** uniformly improve held-out reliability. Exploratory test-only comparisons are not used for production selection.

### F. External validity (V2)

| Eval | n | Status | Note |
|------|---|--------|------|
| V2 full test | 593 | PARTIAL | Not confound-free |
| FLEURS unseen-real | 9 | PILOT | 55.6%; pipeline only |
| Generator-disjoint | 0 | PENDING | No result |
| V2 source probe | 593 | PARTIAL | 98.48% source identity |

---

## VIII. Discussion

Strong V1 discrimination coexists with structural and transfer limitations. The English control failure supports multilingual training for Indic evaluation. Asymmetric LOLO results caution against treating “Indian languages” as a homogeneous transfer class. Negative calibration transfer warns that validation ECE gains need held-out audits. The V1 source–label association remains the central internal-validity threat: future confound-controlled corpora and generator-disjoint splits are required before claiming source- or generator-independent detection. The contribution is therefore scoped to the reproducible machine-evaluation evidence reported here.

---

## IX. Limitations and Threats to Validity

1. V1 source–label confound (Kathbath≈REAL, IndicSynth≈FAKE).  
2. Bounded corpus size; academic speech ≠ scam telephony.  
3. Simulated Opus ≠ WhatsApp transport.  
4. Three-language scope only.  
5. AASIST-compatible NumPy head ≠ canonical AASIST; faithful RawNet2 pending.  
6. V2 incomplete; source probe 98.48%; FLEURS n=9; generator-disjoint n=0.  
7. Calibration transfer uncertainty; unresolved val/test heterogeneity (e.g., Tamil val vs test).  
8. Explainability is spectrogram-energy aligned proxy.  
9. Research prototype deployment, not production fraud detection.  
10. IndicSynth CC BY-NC may limit public audio redistribution.

---

## X. Ethical Considerations

Dataset licences are respected; audio and weights are excluded from version control. Dual-use risks include surveillance and over-reliance on probabilistic detector outputs; release emphasizes bounded research evaluation and licence constraints.

---

## XI. Reproducibility

Authoritative metrics: `artifacts/final_results_manifest.json` at commit `084bd47…`. Manifests record source, label, speaker, split, duration, checksum, generation model. Documents must consume the frozen manifest. Integrity: `scripts/verify_research_integrity.py`. Paper DOCX regenerated via `scripts/generate_ieee_paper_docx.py` / `scripts/build_ieee_final_package.py`.

---

## XII. Future Work

1. Confound-controlled / generator-disjoint corpora; larger external-source evaluation.  
2. Faithful RawNet2 and canonical AASIST checkpoints.  
3. Real messaging-channel capture studies (beyond Opus simulation).  
4. Broader Indian languages only after hi/mr/ta cells are confound-safer.

---

## XIII. Conclusion

VaaniQ provides a reproducible multilingual framework for audio-deepfake detection under language, codec, and calibration shift on Hindi, Marathi, and Tamil. Acoustic and frozen XLS-R pipelines achieve strong held-out discrimination on the bounded V1 benchmark, while transfer, calibration, and source-domain experiments expose material limits. Evidence supports multilingual machine-evaluation practice; it does **not** establish universal source- or generator-independent detection.

---

## References

[1] J. Jung et al., “AASIST: Audio anti-spoofing using integrated spectro-temporal graph attention networks,” in *Proc. ICASSP*, 2022.  
[2] A. Babu et al., “XLS-R: Self-supervised cross-lingual speech representation learning at scale,” arXiv:2111.09296, 2021.  
[3] T. Javed et al., “IndicSUPERB: A speech processing universal performance benchmark for Indian languages,” arXiv:2208.11761, 2022.  
[4] D. V. Sharma, V. Ekbote, and A. Gupta, “IndicSynth: A large-scale multilingual synthetic speech dataset,” ACL, 2025.  
[5] O. Pascu et al., “Towards calibrated and explainable audio deepfake detection,” in *Proc. Interspeech*, 2024.  
[6] AI4Bharat, Kathbath dataset, Hugging Face: `ai4bharat/Kathbath`.  
[7] D. V. Sharma et al., IndicSynth dataset, Hugging Face: `vdivyasharma/IndicSynth`.  
[8] A. Conneau et al., “FLEURS: Few-shot learning evaluation of universal representations of speech,” arXiv:2205.12446, 2022.  
[9] IETF RFC 6716, Definition of the Opus Audio Codec, 2012.  
[10] ASVspoof 2019 Logical Access evaluation plan; English-only control uses a streaming subset of Bisher/ASVspoof_2019_LA (ODC-By).

Citations follow `docs/source/Capstone_Project_Proposal.md` §5. Do not add unsourced references.
