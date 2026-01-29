#!/usr/bin/env pwsh
# Auto-activate virtual environment and run app

Set-Location $PSScriptRoot
Write-Host "Activating virtual environment..." -ForegroundColor Cyan
& .\.venv\Scripts\Activate.ps1
Write-Host "✓ Virtual environment activated" -ForegroundColor Green
Write-Host "`nStarting Face Attendance System...`n" -ForegroundColor Cyan
python app.py
