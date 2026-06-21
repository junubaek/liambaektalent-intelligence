with open('backend/main.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for idx, line in enumerate(lines):
    if 'staticfiles' in line.lower() or 'dist' in line.lower() or 'mount' in line.lower():
        print(f"Line {idx+1}: {line.strip()}")
