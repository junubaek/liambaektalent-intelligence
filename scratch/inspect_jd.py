with open('jd_compiler.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for idx, line in enumerate(lines):
    if 'def api_search_v9' in line:
        print(f"api_search_v9 start: line {idx+1}")
    if 'score_final =' in line or 'Score_final =' in line:
        print(f"score_final calculation: line {idx+1}: {line.strip()}")
