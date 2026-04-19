from jd_compiler import api_search_v8

QUERIES = [
    "SEO 마케터",
    "콘텐츠 기획자",
    "조직문화 담당자"
]

print("=== Final 3 Queries Rescue ===")
for q in QUERIES:
    res = api_search_v8(prompt=q)
    hits = len(res.get('matched', []))
    print(f"{q} | {hits}명")
