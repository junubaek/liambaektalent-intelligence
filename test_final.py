from jd_compiler import api_search_v8
import json

def test_queries():
    queries = [
        'Framework Software Engineer',
        'DevOps Platform Engineer',
        'NPU Library Software Engineer'
    ]
    
    for q in queries:
        print(f"\n========================================")
        print(f"🔍 API 실행: '{q}'")
        res = api_search_v8(q)
        matched = res.get('matched', [])
        print("👉 상위 5명 결과:")
        for i, r in enumerate(matched[:5]):
            print(f"    {i+1}위. {r.get('name', '미상')} (Score: {r.get('score', 0)})")
        
        # 순위 밖으로 밀려났는지 확인용 (타겟)
        targets = {'Framework Software Engineer': '홍기재', 'DevOps Platform Engineer': '오원교', 'NPU Library Software Engineer': '전예찬'}
        target = targets[q]
        rank = -1
        for i, r in enumerate(matched):
            if target in (r.get('name') or ''):
                rank = i + 1
                break
        print(f"    --- 타겟({target}) 실제 랭크: {rank if rank != -1 else '50위 밖'}")

if __name__ == '__main__':
    test_queries()
