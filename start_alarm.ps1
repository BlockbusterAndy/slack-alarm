# Activate virtual environment and run the slack alarm watcher
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptDir

$venvActivate = Join-Path $scriptDir "venv\Scripts\Activate.ps1"

if (-Not (Test-Path $venvActivate)) {
    Write-Error "Virtual environment not found at '$venvActivate'. Run 'python -m venv venv' first."
    exit 1
}

& $venvActivate
python main.py
