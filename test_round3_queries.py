from jd_compiler import api_search_v8
import json

queries = [
    "반도체 공정 엔지니어",
    "사내 변호사",
    "임상시험 CRA",
    "자동차 소프트웨어 개발자",
    "펀드매니저"
]

print("=== Running Round 3 Verification Queries ===")
for q in queries:
    try:
        res = api_search_v8(prompt=q)
        hits = len(res.get('matched', []))
        print(f"Query '{q}': {hits} hits")
    except Exception as e:
        print(f"Query '{q}': Error -> {e}")
