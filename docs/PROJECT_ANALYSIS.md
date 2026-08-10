# VaaniQ — Project Analysis

> Phase 0 Step 2. Every claim cites REQ IDs from `docs/REQUIREMENTS.md`.
> Sources: Proposal (authoritative), Topic Approval slides (supplementary).

---

## 1. Problem statement & motivation

AI voice cloning is an active fraud vector in India (McAfee 2023; Powai case Apr 2024). Scams arrive as **lossy Opus-compressed** WhatsApp voice notes in Indic languages that major detectors are not trained or tested on (**REQ-005**, **REQ-009–011**).

VaaniQ contributes three linked pieces rather than detection alone (**REQ-118**):

1. **Detection** — cross-lingual, compression-robust benchmark for Indic cloning/TTS fraud audio (**REQ-002–005**, **REQ-017–019**).
2. **Calibrated reliability** — trustworthy confidence + reliability flag when compression undermines the score (**REQ-006**, **REQ-054–063**).
3. **Human baseline** — listeners vs model on identical stimuli/conditions (**REQ-008**, **REQ-064–073**).

---

## 2. Research questions RQ1–RQ5

| RQ | Full statement | Hypothesis | Experiment | Deciding metric | Failure condition |
|----|----------------|------------|------------|-----------------|-------------------|
| **RQ1** | How much does WhatsApp-style Opus compression degrade multilingual deepfake detectors vs clean? (**REQ-012**) | Compressed EER worse than clean but degrades gracefully, not collapse (**REQ-115**) | Train primary model; evaluate clean vs Opus; fill cross-condition matrix both directions (**REQ-049**, **REQ-122**) | ΔEER(clean, compressed); cross-condition EER | Collapse to near-chance without documented mechanism (**REQ-078**, **REQ-082**) |
| **RQ2** | Does multilingual (HI+MR+TA) training beat English-only baseline on Indic + compressed audio? (**REQ-013**) | Multilingual model lower EER than English-only ASVspoof-trained control (**REQ-044**) | Train multilingual XLS-R+AASIST vs English-only; same Indic test sets (**REQ-019**, **REQ-042–044**) | EER, min-DCF side-by-side | Multilingual ≤ English-only with no explanatory error analysis (**REQ-080**) |
| **RQ3** | How well does the model generalise zero-shot to an unseen Indian language? (**REQ-014**) | Unseen-language EER meaningfully better than ~45% SVDF-20 narrow-language reference (**REQ-116**) | Train on 2 languages, test held-out 3rd for each rotation (**REQ-048**, **REQ-121**) | Cross-lingual matrix EER | All zero-shot cells ≈45% with no mitigation narrative |
| **RQ4** | Does compression degrade calibration (confidently wrong vs appropriately uncertain)? (**REQ-015**) | Post-temperature ECE/Brier improve vs raw, especially under compression (**REQ-063**, **REQ-021**) | Fit T per language×condition; ECE, reliability diagrams, Brier, coverage curves (**REQ-054–061**) | ECE↓, Brier↓ in majority of cells (**REQ-063**) | Calibration worsens or only aggregate improves while cells fail (**REQ-059**, **REQ-083**) |
| **RQ5** | How do model detection and confidence compare to human listeners across languages/conditions? (**REQ-016**) | Model accuracy above ~71–73% human range; calibrated confidence is the headline (**REQ-117**) | Shared stimulus subset; forced-choice + 1–5 confidence; human vs model tables (**REQ-066–071**) | Accuracy delta; human vs model calibration curves | <12 responses or non-identical stimuli (**REQ-123**) |

---

## 3. Objectives → RQ / REQ map

| Obj | Maps to | Key REQs |
|-----|---------|----------|
| O1 Dataset | RQ2 | REQ-017, 025–035, 101–106 |
| O2 Compression | RQ1 | REQ-018, 035, 113, 122 |
| O3 Benchmarked model | RQ2 | REQ-019, 036–044, 046–047 |
| O4 Generalisation | RQ3 | REQ-020, 048–049, 121 |
| O5 Calibration | RQ4 | REQ-021, 054–063 |
| O6 Human baseline | RQ5 | REQ-022, 064–073, 123 |
| O7 Demo | RQ4 + INFRA | REQ-023, 084–091, 124 |
| O8 Open release | INFRA | REQ-024, 127–128 |

---

## 4. Scope

### In scope (**REQ-119**)
- Languages: Hindi, Marathi, Tamil (**REQ-002–004**, **REQ-139**)
- Detection, calibration, human baseline on shared stimuli
- Explainability suite + working demo
- Open/verified datasets and pretrained models only

### Explicitly out of scope (**REQ-120**)
- WhatsApp plugin; call-centre / LE production deployment
- Production-scale real-time infrastructure
- Languages beyond the three studied
- Large demographically representative human study

### Deferred / future narrative only (Proposal §14)
- Cybercrime helpline 1930 triage; police forensic productisation — documentation framing only, not deliverables.

---

## 5. Datasets

| Dataset | Licence / access | Languages used | Real/Fake | Approx size (source) | Caveats / OQ |
|---------|------------------|----------------|-----------|----------------------|--------------|
| Kathbath | CC0, gated HF `ai4bharat/Kathbath` (**REQ-101**) | subset of 12 Indic | Real | 1,684 hrs / 1,218 speakers total | Hours **per language after curation** not fixed → **OQ-002** |
| IndicVoices-R | Research licence, gated `ai4bharat/indicvoices_r` (**REQ-102**) | subset of 22 | Real | 1,704 hrs / 10,496 speakers | Same → **OQ-002** |
| Common Voice v17 | CC0; `mozilla-foundation/common_voice_17_0` or mirror (**REQ-103**) | hi, mr configs | Real | not stated per-language hours | Tamil CV config not claimed → **OQ-003** |
| IndicSynth | CC BY-NC 4.0 `vdivyasharma/IndicSynth` (**REQ-104**) | 12 Indic incl. HI/MR | Fake | 4,000 hrs total; sample subset | Tamil coverage in IndicSynth → **OQ-004** |
| Team recordings | consent-based (**REQ-029**, **REQ-074**) | HI/MR/(TA) | Real | not specified | Volume → **OQ-005** |
| Parler-TTS / XTTS-v2 | Apache-2.0 / Coqui research (**REQ-105–106**) | generation tools | Fake (supplement) | not specified | Bitrate/prompt templates → **OQ-006** |

Target curated volume: **~50–100 hours per language**, clean+compressed (**REQ-034**, **REQ-035**).

---

## 6. Per-clip metadata schema (sketch)

```text
ClipMetadata:
  clip_id: str                          # required, unique
  speaker_id: str | null                # REQ-131
  language: "hi" | "mr" | "ta"          # REQ-132; never "te"
  source: DatasetSource                 # kathbath | indicvoices_r | common_voice | indicsynth | team_recording | parler_tts | xtts_v2
  label: "real" | "fake"                # REQ-133
  compression_status: "clean" | "opus_whatsapp_sim"
  sample_rate_hz: int                   # required after preprocess
  duration_sec: float                   # required
  split: "train" | "val" | "test"       # speaker-disjoint manifests REQ-099
  attack_type: AttackType | null        # null for real; tts | voice_clone | tts_fraud_pattern | voice_clone_fraud_pattern
  generation_model: str | null          # e.g. indicsynth | indic-parler-tts | xtts-v2
  dataset_source: str                   # exact HF/Git path or local URI
  pair_id: str | null                   # links clean↔compressed twins REQ-035
  consent_ref: str | null               # required if team_recording / cloned voice
```

Nullability and enums enforced by Pydantic v2 at I/O boundaries (**REQ-133**). Exact Opus bitrate/container → **OQ-007**.

---

## 7. Model architecture

```text
audio → preprocess → [optional Opus twin] → frozen Wav2Vec2-XLS-R (HF 300m)
      → cached embedding → AASIST head (~1–5M) → logits
      → temperature scaling (per language × condition) → calibrated probs
      → explainability artefacts → API/UI
```

| Item | Stated | Not stated (OQ) |
|------|--------|-----------------|
| Front-end | Frozen XLS-R; cache embeddings (**REQ-036–037**, **REQ-041**) | Layer tapped for embedding; pooling |
| Back-end | AASIST from `clovaai/aasist` (**REQ-038–039**) | LR, batch size, epochs, loss, input duration |
| Params | ~1–5M head (**REQ-040**) | Exact variant config |
| Aux | Optional jitter/shimmer/spectral entropy/temporal consistency ablation (**REQ-095**) | Fusion method |

---

## 8. Baselines — what each isolates

| Baseline | Isolates | REQs |
|----------|----------|------|
| LFCC + GMM | Non-deep classical ceiling | REQ-042 |
| RawNet2 | Deep end-to-end without XLS-R | REQ-043 |
| English-only XLS-R+AASIST (ASVspoof) | Language-transfer failure (RQ2 control) | REQ-044 |
| Main multilingual XLS-R+AASIST | Full system under test | REQ-019, 036–038 |

SATYAM / IndicSynth / Pascu numbers = **cited context only**, not reproduced (**REQ-045**).

---

## 9. Evaluation protocol

**Metrics:** EER, min-DCF, Accuracy, Precision, Recall, F1, ROC/AUC, confusion matrices, cross-lingual matrix, cross-condition matrix, per-language / per-attack / per-compression (**REQ-046–053**).

**Splits:** speaker-disjoint, versioned manifests (**REQ-099**). Exact ratios → **OQ-008**.

**Statistical tests:** not specified in proposal → **OQ-009** (default: bootstrap CIs on EER; McNemar for human vs model).

---

## 10. Calibration

Temperature scaling; ECE; reliability diagrams; Brier; entropy; coverage/accuracy curves; reliability badge thresholds (**REQ-054–062**, **REQ-140**).

Badge threshold values (when to show LOW/MODERATE/HIGH) → **OQ-010**.

---

## 11. Explainability

Grad-CAM temporal heatmap; frequency-band masking importance; spectrogram clean vs compressed; compression-artifact plots; language-wise confusion (**REQ-075–079**).

---

## 12. Human study protocol

| Aspect | Spec | REQ |
|--------|------|-----|
| N | ~20–30 target; success floor 12–15 | REQ-064, 123 |
| Fluency | HI/MR preferred; self-report | REQ-065 |
| Stimuli | Fixed balanced 3 langs × clean/compressed; identical to model subset | REQ-066 |
| Task | Forced-choice + confidence 1–5 | REQ-067–068 |
| Delivery | Google Forms or static HTML | REQ-069 |
| Analysis | Acc + calibration curves + qualitative | REQ-070–072 |
| Ethics | Anonymous, voluntary, no sensitive PII | REQ-073–074 |

Randomisation procedure not detailed → **OQ-011**.

---

## 13. Compression conditions

Stated: clean + WhatsApp-style Opus via ffmpeg; also resampling and noise in the same pass (**REQ-018**, **REQ-113**).

Exact codec args (bitrate, application=voip, container, SNR) → **OQ-007**. Bitrate ladder / multiple quality levels mentioned in Phase-0 prompt but not enumerated in proposal → **OQ-012**.

---

## 14. UI inventory

| Surface | Widgets | REQs |
|---------|---------|------|
| Landing | Brand, short aim, CTA to upload/live | REQ-134 |
| Upload / Inference | File upload, waveform, verdict, calibrated %, reliability badge, explain panel, re-analyse | REQ-084–091, 124 |
| Live | MediaRecorder, sliding-window status | REQ-096 |
| History | Past predictions list | REQ-134 |
| Research metrics | EER/min-DCF tables, matrices | REQ-046–053 |
| Experiments | Run manifests | REQ-137 |
| Calibration | ECE, diagrams, histograms, coverage | REQ-140 |
| Explainability | Grad-CAM, bands, artifacts | REQ-075–078 |
| Admin / Docs | health, version, guides | REQ-134 |

---

## 15. Backend / API / data / deployment

- Three-tier: React ↔ Node request layer ↔ FastAPI inference (**REQ-092–093**)
- Multi-stage decode + upload validation (**REQ-094**, **REQ-135**)
- Config-driven CORS (**REQ-136**)
- Hosting: HF Spaces CPU or local (**REQ-112**)
- Storage plan: Kaggle + Drive; repo keeps manifests only (**REQ-111**)

Hexagonal ports/DI and generated OpenAPI types are engineering constraints from `vaaniq-core.mdc` (INFRA), complementary to proposal §7.9.

---

## 16. Deliverables & acceptance bar

| Deliverable | Acceptance |
|-------------|------------|
| Open labelled dataset (3 langs, clean+Opus) | Manifests + licence notes; hours in target band or OQ logged |
| Trained model + baseline tables | REQ-019, 121–122 |
| Calibration report | REQ-021, 063 |
| Human-baseline dataset + analysis | REQ-123 |
| Working demo | REQ-023, 124 |
| Report + arXiv/conference draft on RQ1–RQ5 | REQ-024, 128 |

Binary success criteria: **REQ-121–124** (+ calibration majority-cell improvement **REQ-063**).

---

## Cross-references

- Requirements: `docs/REQUIREMENTS.md`
- Open questions: `docs/OPEN_QUESTIONS.md` (esp. **OQ-001**, **OQ-007**, **OQ-013**)
- Architecture: `docs/SYSTEM_ARCHITECTURE.md`
- Execution plan: `docs/PROJECT_ROADMAP.md` phases **P1–P9** / **ROADMAP-001–064**
