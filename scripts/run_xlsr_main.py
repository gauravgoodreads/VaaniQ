#!/usr/bin/env python3
"""Run frozen XLS-R main experiment: extract cache, train head, sync artifacts."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]


def _load_dotenv() -> None:
    env_path = _REPO / ".env"
    if not env_path.is_file():
        return
    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--corpus",
        type=Path,
        default=_REPO / "data" / "publication_corpus",
    )
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--epochs", type=int, default=80)
    args = parser.parse_args()
    _load_dotenv()

    backend = _REPO / "backend"
    cache = _REPO / "data" / "embedding_cache" / "xlsr_300m"
    ckpt_dir = _REPO / "models" / "checkpoints" / "xlsr_main"
    ckpt_dir.mkdir(parents=True, exist_ok=True)
    out_npz = ckpt_dir / "aasist-v1.npz"

    py = [sys.executable]
    # Prefer uv run from backend when available
    extract_cmd = [
        "uv",
        "run",
        "python",
        str(_REPO / "scripts" / "extract_xlsr_embeddings.py"),
        "--corpus",
        str(args.corpus),
        "--cache-root",
        str(cache),
    ]
    train_cmd = [
        "uv",
        "run",
        "python",
        str(_REPO / "scripts" / "train_demo_detector.py"),
        "--corpus",
        str(args.corpus),
        "--front-end",
        "xlsr",
        "--embedding-cache",
        str(cache),
        "--seed",
        str(args.seed),
        "--epochs",
        str(args.epochs),
        "--output",
        str(out_npz),
    ]

    cwd = str(backend)
    print("=== XLS-R embedding extraction ===")
    rc = subprocess.call(extract_cmd, cwd=cwd)
    if rc != 0:
        return rc

    print("=== XLS-R head training ===")
    rc = subprocess.call(train_cmd, cwd=cwd)
    if rc != 0:
        return rc

    report_src = ckpt_dir / "train_report.json"
    if not report_src.is_file():
        report_src = _REPO / "models" / "checkpoints" / "xlsr_aasist" / "train_report.json"
    # train_demo_detector writes report next to output
    report_next = out_npz.with_name("train_report.json")
    if report_next.is_file():
        report_src = report_next

    sys.path.insert(0, str(_REPO / "backend" / "src"))
    from vaaniq.research.artifacts import experiment_dir

    dest = experiment_dir(_REPO, "xlsr_main")
    dest.mkdir(parents=True, exist_ok=True)
    if report_src.is_file():
        payload = json.loads(report_src.read_text(encoding="utf-8"))
        (dest / "metrics.json").write_text(
            json.dumps(
                {
                    "experiment_id": "xlsr_main",
                    "front_end": "frozen_xlsr_300m_mean_pool",
                    **payload,
                },
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
        (dest / "config.json").write_text(
            json.dumps(
                {
                    "experiment_id": "xlsr_main",
                    "xlsr_model_id": "facebook/wav2vec2-xls-r-300m",
                    "cache_root": str(cache),
                    "checkpoint": str(out_npz),
                    "seed": args.seed,
                },
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
    print(json.dumps({"status": "complete", "artifact_dir": str(dest)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
