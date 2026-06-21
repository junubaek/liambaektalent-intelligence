with open('jd_compiler.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for idx in range(2405, 2425):
    print(f"{idx+1}: {lines[idx].rstrip()}")
