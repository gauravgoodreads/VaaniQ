#!/usr/bin/env bash
# Fail if regenerating OpenAPI types changes generated output (Phase 1 step 11/13).
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${ROOT}"

OPENAPI="frontend/src/api/generated/openapi.json"
SCHEMA="frontend/src/api/generated/schema.ts"
hash_or_missing() {
  if [[ -f "$1" ]]; then
    sha256sum "$1" | awk '{print $1}'
  else
    printf 'MISSING\n'
  fi
}

before_openapi="$(hash_or_missing "${OPENAPI}")"
before_schema="$(hash_or_missing "${SCHEMA}")"

./scripts/gen_api_types.sh

after_openapi="$(hash_or_missing "${OPENAPI}")"
after_schema="$(hash_or_missing "${SCHEMA}")"
if [[ "${before_openapi}" != "${after_openapi}" || "${before_schema}" != "${after_schema}" ]]; then
  echo "ERROR: OpenAPI generated types are out of date."
  echo "Run ./scripts/gen_api_types.sh and include frontend/src/api/generated/."
  exit 1
fi

echo "API types are in sync."
