import time
from jd_compiler import api_search_v8

QUERIES = [
    # ── 금융 심화 ──
    "증권사 애널리스트",
    "자산운용 펀드매니저",
    "신용분석 심사역",
    "보험 계리사",
    "핀테크 결제 담당자",
    "외환 딜러 FX",

    # ── 법무·컴플라이언스 ──
    "사내 변호사",
    "개인정보보호 담당자",
    "금융 규제 대응",
    "특허 담당자",

    # ── 엔지니어링·제조 ──
    "반도체 공정 엔지니어",
    "자동차 소프트웨어 개발자",
    "배터리 개발 연구원",
    "로봇 소프트웨어 엔지니어",
    "AI 반도체 설계",

    # ── 바이오·헬스케어 ──
    "임상시험 CRA",
    "RA 인허가 담당자",
    "신약 개발 연구원",
    "의료기기 개발",

    # ── 미디어·콘텐츠 ──
    "영상 PD 연출",
    "작가 시나리오",
    "유튜브 채널 운영",
    "웹툰 작가",

    # ── 물류·SCM ──
    "물류 운영 담당자",
    "구매 바이어",
    "수출입 무역 담당",
    "SCM 기획자",

    # ── 부동산·건설 ──
    "부동산 개발 기획",
    "건축 설계사",
    "인테리어 디자이너",

    # ── 교육·공공 ──
    "에듀테크 기획자",
    "교육 콘텐츠 개발자",

    # ── 커머스 산업별 ──
    "패션 MD",
    "뷰티 MD",
    "식품 MD",

    # ── 글로벌 ──
    "일본어 사업 담당",
    "동남아 진출 담당",
    "글로벌 HR 담당",
]

def main():
    print(f"Headhunter QA Testing v8.5 with {len(QUERIES)} Round 3 Queries...")
    results = {}
    zero_hits = []

    for q in QUERIES:
        print(f"\nQuerying [{q}]...")
        try:
            start = time.time()
            res = api_search_v8(prompt=q)
            hits = len(res.get('matched', []))
            print(f" => {hits} hits ({time.time() - start:.2f}s)")
            
            results[q] = hits
            if hits == 0:
                zero_hits.append(q)
        except Exception as e:
            print(f" => Error: {e}")
            results[q] = 0
            zero_hits.append(q)
            
    print("\n\n" + "="*50)
    print("[Round 3 QA Report]")
    
    print("\n[Zero Hit Queries]")
    if not zero_hits:
        print("None! All queries returned hits.")
    else:
        for z in zero_hits:
            print(f"- {z}")
            
    print("\n[Top 5 Queries by Hits]")
    sorted_res = sorted(results.items(), key=lambda x: x[1], reverse=True)[:5]
    for q, cnt in sorted_res:
        print(f"- {q}: {cnt}명")
    
    with open("headhunter_qa_round3_report.md", "w", encoding="utf-8") as f:
        f.write("# Headhunter Round 3 QA Report\n\n")
        f.write("## Zero Hits\n")
        for z in zero_hits: f.write(f"- {z}\n")
        f.write("\n## Top 5 Hits\n")
        for q, cnt in sorted_res: f.write(f"- {q}: {cnt}명\n")
        f.write("\n## All Results\n")
        for q, cnt in results.items(): f.write(f"- {q}: {cnt}명\n")
        
    print("\nTesting completed! Saved to headhunter_qa_round3_report.md")

if __name__ == "__main__":
    main()
