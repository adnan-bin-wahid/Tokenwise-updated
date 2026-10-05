# TokenWise managed runtime resolver. Installation paths stay outside shared project rules.
function Get-TokenWiseRuntime {
    $WorkspaceRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
    $LinkPath = Join-Path $WorkspaceRoot '.tokenwise\backend-link.json'
    if (-not (Test-Path -LiteralPath $LinkPath -PathType Leaf)) {
        throw 'Run TokenWise: Enable Automatic Context in this workspace to register its shared backend.'
    }
    $Link = Get-Content -LiteralPath $LinkPath -Raw -Encoding UTF8 | ConvertFrom-Json
    if ($Link.schema_version -ne 1 -or -not [IO.Path]::IsPathRooted([string]$Link.registration_path)) {
        throw 'Invalid TokenWise backend link. Run TokenWise: Enable Automatic Context again.'
    }
    $Registration = Get-Content -LiteralPath $Link.registration_path -Raw -Encoding UTF8 | ConvertFrom-Json
    if ($Registration.schema_version -ne 1 -or
        -not [IO.Path]::IsPathRooted([string]$Registration.project_root) -or
        -not [IO.Path]::IsPathRooted([string]$Registration.runtime_dir)) {
        throw 'Invalid shared backend registration. Run TokenWise: Enable Automatic Context again.'
    }
    $ProjectRoot = [IO.Path]::GetFullPath([string]$Registration.project_root)
    $Python = Join-Path $ProjectRoot '.venv\Scripts\python.exe'
    if ([IO.Path]::GetFullPath([string]$Registration.python_path) -ne $Python -or
        -not (Test-Path -LiteralPath $Python -PathType Leaf)) {
        throw 'The shared Python environment is missing or has moved. Run TokenWise: Enable Automatic Context again.'
    }
    $env:PYTHONUTF8 = '1'
    $env:TOKENWISE_RUNTIME_DIR = [IO.Path]::GetFullPath([string]$Registration.runtime_dir)
    return [pscustomobject]@{WorkspaceRoot=$WorkspaceRoot; ProjectRoot=$ProjectRoot; Python=$Python}
}
