import sys
import json
from jd_compiler import api_search_v9

sys.stdout.reconfigure(encoding='utf-8')

query = "senior cfo"
# Increase top_k if possible, or manually check her score
# api_search_v9 doesn't seem to take top_k as a parameter in the definition I saw earlier, 
# but let's check jd_compiler.py to see the retrieval depth.

target_name = "김은형"
target_id = "f5875fc2-99aa-4605-9742-5ec93f4cd51a"

res = api_search_v9(query)
matched = res.get('matched', [])

found = False
for i, c in enumerate(matched):
    if c.get('name_kr') == target_name:
        print(f"FOUND {target_name} at Rank {i+1}")
        print(f"Score: {c.get('hybrid_score')}")
        print(f"Debug: {c.get('debug_score')}")
        found = True
        break

if not found:
    print(f"{target_name} not in top {len(matched)}")
    # Let's check her individual scores
    # I need to see how api_search_v9 works internally to calculate her score even if she's not in the top.
