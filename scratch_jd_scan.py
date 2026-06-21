import re, sys
path = 'jd_compiler.py'
with open(path, encoding='utf-8') as f:
    for i, line in enumerate(f, 1):
        if re.search(r'secrets|api_key', line, re.IGNORECASE):
            print(i, line.rstrip())
