"""Phase 4 research framework tests (RQ1-RQ5 software path)."""

from __future__ import annotations

from pathlib import Path

import numpy as np

from vaaniq.audio.transforms.degrade import resample_waveform, simulate_packet_loss
from vaaniq.config.domains import HumanStudyProtocolConfig, ResearchConditionsConfig
from vaaniq.core.domain.entities import ClipMetadata, Logits, Waveform
from vaaniq.core.types import (
    CompressionCondition,
    DatasetSource,
    ExportFormat,
    Label,
    Language,
    Split,
)
from vaaniq.evaluation.metrics.core import bootstrap_metric_ci
from vaaniq.explainability import misclassified_explorer
from vaaniq.explainability.attention import AttentionMapExplainer
from vaaniq.human_study import (
    CsvHumanStudyExporter,
    assign_clips,
    human_vs_model_report,
    register_participant,
)
from vaaniq.research import (
    ExperimentStore,
    ResearchReportBundle,
    analyze_errors,
    apply_condition,
    condition_catalog,
    leave_one_language_folds,
    run_calibration_suite,
    run_compression_suite,
    run_cross_lingual_suite,
)


def _clip(clip_id: str, lang: Language) -> ClipMetadata:
    return ClipMetadata(
        clip_id=clip_id,
        language=lang,
        source=DatasetSource.TEAM_RECORDING,
        label=Label.REAL,
        compression_status=CompressionCondition.CLEAN,
        sample_rate_hz=16000,
        duration_sec=1.0,
        split=Split.TEST,
        dataset_source="unit",
    )


def test_leave_one_language_folds_cover_hi_mr_ta() -> None:
    folds = leave_one_language_folds()
    assert len(folds) == 3
    tests = {f["test"] for f in folds}
    assert tests == set(Language)


def test_cross_lingual_suite(tmp_path: Path) -> None:
    rng = np.random.default_rng(0)
    embs = {}
    for lang in Language:
        x = rng.normal(0, 1, size=(24, 1024)).astype(np.float32)
        y = np.array([i % 2 for i in range(24)], dtype=np.int64)
        embs[lang] = (x, y)
    store = ExperimentStore(root=tmp_path / "exp")
    result = run_cross_lingual_suite(
        embs, store=store, output_dir=tmp_path / "xl", seed=0, max_epochs=1
    )
    assert Path(result["csv"]).is_file()
    assert Path(result["svg"]).is_file()
    assert store.search(rq_id="RQ3")


def test_compression_and_degrade(tmp_path: Path) -> None:
    sr = 16000
    t = np.arange(sr, dtype=np.float32) / sr
    wav = Waveform(
        samples=(0.2 * np.sin(2 * np.pi * 440 * t)).astype(np.float32), sample_rate_hz=sr
    )
    rng = np.random.default_rng(1)
    lost = simulate_packet_loss(wav, loss_fraction=0.1, rng=rng)
    assert lost.samples.size == wav.samples.size
    rs = resample_waveform(wav, 8000)
    assert rs.sample_rate_hz == sr
    cfg = ResearchConditionsConfig()
    cells = condition_catalog(cfg)
    assert any(c["name"] == "opus_16kbps" for c in cells)
    applied = apply_condition(wav, {"kind": "packet_loss", "loss_fraction": 0.05}, rng=rng)
    assert applied.samples.size == wav.samples.size
    store = ExperimentStore(root=tmp_path / "exp")
    scores = {
        "clean": ([0.1, 0.2, 0.8, 0.9], [0, 0, 1, 1]),
        "opus_16kbps": ([0.2, 0.3, 0.7, 0.8], [0, 0, 1, 1]),
    }
    out = run_compression_suite(scores, store=store, output_dir=tmp_path / "c")
    assert Path(out["csv"]).is_file()
    assert Path(out["svg"]).is_file()


def test_calibration_suite_and_reports(tmp_path: Path) -> None:
    logits = [
        Logits(values=np.array([2.0, 0.1], dtype=np.float32)),
        Logits(values=np.array([0.1, 2.0], dtype=np.float32)),
    ] * 6
    labels = [0, 1] * 6
    store = ExperimentStore(root=tmp_path / "exp")
    cal = run_calibration_suite(logits, labels, store=store, output_dir=tmp_path / "cal")
    assert Path(cal["csv"]).is_file()
    assert cal["n_fit"] == 6
    assert cal["n_eval"] == 6
    assert cal["n_fit"] + cal["n_eval"] == len(labels)
    bundle = ResearchReportBundle(tmp_path / "reports")
    paths = bundle.write_all(
        experiment_id="unit",
        eval_payload={"metrics": {"eer": 0.1}, "matrices": {}, "slices": {}},
        calibration={"ece": cal["ece_temperature"]},
        experiments={"n": 1},
        dataset={"total_clips": 0},
        model={"name": "aasist-v1"},
        human={"n_responses": 0},
        explain={"artefacts": 0},
        figures=[cal["reliability_svg"]],
    )
    assert paths["human"].is_file()
    assert paths["evaluation"].is_file()


def test_error_analysis_and_explorer(tmp_path: Path) -> None:
    rows = [
        {
            "clip_id": "a",
            "language": "hi",
            "condition": "clean",
            "attack_type": "tts",
            "score": 0.9,
            "label": 0,
            "confidence": 0.9,
            "pred": 1,
        },
        {
            "clip_id": "b",
            "language": "mr",
            "condition": "opus_whatsapp_sim",
            "attack_type": "voice_clone",
            "score": 0.1,
            "label": 1,
            "confidence": 0.51,
            "pred": 0,
        },
    ]
    summary = analyze_errors(rows, destination=tmp_path / "err.md")
    assert "worst_language" in summary
    assert (tmp_path / "err.md").is_file()
    assert misclassified_explorer(rows)


def test_attention_map_explainer(tmp_path: Path) -> None:
    wav = Waveform(
        samples=np.zeros(16000, dtype=np.float32),
        sample_rate_hz=16000,
    )
    clip = _clip("att-1", Language.HI)
    arts = AttentionMapExplainer(artefact_root=tmp_path).explain(clip, wav, model_id="aasist-v1")
    assert arts
    assert arts[0].kind == "attention_map"


def test_human_protocol_export_and_stats(tmp_path: Path) -> None:
    clips = [_clip(f"{lang.value}-{i}", lang) for lang in Language for i in range(20)]
    cfg = HumanStudyProtocolConfig()
    assigned = assign_clips(clips, config=cfg, rng=np.random.default_rng(0))
    assert len(assigned) == cfg.clips_per_participant
    langs = {cid.split("-", maxsplit=1)[0] for cid in assigned}
    assert langs <= {"hi", "mr", "ta"}
    p = register_participant("hi+mr")
    assert p.participant_id
    exporter = CsvHumanStudyExporter()
    path = exporter.export(
        [
            {
                "participant_id": p.participant_id,
                "clip_id": assigned[0],
                "choice": "fake",
                "confidence_1_5": "4",
                "email": "should-strip@example.com",
            }
        ],
        fmt=ExportFormat.CSV,
        destination=tmp_path / "h.csv",
    )
    text = path.read_text(encoding="utf-8")
    assert "should-strip" not in text
    stats = human_vs_model_report(
        human_pred=[1, 0, 1, 0],
        human_conf_1_5=[5, 2, 4, 3],
        human_labels=[1, 0, 0, 0],
        model_scores=[0.9, 0.1, 0.8, 0.2],
        model_labels=[1, 0, 0, 0],
    )
    assert "human_accuracy" in stats
    assert "mcnemar" in stats


def test_bootstrap_ci() -> None:
    point, lo, hi = bootstrap_metric_ci([0.1, 0.2, 0.8, 0.9], [0, 0, 1, 1], n_samples=20)
    assert lo <= point <= hi


def test_publication_and_fixture_runner(tmp_path: Path) -> None:
    from vaaniq.research import run_fixture_suites, write_publication_bundle

    pub = write_publication_bundle(
        [0.1, 0.2, 0.8, 0.9],
        [0, 0, 1, 1],
        destination=tmp_path / "pub",
    )
    assert Path(pub["roc_svg"]).is_file()
    assert Path(pub["confusion_svg"]).is_file()
    out = run_fixture_suites(tmp_path / "research", seed=0)
    assert Path(out["reports"]["evaluation"]).is_file()


def test_experiment_store_search_compare(tmp_path: Path) -> None:
    store = ExperimentStore(root=tmp_path)
    from vaaniq.research.records import ResearchRunRecord

    rec = ResearchRunRecord(
        experiment_id="e1",
        timestamp="2026-01-01T00:00:00+00:00",
        git_sha="abc",
        model_version="aasist-v1",
        dataset_version="v0",
        languages=("hi", "mr"),
        compression_settings="clean",
        hyperparameters={"lr": "0.0001"},
        metrics={"eer": 0.2},
        calibration_results={"ece": 0.05},
        hardware={"cpu": "test"},
        seed=42,
        training_duration_sec=1.0,
        rq_ids=("RQ3",),
    )
    store.put(rec)
    assert store.search(language="hi", rq_id="RQ3")
    rows = store.compare("eer")
    assert rows[0]["eer"] == 0.2


def test_audit_blocks_missing_audio_and_speaker_leak(tmp_path: Path) -> None:
    from dataclasses import replace

    from vaaniq.core.types import Split
    from vaaniq.research.leakage import audit_manifest

    a = replace(_clip("a", Language.HI), speaker_id="spk1", split=Split.TRAIN)
    b = replace(_clip("b", Language.HI), speaker_id="spk1", split=Split.TEST)
    ta = replace(_clip("c", Language.TA), speaker_id="spk_ta", split=Split.TRAIN)
    report = audit_manifest([a, b, ta], repo_root=tmp_path)
    assert report["can_train"] is False
    assert report["tamil_in_manifest"] is True
    assert report["tamil_audio_verified"] is False
    assert any("speaker_split_leakage" in item for item in report["blocking"])
    assert any("audio_bytes_missing" in item for item in report["blocking"])


def test_execute_research_phase_pending_tables(tmp_path: Path) -> None:
    from vaaniq.research.execution import execute_research_phase

    repo = Path(__file__).resolve().parents[3]
    fixture = repo / "backend" / "tests" / "fixtures" / "datasets" / "mock_manifest.jsonl"
    out = execute_research_phase(
        repo_root=tmp_path / "empty_repo",
        output_root=tmp_path / "research",
        fixture_manifest=fixture,
    )
    assert out["audit"]["can_train"] is False
    rq1 = (tmp_path / "research" / "results" / "RQ1_clean_vs_opus.csv").read_text(encoding="utf-8")
    assert "PENDING" in rq1
    assert "0.25" not in rq1
    stats = (tmp_path / "research" / "results" / "dataset_statistics.csv").read_text(
        encoding="utf-8"
    )
    assert "research_corpus" in stats
    assert "PENDING" in stats
    findings = (tmp_path / "research" / "reports" / "RESEARCH_FINDINGS.md").read_text(
        encoding="utf-8"
    )
    assert "PENDING" in findings
    status = (tmp_path / "research" / "RESEARCH_EXECUTION_STATUS.md").read_text(encoding="utf-8")
    assert "Research corpus: **0**" in status
    assert "no Opus vs clean evaluation" in status
