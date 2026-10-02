param(
    [int]$Port = 8000,
    [ValidateSet('auto', 'cpu', 'cuda')]
    [string]$Device = 'auto'
)

$ErrorActionPreference = 'Stop'
$ProjectRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$Python = Join-Path $ProjectRoot '.venv\Scripts\python.exe'
$ModelDir = Join-Path $ProjectRoot 'swe-pruner\swe-pruner\model'
$ModelFile = Join-Path $ModelDir 'model.safetensors'
$ArtifactsDir = Join-Path $ProjectRoot 'swe-pruner\swe-pruner\carbon_artifacts'

if (-not (Test-Path -LiteralPath $Python -PathType Leaf)) {
    throw 'Virtual environment is missing. Run .\scripts\setup.ps1 first.'
}
if (-not (Test-Path -LiteralPath $ModelFile -PathType Leaf)) {
    throw 'model.safetensors is missing. Run .\scripts\copy-model.ps1 first.'
}

$env:SWEPRUNER_MODEL_PATH = $ModelDir
$env:SWEPRUNER_CARBON_ARTIFACTS_DIR = $ArtifactsDir
$env:TOKENWISE_DEVICE = $Device
$env:HF_HUB_OFFLINE = '1'
$env:TRANSFORMERS_OFFLINE = '1'
$env:PYTHONUTF8 = '1'

Write-Host "Starting TokenWise at http://127.0.0.1:$Port" -ForegroundColor Cyan
Write-Host "Model:   $ModelDir"
Write-Host "Device:  $Device"
Write-Host 'Keep this terminal open. Press Ctrl+C to stop.'

& $Python -m uvicorn swe_pruner.online_serving:app --host 127.0.0.1 --port $Port
