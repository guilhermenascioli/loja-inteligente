$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath $PSScriptRoot
if (Test-Path -LiteralPath '.venv/Scripts/python.exe') {
    & ./.venv/Scripts/python.exe -m app.local_launcher --port 8001
} else {
    & python -m app.local_launcher --port 8001
}
