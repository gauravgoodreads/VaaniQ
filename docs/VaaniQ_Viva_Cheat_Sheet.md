# VaaniQ Viva Cheat Sheet

Answers are scoped to the approved Round 3 evidence in
`artifacts/final_results_manifest.json`.

## Dataset & methodology

**1. Why Hindi, Marathi, and Tamil?**  
They are the three languages approved in the proposal and provide related but distinct
linguistic conditions. The study makes no claim beyond these languages.

**2. Why Kathbath?**  
Kathbath supplies bonafide Indian-language speech with speaker metadata needed for
speaker-disjoint splitting across Hindi, Marathi, and Tamil.

**3. Why IndicSynth?**  
IndicSynth supplies licensed AI-generated speech in the same languages. Its use enables
controlled fake-speech cells, but also creates the V1 source-label confound.

**4. Why does source-label confounding matter?**  
In V1, REAL always comes from Kathbath and FAKE from IndicSynth. A detector may learn
dataset fingerprints instead of general fake-speech cues.

**5. Does speaker-disjoint splitting solve source confounding?**  
No. It prevents the same speaker appearing across train, validation, and test, but does
not break the association between source dataset and class.

**6. Why only 1,800 source clips?**  
The project uses a declared bounded V1 benchmark: 900 real and 900 fake source clips,
expanded to 2,346 instances through paired validation/test Opus twins.

**7. Why not download all 300+ GB?**  
Storage and compute were bounded. A reproducible, checksummed subset was preferable to
an uncontrolled partial download; conclusions are explicitly restricted to that subset.

**8. What is speaker-disjoint evaluation?**  
Every speaker belongs to exactly one split. This reduces identity leakage while preserving
clean/Opus pairs in the same split.

## Models

**9. Why XLS-R?**  
`facebook/wav2vec2-xls-r-300m` is a multilingual self-supervised speech encoder. It is
the frozen front-end for the separate XLS-R main path, not Baseline V1.

**10. Why freeze XLS-R?**  
Freezing reduces compute and prevents the pretrained backbone from changing. Cached
features make the experiment reproducible and keep training limited to the small head.

**11. What is mean pooling?**  
Frame-level XLS-R representations are averaged over time to form one fixed-dimensional
utterance vector for the classification head.

**12. Is the classifier actually canonical AASIST?**  
No. Both measured paths use an **AASIST-compatible NumPy classification head**. The
project does not claim graph-architecture parity with the official AASIST implementation.

**13. Why call it AASIST-compatible?**  
Its role and anti-spoofing interface follow the planned AASIST head, but the implementation
is lightweight NumPy rather than the canonical spectro-temporal graph model.

## Metrics

**14. What is EER?**  
Equal error rate is the operating point where false-accept and false-reject rates are
approximately equal. Lower is better.

**15. What is ROC-AUC?**  
ROC-AUC measures ranking across all thresholds: the probability that a random fake clip
receives a higher fake score than a random real clip. Higher is better.

**16. What is min-DCF?**  
It is normalized minimum detection cost with P_target=0.05 and C_miss=C_fa=1. The
normalization denominator is P_target × C_miss = 0.05.

**17. Why can EER be good while min-DCF is high?**  
EER/AUC describe separation; min-DCF evaluates a specific prior and cost. At 5% target
prior, false accepts strongly affect normalized cost, so Baseline V1 can have 6.56% EER
and 0.7841 min-DCF without a metric bug.

**18. Why did XLS-R have better AUC but slightly worse EER?**  
XLS-R improved global ranking (0.9828 vs 0.9729 AUC), while its 6.88% EER remained
close to Baseline V1's 6.56%. Different metrics emphasize different operating behavior.

**19. What happened under Opus?**  
For Baseline V1, accuracy fell 93.84%→89.38% and EER rose 5.63%→7.58%.
The condition is a **WhatsApp-style Opus simulation** at 16 kbps.

**20. Why did XLS-R not degrade like Baseline V1?**  
On this bounded split, XLS-R accuracy rose from 91.44% to 92.81% under Opus while EER
fell from 8.13% to 6.06%. Codec effects are model-dependent; no universal benefit is claimed.

## Transfer and calibration

**21. Why is RQ2 English-only performance poor?**  
The English-only ASVspoof control transferred catastrophically: 54.8% accuracy,
76.56% EER, 0.162 AUC, and all predictions REAL at threshold 0.5.

**22. Was RQ2 a score-polarity bug?**  
No global bug was found. Negation improved the diagnostic AUC to 0.838, but the same
canonical score contract gives 0.9729 AUC for multilingual Baseline V1 on the same test.

**23. Why is Hindi zero-shot weaker?**  
Hindi held-out accuracy is 78.83% with 21.83% EER, versus about 93–94% accuracy for
Marathi/Tamil. Transfer is asymmetric; the exact cause remains unresolved.

**24. Did calibration improve?**  
Not uniformly. Baseline V1's validation-selected per-language-and-condition strategy
slightly worsened held-out ECE from 0.0245 to 0.026.

**25. Why did selected calibration worsen test ECE?**  
Validation cells were heterogeneous and the fine-grained strategy did not transfer
perfectly. This is retained as a negative result, not hidden.

**26. Did you select calibration using the test set?**  
No. Production strategies were validation-selected. A separate test-set comparison where
global scaling looked better is explicitly exploratory and was not used for selection.

## V2 and external validity

**27. What is Benchmark V2?**  
It is a partial external-source pilot: Kathbath×real 1,177, IndicSynth×fake 1,169,
and FLEURS×real 50, with freevc24 and xtts_v2 generator tags.

**28. Did V2 solve source confounding?**  
No. The source probe reached 98.48% while the label probe reached 85.83%, showing that
source identity remains highly predictable.

**29. Why is the source probe 98.48%?**  
Each source still has a restricted label/domain role and different acoustic characteristics.
The partial V2 design adds one real source but does not balance source×label cells.

**30. Why is n=9 FLEURS not a valid external benchmark?**  
Nine held-out clips cannot provide a statistically useful estimate. The 55.6% result is
retained only as pipeline-validation evidence and labelled PILOT.

## Scope and contribution

**31. What is still pending?**  
Faithful RawNet2 and generator-disjoint evaluation (n=0) are PENDING. Benchmark V2 is
PARTIAL, and the FLEURS external-source result is only a PILOT.

**32. Why are there no human results?**  
Human-study protocol ready; participant data collection pending (N=0). RQ5 is blocked
on real participant data, and no responses were simulated.

**33. Is this deployable today?**  
No. It is an examiner-ready research prototype, not a production fraud detector.
Deployment would require stronger external validation, monitoring, security, and governance.

**34. Can it detect every fake voice?**  
No. Evidence is limited to the persisted sources, languages, generators, and conditions.
There is no completed unseen-generator result.

**35. What is the strongest result?**  
Frozen XLS-R reached 92.12% accuracy and 0.9828 ROC-AUC on n=584. Baseline V1 reached
91.61% accuracy and 6.56% EER on the same bounded speaker-disjoint test.

**36. What is the biggest weakness?**  
V1 source and label are structurally associated, and partial V2 still has 98.48% source
probe accuracy. External-source, unseen-generator, and human evidence remain incomplete.

**37. What would you do next with more time?**  
Balance source×label and generator cells, complete a genuinely held-out-generator test,
implement faithful RawNet2, expand FLEURS beyond pilot scale, and collect real RQ5 data.

**38. What is genuinely novel about VaaniQ?**  
The contribution is the integrated evaluation framework combining Indic languages,
codec shift, cross-language transfer, calibration, human-study infrastructure, and an
end-to-end reproducible system—not invention of XLS-R or AASIST.

**39. Why is this more than a classifier demo?**  
It includes versioned data, speaker-disjoint evaluation, multiple controls, calibration,
explainability, artifact integrity checks, a human-study protocol, APIs, and a research UI.

## Canonical score contract

Label 0 = REAL/bonafide; label 1 = FAKE/spoof; FAKE is positive. Higher `score_fake`
means greater fake probability, the logit order is `[real, fake]`, and the decision
threshold is 0.5.
