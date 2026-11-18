$ErrorActionPreference = "Stop"

function Invoke-Check {
    param(
        [Parameter(Mandatory = $true)][string]$Name,
        [Parameter(Mandatory = $true)][scriptblock]$Command
    )

    Write-Host "`n>>> $Name" -ForegroundColor Cyan
    & $Command
    if ($LASTEXITCODE -ne 0) {
        throw "$Name failed with exit code $LASTEXITCODE."
    }
}

$nodeVersionText = (node --version).Trim()
if ($LASTEXITCODE -ne 0 -or $nodeVersionText -notmatch '^v(?<major>\d+)\.(?<minor>\d+)\.(?<patch>\d+)') {
    throw "Node.js 22.12.0 or newer is required. Install Node.js and reopen PowerShell."
}
$nodeVersion = [Version]::new([int]$Matches.major, [int]$Matches.minor, [int]$Matches.patch)
if ($nodeVersion -lt [Version]::new(22, 12, 0)) {
    throw "Detected Node.js $nodeVersionText. Node.js 22.12.0 or newer is required."
}

Write-Host "Using Node.js $nodeVersionText" -ForegroundColor Green

Invoke-Check -Name "Install frontend dependencies" -Command { npm install }
Invoke-Check -Name "TypeScript typecheck" -Command { npm run typecheck }
Invoke-Check -Name "Frontend unit tests" -Command { npm test }
Invoke-Check -Name "Production build" -Command { npm run build }

Write-Host "`nFrontend Phase 1 checks completed successfully." -ForegroundColor Green
