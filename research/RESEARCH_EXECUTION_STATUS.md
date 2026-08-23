# Research execution status

Generated: 2026-08-15T13:42:50.130172+00:00

Statuses: COMPLETE = actually run on curated data and validated.
PARTIAL / PENDING / FAILED as defined in the Phase 6 prompt.
Code existing ≠ COMPLETE.

## 1. Actual dataset hours per language

| Language | Research hours | Fixture metadata hours | Status |
|----------|---------------:|-----------------------:|--------|
| Hindi | 0 | 0.0009722222 | PENDING |
| Marathi | 0 | 0.0015277778 | PENDING |
| Tamil | 0 | 0.0013888889 | PENDING |

## 2. Number of speakers

Research corpus: **0**. Schema fixture named speakers: **5**.

## 3. Number of clips

Research corpus: **0**. Schema fixture rows: **6**.
Audio files on disk under data trees: **0**.

## 4. Train / validation / test sizes

Research splits: **PENDING** (not written). Fixture split counts: `{'train': 6, 'val': 0, 'test': 0}`.

## 5. Main model configuration

Intended: frozen Wav2Vec2-XLS-R + AASIST-style head (`aasist-v1`), NumPy CI path.
GPU / clovaai graph AASIST: **PENDING**.
Status: **PENDING** (not trained on curated embeddings).

## 6. Baseline configurations

LFCC-GMM, RawNet2, English-only XLS-R+AASIST modules exist.
ASVspoof ingest + evaluation: **PENDING**.

## 7. RQ1 result status

**PENDING** — no Opus vs clean evaluation on held-out audio.

## 8. RQ2 result status

**PENDING** — multilingual vs English-only not run.

## 9. RQ3 result status

**PENDING** — zero-shot HI+MR→TA / HI+TA→MR / MR+TA→HI not run on real data.

## 10. RQ4 result status

**PENDING** — T-scaling not fit on real val logits.

## 11. RQ5 result status

**PENDING**.

## 12. Human participant count

**0**.

## 13. Calibration status

**PENDING**.

## 14. Explainability status

**PARTIAL** — demo Grad-CAM proxy artefacts exist; not tied to a published test set.

## 15. Figures generated

RQ publication figures: **0**.
Fixture/demo SVGs may exist under software-path runs; they are not RQ figures.

## 16. Tables generated

PENDING stub CSVs with empty metric cells:

- `research/results/dataset_statistics.csv` (actual zeros + fixture metadata hours)
- `research/results/RQ1_clean_vs_opus.csv`
- `research/results/RQ2_multilingual_vs_english.csv`
- `research/results/RQ3_cross_lingual_matrix.csv`
- `research/results/RQ4_calibration.csv`
- `research/results/RQ5_human_vs_model.csv`

## 17. Paper sections completed

Methods/gap/RQs draft: **PARTIAL** (`research/paper/manuscript/VaaniQ_manuscript.md`).
Results sections: **NOT RUN** (explicit).

## 18. Remaining experiments

1. Obtain HF token; download gated Kathbath / IndicVoices-R / IndicSynth / CV hi-mr.
2. Confirm Tamil **audio** (not labels only).
3. Speaker-disjoint manifests; pair clean/Opus in the same split.
4. Freeze XLS-R on GPU; cache embeddings.
5. Train head; run RQ1-RQ4.
6. Recruit ≥12-15 listeners on the same test clip IDs.

## 19. Failed experiments

None failed after start. Acquisition **not started**: `hf_token_present=False`.

## 20. Known limitations

See `docs/KNOWN_LIMITATIONS.md` (authoritative). Not rewritten here.

## 21. Reproducibility information

| Field | Value |
|-------|--------|
| Git SHA | `2d49ac0af9bfb4800996e43feea3f321a10725c2` |
| Dirty | True |
| ffmpeg runnable | True |
| torch | absent |
| cuda | false |
| python | 3.11.13 |
| system | Windows AMD64 |
| seed (unused; no train) | n/a |
| dataset version | none (research corpus empty) |

`can_train` after quality audit: **False**.
