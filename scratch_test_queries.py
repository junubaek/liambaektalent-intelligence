from jd_compiler import api_search_v9

def run_test(query_name, query_text):
    print(f"\n{'='*100}")
    print(f"테스트: {query_name} ({query_text})")
    print(f"{'='*100}")
    
    res = api_search_v9(query_text)
    matched = res['matched'][:5]
    
    header = "순위 | 이름 | final | v_score | g_score | depth | 현직장 | 요약"
    print(header)
    print("-" * 100)
    
    for i, c in enumerate(matched, 1):
        summary = (c['profile_summary'] or "").replace('\n', ' ')[:50]
        row = (
            f"{i} | {c['name_kr']} | {c['final_score']:.4f} | {c['v_score']:.2f} | "
            f"{c['g_score']:.2f} | {c['depth_score']:.4f} | "
            f"{c['current_company'] or 'N/A'} | {summary}..."
        )
        print(row)

if __name__ == "__main__":
    queries = [
        ("SoC 전력 설계 시니어", "SoC 전력 설계 시니어"),
        ("딥러닝 모델 최적화 엔지니어", "딥러닝 모델 최적화 엔지니어"),
        ("반도체 공정 개발 삼성 출신", "반도체 공정 개발 삼성 출신")
    ]
    
    for name, text in queries:
        run_test(name, text)
