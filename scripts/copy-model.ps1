param(
    [Parameter(Mandatory = $true)]
    [string]$Source
)

$ErrorActionPreference = 'Stop'
$ProjectRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$Destination = Join-Path $ProjectRoot 'swe-pruner\swe-pruner\model\model.safetensors'

if (-not (Test-Path -LiteralPath $Source -PathType Leaf)) {
    throw "Source model not found: $Source"
}

$DestinationDir = Split-Path -Parent $Destination
New-Item -ItemType Directory -Force -Path $DestinationDir | Out-Null

Write-Host "Copying model.safetensors..." -ForegroundColor Cyan
Copy-Item -LiteralPath $Source -Destination $Destination -Force

$SourceHash = (Get-FileHash -Algorithm SHA256 -LiteralPath $Source).Hash
$DestinationHash = (Get-FileHash -Algorithm SHA256 -LiteralPath $Destination).Hash

if ($SourceHash -ne $DestinationHash) {
    Remove-Item -LiteralPath $Destination -Force -ErrorAction SilentlyContinue
    throw 'SHA256 mismatch after copy. Destination was removed.'
}

$Size = (Get-Item -LiteralPath $Destination).Length
Write-Host "Model copied successfully." -ForegroundColor Green
Write-Host "Destination: $Destination"
Write-Host "Bytes:       $Size"
Write-Host "SHA256:      $DestinationHash"
