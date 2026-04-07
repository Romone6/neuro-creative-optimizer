$ErrorActionPreference = "Stop"

$RootDir = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$TribeDir = Join-Path $RootDir "third_party/tribev2"
$TribeRepoUrl = if ($env:TRIBE_REPO_URL) { $env:TRIBE_REPO_URL } else { "https://github.com/facebookresearch/tribev2.git" }
$TribeRef = $env:TRIBE_REF

function Require-Command {
  param([string]$Name)

  if (-not (Get-Command $Name -ErrorAction SilentlyContinue)) {
    throw "Missing required command: $Name"
  }
}

Require-Command git
Require-Command uv
Require-Command python

New-Item -ItemType Directory -Force -Path (Join-Path $RootDir "third_party") | Out-Null
New-Item -ItemType Directory -Force -Path (Join-Path $RootDir "artifacts/setup") | Out-Null

Write-Host "[bootstrap] syncing project environment"
Push-Location $RootDir
uv sync --all-groups
Pop-Location

if (-not (Test-Path (Join-Path $TribeDir ".git"))) {
  Write-Host "[bootstrap] cloning TRIBE v2 into $TribeDir"
  git clone $TribeRepoUrl $TribeDir
} else {
  Write-Host "[bootstrap] TRIBE v2 already present, fetching latest refs"
  git -C $TribeDir fetch --all --tags
}

if ($TribeRef) {
  Write-Host "[bootstrap] checking out TRIBE ref $TribeRef"
  git -C $TribeDir checkout $TribeRef
}

Write-Host "[bootstrap] installing TRIBE v2 in editable mode"
try {
  uv pip install --python (Join-Path $RootDir ".venv/Scripts/python.exe") -e $TribeDir
} catch {
  Write-Warning "[bootstrap] TRIBE editable install failed; continuing in degraded mode"
}

Write-Host "[bootstrap] running TRIBE smoke test"
$env:PYTHONPATH = @(
  (Join-Path $RootDir "apps/api/src"),
  (Join-Path $RootDir "packages/bootstrap/src"),
  (Join-Path $RootDir "packages/core/src"),
  (Join-Path $RootDir "packages/llm/src"),
  $env:PYTHONPATH
) -join [IO.Path]::PathSeparator
& (Join-Path $RootDir ".venv/Scripts/python.exe") (Join-Path $RootDir "scripts/smoke_test_tribe.py") --repo-root $RootDir

Write-Host "[bootstrap] completed"
