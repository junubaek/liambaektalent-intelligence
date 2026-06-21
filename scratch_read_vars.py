import sys

sys.stdout.reconfigure(encoding='utf-8')

with open(r'C:\Users\cazam\Downloads\이력서자동분석검색시스템\railway_vars_utf8.txt', 'r', encoding='utf-8') as f:
    vars_data = f.read()

print("--- Railway Vars ---")
# Print first 2000 chars to inspect format
print(vars_data[:2000])

# Look for RAILWAY_TOKEN or similar
for line in vars_data.splitlines():
    if "TOKEN" in line or "SECRET" in line or "KEY" in line or "RAILWAY_" in line:
        print(line)
