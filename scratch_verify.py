import sys; sys.stdout.reconfigure(encoding='utf-8')
from ontology_graph import CANONICAL_MAP, UNIFIED_GRAVITY_FIELD

# 한글 타겟 노드 체크
korean = {k:v for k,v in CANONICAL_MAP.items()
          if any('\uac00' <= c <= '\ud7a3' for c in v)}
print(f'한글 타겟 노드: {len(korean)}개')
if korean:
    for k,v in list(korean.items())[:5]:
        print(f'  {k} -> {v}')

print()

# 검색 테스트
from jd_compiler import api_search_v8

tests = [
    ('해외영업 10년 이상 글로벌 B2B', 'SENIOR'),
    ('디지털마케팅 퍼포먼스 그로스', 'All'),
    ('인사기획 HRM 조직문화', 'All'),
    ('재무회계 결산 K-IFRS', 'All'),
    ('백엔드개발 서버 API MSA', 'All'),
    ('cloud 영업하신 분', 'SENIOR'),
]

print('=== 검색 결과 ===')
for prompt, seniority in tests:
    r = api_search_v8(prompt, seniority=seniority)
    cnt = len(r.get('matched',[]))
    top = r.get('matched',[{}])[0] if r.get('matched') else {}
    name = top.get('이름') or top.get('name_kr','?')
    print(f'{prompt[:25]}: {cnt}명 | 1위={name}')
