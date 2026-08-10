#!/usr/bin/env bash
# Fail if regenerating OpenAPI types produces a git diff (Phase 1 step 11/13).
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${ROOT}"

./scripts/gen_api_types.sh

if ! git diff --quiet -- frontend/src/api/generated/; then
  echo "ERROR: OpenAPI generated types are out of date."
  echo "Run ./scripts/gen_api_types.sh and commit frontend/src/api/generated/"
  git --no-pager diff -- frontend/src/api/generated/
  exit 1
fi

echo "API types are in sync."
