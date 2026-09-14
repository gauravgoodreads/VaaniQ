# Fail if regenerating OpenAPI types changes generated output (Phase 1 step 11/13).
$ErrorActionPreference = "Stop"
$Root = Resolve-Path (Join-Path $PSScriptRoot "..")
Set-Location $Root

$Generated = @(
  "frontend/src/api/generated/openapi.json",
  "frontend/src/api/generated/schema.ts"
)
$Before = @{}
foreach ($Path in $Generated) {
  $Before[$Path] = if (Test-Path $Path) { (Get-FileHash $Path -Algorithm SHA256).Hash } else { "MISSING" }
}

powershell -NoProfile -ExecutionPolicy Bypass -File (Join-Path $Root "scripts/gen_api_types.ps1")
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

$Changed = @(
  foreach ($Path in $Generated) {
    $After = if (Test-Path $Path) { (Get-FileHash $Path -Algorithm SHA256).Hash } else { "MISSING" }
    if ($Before[$Path] -ne $After) { $Path }
  }
)
if ($Changed.Count -ne 0) {
  Write-Host "ERROR: OpenAPI generated types are out of date."
  Write-Host "Changed after regeneration: $($Changed -join ', ')"
  Write-Host "Run scripts/gen_api_types.ps1 and include frontend/src/api/generated/."
  exit 1
}

Write-Host "API types are in sync."
