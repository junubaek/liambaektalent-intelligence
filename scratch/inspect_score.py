with open('jd_compiler.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for idx, line in enumerate(lines):
    if 'score_final' in line.lower() or 'final_score' in line.lower():
        print(f"Line {idx+1}: {line.strip()}")
        # print 5 lines before and after
        start = max(0, idx - 5)
        end = min(len(lines), idx + 10)
        for i in range(start, end):
            print(f"  {i+1}: {lines[i].rstrip()}")
