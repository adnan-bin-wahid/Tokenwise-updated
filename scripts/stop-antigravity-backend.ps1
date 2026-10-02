param([string]$RuntimeDirectory = '')

$ErrorActionPreference = 'Stop'
$TokenWiseRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
if (-not $RuntimeDirectory) { $RuntimeDirectory = Join-Path $TokenWiseRoot '.tokenwise' }
if (-not [IO.Path]::IsPathRooted($RuntimeDirectory)) { throw 'RuntimeDirectory must be an absolute path.' }
$RegistrationPath = Join-Path ([IO.Path]::GetFullPath($RuntimeDirectory)) 'backend.json'
if (-not (Test-Path -LiteralPath $RegistrationPath)) { return }
$Registration = Get-Content -LiteralPath $RegistrationPath -Raw | ConvertFrom-Json
if (($Registration.pid -isnot [int] -and $Registration.pid -isnot [long]) -or $Registration.pid -le 0) {
    throw 'The backend registration does not contain a valid process ID.'
}
$BackendProcess = Get-CimInstance Win32_Process -Filter "ProcessId = $($Registration.pid)"
$ExpectedPython = Join-Path $TokenWiseRoot '.venv\Scripts\python.exe'
if ($BackendProcess -and $BackendProcess.ExecutablePath -eq $ExpectedPython -and
    $BackendProcess.CommandLine -match 'swe_pruner.online_serving:app' -and
    $Registration.project_root -eq $TokenWiseRoot) {
    Stop-Process -Id $Registration.pid
    Write-Host 'TokenWise automatic backend stopped. The next prompt will start it again.'
}
