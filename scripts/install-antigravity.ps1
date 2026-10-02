$ErrorActionPreference = 'Stop'
$TokenWiseRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$ExtensionRoot = Join-Path $TokenWiseRoot 'vscode-extension'
$AntigravityCli = Join-Path $env:LOCALAPPDATA 'Programs\Antigravity IDE\bin\antigravity-ide.cmd'
if (-not (Test-Path -LiteralPath $AntigravityCli -PathType Leaf)) {
    $CliCommand = Get-Command antigravity-ide.cmd -ErrorAction SilentlyContinue
    if (-not $CliCommand) { throw 'Antigravity IDE is not installed in its standard location or PATH.' }
    $AntigravityCli = $CliCommand.Source
}

Push-Location $ExtensionRoot
try {
    & npm.cmd run package
    if ($LASTEXITCODE -ne 0) { throw 'TokenWise packaging failed. Run scripts/setup.ps1 first if dependencies are missing.' }
    $Manifest = Get-Content -LiteralPath 'package.json' -Raw | ConvertFrom-Json
    $PackagePath = Join-Path $ExtensionRoot "$($Manifest.name)-$($Manifest.version).vsix"
    & $AntigravityCli --install-extension $PackagePath --force
    if ($LASTEXITCODE -ne 0) { throw 'TokenWise extension installation failed.' }
}
finally {
    Pop-Location
}

Write-Host 'TokenWise installed. Reload Antigravity IDE, open a Python repository, and run TokenWise: Enable Automatic Context.'
