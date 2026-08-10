# Datasets guide

> Corpus inventory and curation (P2 / ROADMAP-011+). Config stubs:
> `configs/data/*.yaml`.

## Sources (proposal)

| Source | Role | Config |
|--------|------|--------|
| Kathbath | Real Indic speech | `configs/data/kathbath.yaml` |
| IndicVoices-R | Real Indic speech | `configs/data/indicvoices_r.yaml` |
| Common Voice | Real (HI/MR; TA via OQ-003) | `configs/data/common_voice.yaml` |
| IndicSynth | Synthetic fakes | `configs/data/indicsynth.yaml` |
| Team recordings | Phone-mic realism | `configs/data/team_recordings.yaml` |

Languages: Hindi, Marathi, Tamil only. Target ~50–100 curated hours/lang (REQ-034;
exact split → OQ-002).

## Access & licences

Gated Hugging Face datasets require `HF_TOKEN` (see `.env.example`). Fail fast on
licence/config mismatch (REQ-130).

- TODO(ROADMAP-011): document exact HF dataset IDs after first successful download
- TODO(ROADMAP-035 / OQ-035): dual open-release strategy for NC subsets

## Splits

Speaker-disjoint train/val/test manifests only — never on-the-fly (REQ-099).

- TODO(ROADMAP-017): versioned split writer + checksums
- ASSUMPTION: OQ-008 — default ratios 70/15/15 in `configs/train/default.yaml`

## Compression twins

Every curated clip needs clean + Opus WhatsApp-style twin (REQ-035, OQ-028).

- TODO(ROADMAP-021): lock ffmpeg args (blocking OQ-007)
