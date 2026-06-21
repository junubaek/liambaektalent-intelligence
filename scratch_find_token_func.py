with open("jd_compiler.py", "r", encoding="utf-8") as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if "clean_korean_text" in line or "tokenize" in line:
        print(f"Line {i+1}: {line.strip()}")
