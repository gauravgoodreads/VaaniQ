"""Models package public exports."""

from __future__ import annotations

from vaaniq.models.aasist.classifier import AASISTClassifier
from vaaniq.models.baselines.english_only import EnglishOnlyXlsrAasistBaseline
from vaaniq.models.baselines.lfcc_gmm.classifier import LfccGmmClassifier
from vaaniq.models.baselines.rawnet2.classifier import RawNet2Classifier
from vaaniq.models.registry import ModelRegistry

__all__ = [
    "AASISTClassifier",
    "EnglishOnlyXlsrAasistBaseline",
    "LfccGmmClassifier",
    "ModelRegistry",
    "RawNet2Classifier",
]
