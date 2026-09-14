# VaaniQ viva demo walkthrough

Keep this file open. Demo WAVs: docs/assets/demo/upload_clips/
Backup video: docs/assets/demo/VaaniQ_Examiner_Demo.mp4

## Start the app (2 terminals)

Terminal A - API (this PC uses port 8001):

cd backend
$env:PYTHONPATH="src"
.\.venv\Scripts\python.exe -m uvicorn vaaniq.api.app:create_app --factory --host 127.0.0.1 --port 8001

Terminal B - website:

cd frontend
npm run dev -- --host 127.0.0.1 --port 5173

Open http://127.0.0.1:5173

## Pitch

VaaniQ detects whether a voice clip in Hindi, Marathi, or Tamil is a real human or AI-generated, including after WhatsApp-style Opus compression, and reports calibrated confidence. Tamil is the third language. Telugu is not in this project.

## Data

Real = Kathbath. Fake = IndicSynth. Speaker-disjoint 70/15/15. Test n=584.
Limitation: on V1, source and label are linked (Kathbath ~ real, IndicSynth ~ fake). Say this out loud.

## Pipeline

audio in -> 16 kHz preprocess -> 1024-D acoustic embedding (or frozen XLS-R in paper) -> AASIST-compatible head -> P(fake) vs 0.5 -> temperature calibration -> Whisper transcript + English translation -> spectrogram/explain.

Score: 0 = REAL, 1 = FAKE. Higher P(fake) = more fake.

## Click path

1. Dashboard: 91.61% acc, 6.56% EER, ROC-AUC 0.9729, n=584. XLS-R 92.12% / 6.88% EER / 0.9828.
2. Upload file (not Record). Language match. Human WAV then AI WAV for hi, mr, ta from upload_clips. Show verdict, P(real)/P(fake), transcript, translation, analysis, waveform, spectrogram.
3. History / Inference.
4. Calibration: ECE, Brier, reliability diagram, coverage curve. T fit on validation not test. Live charts may follow this session; paper numbers are in artifacts/final_results_manifest.json.
5. Explainability.
6. Experiments RQ1-RQ4.
7. API documentation: http://127.0.0.1:8001/docs

## RQ results to say

RQ1 Opus: acoustic clean 93.84% -> Opus 89.38%. XLS-R clean 91.44%, Opus 92.81%.
RQ2 English-only transfer fails: 54.8% acc, 76.56% EER, AUC 0.162. Multilingual 91.61% / 6.56% EER.
RQ3 leave-one-language: Hindi 78.83%, Marathi 93.29%, Tamil 93.94%.
RQ4 calibration: ECE 0.0245 -> 0.026 on selected strategy.

## Graphs

ECE: |accuracy - confidence| averaged over confidence bins. Lower = better calibrated.
Brier: mean squared error of probabilities vs 0/1 labels. 0 is perfect. V1 test 0.069.
Reliability diagram: confidence on X, observed accuracy on Y. Diagonal = perfect.
Coverage curve: keep only high-confidence clips, accuracy should rise.
Temperature scaling: logits / T before softmax. T from validation.

## Metrics

Accuracy 91.61% at threshold 0.5. Confusion: 276 real correct, 44 real called fake, 5 fake called real, 259 fake correct.
F1 91.36% on FAKE class.
EER 6.56%: threshold where false accept = false reject.
ROC-AUC 0.9729: ranking of fakes above reals.

## Close

RQ1-RQ4 COMPLETE on bounded V1. Source-label confound. FLEURS n=9 PILOT. Research prototype, not a production scam detector.
If the stack dies, play VaaniQ_Examiner_Demo.mp4.
