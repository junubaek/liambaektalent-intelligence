with open('jd_compiler.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for idx, line in enumerate(lines):
    if 'def get_company_boost' in line:
        print(f"Line {idx+1}: {line.strip()}")
        for i in range(idx, idx+15):
            print(f"  {i+1}: {lines[i].rstrip()}")
