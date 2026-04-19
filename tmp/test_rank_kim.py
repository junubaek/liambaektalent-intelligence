import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.stdout.reconfigure(encoding='utf-8')

import jd_compiler

query = "6년차 이상 자금 담당자"
print(f"=== [쿼리] {query} ===")

try:
    res = jd_compiler.api_search_v8(query)
    candidates = res.get("matched", res.get("candidates", []))
    
    if not candidates:
        print("결과 없음")
    else:
        for idx, c in enumerate(candidates[:20]):
            name = c.get('이름', '')
            score = c.get('total_score', c.get('_score'))
            print(f"[{idx+1}위] {name} | Score: {score}")
            if "김대중" in name:
                print(f"  👉 김대중님 달성 (현재 {idx+1}위)")
                
        kim = next((c for c in candidates if '김대중' in c.get('이름', '')), None)
        if not kim:
            print("  👉 김대중님: 권외 (20위 밖)")
            
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()

print("=== 테스트 완료 ===")
