"""Time-frequency attention map (OQ-022 COULD; Phase 4 UI)."""

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


class AttentionMapExplainer(Explainer):
    """Write a downsampled time-frequency attention JSON (REQ-075 family)."""

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
        """Explain via normalised STFT energy as an attention proxy."""
        self._root.mkdir(parents=True, exist_ok=True)
        mag = stft_magnitude(wav.samples, n_fft=512, hop_length=160)
        small = mag[::4, ::4]
        attn = small / (np.max(small) + 1e-8)
        path = self._root / f"{clip.clip_id}_{model_id}_attention.json"
        path.write_text(
            json.dumps(
                {
                    "clip_id": clip.clip_id,
                    "model_id": model_id,
                    "attention": attn.astype(float).tolist(),
                }
            ),
            encoding="utf-8",
        )
        log.info("attention_map_written", path=str(path))
        return [
            ExplanationArtefact(
                kind="attention_map",
                uri=str(path),
                summary="Time-frequency attention proxy (STFT energy)",
                extras={"model_id": model_id},
            )
        ]
