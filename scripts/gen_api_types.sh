#!/usr/bin/env bash
# Generate frontend OpenAPI TypeScript types (Phase 1 step 11 / ROADMAP-008 follow-on).
# Usage (from repo root):
#   ./scripts/gen_api_types.sh
# Optional live URL override:
#   VAANIQ_OPENAPI_URL=http://127.0.0.1:8000/openapi.json ./scripts/gen_api_types.sh
#
# CI should fail if regenerating produces a git diff under frontend/src/api/generated/.

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
GEN_DIR="${ROOT}/frontend/src/api/generated"
OPENAPI_JSON="${GEN_DIR}/openapi.json"
SCHEMA_TS="${GEN_DIR}/schema.ts"

mkdir -p "${GEN_DIR}"

if [[ -n "${VAANIQ_OPENAPI_URL:-}" ]]; then
  echo "fetching OpenAPI from ${VAANIQ_OPENAPI_URL}"
  curl -fsSL "${VAANIQ_OPENAPI_URL}" -o "${OPENAPI_JSON}"
else
  echo "exporting OpenAPI from create_app().openapi()"
  if [[ -x "${ROOT}/backend/.venv/bin/python" ]]; then
    "${ROOT}/backend/.venv/bin/python" "${ROOT}/scripts/export_openapi.py" --out "${OPENAPI_JSON}"
  elif command -v uv >/dev/null 2>&1; then
    (cd "${ROOT}/backend" && uv run python "${ROOT}/scripts/export_openapi.py" --out "${OPENAPI_JSON}")
  else
    PYTHONPATH="${ROOT}/backend/src${PYTHONPATH:+:${PYTHONPATH}}" \
      python "${ROOT}/scripts/export_openapi.py" --out "${OPENAPI_JSON}"
  fi
fi

echo "generating ${SCHEMA_TS}"
(
  cd "${ROOT}/frontend"
  npx --yes openapi-typescript "${OPENAPI_JSON}" -o "${SCHEMA_TS}"
)

# Marker so humans do not hand-edit.
cat > "${GEN_DIR}/README.md" <<'EOF'
# generated

OpenAPI artefacts produced by `scripts/gen_api_types.sh`.

- `openapi.json` — schema dump from FastAPI (`create_app().openapi()` or live URL)
- `schema.ts` — TypeScript types from `openapi-typescript`

**Do not hand-edit.** Regenerate with `./scripts/gen_api_types.sh` (or
`npm run gen:api-types` in `frontend/`).
EOF

echo "done: ${SCHEMA_TS}"
