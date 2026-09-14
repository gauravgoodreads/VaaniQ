# Upload these clips during the viva

This folder is only for the live demo with mam. Each filename is the ground truth.
Audio is gitignored, so these WAV copies stay on this PC.

| File | Language | What it is | Expected verdict |
|---|---|---|---|
| 01_Hindi_HUMAN_REAL.wav | Hindi | Kathbath human speaker | real |
| 02_Hindi_AI_FAKE.wav | Hindi | IndicSynth AI voice | fake |
| 03_Marathi_HUMAN_REAL.wav | Marathi | Kathbath human speaker | real |
| 04_Marathi_AI_FAKE.wav | Marathi | IndicSynth AI voice | fake |
| 05_Tamil_HUMAN_REAL.wav | Tamil | Kathbath human speaker | real |
| 06_Tamil_AI_FAKE.wav | Tamil | IndicSynth AI voice | fake |

How to upload

1. Open http://127.0.0.1:5173/upload
2. Click Upload file (not Record voice)
3. Set Language to match the clip
4. Choose the WAV, then Detect
5. Show verdict, P(real), P(fake), transcript, English translation, analysis, waveform, spectrogram

Do not play the AI WAV into the microphone. Upload the file.
To show your own voice: Record voice, speak, Detect. That should be real.
