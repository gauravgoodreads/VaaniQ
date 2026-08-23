"""Publication-style markdown reports (Phase 4 / REQ-118)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from vaaniq.evaluation.reports.generator import EvalReportGenerator


def _write_report(
    destination: Path,
    *,
    title: str,
    rq: str,
    objective: str,
    proposal: str,
    summary: str,
    tables: dict[str, Any],
    figures: list[str],
    observations: list[str],
    limitations: list[str],
    future_work: list[str],
) -> Path:
    destination = Path(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    fig_lines = [f"- `{p}`" for p in figures] or ["- (none)"]
    obs = [f"- {item}" for item in observations]
    lim = [f"- {item}" for item in limitations]
    fut = [f"- {item}" for item in future_work]
    body = [
        f"# {title}",
        "",
        f"**RQ:** {rq}  ",
        f"**Objective:** {objective}  ",
        f"**Proposal:** {proposal}",
        "",
        "## Summary",
        "",
        summary,
        "",
        "## Tables",
        "",
        "```json",
        json.dumps(tables, indent=2),
        "```",
        "",
        "## Figures",
        "",
        *fig_lines,
        "",
        "## Research observations",
        "",
        *obs,
        "",
        "## Limitations",
        "",
        *lim,
        "",
        "## Future work",
        "",
        *fut,
        "",
    ]
    destination.write_text("\n".join(body), encoding="utf-8")
    return destination


class ResearchReportBundle:
    """Write the seven Phase-4 report types beside an experiment directory."""

    def __init__(self, root: Path) -> None:
        """Bind output root."""
        self._root = Path(root)
        self._root.mkdir(parents=True, exist_ok=True)
        self._eval = EvalReportGenerator()

    def write_all(
        self,
        *,
        experiment_id: str,
        eval_payload: dict[str, Any],
        calibration: dict[str, Any],
        experiments: dict[str, Any],
        dataset: dict[str, Any],
        model: dict[str, Any],
        human: dict[str, Any],
        explain: dict[str, Any],
        figures: list[str],
    ) -> dict[str, Path]:
        """Write every report type. Returns path map."""
        out: dict[str, Path] = {}
        out["evaluation"] = self._eval.write(
            experiment_id,
            self._root / "evaluation_report.md",
            metrics=eval_payload.get("metrics"),
            matrices=eval_payload.get("matrices"),
            slices=eval_payload.get("slices"),
        )
        shared_lim = [
            "Fixture/offline scores unless curated manifests are present.",
            "NumPy AASIST-style head is not clovaai graph-parity (OQ-014).",
        ]
        out["calibration"] = _write_report(
            self._root / "calibration_report.md",
            title="Calibration Report",
            rq="RQ4",
            objective="O5",
            proposal="§7.5",
            summary="Temperature scaling vs raw ECE/Brier on the logged cells.",
            tables=calibration,
            figures=figures,
            observations=["Per-language and per-condition T follow OQ-031."],
            limitations=shared_lim,
            future_work=["Fit T on real val splits only (OQ-032)."],
        )
        out["experiment"] = _write_report(
            self._root / "experiment_report.md",
            title="Experiment Report",
            rq="RQ1-RQ5",
            objective="O3-O4",
            proposal="§7.4-7.5",
            summary="Catalogue of research runs with seeds, git SHA, and metrics.",
            tables=experiments,
            figures=figures,
            observations=["Each run stores hardware and hyperparameters."],
            limitations=shared_lim,
            future_work=["Re-run on curated hours after HF access."],
        )
        out["dataset"] = _write_report(
            self._root / "dataset_report.md",
            title="Dataset Report",
            rq="O1",
            objective="O1",
            proposal="§7.1 / §10",
            summary="Hours/counts by language and label (REQ-034 / OQ-002).",
            tables=dataset,
            figures=[],
            observations=["Languages are hi/mr/ta only (REQ-139)."],
            limitations=["Real gated downloads remain operator-side."],
            future_work=["Publish licence matrix after OQ-035 resolution."],
        )
        out["model"] = _write_report(
            self._root / "model_report.md",
            title="Model Report",
            rq="RQ2",
            objective="O3",
            proposal="§7.3 / §8",
            summary="XLS-R frozen + AASIST head vs LFCC-GMM, RawNet2, English-only.",
            tables=model,
            figures=figures,
            observations=["English-only control uses ASVspoof 2019 LA (OQ-015)."],
            limitations=shared_lim,
            future_work=["Swap NumPy head for clovaai/aasist on GPU."],
        )
        out["human"] = _write_report(
            self._root / "human_study_report.md",
            title="Human Study Report",
            rq="RQ5",
            objective="O6",
            proposal="§7.6",
            summary="Software protocol, export, and human-vs-model statistics.",
            tables=human,
            figures=[],
            observations=["Anonymous IDs only (REQ-069). Clip count from OQ-011."],
            limitations=["N>=12-15 responses not collected in CI (ROADMAP-060)."],
            future_work=["Recruit TA-fluent listeners if available (OQ-025)."],
        )
        out["explainability"] = _write_report(
            self._root / "explainability_report.md",
            title="Explainability Report",
            rq="RQ1/RQ4",
            objective="O7",
            proposal="§7.7",
            summary="Grad-CAM, bands, spectrogram, compression artifacts, error explorer.",
            tables=explain,
            figures=figures,
            observations=["Spectrogram-aligned Grad-CAM proxy (OQ-034)."],
            limitations=["Not a full AASIST graph CAM."],
            future_work=["GPU Grad-CAM on the clovaai graph."],
        )
        return out
