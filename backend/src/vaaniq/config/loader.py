"""Layered configuration loader.

Order: defaults → YAML files → environment → CLI overrides (ROADMAP-004).
Unknown keys raise ``ValidationError`` / ``ConfigurationError``.
"""

from __future__ import annotations

import os
from collections.abc import Mapping, MutableMapping, Sequence
from pathlib import Path
from typing import Any

import yaml
from pydantic import ValidationError

from vaaniq.config.models import AppConfig
from vaaniq.core.errors import ConfigurationError

_ENV_PREFIX = "VAANIQ_"


def _deep_merge(
    base: MutableMapping[str, Any],
    overlay: Mapping[str, Any],
) -> dict[str, Any]:
    """Recursively merge ``overlay`` onto ``base`` without mutating inputs."""
    result: dict[str, Any] = dict(base)
    for key, value in overlay.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, Mapping):
            result[key] = _deep_merge(result[key], value)
        else:
            result[key] = value
    return result


def _read_yaml(path: Path) -> dict[str, Any]:
    """Read a YAML mapping from ``path``."""
    if not path.is_file():
        msg = f"config file not found: {path}"
        raise ConfigurationError(msg)
    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    if raw is None:
        return {}
    if not isinstance(raw, dict):
        msg = f"config root must be a mapping: {path}"
        raise ConfigurationError(msg)
    return raw


def _parse_cors_origins(value: str) -> list[str]:
    """Split a comma-separated CORS origin list."""
    return [part.strip() for part in value.split(",") if part.strip()]


def _env_overlay(environ: Mapping[str, str]) -> dict[str, Any]:
    """Map ``VAANIQ_*`` environment variables onto nested config keys."""
    overlay: dict[str, Any] = {}

    def set_path(*keys: str, value: Any) -> None:
        cursor: dict[str, Any] = overlay
        for key in keys[:-1]:
            nxt = cursor.setdefault(key, {})
            if not isinstance(nxt, dict):
                msg = f"cannot nest env override under non-mapping key {key}"
                raise ConfigurationError(msg)
            cursor = nxt
        cursor[keys[-1]] = value

    mapping: dict[str, tuple[str, ...]] = {
        "ENV": ("env",),
        "LOG_LEVEL": ("log_level",),
        "DATABASE_URL": ("database_url",),
        "SEED": ("seed",),
        "API_HOST": ("api", "host"),
        "API_PORT": ("api", "port"),
        "CORS_ORIGINS": ("api", "cors_origins"),
        "MAX_UPLOAD_BYTES": ("api", "max_upload_bytes"),
        "MAX_AUDIO_DURATION_SEC": ("api", "max_audio_duration_sec"),
        "OBJECT_STORE_ROOT": ("paths", "object_store_root"),
        "EMBEDDING_CACHE_ROOT": ("paths", "embedding_cache_root"),
    }

    for suffix, path in mapping.items():
        env_key = f"{_ENV_PREFIX}{suffix}"
        if env_key not in environ:
            continue
        raw = environ[env_key]
        if suffix == "SEED" or suffix == "API_PORT" or suffix.startswith("MAX_"):
            set_path(*path, value=int(raw))
        elif suffix == "CORS_ORIGINS":
            set_path(*path, value=_parse_cors_origins(raw))
        else:
            set_path(*path, value=raw)
    return overlay


def load_config(
    yaml_paths: Sequence[Path] | None = None,
    *,
    environ: Mapping[str, str] | None = None,
    cli_overrides: Mapping[str, Any] | None = None,
) -> AppConfig:
    """Load ``AppConfig`` with layered precedence.

    Args:
        yaml_paths: Optional YAML files merged in order (later wins).
        environ: Environment mapping; defaults to ``os.environ``.
        cli_overrides: Nested or flat mapping applied last (highest precedence).

    Returns:
        Validated ``AppConfig``.

    Raises:
        ConfigurationError: On missing files, bad YAML shape, or validation failure
            (including unknown keys).
    """
    data: dict[str, Any] = AppConfig().model_dump(mode="json")
    # Re-hydrate Path fields as strings for merge friendliness; validate at end.
    for path in yaml_paths or ():
        data = _deep_merge(data, _read_yaml(Path(path)))

    env_map = environ if environ is not None else os.environ
    data = _deep_merge(data, _env_overlay(env_map))

    if cli_overrides:
        data = _deep_merge(data, dict(cli_overrides))

    try:
        return AppConfig.model_validate(data)
    except ValidationError as exc:
        raise ConfigurationError(str(exc)) from exc


def default_config_paths(repo_root: Path | None = None) -> list[Path]:
    """Return the default YAML stack for local development.

    Args:
        repo_root: Repository root; discovered by walking parents for
            ``configs/base.yaml`` when omitted.
    """
    root = repo_root
    if root is None:
        here = Path(__file__).resolve()
        for parent in here.parents:
            candidate = parent / "configs" / "base.yaml"
            if candidate.is_file():
                root = parent
                break
        else:
            msg = "could not locate configs/base.yaml from package path"
            raise ConfigurationError(msg)
    return [
        root / "configs" / "base.yaml",
        root / "configs" / "env" / "local.yaml",
    ]
