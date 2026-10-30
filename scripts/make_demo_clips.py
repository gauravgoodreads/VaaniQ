#!/usr/bin/env python3
"""Pick demo clips (real + fake per language) from the held-out test split.

Clips come only from ``split == "test"`` (speakers never seen in training).
Each candidate is sent to the running API; a clip is kept only when the live
app returns the ground-truth label, so the demo folder shows working examples.
This is a demo selection, not an evaluation — use train_report.json for metrics.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import httpx
import soundfile as sf

ROOT = Path(__file__).resolve().parents[1]
LANG_NAMES = {"hi": "Hindi", "mr": "Marathi", "ta": "Tamil"}


def main() -> None:
    """Select, verify, and write the demo clips plus a README table."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--corpus", type=Path, default=ROOT / "data" / "publication_corpus")
    parser.add_argument("--out", type=Path, default=ROOT / "demo_clips")
    parser.add_argument("--api", default="http://127.0.0.1:8000")
    parser.add_argument("--per-cell", type=int, default=2)
    parser.add_argument("--min-confidence", type=float, default=0.7)
    args = parser.parse_args()

    rows = [
        json.loads(line)
        for line in (args.corpus / "manifest.jsonl").read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    test_rows = [
        r for r in rows if r.get("split") == "test" and r.get("compression_status") == "clean"
    ]
    args.out.mkdir(parents=True, exist_ok=True)
    kept: list[dict[str, object]] = []
    with httpx.Client(base_url=args.api, timeout=180.0) as client:
        for lang in ("hi", "mr", "ta"):
            for label in ("real", "fake"):
                cands = sorted(
                    (r for r in test_rows if r["language"] == lang and r["label"] == label),
                    key=lambda r: str(r["clip_id"]),
                )
                speakers: set[str] = set()
                n = 0
                tried = 0
                for row in cands:
                    if n >= args.per_cell:
                        break
                    # Prefer distinct speakers so the two demo clips are different voices.
                    if str(row["speaker_id"]) in speakers:
                        continue
                    tried += 1
                    data, sr = sf.read(str(args.corpus / str(row["uri"])), dtype="float32")
                    dest = args.out / lang / f"{label}_{n + 1}.wav"
                    dest.parent.mkdir(parents=True, exist_ok=True)
                    sf.write(dest, data, sr, subtype="PCM_16")
                    with dest.open("rb") as fh:
                        res = client.post(
                            "/api/v1/inference",
                            files={"file": (dest.name, fh, "audio/wav")},
                            data={"language": lang},
                        )
                    res.raise_for_status()
                    pred = res.json()
                    ok = pred["label"] == label and float(pred["confidence"]) >= args.min_confidence
                    if not ok:
                        dest.unlink()
                        continue
                    n += 1
                    speakers.add(str(row["speaker_id"]))
                    kept.append(
                        {
                            "file": dest.relative_to(args.out).as_posix(),
                            "language": lang,
                            "truth": label,
                            "predicted": pred["label"],
                            "confidence": round(float(pred["confidence"]), 4),
                            "reliability": pred.get("reliability"),
                            "clip_id": row["clip_id"],
                            "source": row["dataset_source"],
                            "generation_model": row.get("generation_model"),
                            "duration_sec": row["duration_sec"],
                        }
                    )
                print(f"{lang}/{label}: kept {n}/{args.per_cell} after trying {tried} test clips")

    (args.out / "demo_clips.json").write_text(json.dumps(kept, indent=2), encoding="utf-8")
    lines = [
        "# VaaniQ demo clips",
        "",
        "Held-out **test-split** clips (speakers never used in training), each",
        "verified against the live API when generated. Demo selection only —",
        "headline metrics live in `models/checkpoints/xlsr_aasist/train_report.json`.",
        "",
        "| File | Language | Truth | App says | Confidence | Source |",
        "|---|---|---|---|---|---|",
    ]
    for k in kept:
        src = str(k["source"]) + (f" ({k['generation_model']})" if k["generation_model"] else "")
        lines.append(
            f"| `{k['file']}` | {LANG_NAMES[str(k['language'])]} | {k['truth']} | "
            f"{k['predicted']} | {k['confidence']:.0%} | {src} |"
        )
    (args.out / "README.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {len(kept)} clips to {args.out}")


if __name__ == "__main__":
    main()
