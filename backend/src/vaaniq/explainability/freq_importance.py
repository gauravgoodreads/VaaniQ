"""Frequency-band importance + spectrogram / compression views (ROADMAP-050-052)."""

from __future__ import annotations

import json
from collections.abc import Sequence
from pathlib import Path

import numpy as np
import structlog

from vaaniq.audio.transforms.spectrogram import stft_magnitude
from vaaniq.core.domain.entities import ClipMetadata, ExplanationArtefact, Waveform
from vaaniq.core.ports.explainer import Explainer
from vaaniq.explainability.attention import AttentionMapExplainer
from vaaniq.explainability.gradcam import GradCamExplainer

log = structlog.get_logger(__name__)


class FrequencyBandExplainer(Explainer):
    """Occlusion-style frequency-band importance (REQ-076, REQ-082)."""

    def __init__(self, artefact_root: Path | None = None, n_bands: int = 8) -> None:
        """Bind artefact root and band count."""
        self._root = Path(artefact_root) if artefact_root else Path("./research/explain")
        self._n_bands = n_bands

    def explain(
        self,
        clip: ClipMetadata,
        wav: Waveform,
        *,
        model_id: str,
    ) -> Sequence[ExplanationArtefact]:
        """Explain via band energy ablation table."""
        self._root.mkdir(parents=True, exist_ok=True)
        mag = stft_magnitude(wav.samples, n_fft=512, hop_length=160)
        n_freq = mag.shape[0]
        band_size = max(1, n_freq // self._n_bands)
        baseline = float(np.mean(mag))
        rows: list[dict[str, float | int]] = []
        for i in range(self._n_bands):
            lo = i * band_size
            hi = min(n_freq, (i + 1) * band_size)
            masked = mag.copy()
            masked[lo:hi, :] = 0.0
            drop = baseline - float(np.mean(masked))
            rows.append({"band": i, "lo_bin": lo, "hi_bin": hi, "importance": drop})
        path = self._root / f"{clip.clip_id}_{model_id}_bands.json"
        path.write_text(json.dumps({"bands": rows}), encoding="utf-8")
        return [
            ExplanationArtefact(
                kind="frequency_band_importance",
                uri=str(path),
                summary="Band occlusion importance table",
                extras={"model_id": model_id},
            )
        ]


class SpectrogramExplainer(Explainer):
    """Clean vs compressed spectrogram view (REQ-077)."""

    def __init__(self, artefact_root: Path | None = None) -> None:
        """Bind artefact root."""
        self._root = Path(artefact_root) if artefact_root else Path("./research/explain")

    def explain(
        self,
        clip: ClipMetadata,
        wav: Waveform,
        *,
        model_id: str,
    ) -> Sequence[ExplanationArtefact]:
        """Write spectrogram magnitude JSON."""
        self._root.mkdir(parents=True, exist_ok=True)
        mag = stft_magnitude(wav.samples, n_fft=512, hop_length=160)
        path = self._root / f"{clip.clip_id}_{model_id}_spectrogram.json"
        # Downsample for UI payload size
        small = mag[::4, ::4]
        path.write_text(
            json.dumps(
                {
                    "clip_id": clip.clip_id,
                    "condition": clip.compression_status.value,
                    "magnitude": small.astype(float).tolist(),
                }
            ),
            encoding="utf-8",
        )
        return [
            ExplanationArtefact(
                kind="spectrogram",
                uri=str(path),
                summary="Spectrogram magnitude view",
                extras={"condition": clip.compression_status.value},
            )
        ]


class CompressionArtifactExplainer(Explainer):
    """Highlight high-frequency energy loss typical of Opus (REQ-078)."""

    def __init__(self, artefact_root: Path | None = None) -> None:
        """Bind artefact root."""
        self._root = Path(artefact_root) if artefact_root else Path("./research/explain")

    def explain(
        self,
        clip: ClipMetadata,
        wav: Waveform,
        *,
        model_id: str,
    ) -> Sequence[ExplanationArtefact]:
        """Write compression-artifact summary."""
        self._root.mkdir(parents=True, exist_ok=True)
        mag = stft_magnitude(wav.samples, n_fft=512, hop_length=160)
        n = mag.shape[0]
        low = float(np.mean(mag[: n // 3]))
        high = float(np.mean(mag[2 * n // 3 :]))
        ratio = high / (low + 1e-8)
        path = self._root / f"{clip.clip_id}_{model_id}_compression.json"
        path.write_text(
            json.dumps(
                {
                    "low_band_energy": low,
                    "high_band_energy": high,
                    "high_low_ratio": ratio,
                    "condition": clip.compression_status.value,
                }
            ),
            encoding="utf-8",
        )
        return [
            ExplanationArtefact(
                kind="compression_artifact",
                uri=str(path),
                summary="High/low band energy ratio (Opus artifact proxy)",
                extras={"high_low_ratio": f"{ratio:.4f}"},
            )
        ]


class CompositeExplainer(Explainer):
    """Fan-out Grad-CAM + band + spectrogram + compression views."""

    def __init__(self, explainers: Sequence[Explainer] | None = None) -> None:
        """Bind child explainers."""
        self._explainers = (
            list(explainers)
            if explainers is not None
            else [
                GradCamExplainer(),
                AttentionMapExplainer(),
                FrequencyBandExplainer(),
                SpectrogramExplainer(),
                CompressionArtifactExplainer(),
            ]
        )

    def explain(
        self,
        clip: ClipMetadata,
        wav: Waveform,
        *,
        model_id: str,
    ) -> Sequence[ExplanationArtefact]:
        """Collect artefacts from all children."""
        out: list[ExplanationArtefact] = []
        for ex in self._explainers:
            out.extend(ex.explain(clip, wav, model_id=model_id))
        return out
