$ErrorActionPreference = 'Stop'
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

if (-not (Get-Command uv -ErrorAction SilentlyContinue)) { throw 'uv is required. Install it from https://docs.astral.sh/uv/getting-started/installation/ and rerun.' }
if (-not (Get-Command node -ErrorAction SilentlyContinue)) { throw 'Node.js 24 LTS is required. Install it from https://nodejs.org/en/download/ and reopen PowerShell.' }

$NodeVersion = (node --version).Trim()
if ($NodeVersion -notmatch '^v24\.') { throw "Expected Node.js 24.x from .nvmrc, found $NodeVersion. Install Node.js 24 LTS, then rerun." }

$env:PYTHONPATH = Join-Path $Root 'apps/api/src'
uv run --locked --python 3.13.16 ruff check apps/api/src apps/api/tests
uv run --locked --python 3.13.16 pytest
Push-Location (Join-Path $Root 'apps/web')
try {
  npm run typecheck
  npm run build
} finally {
  Pop-Location
}
Write-Host 'Company OS baseline checks passed.' -ForegroundColor Green
