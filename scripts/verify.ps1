param()

$ErrorActionPreference = 'Stop'
$ProjectRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$Python = Join-Path $ProjectRoot '.venv\Scripts\python.exe'
$ModelDir = Join-Path $ProjectRoot 'swe-pruner\swe-pruner\model'
$ModelFile = Join-Path $ModelDir 'model.safetensors'
$ExtensionRoot = Join-Path $ProjectRoot 'vscode-extension'

if (-not (Test-Path -LiteralPath $Python -PathType Leaf)) {
    throw 'Virtual environment is missing. Run .\scripts\setup.ps1 first.'
}
if (-not (Test-Path -LiteralPath $ModelFile -PathType Leaf)) {
    throw 'model.safetensors is missing. Run .\scripts\copy-model.ps1 first.'
}
if ((Get-Item -LiteralPath $ModelFile).Length -lt 500MB) {
    throw 'model.safetensors looks unexpectedly small. Re-copy the original weight file.'
}

Write-Host '1/5 Python syntax check...' -ForegroundColor Cyan
& $Python -m compileall -q `
    (Join-Path $ProjectRoot 'swe-pruner\swe-pruner\src') `
    (Join-Path $ProjectRoot 'carbon-engine\src') `
    (Join-Path $ProjectRoot 'carbon-engine\scripts') `
    (Join-Path $ProjectRoot 'Test_project')
if ($LASTEXITCODE -ne 0) { throw 'Python syntax check failed.' }

Write-Host '2/5 Demo unit tests...' -ForegroundColor Cyan
$OldPythonPath = $env:PYTHONPATH
$env:PYTHONPATH = Join-Path $ProjectRoot 'Test_project'
try {
    & $Python -m unittest discover -s (Join-Path $ProjectRoot 'Test_project\tests') -v
    if ($LASTEXITCODE -ne 0) { throw 'Demo unit tests failed.' }
}
finally {
    $env:PYTHONPATH = $OldPythonPath
}

Write-Host '3/5 Offline TokenWise smoke tests...' -ForegroundColor Cyan
& $Python (Join-Path $ProjectRoot 'scripts\smoke_test.py') --offline
if ($LASTEXITCODE -ne 0) { throw 'Offline smoke tests failed.' }

Write-Host '4/5 Local tokenizer/config check...' -ForegroundColor Cyan
& $Python -c "from transformers import AutoTokenizer; p=r'$ModelDir'; t=AutoTokenizer.from_pretrained(p, local_files_only=True); assert len(t)>0; print('Tokenizer OK:', len(t))"
if ($LASTEXITCODE -ne 0) { throw 'Tokenizer/config check failed.' }

Write-Host '5/5 VS Code extension compile...' -ForegroundColor Cyan
Push-Location $ExtensionRoot
try {
    & npm.cmd run compile
    if ($LASTEXITCODE -ne 0) { throw 'TypeScript compilation failed.' }
}
finally {
    Pop-Location
}

Write-Host ''
Write-Host 'Static/offline verification passed.' -ForegroundColor Green
Write-Host 'Next: .\scripts\run-backend.ps1'
Write-Host 'Then, in a second terminal: .\.venv\Scripts\python.exe .\scripts\smoke_test.py --full'
