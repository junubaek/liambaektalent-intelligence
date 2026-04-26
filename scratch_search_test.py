import sys; sys.stdout.reconfigure(encoding='utf-8')
from jd_compiler import api_search_v8

r = api_search_v8('cloud 영업하신 분', seniority='SENIOR')
print('총 결과:', r.get('total'), '명')
print('matched 수:', len(r.get('matched',[])))
print()
for c in r.get('matched',[]):
    print(f'{c.get("이름","?")} | score={c.get("score",0):.1f} | nodes={[n.get("skill") for n in c.get("matched_nodes",[])][:3]}')
