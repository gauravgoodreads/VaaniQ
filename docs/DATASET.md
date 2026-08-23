# Dataset (Phase 4)

> O1 / proposal §7.1 / §10. Complements [`DATASETS.md`](DATASETS.md).

## Languages and labels

Hindi (`hi`), Marathi (`mr`), Tamil (`ta`). Real vs fake. Every curated clip is intended to have a clean ↔ Opus twin (OQ-028).

## Explorer

`GET /api/v1/datasets/explorer` and the `/datasets` page report hours and counts via `DatasetStatistics` (REQ-034). Until manifests are ingested, the API uses a **demo pool** (48 synthetic metadata rows). Do not cite demo hours as OQ-002 actuals.

## Sources (proposal §10)

Kathbath, IndicVoices-R, Common Voice (hi/mr), IndicSynth, team recordings, generated clones. Loaders and parsers exist; gated downloads remain operator-side (OQ-003, OQ-024, OQ-035).

## Degradation conditions (RQ1)

Configured in `configs/eval/research_conditions.yaml`:

- Clean
- WhatsApp-style Opus 16 kbps (primary, OQ-007)
- Optional bitrate ladder 8/16/24 kbps (OQ-012)
- Resample round-trip 8 / 16 / 22.05 kHz (OQ-038)
- Packet-loss frame drops (OQ-037)

ffmpeg Opus twins skip in unit tests when the OS blocks spawn.
