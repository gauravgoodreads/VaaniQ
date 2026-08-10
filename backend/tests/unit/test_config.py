"""Tests for layered configuration loading (ROADMAP-004)."""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from vaaniq.config import AppConfig, default_config_paths, load_config
from vaaniq.core.errors import ConfigurationError
from vaaniq.core.types import Language


def test_load_defaults_without_yaml() -> None:
    """Defaults alone produce a valid AppConfig."""
    cfg = load_config(yaml_paths=[], environ={})
    assert cfg.project.name == "VaaniQ"
    assert cfg.seed == 42
    assert list(cfg.languages.codes) == list(Language)


def test_yaml_overrides_defaults(tmp_path: Path) -> None:
    """YAML values override baked-in defaults."""
    path = tmp_path / "cfg.yaml"
    path.write_text(
        yaml.safe_dump({"seed": 7, "log_level": "DEBUG"}),
        encoding="utf-8",
    )
    cfg = load_config(yaml_paths=[path], environ={})
    assert cfg.seed == 7
    assert cfg.log_level == "DEBUG"


def test_env_overrides_yaml(tmp_path: Path) -> None:
    """Environment wins over YAML."""
    path = tmp_path / "cfg.yaml"
    path.write_text(yaml.safe_dump({"api": {"port": 8000}}), encoding="utf-8")
    cfg = load_config(
        yaml_paths=[path],
        environ={"VAANIQ_API_PORT": "9001", "VAANIQ_LOG_LEVEL": "WARNING"},
    )
    assert cfg.api.port == 9001
    assert cfg.log_level == "WARNING"


def test_cli_overrides_env(tmp_path: Path) -> None:
    """CLI overrides have the highest precedence."""
    path = tmp_path / "cfg.yaml"
    path.write_text(yaml.safe_dump({"seed": 1}), encoding="utf-8")
    cfg = load_config(
        yaml_paths=[path],
        environ={"VAANIQ_SEED": "2"},
        cli_overrides={"seed": 3},
    )
    assert cfg.seed == 3


def test_unknown_yaml_key_fails(tmp_path: Path) -> None:
    """Unknown keys are rejected (extra=forbid)."""
    path = tmp_path / "bad.yaml"
    path.write_text(yaml.safe_dump({"not_a_real_key": True}), encoding="utf-8")
    with pytest.raises(ConfigurationError):
        load_config(yaml_paths=[path], environ={})


def test_unknown_nested_key_fails(tmp_path: Path) -> None:
    """Unknown nested keys are rejected."""
    path = tmp_path / "bad.yaml"
    path.write_text(
        yaml.safe_dump({"api": {"host": "127.0.0.1", "mystery": 1}}),
        encoding="utf-8",
    )
    with pytest.raises(ConfigurationError):
        load_config(yaml_paths=[path], environ={})


def test_incomplete_languages_rejected(tmp_path: Path) -> None:
    """Language list must equal the Language enum (REQ-132, REQ-139)."""
    path = tmp_path / "langs.yaml"
    path.write_text(
        yaml.safe_dump({"languages": {"codes": ["hi", "mr"]}}),
        encoding="utf-8",
    )
    with pytest.raises(ConfigurationError):
        load_config(yaml_paths=[path], environ={})


def test_cors_wildcard_forbidden_in_prod() -> None:
    """Prod profile must not allow wildcard CORS (REQ-136)."""
    cfg = AppConfig.model_validate(
        {
            "env": "prod",
            "api": {"cors_origins": ["*"]},
        }
    )
    with pytest.raises(ValueError, match="cors_origins"):
        cfg.cors_origins_for_env()


def test_default_config_paths_exist() -> None:
    """Repo default YAML stack is present on disk."""
    paths = default_config_paths()
    assert paths[0].name == "base.yaml"
    assert paths[0].is_file()
    assert paths[1].name == "local.yaml"
    assert paths[1].is_file()
    cfg = load_config(yaml_paths=paths, environ={})
    assert cfg.env == "local"
    assert [c.value for c in cfg.languages.codes] == ["hi", "mr", "ta"]


def test_missing_yaml_raises(tmp_path: Path) -> None:
    """Missing YAML path raises ConfigurationError."""
    with pytest.raises(ConfigurationError, match="not found"):
        load_config(yaml_paths=[tmp_path / "missing.yaml"], environ={})


def test_cors_origins_from_env() -> None:
    """Comma-separated CORS origins parse into a list."""
    cfg = load_config(
        yaml_paths=[],
        environ={"VAANIQ_CORS_ORIGINS": "http://a.test, http://b.test"},
    )
    assert cfg.api.cors_origins == ["http://a.test", "http://b.test"]
