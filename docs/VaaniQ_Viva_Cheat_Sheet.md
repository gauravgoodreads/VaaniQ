# VaaniQ Viva Cheat Sheet

Answers are scoped to **persisted artifacts** under `artifacts/experiments/` and `models/checkpoints/`.

## Dataset & methodology

**1. Why Kathbath?**  
Gated bonafide Indian-language speech corpus (hi/mr/ta) cited in the proposal for real speech.

**2. Why IndicSynth?**  
Public CC BY-NC fake speech for the same languages; enables balanced real/fake cells.

**3. Why Hindi, Marathi, Tamil?**  
Proposal scope (REQ-004). Telugu is explicitly out of scope.

**4. What is speaker-disjoint split?**  
All clips from one speaker stay in one partition (train/val/test). Prevents the model from memorizing speaker identity.

**5. Why is random clip splitting dangerous?**  
Same speaker could appear in train and test → inflated accuracy.

**6. What is dataset-source confounding?**  
In Baseline V1, real=Kathbath and fake=IndicSynth always. Source correlates with label.

**7. Could the model simply recognize Kathbath vs IndicSynth?**  
Yes, structurally possible. Source-shortcut probe on test: label 84.8%, source 84.6% (similar).

**8. What did we do to test that?**  
`artifacts/experiments/source_shortcut/metrics.json`; Benchmark V2 script adds Common Voice + generator tags.

## Models

**9. Why XLS-R?**  
Multilingual frozen front-end per proposal (wav2vec2-xls-r-300m).

**10. Why freeze XLS-R?**  
REQ-041: use pretrained representation; train only the anti-spoofing head unless ablation justifies fine-tuning.

**11. What is AASIST?**  
Graph-attention anti-spoofing architecture. VaaniQ uses an **AASIST-compatible NumPy head**, not clovaai graph AASIST.

**12. What is LFCC-GMM?**  
Classical cepstral features + diagonal GMMs. Test EER ~23.5% on V1 (artifact: `baseline_matrix`).

**13. What is RawNet2?**  
Raw-waveform CNN anti-spoofing. VaaniQ uses a **lightweight approximation** for CI (EER ~43% on V1).

## Metrics

**14. What is EER?**  
Equal error rate: threshold where false accept ≈ false reject (class-conditional, ASVspoof-style).

**15. Why accuracy isn't enough?**  
Imbalanced costs, threshold choice, and spoofing detection tradition use EER/min-DCF.

**16. What is min-DCF?**  
Minimum detection cost (P_target=0.05, C_miss=C_fa=1). V1 test min-DCF **0.787** despite good EER.

**17. Why is current min-DCF high?**  
Score distribution + prior/cost settings; good ranking (ROC-AUC 0.974) but suboptimal cost at default prior.

**18. What is ECE?**  
Expected calibration error: |confidence − accuracy| averaged over bins.

**19. What is Brier score?**  
Mean squared error of probabilistic fake-class predictions.

## Calibration (RQ4)

**20. Why did per-cell temperature scaling worsen calibration on test?**  
Small val cells (lang×condition) overfit. Global temperature **improves** test ECE 0.0378→0.0279; per-cell used in train_report worsens to 0.0424.

**21. Is that a failed experiment?**  
No — it shows **calibration strategy matters** under multilingual shift.

## Generalization

**22. Why does Hindi zero-shot perform worse?**  
RQ3 held-out hi: acc 78.8%, EER 21.8% vs ~93%/6–7% for mr/ta. Cause **remains unresolved** (speaker counts, phonetics, generator mix).

**23. What does Opus compression change?**  
High-frequency detail, coding noise; clean 95.2% → Opus 92.1% acc (−3.1 pp on V1 test).

**24. Is this actual WhatsApp compression?**  
No — **WhatsApp-style Opus simulation** via ffmpeg/libopus at 16 kbps.

**25. Why 16 kbps?**  
Proposal-aligned messaging-app bitrate; paired twins preserve utterance IDs.

## Scope

**26. Why not use all 300+ GB?**  
Disk/compute bounds; scientific value from controlled speaker-disjoint subset (~4.11 h eval).

**27. Why is ~3–30 h enough with XLS-R?**  
Frozen front-end + head training; diversity and disjoint splits matter more than raw hours for capstone claims.

**28. Pretrained vs trained-from-scratch?**  
XLS-R brings multilingual acoustic knowledge; head learns real/fake boundary on curated data.

**29. How prevent leakage?**  
Speaker hash splits, pair-id checks, test excluded from training/checkpoint selection (`verify_research_integrity.py`).

## Research questions

**30. RQ1 (compression)?** **PARTIAL/COMPLETE** on V1 — clean vs Opus table in artifacts. Bitrate curve: planned.

**31. RQ2 (English-only)?** **PENDING** — ASVspoof control (OQ-015).

**32. RQ3 (cross-lingual)?** **COMPLETE** on V1 — LOO folds in `rq3_crosslingual/metrics.json`.

**33. RQ4 (calibration)?** **COMPLETE** audit — global TS helps; per-cell hurts on held-out test.

**34. RQ5 (human)?** **PENDING data** — protocol ready, **N=0**; never fabricate participants.

**35. Why human listeners?**  
Proposal baseline for perception vs detector under clean/compressed stimuli.

**36. What is novel?**  
Combined setting: Indic languages + Opus robustness + calibration under shift + cross-lingual + open system. Not claiming first deepfake detector.

**37. Biggest limitations?**  
V1 source confound, bounded subset, no human N yet, acoustic front-end for measured V1 (XLS-R path ready not primary metric).

**38. Detect every AI voice?** **No** — only evaluated generators/conditions in manifest.

**39. Deploy for fraud today?** **No** — research prototype; domain shift from scam traffic.

**40. Production needs?**  
Harder benchmarks, unseen generators, calibrated deployment thresholds, human studies, legal review.

**41. Strongest result?**  
Speaker-disjoint V1 detection: **93.7% acc, 6.6% EER** on 584 test instances with paired Opus eval.

**42. Weakest result?**  
Hindi LOO EER 21.8%; LFCC-GMM/RawNet2 baselines weak vs head; min-DCF 0.787.
