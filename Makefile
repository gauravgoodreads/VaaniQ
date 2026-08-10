# VaaniQ developer gates (ROADMAP-009 / Phase 1 step 13).
# Requires: GNU make, uv, Python 3.11, Node 22+, Docker (for docker-* targets).
#
# On Windows without make, run the underlying commands from deployment/README.md
# and frontend/README.md, or use Git Bash.

.PHONY: setup install dev test lint format typecheck check \
	docker-up docker-down clean gen-types migrate telugu

ROOT := $(abspath $(dir $(lastword $(MAKEFILE_LIST))))
BACKEND := $(ROOT)/backend
FRONTEND := $(ROOT)/frontend
UV ?= uv
PYTHON ?= python3
NPM ?= npm

setup: install
	@echo "setup complete"

install:
	cd "$(BACKEND)" && $(UV) venv && $(UV) pip install -e ".[dev]"
	cd "$(FRONTEND)" && $(NPM) ci

dev:
	@echo "Start API:  cd backend && uv run uvicorn vaaniq.api.app:create_app --factory --reload"
	@echo "Start Web:  cd frontend && npm run dev"

lint:
	cd "$(BACKEND)" && $(UV) run ruff check src tests
	cd "$(BACKEND)" && $(UV) run ruff format --check src tests
	cd "$(FRONTEND)" && $(NPM) run lint
	$(PYTHON) "$(ROOT)/scripts/check_no_telugu.py"

format:
	cd "$(BACKEND)" && $(UV) run ruff format src tests
	cd "$(BACKEND)" && $(UV) run ruff check --fix src tests

typecheck:
	cd "$(BACKEND)" && $(UV) run mypy --strict src
	cd "$(FRONTEND)" && $(NPM) run typecheck

test:
	cd "$(BACKEND)" && $(UV) run pytest
	cd "$(FRONTEND)" && $(NPM) run test

gen-types:
	bash "$(ROOT)/scripts/gen_api_types.sh"

migrate:
	cd "$(BACKEND)" && $(UV) run alembic upgrade head

telugu:
	$(PYTHON) "$(ROOT)/scripts/check_no_telugu.py"

check: lint typecheck test
	bash "$(ROOT)/scripts/check_api_types_drift.sh"
	@echo "make check passed"

# Windows without GNU make:
#   powershell -File scripts/check_all.ps1

docker-up:
	docker compose -f "$(ROOT)/deployment/docker-compose.yml" up --build -d

docker-down:
	docker compose -f "$(ROOT)/deployment/docker-compose.yml" down

clean:
	rm -rf "$(BACKEND)/.pytest_cache" "$(BACKEND)/.mypy_cache" "$(BACKEND)/.ruff_cache" \
		"$(BACKEND)/htmlcov" "$(BACKEND)/.coverage" \
		"$(FRONTEND)/dist" "$(FRONTEND)/coverage" \
		"$(ROOT)/vaaniq.db"
	find "$(BACKEND)" -type d -name __pycache__ -prune -exec rm -rf {} +
