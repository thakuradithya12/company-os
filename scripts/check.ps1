$ErrorActionPreference = 'Stop'
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

function Require-Command([string]$Name, [string]$Instruction) {
  if (-not (Get-Command $Name -ErrorAction SilentlyContinue)) {
    throw "$Name is required. $Instruction"
  }
}

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
    throw "Command '$DisplayCommand' raised an error. Checks stopped; checks are NOT passed. $($_.Exception.Message)"
  }
  if ($null -eq $NativeExitCode) { $NativeExitCode = 0 }
  if ($NativeExitCode -ne 0) {
    throw "Command '$DisplayCommand' failed with exit code $NativeExitCode. Checks stopped; checks are NOT passed."
  }
}

Require-Command 'uv' 'Install uv from https://docs.astral.sh/uv/getting-started/installation/ and reopen PowerShell.'
Require-Command 'node' 'Install Node.js 24 LTS from https://nodejs.org/en/download/ and reopen PowerShell.'
Require-Command 'npm' 'Install Node.js 24 LTS; npm is included with the installer.'

$UvVersion = (uv --version).Trim()
if ($LASTEXITCODE -ne 0) { throw "Could not run uv --version (exit $LASTEXITCODE). Checks are NOT passed." }
if ($UvVersion -notmatch '^uv ([0-9]+\.[0-9]+\.[0-9]+)') {
  throw "Could not parse uv version from '$UvVersion'. Checks are NOT passed."
}
if ([version]$Matches[1] -lt [version]'0.13.4') {
  throw "uv 0.13.4 or newer is required; found '$UvVersion'. Checks are NOT passed."
}
$NodeVersion = (node --version).Trim()
if ($LASTEXITCODE -ne 0) { throw "Could not run node --version (exit $LASTEXITCODE). Checks are NOT passed." }
if ($NodeVersion -notmatch '^v24\.') { throw "Expected Node.js 24.x from .nvmrc, found $NodeVersion. Checks are NOT passed." }

Invoke-CheckedNative -Command 'uv' -Arguments @('lock', '--check')
$env:PYTHONPATH = Join-Path $Root 'apps/api/src'
Invoke-CheckedNative -Command 'uv' -Arguments @('run', '--locked', '--python', '3.13.16', 'python', '-m', 'company_os.config_check')
Invoke-CheckedNative -Command 'uv' -Arguments @('run', '--locked', '--python', '3.13.16', 'ruff', 'check', 'apps/api/src', 'apps/api/tests')
Invoke-CheckedNative -Command 'uv' -Arguments @('run', '--locked', '--python', '3.13.16', 'pytest')
Push-Location (Join-Path $Root 'apps/web')
try {
  Invoke-CheckedNative -Command 'npm' -Arguments @('ci', '--no-audit', '--no-fund')
  Invoke-CheckedNative -Command 'npm' -Arguments @('run', 'typecheck')
  Invoke-CheckedNative -Command 'npm' -Arguments @('run', 'build')
} finally {
  Pop-Location
}
Write-Host 'Company OS baseline checks passed.' -ForegroundColor Green
