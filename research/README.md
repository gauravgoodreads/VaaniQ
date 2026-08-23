# Research artifacts

Phase 6 layout. **Code existing is not a completed experiment.**

```
research/
├── datasets/manifests|metadata|reports
├── experiments/rq1-rq5   (run logs; gitignored bulk)
├── results/              PENDING CSVs until curated-hour runs
├── paper/manuscript      methods draft; Results = NOT RUN
└── reports/              dataset, quality, findings, audit, status
```

Generate inventory and PENDING tables (no fabricated metrics)::

    python -m vaaniq.research.cli --mode execute --repo-root . --root ./research

CI software-path demos (not RQ results)::

    python -m vaaniq.research.cli --mode fixtures --root ./research --seed 42
