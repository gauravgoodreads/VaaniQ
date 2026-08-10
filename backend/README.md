# VaaniQ backend

Python 3.11 package for detection, calibration, evaluation, and the FastAPI
inference service.

**REQs served (scaffold):** REQ-001, REQ-092, REQ-139  
**Roadmap:** ROADMAP-002 (this package), ROADMAP-003+ (core onwards)

## Quick commands

```bash
cd backend
uv pip install -e ".[dev]"
ruff check src tests
mypy --strict src
pytest
```

See repo-root `Makefile` (ROADMAP-009) once added.
