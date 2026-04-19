import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.stdout.reconfigure(encoding='utf-8')

import jd_compiler

queries = [
    "자금 담당자",
    "자금 운용 전문가",
    "Treasury 전담",
    "글로벌 자금 관리",
    "Cash Management 전문가"
]

print("=== RESULTS ===")

for q in queries:
    try:
        res = jd_compiler.api_search_v8(q)
        candidates = res.get("matched", res.get("candidates", []))
        
        if not candidates:
            print(f"{q} | 결과 없음 | 권외")
            continue
            
        rank1 = candidates[0]
        rank1_str = f"1위: {rank1.get('이름')} ({rank1.get('total_score', rank1.get('_score'))})"
        
        kim = next((c for c in candidates if '김대중' in c.get('이름', '')), None)
        if kim:
            idx = candidates.index(kim) + 1
            kim_str = f"{idx}위 ({kim.get('total_score', kim.get('_score'))})"
        else:
            kim_str = "권외"
            
        print(f"{q} | {rank1_str} | 김대중: {kim_str}")
    except Exception as e:
        print(f"{q} | Error: {e}")
