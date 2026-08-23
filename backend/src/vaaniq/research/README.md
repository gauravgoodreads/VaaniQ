Research experiment framework. Extends ``training.FileExperimentTracker``
with a searchable catalogue, RQ1-RQ5 runners, SVG/CSV figures, and report bundles.

Phase 6 execution (inventory + quality audit; **does not fabricate metrics**)::

    python -m vaaniq.research.cli --mode execute --repo-root . --root ./research

CI software-path fixtures (not RQ results)::

    python -m vaaniq.research.cli --mode fixtures --root ./research --seed 42
