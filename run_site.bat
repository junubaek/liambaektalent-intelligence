@echo off
chcp 65001 > nul
set PYTHONIOENCODING=utf-8
set PYTHONUTF8=1
echo [Info] Launching AI Recruiter (Antigravity Pipeline v5.9)...
echo If the browser does not open, please visit: http://localhost:8000
echo.
start http://localhost:8000
py -m uvicorn backend.main:app --host 0.0.0.0 --port 8000
pause
