# Contributing

> How to change VaaniQ safely (ROADMAP-010).

## Before you push

1. No Telugu as a project language (`python scripts/check_no_telugu.py`).
2. Backend: `ruff`, `mypy --strict`, `pytest` (coverage ≥ 80%).
3. Frontend: `tsc`, `eslint`, `vitest` — **zero `any`**.
4. If you changed API schemas: `./scripts/gen_api_types.sh` and commit
   `frontend/src/api/generated/`.
5. Conventional Commits; one logical change per commit.

```bash
make check   # preferred on Linux/macOS/Git Bash
```

## Ambiguity protocol

Do not invent proposal numbers. Open an `OQ-###` in `OPEN_QUESTIONS.md`, pick a
defensible default, mark `# ASSUMPTION: OQ-###`.

## Scope

- Do not drop hard research components — ship ABC + stub + xfail + ROADMAP entry.
- Do not expand beyond the current phase — append ideas to `PROJECT_ROADMAP.md`.

## PR checklist

- [ ] Gates green
- [ ] ROADMAP / REQ IDs cited in new public symbols
- [ ] No secrets, audio, or weights committed
- [ ] Docs updated if behaviour changed

## Code owners / review

Capstone team — MPSTME A.Y. 2026–27. See `LICENSE` for authors.

## TODO

- TODO(ROADMAP-010): add PR template under `.github/PULL_REQUEST_TEMPLATE.md`
- TODO(ROADMAP-009): wire `pre-commit install` into `make setup`
