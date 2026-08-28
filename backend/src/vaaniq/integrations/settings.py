"""External model integrations — Groq, Whisper, Hugging Face (optional via env)."""

from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path


def _env(name: str, default: str = "") -> str:
    value = os.environ.get(name, "").strip()
    if value:
        return value
    # Also read repo .env without requiring python-dotenv at import time.
    root = Path(__file__).resolve().parents[4]
    env_path = root / ".env"
    if env_path.is_file():
        for line in env_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, _, v = line.partition("=")
            if k.strip() == name:
                return v.strip().strip('"').strip("'")
    return default


@dataclass(frozen=True, slots=True)
class IntegrationSettings:
    """Runtime flags for optional cloud / local speech models."""

    groq_api_key: str
    hf_token: str
    whisper_backend: str  # auto | groq | local | off
    groq_whisper_model: str
    groq_llm_model: str
    local_whisper_model: str
    enable_llm_enrichment: bool

    @property
    def groq_enabled(self) -> bool:
        return bool(self.groq_api_key)

    @property
    def hf_enabled(self) -> bool:
        return bool(self.hf_token)


@lru_cache(maxsize=1)
def get_integration_settings() -> IntegrationSettings:
    """Load integration settings from process env / `.env`."""
    return IntegrationSettings(
        groq_api_key=_env("GROQ_API_KEY") or _env("GROQ_KEY"),
        hf_token=_env("HF_TOKEN") or _env("HUGGINGFACE_HUB_TOKEN"),
        whisper_backend=_env("VAANIQ_WHISPER_BACKEND", "auto") or "auto",
        groq_whisper_model=_env("VAANIQ_GROQ_WHISPER_MODEL", "whisper-large-v3")
        or "whisper-large-v3",
        groq_llm_model=_env("VAANIQ_GROQ_LLM_MODEL", "openai/gpt-oss-20b")
        or "openai/gpt-oss-20b",
        local_whisper_model=_env("VAANIQ_LOCAL_WHISPER_MODEL", "base") or "base",
        enable_llm_enrichment=(_env("VAANIQ_LLM_ENRICHMENT", "1") or "1") not in {
            "0",
            "false",
            "False",
            "off",
        },
    )
