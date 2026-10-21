[CmdletBinding()]
param(
    [switch]$WithDockerDatabase,
    [switch]$SkipFrontendBuild
)

$ErrorActionPreference = 'Stop'
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

function Require-Command([string]$Name, [string]$Instruction) {
    if (-not (Get-Command $Name -ErrorAction SilentlyContinue)) {
        throw "$Name is required. $Instruction"
    }
}

Require-Command 'git' 'Install Git for Windows and reopen PowerShell.'
Require-Command 'uv' 'Install uv from https://docs.astral.sh/uv/getting-started/installation/ and reopen PowerShell.'
Require-Command 'node' 'Install Node.js 24 LTS from https://nodejs.org/en/download/ and reopen PowerShell.'
Require-Command 'npm' 'Install Node.js 24 LTS; npm is included with the installer.'

$UvVersionLine = (uv --version).Trim()
if ($UvVersionLine -match '^uv ([0-9]+\.[0-9]+\.[0-9]+)') {
    $ParsedUvVersion = [version]$Matches[1]
    if ($ParsedUvVersion -lt [version]'0.13.4') {
        throw "uv 0.13.4 or newer is required to provision the pinned Python runtime. Current: $UvVersionLine. Update with 'uv self update' or reinstall uv from https://docs.astral.sh/uv/getting-started/installation/."
    }
} else {
    throw "Could not parse uv version from: $UvVersionLine"
}

$NodeVersion = (node --version).Trim()
if ($NodeVersion -notmatch '^v24\.') {
    throw "Expected Node.js 24.x (see .nvmrc); found $NodeVersion. Install Node.js 24 LTS and rerun this script."
}

$PythonVersion = '3.13.16'
Write-Host "Preparing Python $PythonVersion lock and environment..." -ForegroundColor Cyan
uv python install $PythonVersion
uv lock --python $PythonVersion
uv sync --locked --python $PythonVersion --group dev

$Web = Join-Path $Root 'apps/web'
Push-Location $Web
try {
    Write-Host 'Generating apps/web/package-lock.json from the pinned package manifest...' -ForegroundColor Cyan
    npm install --package-lock-only --ignore-scripts --no-audit --no-fund
    npm ci --no-audit --no-fund
} finally {
    Pop-Location
}

if (-not (Test-Path (Join-Path $Root '.env'))) {
    Copy-Item (Join-Path $Root '.env.example') (Join-Path $Root '.env')
    Write-Host 'Created .env from the development-only template. Review it before running services.' -ForegroundColor Yellow
}
$EnvironmentLine = Select-String -Path (Join-Path $Root '.env') -Pattern '^COMPANY_OS_ENVIRONMENT=' -ErrorAction SilentlyContinue | Select-Object -First 1
if ($EnvironmentLine -and $EnvironmentLine.Line -notmatch '^COMPANY_OS_ENVIRONMENT=(development|test)$') {
    throw 'Bootstrap checks must run with COMPANY_OS_ENVIRONMENT=development or test. Do not use a production .env for local tests.'
}

$env:PYTHONPATH = Join-Path $Root 'apps/api/src'
uv run --locked --python $PythonVersion python -m company_os.config_check
uv run --locked --python $PythonVersion ruff check apps/api/src apps/api/tests
uv run --locked --python $PythonVersion pytest

if (-not $SkipFrontendBuild) {
    Push-Location $Web
    try {
        npm run typecheck
        npm run build
    } finally {
        Pop-Location
    }
}

if ($WithDockerDatabase) {
    Require-Command 'docker' 'Install/start Docker Desktop, then rerun without changing the source files.'
    docker compose up -d db
    $env:COMPANY_OS_ENVIRONMENT = 'development'
    $env:COMPANY_OS_DATABASE_URL = 'postgresql+psycopg://company_os:company_os_dev_only@localhost:5432/company_os'
    uv run --locked --python $PythonVersion alembic upgrade head
    Remove-Item Env:COMPANY_OS_DATABASE_URL -ErrorAction SilentlyContinue
}

Write-Host ''
Write-Host 'Bootstrap checks passed.' -ForegroundColor Green
Write-Host 'Generated lockfiles: uv.lock and apps/web/package-lock.json.'
Write-Host 'Review changes with: git status --short'
Write-Host 'Then commit and push this work package only after reviewing the test results.'
