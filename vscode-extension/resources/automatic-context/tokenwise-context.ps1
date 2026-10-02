# TokenWise managed command-tool launcher.
param(
    [string]$Query = '',
    [string]$QueryBase64 = '',
    [switch]$Verification
)

$ErrorActionPreference = 'Stop'
$OutputEncoding = [System.Text.UTF8Encoding]::new($false)
[Console]::OutputEncoding = $OutputEncoding
try {
    . (Join-Path $PSScriptRoot 'tokenwise-runtime.ps1')
    $Runtime = Get-TokenWiseRuntime
    if ($QueryBase64) {
        if ($Query) { throw 'Use either Query or QueryBase64, not both.' }
        $Query = [System.Text.UTF8Encoding]::new($false, $true).GetString([Convert]::FromBase64String($QueryBase64))
    }
    $Command = Join-Path $Runtime.ProjectRoot 'scripts\antigravity_context.py'
    $Arguments = @($Command, '--workspace', $Runtime.WorkspaceRoot, '--query-stdin')
    if ($Verification) { $Arguments += '--verification' }
    $Query | & $Runtime.Python @Arguments
    exit $LASTEXITCODE
} catch {
    [Console]::Error.WriteLine("TokenWise: $($_.Exception.Message)")
    exit 1
}
