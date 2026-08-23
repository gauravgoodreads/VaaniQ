"""Grad-CAM style temporal heatmap (ROADMAP-049 / REQ-075).

# ASSUMPTION: OQ-034 - spectrogram-aligned path for inference input.
"""

from __future__ import annotations

import json
from collections.abc import Sequence
from pathlib import Path

import numpy as np
import structlog

from vaaniq.audio.transforms.spectrogram import stft_magnitude
from vaaniq.core.domain.entities import ClipMetadata, ExplanationArtefact, Waveform
from vaaniq.core.ports.explainer import Explainer

log = structlog.get_logger(__name__)


class GradCamExplainer(Explainer):
    """Produce a temporal importance heatmap from spectrogram energy (REQ-075)."""

    def __init__(self, artefact_root: Path | None = None) -> None:
        """Bind artefact output root."""
        self._root = Path(artefact_root) if artefact_root else Path("./research/explain")

    def explain(
        self,
        clip: ClipMetadata,
        wav: Waveform,
        *,
        model_id: str,
    ) -> Sequence[ExplanationArtefact]:
        """Explain a model decision for ``clip``."""
        self._root.mkdir(parents=True, exist_ok=True)
        mag = stft_magnitude(wav.samples, n_fft=512, hop_length=160)
        # Temporal importance = mean frequency energy (proxy Grad-CAM without torch)
        temporal = np.mean(mag, axis=0)
        temporal = temporal / (np.max(temporal) + 1e-8)
        # Simple frequency attention proxy
        freq = np.mean(mag, axis=1)
        freq = freq / (np.max(freq) + 1e-8)
        out = self._root / f"{clip.clip_id}_{model_id}_gradcam.json"
        payload = {
            "clip_id": clip.clip_id,
            "model_id": model_id,
            "temporal_heatmap": temporal.astype(float).tolist(),
            "attention_heatmap": freq.astype(float).tolist(),
        }
        out.write_text(json.dumps(payload), encoding="utf-8")
        log.info("gradcam_written", path=str(out))
        return [
            ExplanationArtefact(
                kind="gradcam_temporal",
                uri=str(out),
                summary="Temporal energy heatmap (spectrogram-aligned Grad-CAM proxy)",
                extras={"model_id": model_id},
            ),
            ExplanationArtefact(
                kind="attention_heatmap",
                uri=str(out),
                summary="Frequency attention proxy from STFT magnitudes",
                extras={"model_id": model_id},
            ),
        ]
