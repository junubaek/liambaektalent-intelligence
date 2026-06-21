import sys
import os

# Ensure UTF-8 output
sys.stdout.reconfigure(encoding='utf-8')
sys.path.append(r'C:\Users\cazam\Downloads\이력서자동분석검색시스템')

from jd_compiler import api_search_v9

query = "NPU 드라이버 커널 엔지니어 찾아줘"
print(f"Executing local v9 search for query: '{query}'")

try:
    res = api_search_v9(query)
    matched = res.get('matched', [])
    print(f"\nTop 10 Results (Local v9):")
    print("-" * 60)
    for i, c in enumerate(matched[:10]):
        name = c.get('name_kr') or c.get('name')
        score = c.get('final_score') or 0.0
        sector = c.get('sector') or ''
        company = c.get('current_company') or '미상'
        print(f"{i+1}. {name} | Score: {score:.3f} | 분야: {sector} | 회사: {company}")
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
