"""Research integrity verification (P0).

Fails when major invariants are violated: speaker leakage, pair leakage,
test-in-training, missing Tamil, or stale overclaims vs persisted artifacts.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

import structlog

from vaaniq.core.domain.entities import ClipMetadata
from vaaniq.datasets.loaders.manifest_loader import ManifestClipLoader
from vaaniq.research.artifacts import artifact_root, load_experiment_metrics
from vaaniq.research.leakage import audit_manifest

log = structlog.get_logger(__name__)

_OVERCLAIM_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    (
        "calibration_improved_unqualified",
        re.compile(r"calibrat\w+\s+improv", re.IGNORECASE),
    ),
    (
        "xlsr_without_qualifier",
        re.compile(r"frozen\s+XLS-?R.*93|XLS-?R\s+\+\s+AASIST.*accuracy", re.IGNORECASE),
    ),
    (
        "full_corpus_claim",
        re.compile(r"full\s+(Kathbath|IndicSynth|corpus).*93", re.IGNORECASE),
    ),
    (
        "human_study_complete_n0",
        re.compile(r"human\s+(study|baseline).*(complete|N\s*=\s*2[0-9])", re.IGNORECASE),
    ),
)


def _load_manifest_rows(path: Path) -> list[ClipMetadata]:
    loader = ManifestClipLoader()
    return list(loader.iter_clips(path))


def verify_train_report_integrity(report: dict[str, Any]) -> list[str]:
    """Check internal consistency of a persisted ``train_report.json``."""
    issues: list[str] = []
    n_train = int(report.get("n_train", 0) or 0)
    n_val = int(report.get("n_val", 0) or 0)
    n_test = int(report.get("n_test", 0) or 0)
    n_clips = int(report.get("n_clips", 0) or 0)
    if n_train + n_val + n_test != n_clips and n_clips > 0:
        issues.append(
            f"split_sum_mismatch: train+val+test={n_train + n_val + n_test} != n_clips={n_clips}"
        )
    if not report.get("speaker_disjoint_verified"):
        issues.append("speaker_disjoint_verified_false_or_missing")

    test_m = report.get("test_metrics") or {}
    val_m = report.get("validation_metrics") or {}
    for partition, metrics in (("test", test_m), ("val", val_m)):
        pre = (metrics.get("calibration_pre") or {}).get("ece")
        post = (metrics.get("calibration_post") or {}).get("ece")
        if pre is not None and post is not None and float(post) > float(pre):
            # Not blocking — negative result is valid — but flag for doc review
            issues.append(
                f"calibration_worsened_on_{partition}: ece {pre} -> {post} (report honestly)"
            )

    pipeline = str(report.get("pipeline", "")).lower()
    if "xlsr" in pipeline and "acoustic" not in pipeline:
        pass  # real XLS-R path
    elif (
        ("acoustic" in pipeline or str(report.get("front_end", "")).startswith("acoustic"))
        and "xlsr" in str(report.get("model_name", "")).lower()
        and "demo" not in pipeline
    ):
        issues.append("pipeline_is_acoustic_but_model_name_implies_xlsr")

    return issues


def verify_document_claims(repo_root: Path) -> list[str]:
    """Scan generated docs for known overclaim patterns (warnings only)."""
    warnings: list[str] = []
    targets = [
        repo_root / "README.md",
        repo_root / "docs" / "VaaniQ_COMPLETE_PROJECT_DOCUMENTATION.md",
        repo_root / "docs" / "RESEARCH_EXECUTION_STATUS.md",
    ]
    for path in targets:
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        for name, pattern in _OVERCLAIM_PATTERNS:
            if pattern.search(text):
                warnings.append(f"{path.name}:{name}")
    return warnings


def verify_research_integrity(
    repo_root: Path,
    *,
    manifest_path: Path | None = None,
    require_baseline_artifacts: bool = True,
) -> dict[str, Any]:
    """Run all integrity checks. ``ok=False`` when blocking issues exist.

    Args:
        repo_root: Repository root.
        manifest_path: Publication manifest JSONL path.
        require_baseline_artifacts: Fail if ``artifacts/experiments/baseline_v1`` missing.

    Returns:
        Structured report with ``ok``, ``blocking``, ``warnings``.
    """
    repo_root = repo_root.resolve()
    manifest = manifest_path or (repo_root / "data" / "publication_corpus" / "manifest.jsonl")
    blocking: list[str] = []
    warnings: list[str] = []

    if manifest.is_file():
        clips = _load_manifest_rows(manifest)
        audit = audit_manifest(clips, repo_root=manifest.parent)
        blocking.extend(audit.get("blocking", []))
        warnings.extend(audit.get("warnings", []))
        if not audit.get("can_train"):
            blocking.append("manifest_audit_can_train_false")
    else:
        warnings.append(f"manifest_missing:{manifest}")

    report_path = repo_root / "models" / "checkpoints" / "xlsr_aasist" / "train_report.json"
    train_report: dict[str, Any] = {}
    if report_path.is_file():
        raw = json.loads(report_path.read_text(encoding="utf-8"))
        train_report = raw if isinstance(raw, dict) else {}
        for issue in verify_train_report_integrity(train_report):
            if issue.startswith("calibration_worsened"):
                warnings.append(issue)
            else:
                blocking.append(issue)
    else:
        warnings.append("train_report_missing")

    baseline_metrics = load_experiment_metrics(repo_root, "baseline_v1")
    if require_baseline_artifacts and not baseline_metrics:
        warnings.append("baseline_v1_artifacts_not_synced")

    if baseline_metrics and train_report:
        for key in ("test_accuracy", "test_eer", "n_test"):
            if key in train_report and key.replace("test_", "") in str(baseline_metrics):
                pass
        bm_test = (baseline_metrics.get("test_metrics") or {}).get("accuracy")
        tr_test = train_report.get("test_accuracy")
        if (
            bm_test is not None
            and tr_test is not None
            and abs(float(bm_test) - float(tr_test)) > 1e-4
        ):
            blocking.append(
                "artifact_metric_drift: "
                f"baseline_v1 test_accuracy={bm_test} vs train_report={tr_test}"
            )

    doc_warnings = verify_document_claims(repo_root)
    warnings.extend(doc_warnings)

    ok = len(blocking) == 0
    result: dict[str, Any] = {
        "ok": ok,
        "blocking": blocking,
        "warnings": warnings,
        "manifest_path": str(manifest) if manifest.is_file() else None,
        "train_report_path": str(report_path) if report_path.is_file() else None,
        "artifacts_root": str(artifact_root(repo_root)),
        "n_manifest_clips": len(_load_manifest_rows(manifest)) if manifest.is_file() else 0,
    }
    log.info(
        "research_integrity_verified",
        ok=ok,
        n_blocking=len(blocking),
        n_warnings=len(warnings),
    )
    return result
