# Research artifacts

Approved Round 3 research-artifact layout. Current results are frozen in
`../artifacts/final_results_manifest.json`; fixture outputs are never substituted.

```
research/
├── datasets/manifests|metadata|reports
├── experiments/rq1-rq5   (run logs; gitignored bulk)
├── results/              persisted RQ CSV/table sources
├── paper/manuscript      synchronized measured-results manuscript
└── reports/              dataset, quality, findings, audit, status
```

Verify the frozen research artifacts:

    cd backend
    uv run python ../scripts/verify_research_integrity.py

CI software-path demos remain non-citable:

    python -m vaaniq.research.cli --mode fixtures --root ./research --seed 42
