# Fail if regenerating OpenAPI types produces a git diff (Phase 1 step 11/13).
$ErrorActionPreference = "Stop"
$Root = Resolve-Path (Join-Path $PSScriptRoot "..")
Set-Location $Root

powershell -NoProfile -ExecutionPolicy Bypass -File (Join-Path $Root "scripts/gen_api_types.ps1")
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

git diff --quiet -- frontend/src/api/generated/
if ($LASTEXITCODE -ne 0) {
  Write-Host "ERROR: OpenAPI generated types are out of date."
  Write-Host "Run scripts/gen_api_types.ps1 and commit frontend/src/api/generated/"
  git --no-pager diff -- frontend/src/api/generated/
  exit 1
}

Write-Host "API types are in sync."
