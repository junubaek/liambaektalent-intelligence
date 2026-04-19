import sys
import asyncio
sys.path.append(r'c:\Users\cazam\Downloads\이력서자동분석검색시스템')
from jd_compiler import api_search_v8

def test_search():
    queries = [
        'npu 런타임 엔지니어',
        '자금 팀장',
        '5년차 이상 devops 엔지니어'
    ]
    for q in queries:
        try:
            res = api_search_v8(prompt=q)
            matched = res.get('matched', [])
            if matched:
                top = matched[0]
                name = top.get('name_kr') or top.get('name')
                score = top.get('total_score')
                print(f"쿼리 [{q}] -> 1위: {name} (Score: {score})")
            else:
                print(f"쿼리 [{q}] -> 결과 없음")
        except Exception as e:
            print(f'에러: {e}')

if __name__ == "__main__":
    test_search()
