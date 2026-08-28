#!/usr/bin/env python3
"""Quick FLEURS stream test for Benchmark V2."""
from __future__ import annotations

import os
import sys
import time
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
env_path = _REPO / ".env"
if env_path.is_file():
    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))

from datasets import Audio, load_dataset

token = os.environ.get("HF_TOKEN")
for cfg in ("hi_in", "mr_in", "ta_in"):
    t0 = time.time()
    try:
        ds = load_dataset(
            "google/fleurs",
            cfg,
            split="train",
            streaming=True,
            token=token,
        )
        ds = ds.cast_column("audio", Audio(decode=False))
        row = next(iter(ds))
        audio = row["audio"]
        nbytes = len(audio.get("bytes") or b"")
        print(f"OK {cfg} keys={list(row.keys())[:6]} audio_bytes={nbytes} dt={time.time()-t0:.1f}s")
    except Exception as exc:
        print(f"FAIL {cfg} {type(exc).__name__}: {exc}", file=sys.stderr)
