# Source extract: `VaaniQ_Topic_Approval_Presentation_Final_B091_B093_B094_B106 (1).pdf`

- Ingested: `2026-08-06T09:36:25.888978+00:00`
- Source path: `c:\Users\Aarav Phutane\Downloads\VaaniQ_Topic_Approval_Presentation_Final_B091_B093_B094_B106 (1).pdf`
- Page/slide count: 19

---

<!-- slide: 1 -->

## Slide 1

Capstone Project
Title Approval Presentation
A.Y. 2026-2027
Project Title: VaaniQ
Cross-Lingual, Compression-Robust Detection and Calibrated Reliability Estimation for AI-Generated Voice in 
Indian Languages, with a Human-Perception Baseline
Presented by :
Gaurav Phadale
70022300092   |   B093
Eshaan Sarkhawas
70022300066   |   B106
Aarav Phutane
70022300152   |   B094
Prajwal Patil
70022300213   |   B091
Under the guidance of : Prof. Rama Bharti Varshney
Computer Engineering Department, MPSTME, Mumbai Campus

<!-- figure: slide 1, embedded image 1 of 1 -->

<!-- slide: 2 -->

## Slide 2

Agenda
1
Introduction
2
Problem Statement
3
Aim & Objectives
4
Literature Review
5
Scope
6
Feasibility
7
Dataset Collection & Verification
8
Technology Stack & Algorithm
9
Expected Results
10
Timeline
11
Conclusion
12
References
2

<!-- figure: slide 2, embedded image 1 of 1 -->

<!-- slide: 3 -->

## Slide 3

Introduction
What is VaaniQ
• A cross-lingual audio deepfake detector for 
Indian languages
• Gives a calibrated confidence score, not just a 
raw verdict
• Flags when compression has degraded audio 
enough to doubt its own verdict
• Three linked contributions: detection, 
calibrated reliability, human baseline
Why it matters: a documented threat
47%
of Indian adults faced or 
knew of an AI voice scam 
(McAfee, 2023)
69%
of Indians can't confidently 
tell a cloned voice from a 
real one
₹80,000
lost in a real Powai, Mumbai 
voice-clone fraud case (Apr 
2024)
Opus
scams arrive as compressed 
WhatsApp voice notes in Hindi 
& Marathi
Almost no published detector is trained or tested on the languages and audio conditions these scams actually 
use.
3

<!-- figure: slide 3, embedded image 1 of 1 -->

<!-- slide: 4 -->

## Slide 4

Problem Statement
Detect AI-generated speech in Hindi, Marathi and one more Indian language under WhatsApp-style 
Opus compression, and report a calibrated, trustworthy confidence, benchmarked against ML 
baselines and human listeners.
Why existing detectors fall short: three gaps that stack up
1
Language Gap
• Major benchmarks 
(ASVspoof, CtrSVDD, SVDD 
2024) are English / Mandarin 
only
• Narrow-language training 
collapses to ~45% EER on 
unseen languages
2
Compression Gap
• RADAR 2026 confirms codec 
compression sharply 
degrades detectors
• Not one Indian language 
appears in its evaluation set
3
Trust Gap
• Confidence scores go 
unchecked once language 
and compression shift
• A confidently wrong answer 
is most dangerous in real 
fraud triage
4

<!-- figure: slide 4, embedded image 1 of 1 -->

<!-- slide: 5 -->

## Slide 5

Aim and Research Questions
AIM
Develop a robust, calibrated, multilingual AI voice deepfake detection system for 
Indian languages, and quantify how far its answers can be trusted.
Five research questions anchor the project. Every method and result maps back to one of them.
RQ1
How much does WhatsApp-style Opus compression degrade detection, relative to clean audio?
RQ2
Does multilingual training beat an English-only baseline on Indian-language and compressed 
audio?
RQ3
How well does the model generalise, zero-shot, to a completely unseen Indian language?
RQ4
Does compression hurt calibration too, making the model confidently wrong instead of 
uncertain?
RQ5
How do the model's accuracy and confidence compare to human listeners on the same clips?
5

<!-- figure: slide 5, embedded image 1 of 1 -->

<!-- slide: 6 -->

## Slide 6

Objectives
O1
Dataset
Curate labelled real + 
AI speech across 3 
Indian languages
O2
Compression
Simulate WhatsApp-
style Opus delivery; 
evaluate under it
O3
Benchmarking
XLS-R + AASIST vs LFCC-
GMM, RawNet2, 
English-only
O4
Generalisation
Cross-lingual and cross-
condition transfer 
studies
O5
Calibration
Measure and improve 
ECE, Brier score and 
reliability curves
O6
Human Baseline
~20-30 volunteers; 
forced-choice + 
confidence rating (RQ5)
O7
Live Demo
Calibrated confidence + 
reliability flag, end to 
end
O8
Open Release
Dataset, code and 
benchmark tables 
published openly
Both add-on modules stay small. Calibration reuses predictions the model already makes, and the human study is a one-time listening test.
6

<!-- figure: slide 6, embedded image 1 of 1 -->

<!-- slide: 7 -->

## Slide 7

Literature Review: Six Research Themes
17 peer reviewed and preprint sources, grouped by what each line of work contributes.
Foundational Architectures
• AASIST (Jung et al., ICASSP 2022): 
~1-5M parameter lightweight 
model
• XLS-R (Babu et al., 2021): 128 
languages, ~436k hrs pretraining
Multilingual Benchmarks
• CtrSVDD / SVDD 2024: mostly 
English and Mandarin
• SVDF-20: ~45% EER on unseen 
languages
Compression Robustness
• RADAR Challenge 2026: codecs, 
noise and reverb degrade detectors
• Covers six languages, none of them 
Indian
Indic-Language Research
• SATYAM / Indic-CodecFake (ACL 
2026): codec-synthesis benchmark
• IndicSynth (ACL 2025): 4,000 hours, 
12 languages
Calibration & Reliability
• Pascu et al. (Interspeech 2024): 
calibrated SSL detection
• Uses temperature scaling and 
entropy-based uncertainty
Human Perception
• Müller et al. (2022): humans 72.8%, 
ML 95.5% accuracy
• Eroding Trust (2026); San Segundo 
et al. (2025)
7

<!-- figure: slide 7, embedded image 1 of 1 -->

<!-- slide: 8 -->

## Slide 8

Literature Review: Closest Works vs VaaniQ
Work
Contribution
Limitation
How VaaniQ Differs
SATYAM / Indic-
CodecFake (ACL 2026)
First large-scale Indic 
benchmark for codec-
synthesised speech
Codec synthesis, not transport 
compression; no calibration or 
human baseline
Targets cloning-fraud audio 
under Opus transport 
compression
IndicSynth (ACL 2025)
4,000-hr multilingual synthetic-
speech dataset for Indic ADD
A dataset, not an evaluation 
study; no compression or 
calibration analysis
Reused as a data resource; 
adds the missing evaluations
RADAR Challenge 2026
Detector robustness under 
codec compression, noise, 
reverb
Covers six languages; no 
Indian language included
Brings the compression 
question to Indic audio (RQ1)
Pascu et al. 
(Interspeech 2024)
Calibrated audio deepfake 
detection with self-supervised 
features
No Indian language; 
WhatsApp-style Opus not 
isolated
Extends calibration to Indic + 
compression conditions 
(RQ4)
Müller et al. (2022, 
2026)
Human listeners score around 
71 to 73%, ML detectors above 
94.5%
No Indian stimuli, listeners, or 
compression condition
First Indic + compression 
human-listener baseline 
(RQ5)
Each of these works is strong on its own axis. None combines Indic languages, Opus compression, calibration and a human baseline.
8

<!-- figure: slide 8, embedded image 1 of 1 -->

<!-- slide: 9 -->

## Slide 9

Research Gap and Novelty: Why VaaniQ
Existing Research
✗
English and Mandarin focused
✗
No WhatsApp / Opus condition for 
Indic audio
✗
Confidence scores never calibrated
✗
No human listener baseline
✗
Little or no explainability
VaaniQ
✓
Hindi, Marathi and one more Indian 
language
✓
WhatsApp-style Opus compression 
tested explicitly (RQ1)
✓
Reliability-aware confidence: ECE, Brier, 
reliability flag
✓
Human listener benchmark on the same 
clips (RQ5)
✓
Explainable AI: Grad-CAM and frequency 
band views
✓
One unified, open, reproducible 
benchmark
Each piece exists somewhere in the literature. No published work combines them all. That 
combination is VaaniQ's contribution.
9

<!-- figure: slide 9, embedded image 1 of 1 -->

<!-- slide: 10 -->

## Slide 10

Scope
In Scope
✓
Hindi, Marathi + one additional Indian 
language
✓
Detection, calibration and a human 
baseline on shared stimuli
✓
Explainability suite and a working 
demo application
✓
Open, verified datasets and pretrained 
models only
Out of Scope  (future work)
✗
WhatsApp plugin, call-centre or law-
enforcement deployment
✗
Real-time, production-scale 
infrastructure
✗
Languages beyond the three studied 
here
✗
Large-scale, demographically 
representative human study
The design is deliberately bounded. Every added module is a light layer on infrastructure the project already needs.
10

<!-- figure: slide 10, embedded image 1 of 1 -->

<!-- slide: 11 -->

## Slide 11

Feasibility
Data
• All corpora are open and verified against their 
live repos: Kathbath, IndicVoices-R, Common 
Voice, IndicSynth
• 50-100 curated hours per language fits free 
storage
Technical
• Frozen XLS-R front end runs once; embeddings 
are cached
• Only the small AASIST head needs training; 
minutes on a free GPU or laptop CPU
Compute
• Colab (free T4) for one-time embedding 
extraction; Kaggle (30 GPU-hrs/week) for the 
fraud-scenario supplement
• Storage on Kaggle Datasets + pooled Google 
Drive; demo hosts free on Hugging Face Spaces
Team
• Four members with defined lead roles: model, 
evaluation, data, systems
• Human study bounded to 20-30 volunteers using 
free tooling (Google Forms)
Every expensive step runs exactly once. All iteration happens on cheap, cached embeddings.
11

<!-- figure: slide 11, embedded image 1 of 1 -->

<!-- slide: 12 -->

## Slide 12

Dataset Collection & Verification
Real Audio
• Kathbath, IndicVoices-R, Common Voice (Hindi/Marathi) curated 
subsets
• Consenting team & classmate recordings for phone-mic realism
AI-Generated Audio
• IndicSynth: 4,000 hrs sampled and curated as the bulk fake-audio 
source
• Targeted supplement via Parler-TTS & Coqui XTTS-v2, modelled 
on real fraud patterns
~50-100 curated hours per language. Every clip produced clean and Opus-compressed via ffmpeg.
Verified Dataset & Tooling Inventory  (checked against live repositories, July 2026)
Resource
Type
Coverage
Licence
Kathbath
Real speech
1,684 hrs, 12 Indian languages
CC0 (gated access)
IndicVoices-R
Real speech
1,704 hrs, 22 Indian languages
Research licence 
(gated)
Common Voice v17
Real, crowd-sourced Hindi (hi) and Marathi (mr) configs
CC0
IndicSynth
Synthetic speech
4,000 hrs, 12 Indic languages
CC BY-NC 4.0
Parler-TTS / Coqui XTTS-v2
TTS / voice-cloning 
tools
20 / 17 languages; 6-sec ref cloning
Apache-2.0 / Coqui 
Licence
Wav2Vec2-XLS-R / AASIST
Frozen front end / 
classifier
128 languages pretrain; bundles 
RawNet2 + EER/t-DCF code
Permissive / 
academic use
12

<!-- figure: slide 12, embedded image 1 of 1 -->

<!-- slide: 13 -->

## Slide 13

Technology Stack: End-to-End Pipeline
1 Dataset
Kathbath, IndicVoices-
R, Common Voice, 
IndicSynth
2 Compression
ffmpeg + Opus codec: 
resample, noise, 
clean/compressed 
pairs
3 Embedding
Wav2Vec2-XLS-R, 
frozen; run once, 
cached
4 Detection
AASIST head (~1-5M 
params) on cached 
embeddings
5 Calibration
Temperature scaling, 
ECE, Brier score
6 Explainability
Grad-CAM, frequency 
band, compression-
artifact views
7 Dashboard
React, Node.js, FastAPI 
inference service
Every stage is modular 
and testable on its own, 
built on pretrained 
models (XLS-R, AASIST) 
rather than from scratch.
Inference runs in about 2 seconds per clip on CPU. Only the AASIST head and the calibration 
scalar are trained; everything else is frozen or pretrained.
13

<!-- figure: slide 13, embedded image 1 of 1 -->

<!-- slide: 14 -->

## Slide 14

Technology Stack: Algorithm & Evaluation Design
How the model works
1
Freeze the XLS-R front end (128 languages, 
~436k hrs pretraining); run once and cache 
embeddings
2
Train only the small AASIST head (~1-5M 
parameters); minutes, not hours
3
Fit temperature scaling per language and 
compression condition on a held-out split
4
Explain every verdict: Grad-CAM temporal 
attention, frequency-band importance, 
compression-artifact view
Baselines for honest comparison
• LFCC + GMM, the classic non-deep baseline
• RawNet2, from the official AASIST repo
• English-only XLS-R + AASIST on ASVspoof, the 
RQ2 control
Evaluation metrics
• EER and min-DCF, the field's standard metrics
• Cross-lingual matrix: train on 2 languages, test 
the unseen third
• Cross-condition matrix: clean vs compressed, 
both directions
• ECE, reliability diagrams, Brier score: is the 
confidence honest?
14

<!-- figure: slide 14, embedded image 1 of 1 -->

<!-- slide: 15 -->

## Slide 15

Expected Results
Metric
Target Direction
Why This Target
EER, clean audio
Single-digit %, matching published 
AASIST / XLS-R clean-condition results
AASIST-class models routinely reach low single-
digit EER on clean, in-domain audio
EER, compressed 
audio
Worse than clean, but degrading 
gracefully, not collapsing
RADAR 2026 confirms compression hurts 
detectors; the target is bounded, documented 
decline
EER, unseen language
Meaningfully better than the ~45% 
EER SVDF-20 reports for narrow-
language training
Tests directly whether multilingual training 
(RQ2, RQ3) closes this gap
ECE, after calibration
Lower than pre-calibration, most 
visible under compression & low-
resource languages
Mirrors the calibration pattern Pascu et al. 
(2024) report for self-supervised 
representations
Brier score
Improves alongside ECE, reported per 
language and condition, not just an 
aggregate
A single aggregate score can hide a language- or 
condition-specific calibration failure
Accuracy vs human 
baseline
Exceeds the ~71-73% human range; 
calibrated confidence is the headline, 
not raw accuracy
Prior studies place humans in the low-70s% and 
ML detectors in the mid-90s%
15

<!-- figure: slide 15, embedded image 1 of 1 -->

<!-- slide: 16 -->

## Slide 16

Timeline: Roadmap to Submission
1
Review 1
• Topic finalised
• Literature reviewed
• Datasets & tools 
verified
2
Review 2
• Dataset built, 
baselines reproduced
• 50-70% working 
module 
demonstrated
• Draft paper and 
report
3
Review 3
• Full evaluation, 
calibration & human 
study
• Explainability 
complete
• Final report, poster, 
publication proof
4
Final Submission
• Dissertation 
structured on RQ1-
RQ5
• Open release: 
dataset, code, 
benchmarks
• arXiv preprint 
targeted
Ongoing: weekly logbook maintained; literature re-checked before the paper draft locks in.
16

<!-- figure: slide 16, embedded image 1 of 1 -->

<!-- slide: 17 -->

## Slide 17

Conclusion
✓
One benchmarked system
Cross-lingual detection, compression 
robustness, calibration and a human 
baseline in one system
✓
Trustworthy by design
A calibrated confidence with a reliability 
flag, not an opaque score
✓
Grounded in a real threat
Built around documented AI voice cloning 
fraud in India, delivered over compressed 
WhatsApp audio
✓
Fully open & reproducible
Every dataset and model verified and free; 
results released openly with the code
VaaniQ asks more than whether a model can spot a fake voice. It asks how far that answer can be 
trusted, and how it compares to human ears.
17

<!-- figure: slide 17, embedded image 1 of 1 -->

<!-- slide: 18 -->

## Slide 18

References 
[1]
Jung, J. et al. “AASIST.” ICASSP 2022, arXiv:2110.01200.
[2]
Babu, A. et al. “XLS-R.” arXiv:2111.09296, 2021.
[3]
Zang, Y. et al. “CtrSVDD.” arXiv:2406.02438, 2024.
[4]
Zhang, Y. et al. “SVDD 2024.” IEEE SLT 2024, arXiv:2408.16132.
[5]
“SVDF-20.” OpenReview submission, ICLR 2026 (withdrawn preprint).
[6]
“Zero-Shot to Zero-Lies: Bengali Deepfake Audio.” arXiv:2512.21702, 2025.
[7]
Luong, H.-T. et al. “RADAR Challenge 2026.” APSIPA Grand Challenge, arXiv:2605.09568, 2026.
[8]
Girish et al. “Indic-CodecFake meets SATYAM.” ACL 2026.
[9]
Sharma, D. V., Ekbote, V., Gupta, A. “IndicSynth.” ACL 2025.
[10]
Javed, T. et al. “IndicSUPERB” (includes Kathbath). arXiv:2208.11761, 2022.
18

<!-- figure: slide 18, embedded image 1 of 1 -->

<!-- slide: 19 -->

## Slide 19

References 
[11]
Sankar, A. et al. “IndicVoices-R.” NeurIPS 2024, arXiv:2409.05356.
[12]
AI4Bharat. “Indic Parler-TTS.” huggingface.co/ai4bharat/indic-parler-tts.
[13]
Coqui AI. “XTTS-v2.” huggingface.co/coqui/XTTS-v2.
[14]
Pascu, O. et al. “Towards Generalisable and Calibrated Audio Deepfake Detection with Self-Supervised Representations.” 
Interspeech 2024, arXiv:2309.05384.
[15]
Müller, N. M., Pizzi, K., Williams, J. “Human Perception of Audio Deepfakes.” DDAM Workshop 2022, arXiv:2107.09667.
[16]
Müller, N. M., Choong, W. H. et al. “Eroding Trust in Real Speech.” arXiv:2605.26136, 2026.
[17]
San Segundo, E. et al. “Human Perception of Audio Deepfakes: The Role of Language and Speaking Style.” arXiv:2512.09221, 
2025.
[18]
McAfee Corp. “The Artificial Imposter.” May 2023.
[19]
Hindustan Times / Mumbai Police records, April 2024. Powai, Mumbai voice-cloning fraud case.
19

<!-- figure: slide 19, embedded image 1 of 1 -->
