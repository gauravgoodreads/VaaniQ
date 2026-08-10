# Generate frontend OpenAPI TypeScript types (Phase 1 step 11).
# Windows equivalent of gen_api_types.sh — run from repo root:
#   powershell -File scripts/gen_api_types.ps1

$ErrorActionPreference = "Stop"
$Root = Resolve-Path (Join-Path $PSScriptRoot "..")
$GenDir = Join-Path $Root "frontend/src/api/generated"
$OpenApiJson = Join-Path $GenDir "openapi.json"
$SchemaTs = Join-Path $GenDir "schema.ts"

New-Item -ItemType Directory -Force -Path $GenDir | Out-Null

if ($env:VAANIQ_OPENAPI_URL) {
  Write-Host "fetching OpenAPI from $($env:VAANIQ_OPENAPI_URL)"
  Invoke-WebRequest -Uri $env:VAANIQ_OPENAPI_URL -OutFile $OpenApiJson
} else {
  Write-Host "exporting OpenAPI from create_app().openapi()"
  $py = Join-Path $Root "backend/.venv/Scripts/python.exe"
  if (-not (Test-Path $py)) {
    $py = "python"
  }
  & $py (Join-Path $Root "scripts/export_openapi.py") --out $OpenApiJson
  if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
}

Write-Host "generating $SchemaTs"
Push-Location (Join-Path $Root "frontend")
try {
  npx --yes openapi-typescript $OpenApiJson -o $SchemaTs
  if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
} finally {
  Pop-Location
}

@'
# generated

OpenAPI artefacts produced by `scripts/gen_api_types.sh` / `gen_api_types.ps1`.

- `openapi.json` — schema dump from FastAPI
- `schema.ts` — TypeScript types from `openapi-typescript`

**Do not hand-edit.** Regenerate with the scripts above or `npm run gen:api-types`.
'@ | Set-Content -Path (Join-Path $GenDir "README.md") -Encoding utf8

Write-Host "done: $SchemaTs"
