$ErrorActionPreference = 'Stop'
$TokenWiseRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$RegistrationPath = Join-Path $TokenWiseRoot '.tokenwise\backend.json'
if (-not (Test-Path -LiteralPath $RegistrationPath)) { return }
$Registration = Get-Content -LiteralPath $RegistrationPath -Raw | ConvertFrom-Json
$BackendProcess = Get-CimInstance Win32_Process -Filter "ProcessId = $($Registration.pid)"
$ExpectedPython = Join-Path $TokenWiseRoot '.venv\Scripts\python.exe'
if ($BackendProcess -and $BackendProcess.ExecutablePath -eq $ExpectedPython -and
    $BackendProcess.CommandLine -match 'swe_pruner.online_serving:app' -and
    $Registration.project_root -eq $TokenWiseRoot) {
    Stop-Process -Id $Registration.pid
    Write-Host 'TokenWise automatic backend stopped. The next prompt will start it again.'
}
