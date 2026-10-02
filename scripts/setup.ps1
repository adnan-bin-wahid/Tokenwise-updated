param(
    [ValidateSet('auto', 'cpu', 'cu126')]
    [string]$TorchMode = 'auto'
)

$ErrorActionPreference = 'Stop'
$ProjectRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$BackendRoot = Join-Path $ProjectRoot 'swe-pruner\swe-pruner'
$ExtensionRoot = Join-Path $ProjectRoot 'vscode-extension'
$VenvRoot = Join-Path $ProjectRoot '.venv'
$VenvPython = Join-Path $VenvRoot 'Scripts\python.exe'

function Resolve-Python312 {
    if (Get-Command py -ErrorAction SilentlyContinue) {
        & py -3.12 -c "import sys; assert sys.version_info[:2] == (3, 12)" 2>$null
        if ($LASTEXITCODE -eq 0) {
            return @{ Command = 'py'; Prefix = @('-3.12') }
        }
    }

    if (Get-Command python -ErrorAction SilentlyContinue) {
        & python -c "import sys; assert sys.version_info[:2] == (3, 12)" 2>$null
        if ($LASTEXITCODE -eq 0) {
            return @{ Command = 'python'; Prefix = @() }
        }
    }

    throw 'Python 3.12 is required. Install Python 3.12.x, then rerun this script.'
}

if (-not (Get-Command npm.cmd -ErrorAction SilentlyContinue)) {
    throw 'Node.js/npm is required. Install current Node.js LTS, then rerun this script.'
}

$Python = Resolve-Python312
if (-not (Test-Path -LiteralPath $VenvPython -PathType Leaf)) {
    Write-Host 'Creating Python 3.12 virtual environment...' -ForegroundColor Cyan
    & $Python.Command @($Python.Prefix) -m venv $VenvRoot
    if ($LASTEXITCODE -ne 0) { throw 'Virtual environment creation failed.' }
}

Write-Host 'Upgrading pip tooling...' -ForegroundColor Cyan
& $VenvPython -m pip install --upgrade pip setuptools wheel
if ($LASTEXITCODE -ne 0) { throw 'pip tooling upgrade failed.' }

if ($TorchMode -eq 'auto') {
    $TorchMode = if (Get-Command nvidia-smi.exe -ErrorAction SilentlyContinue) { 'cu126' } else { 'cpu' }
}

$TorchIndex = if ($TorchMode -eq 'cu126') {
    'https://download.pytorch.org/whl/cu126'
} else {
    'https://download.pytorch.org/whl/cpu'
}

Write-Host "Installing PyTorch ($TorchMode)..." -ForegroundColor Cyan
& $VenvPython -m pip install --upgrade 'torch>=2.5,<3' --index-url $TorchIndex
if ($LASTEXITCODE -ne 0) { throw 'PyTorch installation failed.' }

Write-Host 'Installing TokenWise backend dependencies...' -ForegroundColor Cyan
& $VenvPython -m pip install -e $BackendRoot
if ($LASTEXITCODE -ne 0) { throw 'Backend installation failed.' }

Write-Host 'Installing and compiling VS Code extension...' -ForegroundColor Cyan
Push-Location $ExtensionRoot
try {
    & npm.cmd ci
    if ($LASTEXITCODE -ne 0) { throw 'npm ci failed.' }
    & npm.cmd run compile
    if ($LASTEXITCODE -ne 0) { throw 'TypeScript compilation failed.' }
}
finally {
    Pop-Location
}

Write-Host ''
Write-Host 'Setup complete.' -ForegroundColor Green
Write-Host "Virtual environment: $VenvRoot"
Write-Host "PyTorch mode:        $TorchMode"
Write-Host 'Next: .\scripts\verify.ps1'
