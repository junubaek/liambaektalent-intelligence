with open("jd_compiler.py", "r", encoding="utf-8") as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if "query_domain" in line:
        print(f"Line {i+1}: {line.strip()}")
