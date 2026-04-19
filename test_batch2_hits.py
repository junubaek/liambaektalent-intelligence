import time
from jd_compiler import api_search_v8

QUERIES = [
    "BI 분석가",
    "QA 엔지니어",
    "정보보안 엔지니어",
    "커머스 MD",
    "앱 마케터"
]

print("=== Batch 2 Repair Hit Count ===")
for q in QUERIES:
    try:
        res = api_search_v8(prompt=q)
        hits = len(res.get('matched', []))
        print(f"{q} | {hits}명")
    except Exception as e:
        print(f"{q} | Error: {e}")
