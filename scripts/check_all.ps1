# Windows equivalent of make check (Phase 1 step 15 / ROADMAP-009).
# Run from repo root:
#   powershell -File scripts/check_all.ps1

$ErrorActionPreference = "Stop"
$Root = Resolve-Path (Join-Path $PSScriptRoot "..")
$Backend = Join-Path $Root "backend"
$Frontend = Join-Path $Root "frontend"
$Py = Join-Path $Backend ".venv/Scripts/python.exe"

if (-not (Test-Path $Py)) {
  Write-Host 'Missing backend/.venv - create with: cd backend; uv venv; uv pip install -e ".[dev]"'
  exit 1
}

function Invoke-Step {
  param(
    [Parameter(Mandatory = $true)][string]$Name,
    [Parameter(Mandatory = $true)][scriptblock]$Block
  )
  Write-Host "==> $Name"
  & $Block
  if ($LASTEXITCODE -ne 0) {
    Write-Host "FAILED: $Name"
    exit $LASTEXITCODE
  }
}

Set-Location $Backend
Invoke-Step "ruff check" { & $Py -m ruff check src tests }
Invoke-Step "ruff format" { & $Py -m ruff format --check src tests }
Invoke-Step "mypy" { & $Py -m mypy --strict src }
Invoke-Step "pytest" { & $Py -m pytest -q }

Set-Location $Frontend
Invoke-Step "tsc" { npm run typecheck }
Invoke-Step "eslint" { npm run lint }
Invoke-Step "vitest" { npm run test }

Set-Location $Root
Invoke-Step "no-telugu" { & $Py (Join-Path $Root "scripts/check_no_telugu.py") }
Invoke-Step "api-types-drift" {
  powershell -NoProfile -ExecutionPolicy Bypass -File (Join-Path $Root "scripts/check_api_types_drift.ps1")
}

Write-Host "check_all.ps1 passed"
