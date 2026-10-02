$ErrorActionPreference = 'Stop'
$WorkspaceRoot = Split-Path -Parent $PSScriptRoot
$TokenWiseRoot = Split-Path -Parent $WorkspaceRoot
$TokenWisePython = Join-Path $TokenWiseRoot '.venv\Scripts\python.exe'
$TokenWiseHook = Join-Path $TokenWiseRoot 'scripts\antigravity_hook.py'

if (-not (Test-Path -LiteralPath $TokenWisePython -PathType Leaf)) {
    [Console]::Error.WriteLine('TokenWise: Python environment is missing. Run scripts/setup.ps1 in the TokenWise folder.')
    Write-Output '{}'
    exit 0
}

$env:PYTHONUTF8 = '1'
& $TokenWisePython $TokenWiseHook --workspace $WorkspaceRoot
