with open("jd_compiler.py", "r", encoding="utf-8") as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if "ALLOWED_SECTORS" in line or "DESIGN_KEYWORDS" in line or "HR_KEYWORDS" in line or "query_domain" in line:
        print(f"Line {i+1}: {line.strip()}")
