# VaaniQ IEEE Final Package

## What this is
Publishable IEEE-style archival draft for VaaniQ, generated from frozen Round-3 evidence
(`artifacts/final_results_manifest.json`, commit `084bd47…`).

## Files
- `VaaniQ_IEEE_Research_Paper_Publishable.docx` — full IEEE-style paper
- `VaaniQ_IEEE_Research_Paper_Publishable.pdf` — rendered submission copy
- `VaaniQ_manuscript.md` — markdown source of record for the narrative
- `verified_figures/` — figures embedded in the DOCX
- `README.md` — this file

## Honesty status (do not overclaim)
| Item | Status |
|------|--------|
| RQ1–RQ4 | COMPLETE on bounded V1 |
| Benchmark V2 | PARTIAL pilot |
| Generator-disjoint | PENDING (n=0) |
| Faithful RawNet2 | PENDING |

The paper is scoped to machine evaluation. No human-subject experiment or human-comparison
result is part of the submission.

## Regenerate
```bash
cd backend
..\.venv\Scripts\python.exe ..\scripts\build_ieee_final_package.py
```

Also regenerates legacy DOCX via `scripts/generate_ieee_paper_docx.py`.
