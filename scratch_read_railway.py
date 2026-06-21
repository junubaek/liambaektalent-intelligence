import sys

sys.stdout.reconfigure(encoding='utf-8')

with open(r'C:\Users\cazam\Downloads\이력서자동분석검색시스템\railway_logs.txt', 'r', encoding='utf-16') as f:
    logs = f.read()

print("--- Railway Logs ---")
print(logs[-2000:])  # Print last 2000 characters
