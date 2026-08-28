# Human study (Phase 4)

> RQ5 / O6 / proposal §7.6 / ROADMAP-059.

## Implemented software

- Anonymous volunteer registration (UUID only, REQ-069)
- Balanced HI/MR/TA clip assignment (OQ-011: 36 clips, ≤25 min)
- Real/Fake choice + confidence slider 1–5
- Response timing (`response_ms`)
- CSV/JSON export with PII keys stripped
- Human vs model accuracy, mean confidence, ECE, Brier, McNemar counts (OQ-009)
- UI at `/human-study`
- API: `POST /api/v1/human-study/register`, `POST .../response`, `GET .../export`, `GET .../report`

Protocol YAML: `configs/human_study/protocol.yaml`.

## Not complete (do not mark RQ5 done)

**Status: BLOCKED ON HUMAN DATA.**

Human-study protocol ready; participant data collection pending (**N=0**). There are
no human accuracy, confidence, calibration, or model-versus-human results.

Proposal success floor is **≥12–15 collected responses** on **shared stimuli**
(REQ-123 / ROADMAP-060). CI does not recruit listeners.

Tamil-fluent listeners: recruit if available; otherwise disclose HI/MR listeners on TA clips (OQ-025).

Run the analysis only after real responses exist:

```bash
make analyze-human-study
```
