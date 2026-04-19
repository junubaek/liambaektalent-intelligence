import time
from jd_compiler import api_search_v8

QUERIES = [
    "UI 디자이너",
    "인플루언서 마케터",
    "테크 리크루터",
    "스타트업 CFO",
    "콘텐츠 기획자",
    "엔터프라이즈 영업"
]

print("=== Batch 3 Final Rescue Hit Count ===")
for q in QUERIES:
    try:
        res = api_search_v8(prompt=q)
        hits = len(res.get('matched', []))
        print(f"{q} | {hits}명")
    except Exception as e:
        print(f"{q} | Error: {e}")
