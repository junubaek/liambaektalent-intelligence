import sys
sys.path.append('c:/Users/cazam/Downloads/이력서자동분석검색시스템')

try:
    from ontology_graph import CANONICAL_MAP, EDGES
    import networkx as nx
except Exception as e:
    print(e)
    sys.exit(1)

from collections import Counter

print("=== ONTOLOGY ANALYSIS ===")

# 1. Missing Canonical mappings
can_vals = set(CANONICAL_MAP.values())
edge_nodes = set()
for s, t, r, w in EDGES:
    edge_nodes.add(s)
    edge_nodes.add(t)

# Nodes in CANONICAL_MAP.values() but not in EDGES
isolated = can_vals - edge_nodes
if isolated:
    print("\n[Warning] Isolated Nodes (in Map but No Edges):")
    for n in sorted(isolated):
        print(f"  - {n}")
else:
    print("\n[OK] All Canonical Nodes have at least 1 edge.")

# 2. Cycles in EDGES
G = nx.DiGraph()
for src, tgt, rel, w in EDGES:
    G.add_edge(src, tgt)

cycles = list(nx.simple_cycles(G))
if cycles:
    # simple_cycles can return cycles of length >= 1. We only care about <= 3 for immediate loops 
    short_cycles = [c for c in cycles if len(c) <= 3]
    if short_cycles:
        print(f"\n[Warning] {len(short_cycles)} Short Cycles (length <= 3) detected:")
        for c in short_cycles[:10]:
            print(f"  - {' -> '.join(c)}")
else:
    print("\n[OK] No Cycles detected.")

# 3. Check for similar naming in CANONICAL_MAP (Potential Typos)
from difflib import SequenceMatcher
def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()

print("\n[Info] Checking for similar canonical names (ratio > 0.85):")
arr = sorted(list(can_vals))
found_sim = False
for i in range(len(arr)):
    for j in range(i+1, len(arr)):
        if similar(arr[i], arr[j]) > 0.85:
            # Skip short words and subset words
            if len(arr[i]) < 4 or len(arr[j]) < 4: continue
            if arr[i] in arr[j] or arr[j] in arr[i]: continue
            print(f"  - {arr[i]} vs {arr[j]}")
            found_sim = True
if not found_sim:
    print("  None found.")

# 4. Inconsistent Casing
lower_map = {}
inconsistent_cases = []
for v in can_vals:
    if v.lower() in lower_map:
        inconsistent_cases.append((lower_map[v.lower()], v))
    else:
        lower_map[v.lower()] = v

if inconsistent_cases:
    print("\n[Warning] Inconsistent Casing detected:")
    for a, b in inconsistent_cases:
        print(f"  - {a} vs {b}")
else:
    print("\n[OK] No Inconsistent Casing detected.")

# 5. Missing TGT nodes (these are fine but let's check for misspelled canonicals)
tgt_only = edge_nodes - can_vals
print(f"\n[Info] There are {len(tgt_only)} nodes in EDGES that are not in CANONICAL_MAP (Low-level nodes).")
# Lets see if any tgt_only is extremely similar to a can_val
print("\n[Warning] Low-level nodes that might be typos of Canonical nodes:")
for t in tgt_only:
    for c in can_vals:
        if similar(t, c) > 0.9 and t != c and t not in c and c not in t:
            print(f"  - {t} (in EDGES) vs {c} (in MAP)")

print("\n=== ANALYSIS COMPLETE ===")
