# VaaniQ configuration tree
#
# Layering for runtime AppConfig (ROADMAP-004):
#   defaults → configs/base.yaml → configs/env/{env}.yaml → VAANIQ_* env → CLI
#
# Experiment / pipeline domain configs (Phase 1 step 9) live under
# data/, audio/, model/, train/, eval/, calibration/ and are loaded by
# typed pydantic models in ``vaaniq.config.domains`` — not merged into
# AppConfig (extra=forbid).
#
# Every numeric default that is not in the proposal is tagged
# ``# ASSUMPTION: OQ-###`` in the YAML and mirrored in code.

## Layout

| Path | Purpose | REQs / ROADMAP |
|------|---------|----------------|
| `base.yaml` | App identity, languages, API, paths | ROADMAP-004 |
| `env/*.yaml` | local / dev / prod overlays | ROADMAP-004, REQ-136 |
| `data/*.yaml` | Corpus adapters | ROADMAP-011+ |
| `audio/*.yaml` | Preprocess + Opus | ROADMAP-020–021, OQ-007 |
| `model/*.yaml` | XLS-R+AASIST + baselines | ROADMAP-025–032 |
| `train/*.yaml` | Train / CV / English-only | ROADMAP-030, 033 |
| `eval/*.yaml` | Eval matrices | ROADMAP-036–041 |
| `calibration/*.yaml` | Temperature + ECE | ROADMAP-043–044 |
