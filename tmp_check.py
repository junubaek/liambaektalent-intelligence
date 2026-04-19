import sys
sys.path.append('c:/Users/cazam/Downloads/이력서자동분석검색시스템')
from ontology_graph import CANONICAL_MAP, EDGES

nodes = set(CANONICAL_MAP.values())
for s, t, r, w in EDGES:
    nodes.add(s)
    nodes.add(t)

from collections import Counter
counts = Counter(CANONICAL_MAP.values())
for k, v in counts.items():
    if v > 100: # just an arbitrary number 
        pass

# Check for duplicate edges
edges_list = [(s,t,r) for s,t,r,w in EDGES]
edges_counts = Counter(edges_list)
print('Duplicate edges:')
for k, v in edges_counts.items():
    if v > 1: print(k, v)

# Check missing canonical mapping
print('Nodes in edges but not in canonical map values:')
can_vals = set(CANONICAL_MAP.values())
for s, t, r, w in EDGES:
    if s not in can_vals:
        print('Missing (SRC):', s)
    if t not in can_vals:
        print('Missing (TGT):', t)

# Check for nodes with the exact same name but different cases or similar issues
