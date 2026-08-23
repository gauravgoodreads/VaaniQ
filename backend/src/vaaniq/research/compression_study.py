"""Compression robustness study (RQ1 / O2 / ROADMAP-039)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np

from vaaniq.audio.transforms.degrade import resample_waveform, simulate_packet_loss
from vaaniq.config.domains import ResearchConditionsConfig
from vaaniq.core.domain.entities import Waveform
from vaaniq.core.types import Language
from vaaniq.evaluation.metrics.core import classification_report_scores, equal_error_rate
from vaaniq.research.figures import write_csv, write_line_svg
from vaaniq.research.records import ResearchRunRecord
from vaaniq.research.store import ExperimentStore, collect_hardware


def condition_catalog(cfg: ResearchConditionsConfig) -> list[dict[str, Any]]:
    """Named degradation cells for RQ1 (primary Opus 16 kbps plus SHOULD ladder)."""
    cells: list[dict[str, Any]] = [{"name": "clean", "kind": "clean"}]
    for br in cfg.bitrate_ladder_kbps:
        cells.append({"name": f"opus_{br}kbps", "kind": "opus", "bitrate_kbps": br})
    for hz in cfg.resample_hz:
        cells.append({"name": f"resample_{hz}", "kind": "resample", "target_hz": hz})
    for frac in cfg.packet_loss_fractions:
        pct = round(frac * 100)
        cells.append(
            {"name": f"packet_loss_{pct}pct", "kind": "packet_loss", "loss_fraction": frac}
        )
    return cells


def apply_condition(
    wav: Waveform,
    cell: dict[str, Any],
    *,
    rng: np.random.Generator,
) -> Waveform:
    """Apply a non-ffmpeg degradation cell (resample / packet loss).

    Opus bitrate cells are metadata-only here; live Opus uses ``FFmpegOpusCompressor``.
    """
    kind = str(cell["kind"])
    if kind == "resample":
        return resample_waveform(wav, int(cell["target_hz"]))
    if kind == "packet_loss":
        return simulate_packet_loss(wav, loss_fraction=float(cell["loss_fraction"]), rng=rng)
    return wav


def run_compression_suite(
    scores_by_condition: dict[str, tuple[list[float], list[int]]],
    *,
    store: ExperimentStore,
    output_dir: Path,
    seed: int = 42,
    dataset_version: str = "fixtures",
) -> dict[str, Any]:
    """Evaluate provided scores under every named condition (RQ1).

    Args:
        scores_by_condition: ``name -> (scores, labels)``.
        store: Catalogue.
        output_dir: Figures/tables.
        seed: Seed logged on the record.
        dataset_version: Dataset version string.

    Returns:
        Table/figure paths and EER series.
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    rows: list[list[object]] = []
    xs: list[float] = []
    ys: list[float] = []
    for i, (name, (scores, labels)) in enumerate(sorted(scores_by_condition.items())):
        eer = equal_error_rate(scores, labels)
        clf = classification_report_scores(scores, labels)
        rows.append([name, eer, clf["accuracy"], clf["f1"]])
        xs.append(float(i))
        ys.append(eer)
        store.put(
            ResearchRunRecord(
                experiment_id=f"compress_{name}",
                timestamp=store.now_iso(),
                git_sha=store.git_sha(),
                model_version="aasist-v1",
                dataset_version=dataset_version,
                languages=tuple(lang.value for lang in Language),
                compression_settings=name,
                hyperparameters={"seed": str(seed)},
                metrics={"eer": eer, "accuracy": clf["accuracy"], "f1": clf["f1"]},
                calibration_results={},
                hardware=collect_hardware(),
                seed=seed,
                training_duration_sec=0.0,
                rq_ids=("RQ1",),
                notes="compression robustness cell",
            )
        )
    csv_path = write_csv(
        output_dir / "compression_robustness.csv",
        ["condition", "eer", "accuracy", "f1"],
        rows,
    )
    svg_path = write_line_svg(
        output_dir / "compression_degradation.svg",
        xs=xs,
        ys=ys,
        title="EER vs compression / delivery condition",
        xlabel="Condition index (sorted name)",
        ylabel="EER",
        caption="Fig. RQ1. Degradation curve. Primary WhatsApp cell is opus_16kbps (OQ-007).",
    )
    return {"csv": str(csv_path), "svg": str(svg_path), "rows": rows}
