# Human Study Report

**RQ:** RQ5  
**Objective:** O6  
**Proposal:** §7.6 / ROADMAP-059

## Summary

Complete listening-test **protocol and software** are implemented. **Participant data have not been collected (N=0).** No human accuracy, confidence, ECE, Brier, or McNemar-versus-model result is claimed. Fabricating listener outcomes would be research misconduct.

## Protocol (implemented)

| Element | Spec |
|---------|------|
| Clips / session | 36 (`configs/human_study/protocol.yaml`) |
| Session cap | ≤25 minutes |
| Confidence | 1–5 |
| Languages | hi, mr, ta |
| Privacy | Anonymous UUID; PII stripped on export |
| UI | `/human-study` |
| API | register / response / export / report |

## Results (actual)

```json
{
  "n_participants": 0,
  "n_responses": 0,
  "status": "BLOCKED_ON_HUMAN_DATA"
}
```

## Literature context (not VaaniQ results)

Müller et al. report ~72.8% human accuracy vs strong ML on ASVspoof-style tasks. Those figures are **background only** and must not be substituted for VaaniQ participants.

## Target for completion

Proposal success floor: ≥12–15 collected responses on shared stimuli (target ~20–30). Recruit Tamil-fluent listeners if available (OQ-025).

```bash
make analyze-human-study
```

Run analysis only after real responses exist.
