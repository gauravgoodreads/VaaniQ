# VaaniQ — Open Questions

> Phase 0 Step 3. Gaps, ambiguities, and Proposal-vs-PPT conflicts.
> Do **not** invent answers. Defaults are provisional; cite `OQ-###` at point of use (`# ASSUMPTION: OQ-###`).

| ID | Question | Why it matters | Blocking? | Proposed default | Source |
|----|----------|----------------|-----------|------------------|--------|
| OQ-001 | Is the third language definitively **Tamil**? Body says “one additional Indian language”; Fig.2 mockup labels Hindi/Marathi/**Tamil**. | Language enum, datasets, UI, zero-shot design | Yes (before P2 download) | Tamil (`ta`); Telugu is **not** a project language | Proposal p.3 vs p.14 Fig.2; Slide 4 |
| OQ-002 | Exact curated hours **per language** after sampling (within 50–100)? | Split sizing, compute, fairness across langs | No | Aim midpoint ~75 h/lang; log actuals in dataset report | Proposal p.6; Slide 11 |
| OQ-003 | Real Tamil audio source if Common Voice only lists hi/mr configs? | REQ-004 needs real TA speech | Yes (before P2 TA real layer) | Prefer Kathbath + IndicVoices-R TA subsets; confirm configs on first load | Proposal p.11 vs REQ-004 |
| OQ-004 | Does IndicSynth include Tamil fakes at usable quality/volume? | Fake-layer balance for TA | No | Sample IndicSynth TA if present; else overweight Parler-TTS TA | Proposal p.11 |
| OQ-005 | Target hours / speaker count for team phone-mic recordings? | Realism ablation size | No | ≥30 min/lang from consenting speakers | Proposal p.5 §7.1 |
| OQ-006 | Fraud-pattern generation: max clip length, reference seconds, prompt set? | Reproducible Layer-3 fakes | No | ≤8 s clips; XTTS 6 s ref (tool default); prompt bank in `configs/data/` | Proposal p.6; p.11 |
| OQ-007 | Exact ffmpeg Opus args (bitrate, `application`, sample rate, container, noise SNR)? | RQ1 reproducibility | Yes (before P3) | Opus 16 kbps VoIP-ish, 16 kHz mono OGG/Opus; light noise optional off-by-default | Proposal p.6, p.11; Slide 13 |
| OQ-008 | Train/val/test ratios and speaker-disjoint algorithm? | Fair eval | No | 70/15/15 speaker-disjoint; seed in config | Not stated; vaaniq-core |
| OQ-009 | Statistical tests for metrics / human vs model? | Paper rigor | No | Bootstrap 95% CI on EER; McNemar human vs model | Not stated |
| OQ-010 | Reliability badge thresholds (entropy / confidence / compression detector)? | UI honesty (REQ-062) | No | Flag MODERATE if Opus detected or confidence∈[0.55,0.70]; LOW if entropy high | Proposal p.14 Fig.2 example only |
| OQ-011 | Human-study randomisation, clip count per participant, time cap? | Protocol ethics & power | No | ~30–40 clips; shuffled; ≤25 min session | Proposal p.7 §7.6 |
| OQ-012 | Is a multi-bitrate Opus ladder required, or single WhatsApp-style setting? | Scope of RQ1 | No | Single primary Opus setting + optional ladder as SHOULD | Phase-0 prompt vs Proposal “Opus pass” |
| OQ-013 | XLS-R embedding: which layer / pooling / segment length? | Cache schema, AASIST input | Yes (before P4) | Mean-pool last transformer layer; 4 s windows hop 2 s | Not stated |
| OQ-014 | AASIST training hyperparameters (lr, batch, epochs, loss, WD)? | Reproducibility | No | Start from clovaai/aasist defaults; record in run manifest | Not stated |
| OQ-015 | ASVspoof subset/year for English-only baseline? | RQ2 control validity | No | ASVspoof 2019 LA train | Proposal p.6 “ASVspoof” |
| OQ-016 | Node.js request layer: Express vs Nest vs thin BFF? Proposal requires Node + FastAPI. Engineering rules emphasize FastAPI. | Architecture compliance | No | Thin Express/Fastify BFF proxying to FastAPI; FastAPI owns domain | Proposal p.8–9 vs vaaniq-core |
| OQ-017 | ECE bin count and binning scheme? | Calibration comparability | No | 15 equal-width bins | Not stated |
| OQ-018 | min-DCF cost parameters (P_target, C_miss, C_fa)? | Metric convention | No | ASVspoof defaults from AASIST metric code | Proposal p.11 AASIST metrics |
| OQ-019 | Streaming window size / hop for live MediaRecorder mode? | Live demo UX | No | 2.0 s window, 0.5 s hop | Proposal p.8 “sliding-window” |
| OQ-020 | HF Spaces vs docker-compose local as primary demo host for reviews? | Ops | No | docker-compose for development; HF Spaces optional publish | Proposal p.11 |
| OQ-021 | Database for uploads/predictions: SQLite vs Postgres in prod profile? | Persistence | No | SQLite local; Postgres in compose prod profile | Not in proposal; Phase-1 scaffold |
| OQ-022 | Attention visualisation beyond Grad-CAM — required or optional? | Explainability scope | No | Grad-CAM + band + artifact MUST; raw attention COULD | Proposal §7.7 list |
| OQ-023 | Does “noise” in compression pipeline mean additive noise, codec noise only, or both? | RQ1 definition | No | Codec only for primary; additive noise as optional config | Proposal p.6 “Opus, resampling, noise” |
| OQ-024 | Common Voice: official gated vs ungated mirror `fsicoli/...` for CI? | Access | No | Prefer official; mirror allowed in config with checksum note | Proposal p.11 |
| OQ-025 | Human study: include Tamil-fluent listeners or HI/MR only? | RQ5 fairness for TA stimuli | No | Recruit TA-fluent if available; else disclose HI/MR listeners on TA clips as limitation | Proposal p.7 |
| OQ-026 | Is Node request layer mandatory for academic demo, or may FastAPI serve React directly in P1? | Phase-1 scope | No | P1: FastAPI↔React; ROADMAP item adds Node BFF before final demo | Proposal §7.9 vs scaffold practicality |
| OQ-027 | Exact Wav2Vec2-XLS-R size: 300m only, or allow 1b? | VRAM on Colab T4 | No | 300m only (**REQ-041**) | Proposal p.11 |
| OQ-028 | Should pair_id enforce 1:1 clean↔compressed for all sources including team recordings? | Matrix completeness | No | Yes for all curated clips | Proposal p.6 |
| OQ-029 | Publication venue priority among ICCCNT / ICACCS / INDICON? | Timeline | No | Decide after Review 2 draft | Proposal §21 |
| OQ-030 | PPT Slide wording “Hindi & Marathi” in intro threat (Slide 3) vs three-language scope — conflict? | Messaging consistency | No | Proposal wins: three languages; Slide 3 is threat framing not scope | Slide 3 vs Proposal p.3 |
| OQ-031 | Temperature: one T per (language×condition) vs shared T? | REQ-055–056 | No | Per (language×condition) as stated | Proposal p.6 §7.5 |
| OQ-032 | May validation split used for T-fitting overlap any test speakers? | Leakage | No | Strict: T fit on val only; speakers disjoint from test | Proposal “held-out”; good practice |
| OQ-033 | Aux acoustic features: early fusion, late fusion, or meta-classifier? | Ablation design | No | Late concatenation into AASIST input projection | Proposal p.8 |
| OQ-034 | Grad-CAM on spectrogram vs on AASIST graph features — which input? | Implementation | No | Spectrogram/path aligned to model input used at inference | Proposal p.7 “spectrogram input used here” |
| OQ-035 | Dataset open release under which umbrella licence given CC BY-NC IndicSynth subset? | Legal | Yes (before public release) | Dual: release manifests + scripts; redistribute only licence-compatible subsets; document NonCommercial | Proposal p.11, §20 |

## Conflict log (Proposal wins)

| Conflict | Proposal | Topic Approval | Resolution |
|----------|----------|----------------|------------|
| Third language named? | “one additional” + Fig.2 Tamil | “one more Indian language” | **Tamil** pending supervisor confirm (OQ-001) |
| Threat languages on Slide 3 | HI/MR/other Indic | “Hindi & Marathi” WhatsApp notes | Scope remains 3 langs (OQ-030) |
| Telugu | Tool coverage only (Parler-TTS) | Not a project language | Never emit `te` as Language (REQ-139) |

## Template for new rows

```markdown
| OQ-XXX | Question | Why it matters | Yes/No | Proposed default | Proposal p.N / Slide N |
```

## Cross-references

- Blocking before P2: **OQ-001**, **OQ-003** → `PROJECT_ROADMAP.md` P2
- Blocking before P3: **OQ-007** → **ROADMAP-021**
- Blocking before P4: **OQ-013** → **ROADMAP-025**
- Requirements that encode defaults: **REQ-004**, **REQ-113**, **REQ-132**, **REQ-139**
