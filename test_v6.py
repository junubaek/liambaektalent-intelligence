import asyncio
from backend.search_engine_v6 import search_candidates_v6

res = search_candidates_v6(
    prompt="자금 담당자를 찾고 있어. IPO 혹은 유상증자 등의 대규모 자금 유입을 경험해본 분이여야 해. 최소 7년 이상의 경력자를 구해줘",
    sectors=[],
    seniority="All",
    required=[],
    preferred=[]
)

print(f"Matched: {len(res['matched'])}")
print(f"Nearby: {len(res['nearby'])}")
for r in res['matched']:
    print(r['이름'], r['_score'], r['Experience Summary'])
