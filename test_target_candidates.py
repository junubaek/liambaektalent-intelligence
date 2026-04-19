import sys
import json
from jd_compiler import api_search_v8

QUERIES = [
    "Framework Software Engineer",
    "NPU Library Software Engineer"
]

TARGETS = ["홍기재", "전예찬"]

for q, target in zip(QUERIES, TARGETS):
    print(f"\n--- Testing Query: {q} (Target: {target}) ---")
    res = api_search_v8(prompt=q)
    matched = res.get('matched', [])
    
    found = False
    for i, c in enumerate(matched[:30]):
        if c['이름'] == target or c['name'] == target:
            print(f"✅ {target} found at Rank {i+1} (Score: {c.get('score', c.get('_score', 0))})")
            found = True
            break
            
    if not found:
        print(f"❌ {target} NOT found in Top 30.")
