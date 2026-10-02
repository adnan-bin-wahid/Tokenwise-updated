param(
    [string]$Query = '',
    [string]$QueryBase64 = '',
    [switch]$Verification
)

$ErrorActionPreference = 'Stop'
$WorkspaceRoot = Split-Path -Parent $PSScriptRoot
$TokenWiseRoot = Split-Path -Parent $WorkspaceRoot
$TokenWisePython = Join-Path $TokenWiseRoot '.venv\Scripts\python.exe'
$ContextCommand = Join-Path $TokenWiseRoot 'scripts\antigravity_context.py'

if (-not (Test-Path -LiteralPath $TokenWisePython -PathType Leaf)) {
    [Console]::Error.WriteLine('TokenWise: Python environment is missing. Run scripts/setup.ps1 in the TokenWise folder.')
    exit 1
}

$env:PYTHONUTF8 = '1'
$OutputEncoding = [System.Text.UTF8Encoding]::new($false)
[Console]::OutputEncoding = $OutputEncoding
if ($QueryBase64) {
    try {
        if ($Query) {
            throw 'Use either Query or QueryBase64, not both.'
        }
        $Query = [System.Text.UTF8Encoding]::new($false, $true).GetString([Convert]::FromBase64String($QueryBase64))
    } catch {
        [Console]::Error.WriteLine("TokenWise: Invalid encoded query: $($_.Exception.Message)")
        exit 1
    }
}
$Arguments = @($ContextCommand, '--workspace', $WorkspaceRoot, '--query-stdin')
if ($Verification) {
    $Arguments += '--verification'
}
$Query | & $TokenWisePython @Arguments
exit $LASTEXITCODE
