with open('frontend_v2/src/App.jsx', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for idx, line in enumerate(lines):
    if 'const TierBadge' in line:
        print(f"Line {idx+1}: {line.strip()}")
        for i in range(idx-2, idx+15):
            print(f"  {i+1}: {lines[i].rstrip()}")
