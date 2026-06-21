with open('jd_compiler.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

in_v9 = False
for idx, line in enumerate(lines):
    if 'def api_search_v9' in line:
        in_v9 = True
    if in_v9 and idx > 2500 and 'return' in line:
        print(f"Line {idx+1}: {line.strip()}")
