# VaaniQ Audio Preprocessing Complete Technical Record

## Purpose and evidence boundary

This document records the preprocessing actually implemented and used by VaaniQ for corpus construction, training, evaluation, uploaded-file inference, and live microphone inference. It separates the one-time corpus preparation operations from the shared runtime operations. The stored publication audio is already normalized 16 kHz mono FLAC, but training and inference still apply the shared runtime preprocessor before feature extraction.

The submitted machine study covers Hindi (`hi`), Marathi (`mr`), and Tamil (`ta`). Labels use `0 = REAL` and `1 = FAKE`. A larger `score_fake` means stronger fake evidence. The default decision threshold is `0.5`.

## End-to-end preprocessing map

```text
Kathbath real / IndicSynth fake source audio
  -> streamed source-row selection with seed 42
  -> decode to NumPy float32
  -> downmix channels by arithmetic mean
  -> deterministic linear-interpolation resampling to 16,000 Hz
  -> keep at most the first 12 seconds (192,000 samples)
  -> peak-normalize to 0.95
  -> store lossless FLAC
  -> calculate file SHA-256 and persist metadata
  -> deterministic speaker-disjoint train/validation/test assignment
  -> create paired 16 kbps Opus validation/test twins
  -> upload validation and runtime decoding
  -> shared silence trim, duration bound, and peak normalization
  -> acoustic 1,024-D, frozen XLS-R, or LFCC feature path
  -> classifier logits
  -> validation-selected temperature calibration
  -> REAL/FAKE probability and verdict
```

## 1. Dataset sources and bounded selection

The publication subset is constructed by `scripts/prepare_publication_corpus.py`.

| Class | Dataset | Repository | Per-language count | Total |
|---|---|---|---:|---:|
| REAL | Kathbath | `ai4bharat/Kathbath` | 300 | 900 |
| FAKE | IndicSynth | `vdivyasharma/IndicSynth` | 300 | 900 |

Each language contributes 300 real and 300 fake clean clips. Dataset rows are accessed in streaming mode and shuffled with seed `42` and buffer size `1,000` before collection. The resulting clean subset contains 1,800 clips and 3.1506 hours. This is a bounded subset, not a claim to have processed all upstream data.

The source mappings are:

- Hindi: Kathbath configuration `hindi`, IndicSynth configuration `Hindi`.
- Marathi: Kathbath configuration `marathi`, IndicSynth configuration `Marathi`.
- Tamil: Kathbath configuration `tamil`, IndicSynth configuration `Tamil`.
- Kathbath audio column: `audio_filepath`.
- IndicSynth audio column: `audio`.
- Kathbath speaker field: `speaker_id`.
- IndicSynth speaker field: `Target Speaker ID`.
- IndicSynth model field: `Generative Model`.
- Gender fields are retained when available.

## 2. Source decoding

Corpus construction obtains the encoded byte field from each streamed dataset record and decodes it with `soundfile` using:

```python
sf.read(BytesIO(audio_bytes), dtype="float32", always_2d=False)
```

The decoded samples are immediately represented as NumPy `float32`, and the decoder-provided source sample rate is retained for resampling. Empty byte payloads, missing mappings, invalid shapes, decode failures, and malformed metadata are rejected. Collection continues past rejected source rows and requires the requested count for each source-language cell before succeeding.

## 3. Channel normalization

Both corpus and runtime processing use arithmetic channel averaging:

```text
x_mono[t] = (1 / C) * sum(x[t, c] for c = 1..C)
```

One-dimensional input is retained. Conventional two-dimensional `(samples, channels)` input is averaged across the channel axis. Other array ranks are rejected. The stored and model-facing waveform is mono.

## 4. Sample-rate normalization

The target sample rate is 16,000 Hz. When source and target rates differ, the implemented resampler uses one-dimensional linear interpolation. Its output length is:

```text
N_out = max(1, round(N_in * 16000 / source_rate))
```

The implementation creates equally spaced normalized source and target coordinates with the endpoint excluded and applies `numpy.interp`. Output is cast back to `float32`. If the source rate already equals 16 kHz, samples pass through unchanged.

This method is deterministic and dependency-light. It is not a band-limited or polyphase resampler, so anti-aliasing quality is a documented limitation. Replacing it with `soxr`, `resampy`, or a polyphase implementation would require a new preprocessing fingerprint and new frozen results.

## 5. Corpus duration handling

Corpus preparation retains at most the first 12 seconds:

```text
N_max = 16000 * 12 = 192000 samples
x = x[0:N_max]
```

The source clip is rejected if it becomes empty or has fewer than 16,000 samples, meaning less than one second, after conversion. The first 12 seconds are retained rather than a random or speech-centered crop. This ensures determinism but can bias the retained content toward the start of each recording.

The shared runtime configuration has a wider maximum of 120 seconds and validates a minimum post-transform duration of 0.5 seconds. For the prepared publication files, the 12-second corpus limit is therefore the effective maximum.

## 6. Peak-amplitude normalization

For a non-silent waveform, preprocessing calculates:

```text
p = max(abs(x))
scale = 0.95 / p
x_normalized = float32(x * scale)
```

The target absolute peak is `0.95`, leaving headroom below full scale. A perfectly silent signal is not divided and remains unchanged. Peak normalization is run during corpus construction and again after runtime trimming. The second pass is necessary because silence trimming can change the retained signal interval and because arbitrary uploads were not prepared by the corpus script.

Peak normalization is not RMS normalization and is not LUFS loudness normalization. It equalizes the maximum sample magnitude, not perceived loudness, and may amplify background noise in very quiet recordings.

## 7. Lossless storage and checksums

Prepared clean audio is stored as FLAC at 16 kHz. FLAC is lossless, so no additional lossy codec is introduced into the clean condition. Paths follow:

```text
audio/<language>/<label>/<clip_id>.flac
```

After writing, the pipeline calculates SHA-256 over the actual FLAC file bytes. The checksum is stored in the manifest and later validated by research-integrity checks. This detects missing, replaced, or corrupted files.

## 8. Clip identifiers and manifest fields

The clean clip identity string is:

```text
<source>:<language>:<normalized-speaker-id>:<stream-row-index>
```

The first 16 hexadecimal characters of its SHA-256 form the unique suffix. A complete identifier resembles `hi-fake-001e561f224bb2cc`.

Every record persists:

- `clip_id`;
- `language`;
- `label`;
- `compression_status`;
- `sample_rate_hz`;
- `duration_sec`;
- `split`;
- `dataset_source` and normalized `source`;
- `speaker_id`;
- `attack_type` for fake speech;
- `generation_model` when available;
- `gender` when available;
- `checksum_sha256`;
- relative audio `uri`;
- `pair_id` for clean/compressed evaluation pairs;
- compressed file size for codec twins.

Labels are derived from the selected source cell, not inferred from filenames. Real clips have a null attack type. IndicSynth clips are recorded as `voice_clone` with their source generation model when supplied.

## 9. Speaker-disjoint train, validation, and test split

Splits are assigned deterministically at speaker level:

```text
digest = SHA256("42:" + speaker_id)
bucket = integer(first four digest bytes, big-endian) mod 10000

train      if bucket < 7000
validation if 7000 <= bucket < 8500
test       if bucket >= 8500
```

This implements nominal 70/15/15 partitions without clip-level random leakage. Persisted clean counts are:

| Split | Clean clips | Unique speakers |
|---|---:|---:|
| Train | 1,254 | 178 |
| Validation | 254 | 45 |
| Test | 292 | 44 |

Training reconstructs the speaker sets and terminates if any train/validation, train/test, or validation/test intersection is non-empty. Test rows never participate in fitting, checkpoint selection, temperature fitting, or calibration-strategy selection.

The split algorithm hashes the normalized speaker ID. If two different datasets reuse the same numeric speaker ID, they are conservatively forced into the same split rather than allowed to cross splits.

## 10. WhatsApp-style Opus construction

Every clean validation and test clip receives a paired codec twin. There are 254 validation and 292 test clean clips, so 546 compressed twins are added:

```text
1800 clean + 546 Opus twins = 2346 manifest records
```

The corpus augmentation invokes FFmpeg to encode with `libopus`, 16 kbps, and variable bitrate enabled. It then decodes back to 16 kHz mono FLAC for model input. The reusable compressor additionally fixes the Opus application profile to `voip` and stores compression metadata.

| Codec setting | Primary value |
|---|---|
| Encoder | FFmpeg `libopus` |
| Bitrate | 16 kbps |
| Variable bitrate | Enabled during corpus augmentation |
| Application | `voip` in reusable compressor |
| Channels | 1 |
| Sample rate | 16 kHz |
| Encoded container | Ogg/Opus |
| Classifier input | Decoded float32 PCM/FLAC |
| Manifest condition | `opus_whatsapp_sim` |

The twin inherits the original language, label, speaker, and split. The shared `pair_id` supports paired clean-versus-compressed analysis. The compressed file receives its own identifier, URI, file size, and SHA-256.

The default configuration disables additive noise and disables the optional 8/16/24 kbps bitrate ladder. The primary reported condition is a controlled WhatsApp-style codec simulation. It is not audio captured after transport through the WhatsApp application or network.

## 11. Upload validation before decoding

The upload validator checks the encoded payload before any feature work:

- size must be greater than zero and no larger than 25 MiB by default;
- declared byte count must equal the in-memory payload length;
- MIME must be WAV, Ogg, Opus, FLAC, MPEG audio, or `application/octet-stream`;
- magic bytes must identify RIFF/WAV, Ogg, FLAC, ID3-tagged MP3, or MP3 frame sync.

Renaming an arbitrary file to `.wav` is not sufficient. Invalid content receives a typed validation error and does not reach the model.

## 12. Runtime audio decoding

The primary runtime loader is `soundfile/libsndfile`. It calls `sf.read(..., always_2d=True, dtype="float32")`, then averages channels to mono.

If the primary loader cannot decode the format, the FFmpeg fallback converts the input to:

```text
1 channel, 16,000 Hz, float32 little-endian PCM
```

The raw PCM bytes are loaded into a copied NumPy `float32` array. Missing FFmpeg, failed subprocess execution, or missing decoded output causes an audio-decode error instead of a silent fallback to fabricated samples.

## 13. Shared runtime waveform operations

`DefaultPreprocessor` is shared by training, research evaluation, and file inference. Defaults are declared in `configs/audio/preprocessing.yaml`:

| Parameter | Value |
|---|---|
| `sample_rate_hz` | 16,000 |
| `mono` | true |
| `trim_silence` | true |
| `normalize_peak` | true |
| `target_peak` | 0.95 |
| `min_duration_sec` | 0.5 |
| `max_duration_sec` | 120 |
| Numeric dtype | `float32` |

The exact runtime order is:

1. Convert to mono.
2. Resample to 16 kHz.
3. Trim leading and trailing silence.
4. Truncate to the configured maximum duration.
5. Peak-normalize to 0.95.
6. Reject output below the configured minimum duration.

For publication-corpus files, mono conversion, resampling, and 120-second truncation are normally no-ops because construction already produced 16 kHz mono files of at most 12 seconds. Silence trimming and final peak normalization still execute.

## 14. Silence trimming in minute detail

Silence trimming uses non-overlapping 20 ms frames. At 16 kHz:

```text
frame_length = int(16000 * 20 / 1000) = 320 samples
```

The waveform is zero-padded only for the purpose of forming a complete final analysis frame. For each frame `i`, RMS is:

```text
rms[i] = sqrt(mean(frame[i] ** 2))
```

A frame is active when `rms[i] >= 0.01`. The output begins at the first active frame boundary and ends after the last active frame, capped at the original waveform length. Interior pauses are retained; only leading and trailing inactive frames are removed.

If every frame is below 0.01, the function returns the original waveform rather than an empty array. Downstream near-silence handling and duration validation can then make an explicit decision. The threshold is absolute after float decoding and before the final peak-normalization pass.

## 15. Acoustic 1,024-dimensional feature vector

The acoustic baseline converts one preprocessed clip to one L2-normalized vector in `backend/src/vaaniq/features/acoustic.py`.

### 15.1 Time-domain entries

| Vector indices | Feature |
|---|---|
| 0 | Mean sample value |
| 1 | Sample standard deviation |
| 2 | Maximum sample |
| 3 | Minimum sample |
| 4 | Mean absolute sample |
| 5 | Mean squared sample energy |
| 6 | Mean sign-bit change rate |
| 7 | Standard deviation of 20 ms frame energies |
| 8 | Mean 20 ms frame energy |
| 9 | 90th percentile of 20 ms frame energy |

Short-time energy entries are calculated only when at least four complete 20 ms blocks exist. Any incomplete tail is excluded from that block reshape.

### 15.2 Spectral entries

The spectral analysis uses at most the first 2,048 samples, about 128 ms at 16 kHz:

```text
n_fft = min(2048, number_of_samples)
spectrum = abs(rFFT(first_n_fft_samples * Hann(n_fft)))
spectrum_normalized = spectrum / (max(spectrum) + 1e-8)
```

Up to the first 512 normalized magnitude bins are stored at indices 16-527. Spectral centroid, bandwidth, and 85% roll-off are calculated from the unnormalized magnitude spectrum and stored at indices 10-12 after division by 8,000 Hz.

### 15.3 Log-band entries

The spectrum is divided into 64 equally spaced index bands. For each band:

```text
feature = log(1 + mean(band_magnitude))
```

These occupy indices 528-591. The source calls them mel-like, but the edges are linearly spaced in FFT-bin index; they are not a true mel filterbank.

### 15.4 Roughness entries

For sufficiently long spectra, first differences over the first 256 magnitude bins provide:

- index 656: mean absolute spectral difference;
- index 657: standard deviation of spectral differences;
- index 658: fraction of interior bins that are strict local peaks.

Unused vector positions remain zero. Finally:

```text
embedding = vector / (L2_norm(vector) + 1e-8)
```

The output dtype is `float32` and the default dimension is exactly 1,024. The same function is used by training, uploaded-file inference, and live streaming, avoiding train/serve feature skew for this path.

## 16. Frozen XLS-R feature path

The alternative main representation uses `facebook/wav2vec2-xls-r-300m`:

1. Pass the preprocessed sample array and declared sample rate to Hugging Face `AutoFeatureExtractor`.
2. Load `Wav2Vec2Model` lazily.
3. Switch the model to evaluation mode.
4. Set every model parameter to `requires_grad_(False)`.
5. Run inference inside `torch.inference_mode()`.
6. Read the last hidden-state tensor.
7. Mean-pool across time because configuration sets `pooling: mean` and `transformer_layer: last`.
8. Squeeze the batch dimension and convert to NumPy `float32`.

The front end remains frozen; it is not fine-tuned. Configuration also records a 4-second window and 2-second hop for model-level windowing, although the extractor shown here accepts each preprocessed waveform and pools its returned sequence.

Embeddings may be cached. The key hashes:

```text
clip_id | facebook/wav2vec2-xls-r-300m | default_preproc_v1
```

Cache reads validate vector shape, dtype, finite values, metadata, and checksum. A changed clip, model identifier, or preprocessing fingerprint therefore produces a different key. Cached arrays and downloaded model weights remain local and are not committed.

## 17. LFCC-GMM baseline preprocessing

The classical baseline uses the same runtime-preprocessed waveform and applies:

- zero padding when the clip has fewer than 512 samples;
- frame length 400 samples, equal to 25 ms at 16 kHz;
- hop length 160 samples, equal to 10 ms;
- Hann windowing;
- 512-point real FFT magnitude;
- up to `2 * 60 = 120` triangular filters spaced linearly across FFT bins;
- energy floor `1e-10`;
- natural logarithm;
- DCT-II retaining 60 coefficients;
- mean pooling over time to one 60-dimensional vector.

Separate diagonal-covariance GMMs model real and fake vectors. Configuration declares 512 components, but the compact NumPy implementation caps the practical count at eight. Each model runs five expectation-maximization iterations and floors variance at `1e-4`. The final two logits are real and fake log-likelihoods.

This is a transparent LFCC-GMM baseline, not a claim of a fully tuned 512-component external reproduction.

## 18. Training-only feature augmentation

After manifest filtering and feature extraction, training uses only rows whose split is `train` and whose language is in the selected training-language set. Validation and test matrices are separate.

For each NumPy classifier epoch, zero-mean Gaussian noise with the command-configured standard deviation is added to training embeddings only:

```text
X_aug = X_train + Normal(mean=0, std=noise_std)
```

The random generator uses seed 42 unless overridden. Validation features are not augmented. The retained checkpoint has the highest validation accuracy, with lower validation EER as the tie-breaker.

## 19. Temperature calibration preprocessing

Calibration happens after classifier logits and does not change waveform samples or embeddings.

1. Produce uncalibrated validation and test logits.
2. Fit a global temperature on validation logits.
3. Fit per-language/per-condition temperatures on validation cells where data exists.
4. Calculate validation expected calibration error for both strategies.
5. Select the strategy with lower validation ECE.
6. Freeze the selected scaler.
7. Apply it to held-out test logits without refitting.

ECE uses predicted-class confidence and correctness. Brier score uses the fake-class probability and binary label. The frozen result records pre-calibration held-out ECE `0.0245` and post-calibration ECE `0.026`. Because the post value is slightly worse, the project reports the result without claiming calibration improved held-out ECE.

## 20. Live microphone path

The browser recorder supplies microphone audio to the live endpoint. The server operates at 16 kHz mono and divides PCM into fixed sliding windows. Near-silent or short impulsive windows are skipped before acoustic classification.

The application also contains a disclosed microphone-source adjustment because the bounded benchmark uses Kathbath and IndicSynth source conditions rather than laptop microphones. This adjustment uses speech-energy dynamics and recording-source metadata to reduce known studio-versus-microphone domain mismatch. It is a product heuristic for the live demonstration. It is not included in the frozen benchmark predictions and is not human-validation evidence.

## 21. Train, evaluation, and inference parity

The following components are intentionally shared:

- `DefaultPreprocessor` for offline training/evaluation and uploaded-file inference;
- `acoustic_embedding` for offline acoustic training, file inference, and live inference;
- fixed `Label.REAL, Label.FAKE` logit ordering;
- a common positive-class score contract;
- persisted temperature parameters selected on validation data;
- the manifest condition strings `clean` and `opus_whatsapp_sim`.

This sharing prevents accidental differences such as training at 16 kHz but serving at 44.1 kHz, reversing score polarity, or applying a normalizer only at inference.

## 22. Reproduction commands

Use an authorized Hugging Face token for gated Kathbath access. Do not commit the token.

```powershell
cd backend
uv pip install -e ".[dev,data,ml]"
cd ..
$env:HF_TOKEN = "<authorized-token>"

python scripts/prepare_publication_corpus.py `
  --seed 42 `
  --sample-rate 16000 `
  --max-duration-sec 12 `
  --clips-per-source-language 300

python scripts/prepare_publication_corpus.py --augment-existing-opus

python scripts/train_demo_detector.py `
  --corpus data/publication_corpus `
  --front-end acoustic

python scripts/verify_research_integrity.py
```

Replace `--front-end acoustic` with `--front-end xlsr` for the frozen XLS-R path. Dataset audio, embeddings, model weights, checkpoints, local uploads, and secret environment files are ignored by Git. The code, configuration, frozen result manifest, figures, documents, and validation report are versioned.

## 23. Verification coverage and invariants

The preprocessing contract is guarded by automated checks for:

- mono conversion and invalid-rank rejection;
- deterministic resampling and target sample count;
- silence trimming and all-silent behavior;
- duration truncation and minimum-duration rejection;
- peak normalization and silent no-op;
- upload MIME, size, and magic-byte validation;
- primary and fallback decoding;
- Opus configuration and clean/compressed pairing;
- acoustic and LFCC feature dimensions;
- XLS-R frozen-mode enforcement and embedding-cache validation;
- speaker-overlap rejection;
- label and score orientation;
- manifest checksums, language/class/condition values, and reported metrics.

The frozen research manifest contains 2,346 records and zero blocking integrity findings. Generated result figures and final documents consume the versioned result manifest instead of independently typed metric values.

## 24. Known preprocessing limitations

1. Linear interpolation is reproducible but lacks the anti-alias filtering of a high-quality band-limited resampler.
2. Peak normalization is not perceptual loudness normalization and can amplify low-level noise.
3. A fixed RMS silence threshold can react differently to device noise and recording gain.
4. Corpus truncation always uses the first 12 seconds instead of a speech-centered crop.
5. The acoustic vector analyzes only an initial short segment for its direct FFT bins.
6. The 64 acoustic log bands are linearly spaced rather than true mel filters.
7. The compact LFCC implementation caps GMM mixtures at eight despite the larger configuration value.
8. The Benchmark V1 real/fake labels are associated with Kathbath/IndicSynth sources, creating a known source-class confound.
9. Opus evaluation simulates codec processing but not messaging-network transport, packet loss, automatic gain control, or application transcoding.
10. Live microphone correction is outside the formal benchmark and must remain disclosed as a heuristic.

These limits constrain generalization; they do not change the recorded implementation or invalidate reproducibility within the bounded experiment.

## 25. Authoritative implementation files

- `scripts/prepare_publication_corpus.py`: source streaming, conversion, splitting, metadata, and Opus twins.
- `configs/audio/preprocessing.yaml`: shared waveform defaults.
- `configs/audio/compression.yaml`: primary Opus condition.
- `backend/src/vaaniq/audio/transforms/ops.py`: mono, resample, silence, duration, and peak operations.
- `backend/src/vaaniq/audio/transforms/preprocessor.py`: ordered preprocessing and duration validation.
- `backend/src/vaaniq/audio/transforms/validator.py`: upload validation.
- `backend/src/vaaniq/audio/io/`: primary and fallback decoding.
- `backend/src/vaaniq/features/acoustic.py`: 1,024-dimensional acoustic vector.
- `backend/src/vaaniq/features/xlsr/extractor.py`: frozen XLS-R pooling and caching.
- `backend/src/vaaniq/models/baselines/lfcc_gmm/classifier.py`: LFCC and diagonal GMM baseline.
- `scripts/train_demo_detector.py`: split enforcement, feature training, checkpoint selection, and calibration.
- `artifacts/final_results_manifest.json`: frozen score contract and reported results.
- `scripts/verify_research_integrity.py`: final evidence verification.
