import sys
import os

# Ensure UTF-8 output
sys.stdout.reconfigure(encoding='utf-8')
sys.path.append(r'C:\Users\cazam\Downloads\이력서자동분석검색시스템')

from jd_compiler import api_search_v8

query = "NPU 드라이버 커널 엔지니어"
print(f"Executing search for query: '{query}'")

try:
    res = api_search_v8(prompt=query)
    matched = res.get('matched', [])
    print(f"\nTop 5 Results for '{query}':")
    print("-" * 60)
    for i, top in enumerate(matched[:5]):
        name = top.get('name_kr') or top.get('name')
        score = top.get('final_score') or top.get('score') or top.get('total_score') or 0.0
        company = top.get('current_company') or '미상'
        sector = top.get('sector') or '미상'
        summary = top.get('profile_summary') or ''
        # Truncate summary
        if len(summary) > 100:
            summary = summary[:100] + "..."
        print(f"{i+1}. {name} | Score: {score:.4f} | 회사: {company} | 분야: {sector}")
        print(f"   요약: {summary.strip()}")
        print("-" * 60)
except Exception as e:
    print(f"Error during search: {e}")
    import traceback
    traceback.print_exc()
