import sys
import json

def main():
    sys.stdout.reconfigure(encoding='utf-8')
    sys.path.append(r'C:\Users\cazam\Downloads\이력서자동분석검색시스템')
    from jd_compiler import api_search_v9

    queries = [
        "NPU 드라이버 커널 엔지니어 찾아줘",
        "LLM 서빙 추론 최적화 엔지니어",
        "SoC 아키텍트 찾아줘"
    ]

    for q in queries:
        print(f"\n==========================================")
        print(f"🔍 쿼리 테스트: '{q}'")
        print(f"==========================================")
        res = api_search_v9(q)
        matched = res.get('matched', [])
        
        # Print Top 10 for analysis
        print(f"Top 10 결과:")
        for i, c in enumerate(matched[:10]):
            name = c.get('name_kr', c.get('name', 'Unknown'))
            score = c.get('final_score', 0)
            v = c.get('v_score', 0)
            g = c.get('g_score', 0)
            sector = c.get('sector', '미분류')
            print(f"  {i+1}위: {name} (Final: {score:.4f} | V: {v:.4f} | G: {g:.4f} | Sector: {sector})")

if __name__ == '__main__':
    main()
