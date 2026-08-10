"""Typed application configuration models.

Fails loudly on unknown keys (``extra='forbid'``). ROADMAP-004 / REQ-136.
"""

from __future__ import annotations

from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from vaaniq.core.types import Language

EnvName = Literal["local", "dev", "prod"]


class ProjectConfig(BaseModel):
    """Project identity metadata (REQ-001)."""

    model_config = ConfigDict(extra="forbid")

    name: str = "VaaniQ"
    version: str = "0.1.0"


class LanguagesConfig(BaseModel):
    """Configured project languages (REQ-132, REQ-139)."""

    model_config = ConfigDict(extra="forbid")

    codes: list[Language] = Field(default_factory=lambda: list(Language))

    @field_validator("codes")
    @classmethod
    def _must_match_language_enum(cls, value: list[Language]) -> list[Language]:
        """Reject empty or incomplete language sets."""
        if not value:
            msg = "languages.codes must be non-empty"
            raise ValueError(msg)
        expected = set(Language)
        got = set(value)
        if got != expected:
            want = sorted(m.value for m in Language)
            got_vals = sorted(m.value for m in got)
            msg = f"languages.codes must equal {want}, got {got_vals}"
            raise ValueError(msg)
        # Preserve enum iteration order
        return list(Language)


class ApiConfig(BaseModel):
    """HTTP API surface settings (REQ-136, REQ-135)."""

    model_config = ConfigDict(extra="forbid")

    host: str = "0.0.0.0"
    port: int = 8000
    cors_origins: list[str] = Field(
        default_factory=lambda: [
            "http://localhost:5173",
            "http://127.0.0.1:5173",
        ]
    )
    # ASSUMPTION: values introduced in .env.example (ROADMAP-001); refine in OQ if needed.
    max_upload_bytes: int = 26_214_400
    max_audio_duration_sec: int = 120


class PathsConfig(BaseModel):
    """Local filesystem roots for blobs and caches."""

    model_config = ConfigDict(extra="forbid")

    object_store_root: Path = Path("./data/object_store")
    embedding_cache_root: Path = Path("./data/embedding_cache")


class AppConfig(BaseModel):
    """Root VaaniQ configuration object.

    Loaded via ``load_config`` with layering: defaults → YAML → env → CLI.
    """

    model_config = ConfigDict(extra="forbid")

    env: EnvName = "local"
    log_level: str = "INFO"
    # ASSUMPTION: OQ-021 — SQLite by default for local.
    database_url: str = "sqlite:///./vaaniq.db"
    seed: int = 42
    project: ProjectConfig = Field(default_factory=ProjectConfig)
    languages: LanguagesConfig = Field(default_factory=LanguagesConfig)
    api: ApiConfig = Field(default_factory=ApiConfig)
    paths: PathsConfig = Field(default_factory=PathsConfig)

    def cors_origins_for_env(self) -> list[str]:
        """Return CORS origins; prod must not use wildcard (REQ-136)."""
        origins = list(self.api.cors_origins)
        if self.env == "prod" and "*" in origins:
            msg = "cors_origins must not contain '*' in prod"
            raise ValueError(msg)
        return origins
