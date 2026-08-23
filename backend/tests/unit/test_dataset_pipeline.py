"""Dataset pipeline unit tests (ROADMAP-011-018), offline fixtures only."""

from __future__ import annotations

from pathlib import Path

import pytest

from vaaniq.core.errors import DatasetError
from vaaniq.core.types import Label, Language, Split
from vaaniq.datasets import (
    CommonVoiceSource,
    CorpusCache,
    DatasetStatistics,
    GeneratedAudioSource,
    IndicSynthSource,
    IndicVoicesRSource,
    KathbathSource,
    LocalCacheDownloader,
    ManifestClipLoader,
    MockDownloader,
    SpeakerDisjointSplitter,
    TeamRecordingsSource,
    format_preview,
    language_filter,
    licence_gate,
    normalize_clip_id,
    normalize_speaker_id,
    require_fields,
)

_FIXTURES = Path(__file__).resolve().parents[1] / "fixtures" / "datasets"
_MANIFEST = _FIXTURES / "mock_manifest.jsonl"


def test_mock_downloader_copies_fixture_tree(tmp_path: Path) -> None:
    dest = tmp_path / "out"
    path = MockDownloader(_FIXTURES).ensure_local("mock", dest)
    assert path.exists()
    assert (path / "mock_manifest.jsonl").is_file() or path.is_dir()


def test_manifest_loader_yields_six_clips() -> None:
    clips = list(ManifestClipLoader().iter_clips(_MANIFEST))
    assert len(clips) == 6
    langs = {c.language for c in clips}
    assert langs == set(Language)
    labels = {c.label for c in clips}
    assert labels == {Label.REAL, Label.FAKE}


def test_adapters_iter_clips_from_manifest() -> None:
    src = KathbathSource(manifest_path=_MANIFEST)
    clips = list(src.iter_clips())
    assert len(clips) == 6
    assert src.source_id.value == "kathbath"


def test_adapters_iter_clips_from_rows() -> None:
    rows = [
        {
            "clip_id": " row1 ",
            "language": "hi",
            "label": "real",
            "compression_status": "clean",
            "sample_rate_hz": 16000,
            "duration_sec": 1.0,
            "split": "train",
            "dataset_source": "ai4bharat/Kathbath",
            "speaker_id": " spk ",
        }
    ]
    clip = next(iter(KathbathSource(rows=rows).iter_clips()))
    assert clip.clip_id == "row1"
    assert clip.speaker_id == "spk"
    assert clip.source.value == "kathbath"


def test_generated_audio_source_default_id() -> None:
    assert GeneratedAudioSource().source_id.value == "parler_tts"


@pytest.mark.parametrize(
    "source_cls",
    [
        KathbathSource,
        IndicVoicesRSource,
        CommonVoiceSource,
        IndicSynthSource,
        TeamRecordingsSource,
        GeneratedAudioSource,
    ],
)
def test_adapters_require_offline_input(source_cls: type) -> None:
    with pytest.raises(DatasetError):
        next(iter(source_cls().iter_clips()))


def test_stats_and_preview() -> None:
    clips = list(ManifestClipLoader().iter_clips(_MANIFEST))
    stats = DatasetStatistics.compute(clips)
    assert stats.total_clips == 6
    assert set(stats.counts_by_language) == set(Language)
    assert stats.counts_by_language[Language.HI] == 2
    expected_hours = sum(c.duration_sec for c in clips) / 3600.0
    assert stats.total_hours == pytest.approx(expected_hours)
    preview = format_preview(clips, 2)
    assert "clip_id" in preview
    assert "hi_real_001" in preview
    assert format_preview(clips, -1) == "clip_id\tlanguage\tlabel\tsource\tsplit\tduration_sec"


def test_language_filter_and_validators() -> None:
    clips = list(ManifestClipLoader().iter_clips(_MANIFEST))
    only_hi = language_filter(clips, [Language.HI])
    assert len(only_hi) == 2
    require_fields(only_hi[0])
    licence_gate(gated=True, token_present=True)
    with pytest.raises(DatasetError):
        licence_gate(gated=True, token_present=False)


def test_normalizers() -> None:
    assert normalize_clip_id("  a  ") == "a"
    assert normalize_speaker_id("  s  ") == "s"
    assert normalize_speaker_id("   ") is None
    assert normalize_speaker_id(None) is None


def test_corpus_cache(tmp_path: Path) -> None:
    cache = CorpusCache(tmp_path / "cache")
    assert cache.root == tmp_path / "cache"
    assert cache.get("kathbath", "deadbeef") is None
    path = cache.ensure_dir("kathbath", "deadbeef")
    assert path.exists()
    assert cache.get("kathbath", "deadbeef") == path


def test_local_cache_downloader(tmp_path: Path) -> None:
    cache_root = tmp_path / "cache"
    src = cache_root / "kathbath"
    src.mkdir(parents=True)
    (src / "note.txt").write_text("ok", encoding="utf-8")
    dest = tmp_path / "dest"
    out = LocalCacheDownloader(cache_root).ensure_local("kathbath", dest)
    assert (out / "note.txt").read_text(encoding="utf-8") == "ok"
    # second call is idempotent
    assert LocalCacheDownloader(cache_root).ensure_local("kathbath", dest) == out
    with pytest.raises(DatasetError):
        LocalCacheDownloader(cache_root).ensure_local("missing", dest)


def test_common_voice_and_generated_parsers() -> None:
    from vaaniq.datasets.parsers import (
        CommonVoiceRowParser,
        GeneratedAudioRowParser,
        IndicSynthRowParser,
    )

    cv = CommonVoiceRowParser().parse(
        {
            "clip_id": "cv1",
            "language": "hi",
            "label": "real",
            "compression_status": "clean",
            "sample_rate_hz": 16000,
            "duration_sec": 1.0,
            "split": "train",
            "dataset_source": "cv",
            "client_id": "client-a",
        }
    )
    assert cv.speaker_id == "client-a"
    assert cv.source.value == "common_voice"
    gen = GeneratedAudioRowParser().parse(
        {
            "clip_id": "g1",
            "language": "mr",
            "compression_status": "clean",
            "sample_rate_hz": 16000,
            "duration_sec": 1.0,
            "split": "train",
            "dataset_source": "local",
        }
    )
    assert gen.label is Label.FAKE
    synth = IndicSynthRowParser().parse(
        {
            "clip_id": "s1",
            "language": "ta",
            "compression_status": "clean",
            "sample_rate_hz": 16000,
            "duration_sec": 1.0,
            "split": "train",
            "dataset_source": "indicsynth",
            "path": "/tmp/s1.wav",
        }
    )
    assert synth.uri == "/tmp/s1.wav"


def test_manifest_json_and_require_fields_errors(tmp_path: Path) -> None:
    path = tmp_path / "clips.json"
    path.write_text(
        '[{"clip_id":"j1","language":"hi","source":"kathbath","label":"real",'
        '"compression_status":"clean","sample_rate_hz":16000,"duration_sec":1.0,'
        '"split":"train","dataset_source":"x"}]',
        encoding="utf-8",
    )
    clips = list(ManifestClipLoader().iter_clips(path))
    assert len(clips) == 1
    with pytest.raises(DatasetError):
        list(ManifestClipLoader().iter_clips(tmp_path / "missing.jsonl"))
    bad = clips[0]
    from dataclasses import replace

    with pytest.raises(DatasetError):
        require_fields(replace(bad, clip_id="  "))
    with pytest.raises(DatasetError):
        require_fields(replace(bad, sample_rate_hz=0))
    with pytest.raises(DatasetError):
        require_fields(replace(bad, duration_sec=0.0))
    with pytest.raises(DatasetError):
        require_fields(replace(bad, dataset_source=""))


def test_speaker_disjoint_bad_ratios(tmp_path: Path) -> None:
    clips = list(ManifestClipLoader().iter_clips(_MANIFEST))
    with pytest.raises(DatasetError):
        SpeakerDisjointSplitter().build(
            clips,
            seed=1,
            destination=tmp_path / "bad",
            train_ratio=0.5,
            val_ratio=0.5,
            test_ratio=0.5,
        )


def test_speaker_disjoint_splitter(tmp_path: Path) -> None:
    clips = list(ManifestClipLoader().iter_clips(_MANIFEST))
    paths = SpeakerDisjointSplitter().build(clips, seed=42, destination=tmp_path / "splits")
    assert set(paths) == set(Split)
    for split, path in paths.items():
        assert path.is_file()
        loaded = list(ManifestClipLoader().iter_clips(path))
        for clip in loaded:
            assert clip.split is split
    # Speakers must not appear in more than one split.
    speaker_to_split: dict[str, Split] = {}
    for split, path in paths.items():
        for clip in ManifestClipLoader().iter_clips(path):
            key = clip.speaker_id if clip.speaker_id else f"clip:{clip.clip_id}"
            if key in speaker_to_split:
                assert speaker_to_split[key] is split
            else:
                speaker_to_split[key] = split
    assert (tmp_path / "splits" / "split_version.json").is_file()


def test_splitter_rejects_pair_id_split_leakage(tmp_path: Path) -> None:
    from dataclasses import replace

    from vaaniq.core.domain.entities import ClipMetadata
    from vaaniq.core.types import CompressionCondition, DatasetSource, Label, Language

    clean = ClipMetadata(
        clip_id="c1",
        language=Language.HI,
        source=DatasetSource.KATHBATH,
        label=Label.REAL,
        compression_status=CompressionCondition.CLEAN,
        sample_rate_hz=16000,
        duration_sec=1.0,
        split=Split.TRAIN,
        dataset_source="test",
        speaker_id="spk_a",
        pair_id="pair_shared",
    )
    compressed = replace(
        clean,
        clip_id="c1_opus",
        compression_status=CompressionCondition.OPUS_WHATSAPP_SIM,
        speaker_id="spk_b",
    )
    with pytest.raises(DatasetError, match="pair_id spans splits"):
        SpeakerDisjointSplitter().build(
            [clean, compressed],
            seed=0,
            destination=tmp_path / "pair_leak",
        )


def test_splitter_empty_clips(tmp_path: Path) -> None:
    paths = SpeakerDisjointSplitter().build([], seed=0, destination=tmp_path / "empty")
    assert set(paths) == set(Split)
    for path in paths.values():
        assert path.read_text(encoding="utf-8") == ""
