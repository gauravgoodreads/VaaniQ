# Research findings — approved Round 3

Source: `artifacts/final_results_manifest.json`.

## Primary models

- **Baseline V1:** n=584, accuracy 91.61%, F1 91.36%, EER 6.56%,
  ROC-AUC 0.9729, normalized min-DCF 0.7841.
- **Frozen XLS-R main:** n=584, accuracy 92.12%, EER 6.88%,
  ROC-AUC 0.9828, normalized min-DCF 0.3144.

Frozen XLS-R improved ranking performance while classification performance remained
broadly comparable.

## Research questions

- **RQ1 COMPLETE:** Compression was model-dependent. Acoustic accuracy changed
  93.84%→89.38%; XLS-R changed 91.44%→92.81% under WhatsApp-style Opus simulation.
- **RQ2 COMPLETE:** English-only→Indic transfer was catastrophic: 54.8% accuracy,
  76.56% EER, 0.162 AUC, and all predictions REAL at threshold 0.5.
- **RQ3 COMPLETE:** Held-out accuracy was Hindi 78.83%, Marathi 93.29%, Tamil 93.94%;
  cross-language transfer was asymmetric.
- **RQ4 COMPLETE:** Baseline V1's validation-selected calibration changed held-out
  ECE from 0.0245 to 0.026; calibration did not uniformly transfer.
- **RQ5 BLOCKED ON HUMAN DATA:** Human-study protocol ready; participant data
  collection pending (N=0).

## External validity

Benchmark V2 is a **PARTIAL external-source pilot** and does not solve source-label
confounding. FLEURS n=9 is **PILOT** evidence only. Generator-disjoint evaluation
has n=0 and is **PENDING**. Faithful RawNet2 is **PENDING**.
