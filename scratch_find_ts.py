import sys; sys.stdout.reconfigure(encoding='utf-8')
with open('ontology_graph.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()
for i, line in enumerate(lines):
    if '"Technical_Sales"' in line:
        start = max(0, i-2)
        end = min(len(lines), i+15)
        for j in range(start, end):
            print(f'{j+1}: {lines[j].rstrip()}')
        break
