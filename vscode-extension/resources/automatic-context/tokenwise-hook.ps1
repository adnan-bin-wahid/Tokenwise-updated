# TokenWise managed PreInvocation launcher. Failure must not block Antigravity.
$ErrorActionPreference = 'Stop'
try {
    . (Join-Path $PSScriptRoot 'tokenwise-runtime.ps1')
    $Runtime = Get-TokenWiseRuntime
    $Hook = Join-Path $Runtime.ProjectRoot 'scripts\antigravity_hook.py'
    & $Runtime.Python $Hook --workspace $Runtime.WorkspaceRoot
    if ($LASTEXITCODE -ne 0) { throw 'The shared hook adapter could not run.' }
} catch {
    [Console]::Error.WriteLine("TokenWise: $($_.Exception.Message)")
    Write-Output '{}'
}
exit 0
