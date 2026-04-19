Write-Host "Starting dynamic_parser.py (Estimated time: 2-3 hours due to API limits)..."
python dynamic_parser.py
Write-Host "Parser completed. Restoring preflight_unique.json..."
if (Test-Path preflight_unique.bak) { Rename-Item preflight_unique.bak preflight_unique.json -Force }
Write-Host "Running pattern analysis..."
python analyze_patterns.py
Write-Host "All tasks completed successfully!"
