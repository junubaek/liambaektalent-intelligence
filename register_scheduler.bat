@echo off
echo registering schtasks...

schtasks /create /tn "TalentOS_Recovery" /tr "python C:\Users\cazam\Downloads\이력서자동분석검색시스템\recovery_worker.py" /sc daily /st 00:00 /f

echo Registration completed.
