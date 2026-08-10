"""Package metadata smoke tests (ROADMAP-002)."""

from __future__ import annotations

import importlib
import pkgutil
from collections.abc import Iterator

import vaaniq


def _walk_modules(package_name: str) -> Iterator[str]:
    """Yield importable module names under ``package_name``."""
    package = importlib.import_module(package_name)
    if not hasattr(package, "__path__"):
        return
    prefix = package.__name__ + "."
    for module in pkgutil.walk_packages(package.__path__, prefix=prefix):
        yield module.name


def test_version_is_semver_stub() -> None:
    """Package version is set for scaffolding (REQ-001)."""
    assert vaaniq.__version__ == "0.1.0"


def test_import_all_scaffold_packages() -> None:
    """Every scaffolded subpackage imports cleanly (ROADMAP-002)."""
    names = list(_walk_modules("vaaniq"))
    assert names, "expected scaffold packages under vaaniq"
    for name in names:
        importlib.import_module(name)
