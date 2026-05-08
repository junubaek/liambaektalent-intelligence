import re
from collections import defaultdict
import sys

# Ensure UTF-8 output
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

with open('ontology_graph.py', 'r', encoding='utf-8') as f:
    content = f.read()

edge_pattern = re.findall(r'\(\"([^\"]+)\",\s*\"([^\"]+)\",\s*\"([^\"]+)\",\s*([\d.]+)\)', content)
edge_map = defaultdict(list)
for s,d,r,w in edge_pattern:
    edge_map[s].append((d,r,float(w)))
    edge_map[d].append((s,r,float(w)))

nodes_to_check = ['AI_Core', 'AI_Infra', 'AI_Engineering', 'AI_Cloud_Platform', 'Platform_AI']
for node in nodes_to_check:
    conns = edge_map.get(node, [])
    print(f'[{node}] {len(conns)}개')
    for d,r,w in conns:
        print(f'  → {d} ({r}, {w})')
    print()
