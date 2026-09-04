$ErrorActionPreference = 'Stop'

$projectRoot = Resolve-Path (Join-Path $PSScriptRoot '..')
Write-Host "Installing CRIZ_SPOTPIE from $projectRoot"

py -m pip install --user $projectRoot

$pythonUserBase = py -c "import site; print(site.USER_BASE)"
$userScripts = Join-Path $pythonUserBase 'Scripts'

Write-Host ""
Write-Host "[OK] CRIZ_SPOTPIE installed successfully."
Write-Host "Run it with:"
Write-Host "  criz-spotpie"
Write-Host ""
Write-Host "If PATH is not updated yet, add this manually:"
Write-Host "  $userScripts"
Write-Host "Then open a new terminal window and run criz-spotpie."
