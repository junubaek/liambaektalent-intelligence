@echo off
chcp 65001 > nul
echo [Info] Launching AI Recruiter (Antigravity Pipeline v7.1) with Auto-Reload...
echo If the browser does not open, please visit: http://localhost:8000
echo.
start http://localhost:8000
set PYTHONIOENCODING=utf-8
py -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
pause
