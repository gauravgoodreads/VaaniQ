"""Phase 6 research execution: inventory, audit, PENDING artifacts.

Never writes fabricated EER/ECE/human scores. RQ CSVs are empty of metric
values until a curated corpus and GPU run exist.
"""

from __future__ import annotations

import csv
import json
import os
import shutil
import subprocess
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import structlog

from vaaniq.core.domain.entities import ClipMetadata
from vaaniq.core.types import Label, Language
from vaaniq.datasets.loaders.manifest_loader import ManifestClipLoader
from vaaniq.datasets.stats.statistics import DatasetStatistics
from vaaniq.research.leakage import audit_manifest
from vaaniq.research.store import collect_hardware

log = structlog.get_logger(__name__)

_RQ_METRIC_HEADER = (
    "status",
    "reason",
    "model",
    "language",
    "condition",
    "eer",
    "min_dcf",
    "accuracy",
    "precision",
    "recall",
    "f1",
    "roc_auc",
)


def _now_iso() -> str:
    return datetime.now(UTC).isoformat()


def _ffmpeg_ok() -> bool:
    exe = shutil.which("ffmpeg")
    if not exe:
        return False
    try:
        proc = subprocess.run(
            [exe, "-version"],
            capture_output=True,
            check=False,
            timeout=8,
        )
        return proc.returncode == 0
    except (OSError, subprocess.TimeoutExpired):
        return False


def _count_audio_files(root: Path) -> int:
    if not root.is_dir():
        return 0
    n = 0
    for suffix in ("*.wav", "*.mp3", "*.opus", "*.flac", "*.ogg"):
        n += sum(1 for _ in root.rglob(suffix))
    return n


def inventory_environment(repo_root: Path) -> dict[str, Any]:
    """Probe disk, credentials, and hardware. No downloads."""
    from vaaniq.training.trainer import _git_sha

    sha, dirty = _git_sha()
    data_audio = _count_audio_files(repo_root / "data") + _count_audio_files(
        repo_root / "backend" / "data"
    )
    return {
        "timestamp": _now_iso(),
        "git_sha": sha,
        "git_dirty": dirty,
        "hf_token_present": bool(
            os.environ.get("HF_TOKEN") or os.environ.get("HUGGING_FACE_HUB_TOKEN")
        ),
        "ffmpeg_runnable": _ffmpeg_ok(),
        "audio_files_under_data": data_audio,
        "hardware": collect_hardware(),
    }


def execute_research_phase(
    *,
    repo_root: Path,
    output_root: Path,
    fixture_manifest: Path | None = None,
) -> dict[str, Any]:
    """Write inventory, fixture stats, quality audit, and PENDING RQ tables.

    Args:
        repo_root: Repository root.
        output_root: ``research/`` directory.
        fixture_manifest: Optional schema-fixture JSONL (not a research corpus).

    Returns:
        Summary dict (no fabricated metrics).
    """
    repo_root = Path(repo_root)
    output_root = Path(output_root)
    env = inventory_environment(repo_root)
    manifest = fixture_manifest or (
        repo_root / "backend" / "tests" / "fixtures" / "datasets" / "mock_manifest.jsonl"
    )
    clips = list(ManifestClipLoader().iter_clips(manifest)) if manifest.is_file() else []
    stats = DatasetStatistics.compute(clips)
    audit = audit_manifest(clips, repo_root=repo_root)

    dirs = [
        output_root / "datasets" / "manifests",
        output_root / "datasets" / "metadata",
        output_root / "datasets" / "reports",
        output_root / "experiments" / "rq1",
        output_root / "experiments" / "rq2",
        output_root / "experiments" / "rq3",
        output_root / "experiments" / "rq4",
        output_root / "experiments" / "rq5",
        output_root / "results" / "tables",
        output_root / "results" / "figures",
        output_root / "results" / "raw_metrics",
        output_root / "results" / "experiment_logs",
        output_root / "paper" / "manuscript",
        output_root / "paper" / "figures",
        output_root / "paper" / "tables",
        output_root / "paper" / "references",
        output_root / "reports",
    ]
    for path in dirs:
        path.mkdir(parents=True, exist_ok=True)

    _write_dataset_csvs(output_root, clips, stats, env)
    _write_pending_rq_tables(output_root / "results")
    _write_dataset_report(output_root, clips, stats, audit, env)
    _write_quality_report(output_root, audit, env)
    _write_findings(output_root)
    _write_results_audit(output_root, env, audit)
    _write_execution_status(output_root, repo_root, env, stats, audit, clips)
    _write_methods_paper(output_root, env)
    _write_artifact_inventory(output_root, repo_root, env)
    env_log = output_root / "results" / "experiment_logs" / "environment.json"
    env_log.write_text(json.dumps(env, indent=2), encoding="utf-8")
    log.info(
        "research_execution_inventory_written",
        n_fixture_clips=len(clips),
        audio_files=env["audio_files_under_data"],
        can_train=audit["can_train"],
    )
    return {"environment": env, "audit": audit, "n_fixture_clips": len(clips)}


def _write_dataset_csvs(
    output_root: Path,
    clips: list[ClipMetadata],
    stats: DatasetStatistics,
    env: dict[str, Any],
) -> None:
    stats_path = output_root / "results" / "dataset_statistics.csv"
    with stats_path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.writer(fh)
        writer.writerow(
            [
                "corpus_role",
                "language",
                "n_clips",
                "n_speakers",
                "hours",
                "n_real",
                "n_fake",
                "audio_files_on_disk",
                "status",
            ]
        )
        speakers = {c.speaker_id for c in clips if c.speaker_id}
        for lang in Language:
            lang_clips = [c for c in clips if c.language == lang]
            writer.writerow(
                [
                    "schema_fixture",
                    lang.value,
                    stats.counts_by_language[lang],
                    len({c.speaker_id for c in lang_clips if c.speaker_id}),
                    f"{stats.hours_by_language[lang]:.10f}",
                    sum(1 for c in lang_clips if c.label == Label.REAL),
                    sum(1 for c in lang_clips if c.label == Label.FAKE),
                    0,
                    "FIXTURE_METADATA_ONLY",
                ]
            )
            writer.writerow(
                [
                    "research_corpus",
                    lang.value,
                    0,
                    0,
                    "0.0000000000",
                    0,
                    0,
                    env["audio_files_under_data"],
                    "PENDING",
                ]
            )
        writer.writerow(
            [
                "schema_fixture",
                "all",
                stats.total_clips,
                len(speakers),
                f"{stats.total_hours:.10f}",
                stats.counts_by_label[Label.REAL],
                stats.counts_by_label[Label.FAKE],
                0,
                "FIXTURE_METADATA_ONLY",
            ]
        )

    man_path = output_root / "datasets" / "manifests" / "dataset_manifest_v1.csv"
    with man_path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.writer(fh)
        writer.writerow(
            [
                "sample_id",
                "source_id",
                "speaker_id",
                "language",
                "label",
                "dataset",
                "attack_type",
                "generation_model",
                "compression",
                "bitrate",
                "sample_rate",
                "duration",
                "split",
                "checksum",
                "corpus_role",
                "audio_bytes_present",
            ]
        )
        for clip in clips:
            writer.writerow(
                [
                    clip.clip_id,
                    clip.source.value,
                    clip.speaker_id or "",
                    clip.language.value,
                    clip.label.value,
                    clip.dataset_source,
                    clip.attack_type.value if clip.attack_type else "",
                    clip.generation_model or "",
                    clip.compression_status.value,
                    "",
                    clip.sample_rate_hz,
                    clip.duration_sec,
                    clip.split.value,
                    clip.checksum_sha256 or "",
                    "schema_fixture",
                    "false",
                ]
            )


def _write_pending_row(path: Path, header: tuple[str, ...], reason: str) -> None:
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.writer(fh)
        writer.writerow(header)
        row = ["PENDING", reason] + [""] * (len(header) - 2)
        writer.writerow(row)


def _write_pending_rq_tables(results: Path) -> None:
    reason = "no_curated_audio_bytes_no_cached_xlsr_embeddings"
    _write_pending_row(results / "RQ1_clean_vs_opus.csv", _RQ_METRIC_HEADER, reason)
    _write_pending_row(
        results / "RQ2_multilingual_vs_english.csv",
        (
            "status",
            "reason",
            "model",
            "training_languages",
            "evaluation_language",
            "condition",
            "eer",
            "min_dcf",
            "accuracy",
            "f1",
        ),
        reason,
    )
    _write_pending_row(
        results / "RQ3_cross_lingual_matrix.csv",
        (
            "status",
            "reason",
            "train_languages",
            "test_language",
            "eer",
            "min_dcf",
            "accuracy",
            "f1",
        ),
        reason,
    )
    _write_pending_row(
        results / "RQ4_calibration.csv",
        (
            "status",
            "reason",
            "language",
            "condition",
            "calibration_state",
            "ece",
            "brier",
            "mean_confidence",
            "accuracy",
            "entropy",
        ),
        reason,
    )
    _write_pending_row(
        results / "RQ5_human_vs_model.csv",
        (
            "status",
            "reason",
            "participant_or_model",
            "language",
            "condition",
            "accuracy",
            "mean_confidence",
            "ece",
            "sample_count",
        ),
        "human_n=0_and_no_shared_test_clip_ids_from_trained_model",
    )
    (results / "tables" / "README.md").write_text(
        "RQ CSVs live in the parent `results/` folder. "
        "Metric cells are empty until experiments run.\n",
        encoding="utf-8",
    )
    (results / "figures" / "README.md").write_text(
        "No publication figures yet. Fixture SVGs from "
        "`python -m vaaniq.research.cli --mode fixtures` "
        "are software-path demos, not RQ results.\n",
        encoding="utf-8",
    )


def _write_dataset_report(
    output_root: Path,
    clips: list[ClipMetadata],
    stats: DatasetStatistics,
    audit: dict[str, Any],
    env: dict[str, Any],
) -> None:
    sources = Counter(c.source.value for c in clips)
    attacks = Counter(c.attack_type.value if c.attack_type else "none" for c in clips)
    conds = Counter(c.compression_status.value for c in clips)
    rates = Counter(c.sample_rate_hz for c in clips)
    durs = [c.duration_sec for c in clips]
    text = f"""# Dataset report

Generated: {env["timestamp"]}
Git: `{env["git_sha"]}` dirty={env["git_dirty"]}

## Research corpus (authoritative)

| Language | Hours | Clips | Speakers | Status |
|----------|------:|------:|---------:|--------|
| hi | 0 | 0 | 0 | PENDING |
| mr | 0 | 0 | 0 | PENDING |
| ta | 0 | 0 | 0 | PENDING |
| **total** | **0** | **0** | **0** | **PENDING** |

Audio files under `data/` and `backend/data/`: **{env["audio_files_under_data"]}**.
HF token present: **{env["hf_token_present"]}**.
Gated sources (Kathbath, IndicVoices-R, IndicSynth) were **not downloaded** (REQ-130).

Tamil is the project third language. Tamil **audio bytes are not verified** on disk.
Fixture metadata contains `language=ta` rows; that is not a Tamil corpus.

## Schema fixture only (not a research result)

The six-row mock manifest at `backend/tests/fixtures/datasets/mock_manifest.jsonl`
was inventoried so hours are computed, not invented.

| Language | Fixture clips | Fixture hours |
|----------|--------------:|--------------:|
| hi | {stats.counts_by_language[Language.HI]} | {stats.hours_by_language[Language.HI]:.10f} |
| mr | {stats.counts_by_language[Language.MR]} | {stats.hours_by_language[Language.MR]:.10f} |
| ta | {stats.counts_by_language[Language.TA]} | {stats.hours_by_language[Language.TA]:.10f} |
| total | {stats.total_clips} | {stats.total_hours:.10f} |

Real/fake fixture counts: real={stats.counts_by_label[Label.REAL]} \
fake={stats.counts_by_label[Label.FAKE]}.
Sources: {dict(sources)}.
Attack types: {dict(attacks)}.
Compression labels: {dict(conds)}.
Sample rates: {dict(rates)}.
Duration range (fixture metadata seconds): \
min={min(durs) if durs else 0} max={max(durs) if durs else 0}.

Team recordings: **0 clips**. They must remain a small phone-mic supplement when collected.

Do not cite fixture hours as O1 completion.
"""
    (output_root / "reports" / "DATASET_REPORT.md").write_text(text, encoding="utf-8")
    (output_root / "results" / "DATASET_REPORT.md").write_text(text, encoding="utf-8")
    (output_root / "datasets" / "reports" / "DATASET_REPORT.md").write_text(text, encoding="utf-8")


def _write_quality_report(
    output_root: Path,
    audit: dict[str, Any],
    env: dict[str, Any],
) -> None:
    blocking = "\n".join(f"- {x}" for x in audit["blocking"]) or "- none"
    warnings = "\n".join(f"- {x}" for x in audit["warnings"]) or "- none"
    text = f"""# Data quality report

Generated: {env["timestamp"]}
Git: `{env["git_sha"]}`

## Blocking (must fix before training)

{blocking}

`can_train`: **{audit["can_train"]}**

## Warnings

{warnings}

## Checks run

| Check | Result |
|-------|--------|
| Required metadata fields | {audit["n_require_ok"]} / {audit["n_clips"]} ok |
| Duplicate clip ids | see blocking |
| Speaker split leakage | see blocking |
| Clean/compressed pair split leakage | see blocking |
| Tamil in manifest labels | {audit["tamil_in_manifest"]} |
| Tamil audio bytes verified | {audit["tamil_audio_verified"]} |
| Missing audio files for `uri` | {audit["n_missing_audio_bytes"]} |
| Orphan speaker_id | {audit["n_orphan_speakers"]} |
| Split counts | {audit["split_counts"]} |

Training is **stopped** until a curated, speaker-disjoint corpus with on-disk audio exists.
"""
    (output_root / "reports" / "DATA_QUALITY_REPORT.md").write_text(text, encoding="utf-8")
    (output_root / "datasets" / "reports" / "DATA_QUALITY_REPORT.md").write_text(
        text, encoding="utf-8"
    )


def _write_findings(output_root: Path) -> None:
    text = """# Research findings

No RQ is answered. Experiments were **not run** on curated hours.

## RQ1

PENDING. No clean vs Opus evaluation on held-out Indic test audio.

## RQ2

PENDING. English-only vs multilingual comparison not executed on real embeddings.

## RQ3

PENDING. Leave-one-language-out (HI+MR→TA, HI+TA→MR, MR+TA→HI) not executed on real data.
Software folds exist; they are not results.

## RQ4

PENDING. Temperature scaling was not fit on a speaker-disjoint validation set of real logits.

## RQ5

PENDING. Human participant count = 0. No shared test clip IDs from a trained model.

Do not copy numbers from `python -m vaaniq.research.cli --mode fixtures` into this file.
"""
    (output_root / "reports" / "RESEARCH_FINDINGS.md").write_text(text, encoding="utf-8")


def _write_results_audit(output_root: Path, env: dict[str, Any], audit: dict[str, Any]) -> None:
    text = f"""# Results audit

Generated: {env["timestamp"]}
Git: `{env["git_sha"]}`

| Check | Result |
|-------|--------|
| RQ1-RQ5 metric cells empty / PENDING | YES |
| Fixture EER copied into RQ CSVs | NO |
| Proposal target hours treated as measured hours | NO |
| Speaker-disjoint research split written | NO (no corpus) |
| Temperature fit on test | N/A (not run) |
| Human clips = model test IDs | N/A (n=0) |
| Tamil audio verified | {audit["tamil_audio_verified"]} |
| can_train | {audit["can_train"]} |

Existing `backend/research/explain/*.json` files are **demo inference artefacts**, not RQ tables.
Existing fixture SVG from `--mode fixtures` are **software-path demos**.
"""
    (output_root / "reports" / "RESULTS_AUDIT.md").write_text(text, encoding="utf-8")


def _write_execution_status(
    output_root: Path,
    repo_root: Path,
    env: dict[str, Any],
    stats: DatasetStatistics,
    audit: dict[str, Any],
    clips: list[ClipMetadata],
) -> None:
    hw = env["hardware"]
    speakers = {c.speaker_id for c in clips if c.speaker_id}
    text = f"""# Research execution status

Generated: {env["timestamp"]}

Statuses: COMPLETE = actually run on curated data and validated.
PARTIAL / PENDING / FAILED as defined in the Phase 6 prompt.
Code existing ≠ COMPLETE.

## 1. Actual dataset hours per language

| Language | Research hours | Fixture metadata hours | Status |
|----------|---------------:|-----------------------:|--------|
| Hindi | 0 | {stats.hours_by_language[Language.HI]:.10f} | PENDING |
| Marathi | 0 | {stats.hours_by_language[Language.MR]:.10f} | PENDING |
| Tamil | 0 | {stats.hours_by_language[Language.TA]:.10f} | PENDING |

## 2. Number of speakers

Research corpus: **0**. Schema fixture named speakers: **{len(speakers)}**.

## 3. Number of clips

Research corpus: **0**. Schema fixture rows: **{stats.total_clips}**.
Audio files on disk under data trees: **{env["audio_files_under_data"]}**.

## 4. Train / validation / test sizes

Research splits: **PENDING** (not written). Fixture split counts: `{audit["split_counts"]}`.

## 5. Main model configuration

Intended: frozen Wav2Vec2-XLS-R + AASIST-style head (`aasist-v1`), NumPy CI path.
GPU / clovaai graph AASIST: **PENDING**.
Status: **PENDING** (not trained on curated embeddings).

## 6. Baseline configurations

LFCC-GMM, RawNet2, English-only XLS-R+AASIST modules exist.
ASVspoof ingest + evaluation: **PENDING**.

## 7. RQ1 result status

**PENDING** — no Opus vs clean evaluation on held-out audio.

## 8. RQ2 result status

**PENDING** — multilingual vs English-only not run.

## 9. RQ3 result status

**PENDING** — zero-shot HI+MR→TA / HI+TA→MR / MR+TA→HI not run on real data.

## 10. RQ4 result status

**PENDING** — T-scaling not fit on real val logits.

## 11. RQ5 result status

**PENDING**.

## 12. Human participant count

**0**.

## 13. Calibration status

**PENDING**.

## 14. Explainability status

**PARTIAL** — demo Grad-CAM proxy artefacts exist; not tied to a published test set.

## 15. Figures generated

RQ publication figures: **0**.
Fixture/demo SVGs may exist under software-path runs; they are not RQ figures.

## 16. Tables generated

PENDING stub CSVs with empty metric cells:

- `research/results/dataset_statistics.csv` (actual zeros + fixture metadata hours)
- `research/results/RQ1_clean_vs_opus.csv`
- `research/results/RQ2_multilingual_vs_english.csv`
- `research/results/RQ3_cross_lingual_matrix.csv`
- `research/results/RQ4_calibration.csv`
- `research/results/RQ5_human_vs_model.csv`

## 17. Paper sections completed

Methods/gap/RQs draft: **PARTIAL** (`research/paper/manuscript/VaaniQ_manuscript.md`).
Results sections: **NOT RUN** (explicit).

## 18. Remaining experiments

1. Obtain HF token; download gated Kathbath / IndicVoices-R / IndicSynth / CV hi-mr.
2. Confirm Tamil **audio** (not labels only).
3. Speaker-disjoint manifests; pair clean/Opus in the same split.
4. Freeze XLS-R on GPU; cache embeddings.
5. Train head; run RQ1-RQ4.
6. Recruit ≥12-15 listeners on the same test clip IDs.

## 19. Failed experiments

None failed after start. Acquisition **not started**: `hf_token_present={env["hf_token_present"]}`.

## 20. Known limitations

See `docs/KNOWN_LIMITATIONS.md` (authoritative). Not rewritten here.

## 21. Reproducibility information

| Field | Value |
|-------|--------|
| Git SHA | `{env["git_sha"]}` |
| Dirty | {env["git_dirty"]} |
| ffmpeg runnable | {env["ffmpeg_runnable"]} |
| torch | {hw.get("torch")} |
| cuda | {hw.get("cuda")} |
| python | {hw.get("python")} |
| system | {hw.get("system")} {hw.get("machine")} |
| seed (unused; no train) | n/a |
| dataset version | none (research corpus empty) |

`can_train` after quality audit: **{audit["can_train"]}**.
"""
    (output_root / "reports" / "RESEARCH_EXECUTION_STATUS.md").write_text(text, encoding="utf-8")
    (output_root / "RESEARCH_EXECUTION_STATUS.md").write_text(text, encoding="utf-8")
    docs = repo_root / "docs"
    if docs.is_dir():
        (docs / "RESEARCH_EXECUTION_STATUS.md").write_text(text, encoding="utf-8")


def _write_methods_paper(output_root: Path, env: dict[str, Any]) -> None:
    text = f"""# VaaniQ manuscript (research execution snapshot)

**Status of experimental results: NOT RUN.**
Generated: {env["timestamp"]}. Git `{env["git_sha"]}`.

This draft records methods and questions from the capstone proposal. It does **not**
contain measured EER, min-DCF, ECE, Brier, hours, or human accuracy.

## 1. Abstract

NOT RUN: abstract with numbers will be written after RQ1-RQ5 execute on curated data.

## 2. Introduction

AI voice cloning is used in fraud delivered as compressed WhatsApp-style voice notes.
VaaniQ studies detection of AI-generated speech in Hindi, Marathi, and Tamil, under
WhatsApp-style Opus, with calibrated confidence and a human-listener baseline
(proposal §§1-4). Tamil is the third language. Telugu is not in scope.

## 3. Related Work

Literature (proposal §5): AASIST (Jung et al.); Wav2Vec2-XLS-R (Babu et al.);
Indic-CodecFake/SATYAM; IndicSynth; Pascu et al. on calibrated audio deepfake
detection; Müller et al. on human perception of audio deepfakes. This section
summarises prior work; it is not a VaaniQ result.

## 4. Research Gap

No published combination of (a) Indian-language cloning/TTS fraud audio, (b)
WhatsApp-style Opus as a named condition, (c) detector calibration, and (d) a
human baseline on the same stimuli (proposal §5.7).

## 5. Research Questions

- RQ1: Opus degradation vs clean.
- RQ2: Multilingual vs English-only robustness.
- RQ3: Zero-shot transfer among HI, MR, TA (train-2 / test-1).
- RQ4: Calibration under compression (ECE, Brier, reliability, coverage).
- RQ5: Human vs model on identical clip IDs.

## 6. Dataset and Benchmark Construction

PENDING. Measured research hours: Hindi 0, Marathi 0, Tamil 0.
See `research/reports/DATASET_REPORT.md`.

## 7. Methodology

### 7.1 Dataset

Adapters exist for Kathbath, IndicVoices-R, Common Voice, IndicSynth, generated
audio, and team recordings. Ingest is blocked without an HF token (REQ-130).

### 7.2 Preprocessing

16 kHz mono, peak normalisation, duration bounds (config YAML).

### 7.3 Opus compression

ffmpeg WhatsApp-style simulation (OQ-007). Not byte-identical WhatsApp.

### 7.4 XLS-R

Frozen feature extractor. Must not be fine-tuned.

### 7.5 AASIST

AASIST-style head on cached embeddings in this repository; not claimed as
clovaai graph-attention parity (see `docs/KNOWN_LIMITATIONS.md`).

### 7.6 Baselines

LFCC-GMM, RawNet2, English-only XLS-R+AASIST. Not yet evaluated on curated hours.

### 7.7 Calibration

Temperature scaling on validation only (OQ-032). Not yet fit on real val logits.

### 7.8 Explainability

Grad-CAM proxy, band masking, compression artefacts (OQ-034). Demo artefacts only.

### 7.9 Human baseline

Protocol implemented (anonymous ID, 1-5 confidence, timing). N = 0.

## 8. Experimental Setup

Speaker-disjoint 70/15/15 is the required split (OQ-008). **Not written** for a
research corpus because no audio is on disk. Training on fixtures is forbidden
as an RQ result.

## 9. Results

### 9.1 RQ1

NOT RUN.

### 9.2 RQ2

NOT RUN.

### 9.3 RQ3

NOT RUN.

### 9.4 RQ4

NOT RUN.

### 9.5 RQ5

NOT RUN. Human n = 0.

## 10. Error Analysis

NOT RUN.

## 11. Discussion

WITHHELD until §9 has measured values.

## 12. Limitations

Incorporated from `docs/KNOWN_LIMITATIONS.md` (authoritative). Additional
execution fact: research corpus hours are zero in this environment.

## 13. Ethical Considerations

Gated licences (REQ-130). IndicSynth CC BY-NC may block full audio release (OQ-035).
Human study is anonymous and bounded.

## 14. Conclusion

NOT WRITTEN as a results claim. Software apparatus exists; evidence does not.

## 15. Future Work

See `docs/FUTURE_WORK.md`.

## References

As cited in `docs/source/Capstone_Project_Proposal.md` §5. Do not add unsourced
citations here.
"""
    (output_root / "paper" / "manuscript" / "VaaniQ_manuscript.md").write_text(
        text, encoding="utf-8"
    )
    (output_root / "paper" / "references" / "SOURCES.md").write_text(
        "Authoritative citations: docs/source/Capstone_Project_Proposal.md §5.\n",
        encoding="utf-8",
    )


def _write_artifact_inventory(output_root: Path, repo_root: Path, env: dict[str, Any]) -> None:
    """Classify existing research files. Does not overwrite demo JSON."""
    rows: list[tuple[str, str, str]] = []
    explain = repo_root / "backend" / "research" / "explain"
    if explain.is_dir():
        for path in sorted(explain.glob("*.json")):
            rows.append(
                (path.relative_to(repo_root).as_posix(), "demo_inference", "not_rq_result")
            )
    for rel in (
        "research/figures/README.md",
        "research/paper/README.md",
        "research/experiments/README.md",
    ):
        path = repo_root / rel
        if path.is_file():
            rows.append((rel, "placeholder", "incomplete"))
    text = f"""# Research artifact inventory (Phase K)

Generated: {env["timestamp"]}
Git: `{env["git_sha"]}`

Classifications: `final` (validated RQ), `intermediate`, `obsolete`,
`incomplete`, `demo_inference` (software path, not a result).

No file below is a validated RQ1-RQ5 result. Demo JSON under
`backend/research/explain/` was **not overwritten**.

| Path | Class | Notes |
|------|-------|-------|
"""
    for rel_path, cls, notes in rows:
        text += f"| `{rel_path}` | {cls} | {notes} |\n"
    if not rows:
        text += "| (none found) | incomplete | empty inventory |\n"
    (output_root / "reports" / "ARTIFACT_INVENTORY.md").write_text(text, encoding="utf-8")
    (output_root / "results" / "raw_metrics" / "README.md").write_text(
        "Empty until a curated-hour evaluation writes metric JSON.\n",
        encoding="utf-8",
    )
