<#
Register a Windows scheduled task to run the pipeline weekly.
Run this PowerShell script as Administrator.

Usage:
.
#> 
param(
    [string]$TaskName = "PredictiveSalesForecast",
    [string]$StartTime = "03:00",
    [string]$Days = "MON"
)

function Find-Python {
    $cmd = Get-Command python -ErrorAction SilentlyContinue
    if ($cmd) { return $cmd.Source }
    throw "Python not found in PATH. Provide full path to python.exe or add to PATH."
}

$python = Find-Python
$repo = Split-Path -Parent $MyInvocation.MyCommand.Path
$action = "$python -m src.run_pipeline"

Write-Output "Creating scheduled task '$TaskName' to run weekly at $StartTime"

schtasks /Create /SC WEEKLY /D $Days /ST $StartTime /TN $TaskName /TR $action /F

Write-Output "Task created. Use `schtasks /Query /TN $TaskName` to verify."
