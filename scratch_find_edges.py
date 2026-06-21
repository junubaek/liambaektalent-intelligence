with open(r'C:\Users\cazam\Downloads\이력서자동분석검색시스템\ontology_graph.py', 'r', encoding='utf-8') as f:
    content = f.read()

lines = content.splitlines()
found = 0
for i, line in enumerate(lines):
    if 'edge' in line.lower() or 'canonical' in line.lower():
        if '=' in line and found < 10:
            print(f"Line {i+1}: {line[:120]}")
            found += 1
