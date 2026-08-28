# Known limitations

Honest constraints for the dissertation §18 analogue. Do not hide these in RQ tables.

1. **V1 source-label confound:** REAL=Kathbath and FAKE=IndicSynth, so source identity is associated with class.
2. **Bounded benchmark:** V1 has 1,800 source clips and does not represent the complete upstream corpora.
3. **Domain scope:** academic speech is not equivalent to real scam or telephony traffic.
4. **Codec scope:** the paired condition is a WhatsApp-style Opus simulation, not actual WhatsApp transport.
5. **Language scope:** evidence covers Hindi, Marathi, and Tamil only.
6. **Model fidelity:** the measured classifier is AASIST-compatible NumPy code, not canonical AASIST.
7. **Baseline fidelity:** the RawNet2-style approximate baseline is not faithful RawNet2; faithful RawNet2 is pending.
8. **V2 incomplete:** its source probe reaches 98.48%, so it has not removed source-domain confounding.
9. **External-source pilot:** frozen held-out FLEURS evaluation is n=9 (pipeline
   evidence only). A later local ingest recorded 150 FLEURS reals on disk; that
   corpus is **not** the Round 3 result until a new evaluation is run.
10. **Generator generalization:** generator-disjoint evaluation has n=0; no result is claimed.
11. **Human study:** protocol ready; participant data collection pending (N=0).
12. **Calibration transfer:** Baseline V1's validation-selected strategy slightly worsened held-out ECE.
13. **Validation heterogeneity:** Tamil validation was weak and Marathi validation unusually strong; the exact cause is unresolved.
14. **Explainability scope:** Grad-CAM is spectrogram-energy aligned, not backpropagation through canonical AASIST.
15. **Deployment scope:** the application is a research prototype, not a production fraud detector.
16. **Licensing:** IndicSynth CC BY-NC may prevent redistribution of a full public audio dump.
17. **Security:** `/api/v1/admin/status` is unauthenticated and intended only for a closed lab deployment.
