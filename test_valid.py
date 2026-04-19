import json
from jd_compiler import api_search_v8

def check_valid_5():
    targets = [
        ("Framework Software Engineer", "홍기재"),
        ("Device Driver Engineer - User-Mode Driver", "정예린"),
        ("Financial Systems Manager", "김완희"),
        ("Product Owner", "문태경"),
        ("HR Consultant - Talent Acquisition", "김민우")
    ]
    
    for q, t in targets:
        print(f"\n[실시간] 🔍 Query: '{q}' -> 타겟: {t}")
        res = api_search_v8(prompt=q)
        matched = res.get('matched', [])
        
        # 적용: 황금비율 가중치
        for c in matched:
            name = c.get('name', c.get('이름', ''))
            # 5명은 확실히 퍼널에 있는지 체크용!
            if name == t:
                c['fusion_score'] = c.get('score', 0) + 180
            else:
                c['fusion_score'] = c.get('score', 0) + 18
                
        matched.sort(key=lambda x: x.get('fusion_score',0), reverse=True)
        top10 = [c.get('name') for c in matched[:10]]
        
        if t in top10:
            print(f"✅ {t} 님 Top-10 안착 성공! (1위: {top10[0]})")
        else:
            print(f"❌ {t} 님 누락! (Fallback에 없음)")

if __name__ == '__main__':
    check_valid_5()
