import sys
import json
from jd_compiler import api_search_v9

# Ensure UTF-8 output
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

print("--- Enterprise Sales Manager Search Results ---")
res = api_search_v9(prompt='Enterprise Sales Manager', seniority='All')
candidates = res.get('matched', [])

target_name = "최우성"
found_target = False

for i, c in enumerate(candidates):
    name = c.get('name_kr', '?')
    final = c.get('final_score', 0)
    v = c.get('vector_score', 0)
    g = c.get('graph_score', 0)
    
    if i < 20 or name == target_name:
        print(f'{i+1:2d}. {name:10s} FINAL:{final:.3f} V:{v:.3f} G:{g:.3f}')
        if name == target_name:
            found_target = True
    
    if i >= 50 and found_target:
        break

if not found_target:
    print(f"\n[WARN] {target_name} not found in top {len(candidates)} results.")
