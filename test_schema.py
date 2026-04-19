import sys
sys.path.append(r'c:\Users\cazam\Downloads\이력서자동분석검색시스템')
from jd_compiler import api_search_v8

for q in ['자금 팀장', '5년차 이상 devops 엔지니어']:
    res = api_search_v8(q)
    matched = res.get('matched', [])
    if matched:
        top = matched[0]
        print(f'Keys for {q}: {list(top.keys())}')
        print(f"Candidate for {q}: {top.get('candidate', {}).get('name_kr')}")
        print(f"Score for {q}: {top.get('score')} / Fused: {top.get('fused_score')}")
    else:
        print(f'{q} 결과 없음')
