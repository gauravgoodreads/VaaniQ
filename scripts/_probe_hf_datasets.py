#!/usr/bin/env python3
"""Probe HF dataset streaming for V2 second-source selection."""
from __future__ import annotations

import os
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

token = os.environ.get("HF_TOKEN")
os.environ["HF_TOKEN"] = token or ""

from datasets import Audio, load_dataset

CANDIDATES = [
    ("ai4bharat/indicvoices_r", "hindi", "audio", "speaker_id"),
    ("ai4bharat/indicvoices_r", "marathi", "audio", "speaker_id"),
    ("ai4bharat/indicvoices_r", "tamil", "audio", "speaker_id"),
    ("ai4bharat/IndicVoices-R", "hindi", "audio", "speaker_id"),
    ("mozilla-foundation/common_voice_17_0", "hi", "audio", "client_id"),
    ("mozilla-foundation/common_voice_17_0", "mr", "audio", "client_id"),
    ("mozilla-foundation/common_voice_17_0", "ta", "audio", "client_id"),
    ("google/fleurs", "hi_in", "audio", "id"),
    ("google/fleurs", "mr_in", "audio", "id"),
    ("google/fleurs", "ta_in", "audio", "id"),
]

for repo, cfg, audio_col, spk in CANDIDATES:
    try:
        ds = load_dataset(repo, cfg, split="train", streaming=True, token=token)
        row = next(iter(ds))
        keys = sorted(row.keys())[:10]
        print(f"OK {repo}::{cfg} keys={keys} spk={row.get(spk)!r}")
    except Exception as exc:
        print(f"FAIL {repo}::{cfg} -> {type(exc).__name__}: {exc}")
