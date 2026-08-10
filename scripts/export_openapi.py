"""Export the FastAPI OpenAPI schema to JSON (Phase 1 step 11).

Does not require a running server — uses ``create_app().openapi()``, which is the
same document served at ``/openapi.json``.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def _repo_root() -> Path:
    """Return the repository root (parent of ``scripts/``)."""
    return Path(__file__).resolve().parents[1]


def export_openapi(destination: Path) -> None:
    """Write the OpenAPI document to ``destination``.

    Args:
        destination: Output JSON path.
    """
    # Ensure backend package is importable when run from repo root.
    backend_src = _repo_root() / "backend" / "src"
    if str(backend_src) not in sys.path:
        sys.path.insert(0, str(backend_src))

    from vaaniq.api.app import create_app

    schema = create_app().openapi()
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(
        json.dumps(schema, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def main(argv: list[str] | None = None) -> int:
    """CLI entrypoint."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--out",
        type=Path,
        default=_repo_root() / "frontend" / "src" / "api" / "generated" / "openapi.json",
        help="Output path for openapi.json",
    )
    args = parser.parse_args(argv)
    export_openapi(args.out)
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
