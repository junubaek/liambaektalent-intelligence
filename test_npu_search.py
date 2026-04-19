import json
import sys
from jd_compiler import api_search_v8

queries = [
    "NPU 런타임 엔지니어",
    "AI 가속기 시스템SW"
]

print("=== Search Test Results (Post-Repair) ===")
for q in queries:
    try:
        res = api_search_v8(q)
        matched = len(res.get('matched', []))
        nearby = len(res.get('nearby', []))
        total = res.get('total', 0)
        print(f"Query: '{q}' -> Matched: {matched}명, Nearby: {nearby}명 (전체: {total}명)")
    except Exception as e:
        print(f"Query: '{q}' -> Error: {e}")
