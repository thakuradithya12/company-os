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

# Windows PowerShell 5.1 and PowerShell 7 do not consistently turn a native
# executable's non-zero exit code into a terminating error. Always inspect
# $LASTEXITCODE so a failed npm/uv/docker/alembic command cannot be followed by
# a misleading "checks passed" message.
function Invoke-CheckedNative {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true)][string]$Command,
        [Parameter(Mandatory = $true)][string[]]$Arguments
    )

    $DisplayCommand = "$Command $($Arguments -join ' ')"
    try {
        & $Command @Arguments
        $NativeExitCode = $LASTEXITCODE
    } catch {
        throw "Command '$DisplayCommand' raised an error. Bootstrap stopped; checks are NOT passed. $($_.Exception.Message)"
    }

    if ($null -eq $NativeExitCode) {
        $NativeExitCode = 0
    }
    if ($NativeExitCode -ne 0) {
        throw "Command '$DisplayCommand' failed with exit code $NativeExitCode. Bootstrap stopped; checks are NOT passed."
    }
}

function Invoke-CheckedNativeOutput {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true)][string]$Command,
        [Parameter(Mandatory = $true)][string[]]$Arguments
    )

    $DisplayCommand = "$Command $($Arguments -join ' ')"
    try {
        $NativeOutput = & $Command @Arguments
        $NativeExitCode = $LASTEXITCODE
    } catch {
        throw "Command '$DisplayCommand' raised an error. Bootstrap stopped; checks are NOT passed. $($_.Exception.Message)"
    }

    if ($null -eq $NativeExitCode) {
        $NativeExitCode = 0
    }
    if ($NativeExitCode -ne 0) {
        throw "Command '$DisplayCommand' failed with exit code $NativeExitCode. Bootstrap stopped; checks are NOT passed."
    }

    return (($NativeOutput | ForEach-Object { [string]$_ }) -join [Environment]::NewLine).Trim()
}

Require-Command 'git' 'Install Git for Windows and reopen PowerShell.'
Require-Command 'uv' 'Install uv from https://docs.astral.sh/uv/getting-started/installation/ and reopen PowerShell.'
Require-Command 'node' 'Install Node.js 24 LTS from https://nodejs.org/en/download/ and reopen PowerShell.'
Require-Command 'npm' 'Install Node.js 24 LTS; npm is included with the installer.'

$UvVersionLine = Invoke-CheckedNativeOutput -Command 'uv' -Arguments @('--version')
if ($UvVersionLine -match '^uv ([0-9]+\.[0-9]+\.[0-9]+)') {
    $ParsedUvVersion = [version]$Matches[1]
    if ($ParsedUvVersion -lt [version]'0.13.4') {
        throw "uv 0.13.4 or newer is required to provision the pinned Python runtime. Current: $UvVersionLine. Update with 'uv self update' or reinstall uv from https://docs.astral.sh/uv/getting-started/installation/."
    }
} else {
    throw "Could not parse uv version from: $UvVersionLine"
}

$NodeVersion = Invoke-CheckedNativeOutput -Command 'node' -Arguments @('--version')
if ($NodeVersion -notmatch '^v24\.') {
    throw "Expected Node.js 24.x (see .nvmrc); found $NodeVersion. Install Node.js 24 LTS and rerun this script."
}

$PythonVersion = '3.13.16'
Write-Host "Preparing Python $PythonVersion lock and environment..." -ForegroundColor Cyan
Invoke-CheckedNative -Command 'uv' -Arguments @('python', 'install', $PythonVersion)
Invoke-CheckedNative -Command 'uv' -Arguments @('lock', '--python', $PythonVersion)
Invoke-CheckedNative -Command 'uv' -Arguments @('sync', '--locked', '--python', $PythonVersion, '--group', 'dev')

$Web = Join-Path $Root 'apps/web'
Push-Location $Web
try {
    Write-Host 'Generating apps/web/package-lock.json from the pinned package manifest...' -ForegroundColor Cyan
    Invoke-CheckedNative -Command 'npm' -Arguments @('install', '--package-lock-only', '--ignore-scripts', '--no-audit', '--no-fund')
    Invoke-CheckedNative -Command 'npm' -Arguments @('ci', '--no-audit', '--no-fund')
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
Invoke-CheckedNative -Command 'uv' -Arguments @('run', '--locked', '--python', $PythonVersion, 'python', '-m', 'company_os.config_check')
Invoke-CheckedNative -Command 'uv' -Arguments @('run', '--locked', '--python', $PythonVersion, 'ruff', 'check', 'apps/api/src', 'apps/api/tests')
Invoke-CheckedNative -Command 'uv' -Arguments @('run', '--locked', '--python', $PythonVersion, 'pytest')

if (-not $SkipFrontendBuild) {
    Push-Location $Web
    try {
        Invoke-CheckedNative -Command 'npm' -Arguments @('run', 'typecheck')
        Invoke-CheckedNative -Command 'npm' -Arguments @('run', 'build')
    } finally {
        Pop-Location
    }
}

if ($WithDockerDatabase) {
    Require-Command 'docker' 'Install/start Docker Desktop, then rerun without changing the source files.'

    # Fail before touching localhost:5432 if Docker Desktop's engine is down.
    # Without this preflight, Alembic might accidentally connect to an unrelated
    # PostgreSQL service installed on Windows.
    [void](Invoke-CheckedNativeOutput -Command 'docker' -Arguments @('info', '--format', '{{.ServerVersion}}'))
    Invoke-CheckedNative -Command 'docker' -Arguments @('compose', 'up', '-d', 'db')

    $DatabaseReady = $false
    for ($Attempt = 1; $Attempt -le 30; $Attempt++) {
        try {
            & docker compose exec -T db pg_isready -U 'company_os' -d 'company_os' *> $null
            $ProbeExitCode = $LASTEXITCODE
        } catch {
            $ProbeExitCode = 1
        }
        if ($ProbeExitCode -eq 0) {
            $DatabaseReady = $true
            break
        }
        Start-Sleep -Seconds 2
    }
    if (-not $DatabaseReady) {
        throw 'The Company OS PostgreSQL container did not become ready within 60 seconds. Bootstrap stopped; migrations were not run.'
    }

    $PostgresHostPort = '55432'
    $HostPortLine = Select-String -Path (Join-Path $Root '.env') -Pattern '^COMPANY_OS_POSTGRES_HOST_PORT=' -ErrorAction SilentlyContinue | Select-Object -First 1
    if ($HostPortLine) {
        $ConfiguredHostPort = $HostPortLine.Line.Substring($HostPortLine.Line.IndexOf('=') + 1).Trim()
        if (-not [string]::IsNullOrWhiteSpace($ConfiguredHostPort)) {
            if ($ConfiguredHostPort -notmatch '^[0-9]{1,5}$' -or [int]$ConfiguredHostPort -lt 1 -or [int]$ConfiguredHostPort -gt 65535) {
                throw 'COMPANY_OS_POSTGRES_HOST_PORT must be an integer between 1 and 65535.'
            }
            $PostgresHostPort = $ConfiguredHostPort
        }
    }

    $PreviousEnvironment = $env:COMPANY_OS_ENVIRONMENT
    $PreviousDatabaseUrl = $env:COMPANY_OS_DATABASE_URL
    try {
        $env:COMPANY_OS_ENVIRONMENT = 'development'
        $env:COMPANY_OS_DATABASE_URL = "postgresql+psycopg://company_os:company_os_dev_only@localhost:$PostgresHostPort/company_os"
        Invoke-CheckedNative -Command 'uv' -Arguments @('run', '--locked', '--python', $PythonVersion, 'alembic', 'upgrade', 'head')
    } finally {
        if ($null -eq $PreviousEnvironment) {
            Remove-Item Env:COMPANY_OS_ENVIRONMENT -ErrorAction SilentlyContinue
        } else {
            $env:COMPANY_OS_ENVIRONMENT = $PreviousEnvironment
        }
        if ($null -eq $PreviousDatabaseUrl) {
            Remove-Item Env:COMPANY_OS_DATABASE_URL -ErrorAction SilentlyContinue
        } else {
            $env:COMPANY_OS_DATABASE_URL = $PreviousDatabaseUrl
        }
    }
}

Write-Host ''
Write-Host 'Bootstrap checks passed.' -ForegroundColor Green
Write-Host 'Generated lockfiles: uv.lock and apps/web/package-lock.json.'
Write-Host 'Review changes with: git status --short'
Write-Host 'Then commit and push this work package only after reviewing the test results.'
