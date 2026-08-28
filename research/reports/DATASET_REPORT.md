# Dataset report

Generated: 2026-08-27T17:59:43.353502+00:00
Git: `8f439439a32f6ae9111ffeb5da367f7c7b4eb1d2` dirty=True

## Research corpus (authoritative)

| Language | Hours | Clips | Speakers | Status |
|----------|------:|------:|---------:|--------|
| hi | 0 | 0 | 0 | PENDING |
| mr | 0 | 0 | 0 | PENDING |
| ta | 0 | 0 | 0 | PENDING |
| **total** | **0** | **0** | **0** | **PENDING** |

Audio files under `data/` and `backend/data/`: **121**.
HF token present: **False**.
Gated sources (Kathbath, IndicVoices-R, IndicSynth) were **not downloaded** (REQ-130).

Tamil is the project third language. Tamil **audio bytes are not verified** on disk.
Fixture metadata contains `language=ta` rows; that is not a Tamil corpus.

## Schema fixture only (not a research result)

The six-row mock manifest at `backend/tests/fixtures/datasets/mock_manifest.jsonl`
was inventoried so hours are computed, not invented.

| Language | Fixture clips | Fixture hours |
|----------|--------------:|--------------:|
| hi | 2 | 0.0009722222 |
| mr | 2 | 0.0015277778 |
| ta | 2 | 0.0013888889 |
| total | 6 | 0.0038888889 |

Real/fake fixture counts: real=3 fake=3.
Sources: {'kathbath': 1, 'indicsynth': 1, 'indicvoices_r': 1, 'parler_tts': 1, 'common_voice': 1, 'xtts_v2': 1}.
Attack types: {'none': 3, 'tts': 1, 'tts_fraud_pattern': 1, 'voice_clone_fraud_pattern': 1}.
Compression labels: {'clean': 5, 'opus_whatsapp_sim': 1}.
Sample rates: {16000: 6}.
Duration range (fixture metadata seconds): min=1.0 max=4.0.

Team recordings: **0 clips**. They must remain a small phone-mic supplement when collected.

Do not cite fixture hours as O1 completion.
