"""LFCC + GMM baseline (ROADMAP-031 / REQ-042).

Classical front-end: linear-frequency cepstral coefficients + diagonal GMMs
for real vs fake. Pure NumPy (no sklearn) for CI without ``[ml]``.
# ASSUMPTION: OQ-014-style defaults from ``configs/model/lfcc_gmm.yaml``.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import structlog
from numpy.typing import NDArray

from vaaniq.config.domains import LfccGmmConfig
from vaaniq.core.domain.entities import Embedding, Logits, Waveform
from vaaniq.core.errors import ModelNotReadyError
from vaaniq.core.ports.classifier import Classifier
from vaaniq.core.types import Label

log = structlog.get_logger(__name__)

Float32Array = NDArray[np.float32]


def extract_lfcc(wav: Waveform, config: LfccGmmConfig) -> Float32Array:
    """Extract mean LFCC vector from a mono waveform (REQ-042).

    Args:
        wav: Preprocessed waveform.
        config: LFCC/GMM hyperparameters.

    Returns:
        Mean cepstral vector of length ``n_lfcc``.
    """
    samples = np.asarray(wav.samples, dtype=np.float32)
    if samples.size < config.n_fft:
        samples = np.pad(samples, (0, config.n_fft - samples.size))
    # Framing
    hop = config.hop_length
    win = config.win_length
    n_frames = 1 + max(0, (samples.size - win) // hop)
    frames = np.stack(
        [samples[i * hop : i * hop + win] for i in range(n_frames)],
        axis=0,
    ).astype(np.float32)
    window = np.hanning(win).astype(np.float32)
    frames = frames * window
    spec = np.abs(np.fft.rfft(frames, n=config.n_fft)).astype(np.float32)
    # Linear filterbank energies → log → DCT (LFCC)
    n_bins = spec.shape[1]
    n_filters = min(config.n_lfcc * 2, n_bins)
    edges = np.linspace(0, n_bins, n_filters + 2, dtype=np.float32)
    fb = np.zeros((n_filters, n_bins), dtype=np.float32)
    for i in range(n_filters):
        left, center, right = int(edges[i]), int(edges[i + 1]), int(edges[i + 2])
        if center > left:
            fb[i, left:center] = np.linspace(0, 1, center - left, dtype=np.float32)
        if right > center:
            fb[i, center:right] = np.linspace(1, 0, right - center, dtype=np.float32)
    energies = np.maximum(spec @ fb.T, 1e-10)
    log_e = np.log(energies).astype(np.float32)
    # DCT-II
    n = log_e.shape[1]
    k = np.arange(config.n_lfcc)[:, None]
    n_idx = np.arange(n)[None, :]
    dct = np.cos(np.pi * k * (2 * n_idx + 1) / (2 * n)).astype(np.float32)
    cepstra = (log_e @ dct.T).astype(np.float32)
    return np.asarray(np.mean(cepstra, axis=0), dtype=np.float32)


class _DiagGmm:
    """Diagonal-covariance GMM with EM (compact implementation)."""

    def __init__(self, n_components: int, dim: int, rng: np.random.Generator) -> None:
        self.n_components = n_components
        self.dim = dim
        self.rng = rng
        self.weights = np.full(n_components, 1.0 / n_components, dtype=np.float32)
        self.means = rng.normal(0.0, 0.1, size=(n_components, dim)).astype(np.float32)
        self.vars = np.ones((n_components, dim), dtype=np.float32)

    def fit(self, x: Float32Array, n_iter: int = 5) -> None:
        """Run a few EM iterations."""
        if x.shape[0] == 0:
            return
        # k-means++ style init on subset
        n = min(self.n_components, x.shape[0])
        idx = self.rng.choice(x.shape[0], size=n, replace=False)
        self.means[:n] = x[idx]
        for _ in range(n_iter):
            resp = self._responsibilities(x)
            nk = np.sum(resp, axis=0) + 1e-6
            self.weights = (nk / float(x.shape[0])).astype(np.float32)
            self.means = ((resp.T @ x) / nk[:, None]).astype(np.float32)
            diff = x[:, None, :] - self.means[None, :, :]
            self.vars = (np.sum(resp[:, :, None] * np.square(diff), axis=0) / nk[:, None]).astype(
                np.float32
            )
            self.vars = np.maximum(self.vars, 1e-4)

    def _responsibilities(self, x: Float32Array) -> Float32Array:
        log_prob = self._log_prob(x)
        log_prob -= np.max(log_prob, axis=1, keepdims=True)
        prob = np.exp(log_prob)
        return np.asarray(prob / np.sum(prob, axis=1, keepdims=True), dtype=np.float32)

    def _log_prob(self, x: Float32Array) -> Float32Array:
        # [N, K]
        out = np.zeros((x.shape[0], self.n_components), dtype=np.float32)
        for k in range(self.n_components):
            var = self.vars[k]
            diff = x - self.means[k]
            quad = np.sum(np.square(diff) / var, axis=1)
            log_det = np.sum(np.log(var))
            out[:, k] = np.log(self.weights[k] + 1e-12) - 0.5 * (
                log_det + quad + self.dim * np.log(2 * np.pi)
            )
        return out

    def score(self, x: Float32Array) -> Float32Array:
        """Log-likelihood per sample."""
        log_prob = self._log_prob(x)
        m = np.max(log_prob, axis=1, keepdims=True)
        return np.asarray(
            m[:, 0] + np.log(np.sum(np.exp(log_prob - m), axis=1)),
            dtype=np.float32,
        )


class LfccGmmClassifier(Classifier):
    """LFCC + dual GMM baseline (REQ-042)."""

    def __init__(
        self,
        config: LfccGmmConfig | None = None,
        *,
        rng: np.random.Generator | None = None,
    ) -> None:
        """Bind config and empty GMMs."""
        self._config = config or LfccGmmConfig()
        self._rng = rng or np.random.default_rng(42)
        # Unit tests may pass small n_components via config; keep practical default
        # for CI speed when n_components is large.
        self._n_components = min(self._config.n_components, 8)
        self._real: _DiagGmm | None = None
        self._fake: _DiagGmm | None = None
        self._dim = self._config.n_lfcc

    def fit(self, waveforms: list[Waveform], labels: list[Label]) -> None:
        """Fit real/fake GMMs from waveforms.

        Args:
            waveforms: Training waveforms.
            labels: Aligned labels.
        """
        feats = np.stack([extract_lfcc(w, self._config) for w in waveforms], axis=0)
        y = np.array([0 if lab == Label.REAL else 1 for lab in labels], dtype=np.int64)
        self._dim = feats.shape[1]
        self._real = _DiagGmm(self._n_components, self._dim, self._rng)
        self._fake = _DiagGmm(self._n_components, self._dim, self._rng)
        self._real.fit(feats[y == 0])
        self._fake.fit(feats[y == 1])
        log.info("lfcc_gmm_fitted", n=int(feats.shape[0]), dim=self._dim)

    def predict(self, emb: Embedding) -> Logits:
        """Score an LFCC vector packaged as ``Embedding.vector`` (REQ-042).

        For waveform inference use ``predict_waveform``.
        """
        if self._real is None or self._fake is None:
            raise ModelNotReadyError("LfccGmmClassifier is not fitted")
        x = np.asarray(emb.vector, dtype=np.float32).reshape(1, -1)
        if x.shape[1] != self._dim:
            padded = np.zeros((1, self._dim), dtype=np.float32)
            n = min(self._dim, x.shape[1])
            padded[:, :n] = x[:, :n]
            x = padded
        ll_real = float(self._real.score(x)[0])
        ll_fake = float(self._fake.score(x)[0])
        return Logits(
            values=np.array([ll_real, ll_fake], dtype=np.float32),
            class_order=(Label.REAL, Label.FAKE),
        )

    def predict_waveform(self, wav: Waveform) -> Logits:
        """Extract LFCC then score."""
        feat = extract_lfcc(wav, self._config)
        return self.predict(Embedding(vector=feat, model_id="lfcc_gmm", clip_id="adhoc"))

    def save(self, path: Path) -> None:
        """Persist GMM parameters."""
        if self._real is None or self._fake is None:
            raise ModelNotReadyError("nothing to save")
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        np.savez_compressed(
            path,
            real_w=self._real.weights,
            real_m=self._real.means,
            real_v=self._real.vars,
            fake_w=self._fake.weights,
            fake_m=self._fake.means,
            fake_v=self._fake.vars,
        )
        path.with_suffix(".json").write_text(
            json.dumps({"dim": self._dim, "n_components": self._n_components}),
            encoding="utf-8",
        )

    def load(self, path: Path) -> None:
        """Load GMM parameters."""
        path = Path(path)
        data = np.load(path)
        meta = json.loads(path.with_suffix(".json").read_text(encoding="utf-8"))
        self._dim = int(meta["dim"])
        self._n_components = int(meta["n_components"])
        self._real = _DiagGmm(self._n_components, self._dim, self._rng)
        self._fake = _DiagGmm(self._n_components, self._dim, self._rng)
        self._real.weights = data["real_w"].astype(np.float32)
        self._real.means = data["real_m"].astype(np.float32)
        self._real.vars = data["real_v"].astype(np.float32)
        self._fake.weights = data["fake_w"].astype(np.float32)
        self._fake.means = data["fake_m"].astype(np.float32)
        self._fake.vars = data["fake_v"].astype(np.float32)
