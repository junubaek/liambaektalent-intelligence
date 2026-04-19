$env:PYTHONPATH = (Get-Item .).FullName
$env:PYTHONIOENCODING = "utf-8"
Write-Host "Starting FastAPI Backend on port 8000 (Logs: fastapi.log)..."
Start-Process -FilePath "python" -ArgumentList "-m", "uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000" -NoNewWindow -RedirectStandardOutput "fastapi.log" -RedirectStandardError "fastapi_err.log"

Write-Host "Service started. Waiting 5s for initialization..."
Start-Sleep -Seconds 5
Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue
