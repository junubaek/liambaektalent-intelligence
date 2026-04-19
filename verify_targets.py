import json
from jd_compiler import api_search_v8

def check_targets():
    q1 = "Framework Software Engineer"
    t1 = "홍기재"
    q2 = "NPU Library Software Engineer"
    t2 = "전예찬"
    
    for q, t in [(q1, t1), (q2, t2)]:
        print(f"Testing {q}...")
        res = api_search_v8(prompt=q)
        matched = res.get('matched', [])
        found = False
        for i, c in enumerate(matched[:30]):
            if c.get('name') == t or c.get('name_kr') == t:
                print(f"✅ {t} found in top 30! Rank: {i+1}")
                found = True
                break
        if not found:
            print(f"❌ {t} NOT found in top 30! Total passed: {len(matched)}")

if __name__ == '__main__':
    check_targets()
