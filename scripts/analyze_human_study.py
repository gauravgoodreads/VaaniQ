#!/usr/bin/env python3
"""Analyze human-study responses when N>0; otherwise emit PENDING artifact."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_REPO / "backend" / "src"))

from vaaniq.human_study.stats import human_vs_model_report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--responses",
        type=Path,
        default=_REPO / "artifacts" / "experiments" / "rq5_human" / "responses.csv",
    )
    parser.add_argument(
        "--model-scores",
        type=Path,
        default=_REPO / "artifacts" / "experiments" / "baseline_v1" / "predictions.csv",
    )
    args = parser.parse_args()

    dest = _REPO / "artifacts" / "experiments" / "rq5_human"
    dest.mkdir(parents=True, exist_ok=True)

    if not args.responses.is_file():
        payload = {
            "experiment_id": "rq5_human",
            "status": "PENDING",
            "n_participants": 0,
            "note": "Human-study protocol ready; participant data collection pending (N=0).",
        }
        (dest / "metrics.json").write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        print(json.dumps(payload, indent=2))
        return 0

    rows: list[dict[str, str]] = []
    with args.responses.open(encoding="utf-8", newline="") as fh:
        rows = list(csv.DictReader(fh))
    if not rows:
        payload = {"experiment_id": "rq5_human", "status": "PENDING", "n_responses": 0}
        (dest / "metrics.json").write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        print(json.dumps(payload, indent=2))
        return 0

    model_map: dict[str, float] = {}
    if args.model_scores.is_file():
        with args.model_scores.open(encoding="utf-8", newline="") as fh:
            for row in csv.DictReader(fh):
                if row.get("split") == "test":
                    model_map[str(row["clip_id"])] = float(row["score_fake"])

    human_pred = [1 if r.get("choice") == "fake" else 0 for r in rows]
    human_conf = [int(r["confidence_1_5"]) for r in rows]
    labels = [1 if r.get("gold_label") == "fake" else 0 for r in rows]
    model_scores = [model_map.get(str(r["clip_id"]), 0.5) for r in rows]

    stats = human_vs_model_report(
        human_pred=human_pred,
        human_conf_1_5=human_conf,
        human_labels=labels,
        model_scores=model_scores,
        model_labels=labels,
    )
    payload = {
        "experiment_id": "rq5_human",
        "status": "COMPLETE",
        "n_responses": len(rows),
        "stats": stats,
    }
    (dest / "metrics.json").write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
