# ML review (Phase 5)

Review of training, inference, evaluation, calibration, leakage, and reproducibility. After this audit, EER/min-DCF and the calibration fit/eval split are corrected. Remaining issues are leakage footguns and the gap between NumPy heads and the proposal’s clovaai AASIST.

## Training

| Check | Finding |
|-------|---------|
| Entry seed | `seed_everything` seeds `random`, NumPy, and torch when present (REQ-137). |
| Determinism | `torch.use_deterministic_algorithms` is not forced in the NumPy default path (acceptable for CI). |
| Loop | `Trainer.fit` supports early stopping, checkpoints, run manifest (git SHA, dirty, seed, config). |
| Val split | If `val_features` is omitted, the trainer uses a **prefix of train**. That is leakage. A structured warning is now emitted; callers must still pass a real val set. |
| AASIST | NumPy MLP-style head with residual blocks — **not** graph attention AASIST. Disclose in every paper table. |
| Loss | Cross-entropy on 2-class logits in the NumPy trainer. No weighted CE / focal unless added later (would need an OQ). |
| AMP | Optional `use_amp` when torch is installed. Untested on GPU in this environment. |

## Inference

| Check | Finding |
|-------|---------|
| Pipeline | validate → load → duration check → preprocess → embed → classify → temperature transform → badge. |
| Embedding cache | Filesystem cache with path traversal guards. Demo extractor can fall back to waveform stats if HF weights fail (logged). |
| Live path | Sliding window (OQ-019: 2.0 s / 0.5 s). Browser ingest does **not** decode WebM to PCM. |
| Model registry | `aasist-v1` plus baselines. Invalid `Language` now 400 instead of 500. |

## Evaluation / metric correctness

**P0 (fixed):** `equal_error_rate` and `min_dcf` previously used joint probabilities (`mean(pred & y==0)` = P(FA and real), not FPR). Known-answer test: eight equal scores, six real + two fake → class-conditional EER = 1.0 (joint would be 0.75).

ROC uses score-sorted cumulative TPR/FPR. Confusion is `[[TN, FP], [FN, TP]]`. Bootstrap CI resamples pairs with a seeded RNG (OQ-009).

Empty-history `/api/v1/metrics` still invents four toy scores. Do not cite that payload.

## Calibration

| Check | Finding |
|-------|---------|
| Temperature | Per `(language, condition)` keys (OQ-031). |
| Fit split | Suite now fits on the first half and scores the second when `n >= 4`. For `n < 4` it still fits and scores the same tensors (logged by the small-n branch). |
| OQ-032 | Strict speaker-disjoint **val** for T-fit is **not** enforced by the suite; the caller must pass val logits. |
| ECE bins | 15 equal-width (OQ-017). |
| Badge | Entropy + compression heuristics (OQ-010). |

## Data leakage

| Risk | Status |
|------|--------|
| Speaker-disjoint manifests | Implemented. Missing `speaker_id` → one bucket per clip (now warned). That can leak a speaker who appears under several clip IDs. |
| Train prefix as val | Warned; still possible. |
| Pair clean/Opus | `pair_id` in schema (OQ-028); pairing helper exists. Not proven on full corpora. |
| Test in temperature fit | Mitigated in the suite by a half-split; not equivalent to manifest val. |
| English-only baseline | Protocol default ASVspoof 2019 LA (OQ-015). Domain shift vs Indic test must be disclosed. |

## Random seeds and reproducibility

Experiment store records git SHA, seed, hardware, hyperparameters, RQ ids. Splits are written to JSONL, not computed ad hoc at eval time **if** the splitter is used. Demo inference is not a published run.

## Residual ML work (aligned with proposal, not feature bloat)

1. Run freeze-XLS-R once on curated clips; cache embeddings; train only the head.
2. Always pass speaker-disjoint val into `Trainer` and `TemperatureScaler.fit`.
3. Replace NumPy AASIST with official graph code on GPU when Colab/Kaggle is available (proposal §11).
4. Stop serving synthetic metrics when history is empty.
