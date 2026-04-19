import json
import sys
from jd_compiler import api_search_v8

queries = [
    "C/C++ NPU 런타임 커널 튜닝",
    "HBM 설계 엔지니어",
    "PCIe 검증 엔지니어"
]

print("=== Search Test Results ===")
for q in queries:
    try:
        res = api_search_v8(q)
        candidates = res.get('candidates', [])
        print(f"Query: '{q}' -> {len(candidates)}명")
    except Exception as e:
        print(f"Query: '{q}' -> Error: {e}")
