import time
import json
from jd_compiler import api_search_v8

QUERIES = [
    # ── 개발 심화 ──
    "서버 개발자 Java Spring MSA",
    "클라우드 엔지니어 AWS Kubernetes",
    "MLOps 엔지니어",
    "AI 엔지니어 LLM",
    "블록체인 개발자",
    "임베디드 개발자",
    "QA 엔지니어",
    "DBA 데이터베이스 관리자",

    # ── 데이터 심화 ──
    "데이터 엔지니어 Kafka Spark",
    "BI 분석가 Tableau",
    "추천 시스템 개발자",

    # ── 보안 ──
    "정보보안 엔지니어",
    "보안 컨설턴트",
    "침투 테스트 모의해킹",

    # ── 기획 심화 ──
    "서비스 기획자 핀테크",
    "게임 기획자",
    "콘텐츠 기획자",
    "사업 기획자 스타트업",

    # ── 마케팅 심화 ──
    "앱 마케터 UA",
    "SEO 마케터",
    "B2B 마케터 SaaS",
    "인플루언서 마케터",

    # ── 영업·BD 심화 ──
    "엔터프라이즈 영업",
    "파트너십 매니저",
    "커머스 MD",
    "B2B SaaS 영업",

    # ── 경영·전략 ──
    "전략 컨설턴트",
    "사업 운영 매니저 Biz-Ops",
    "스타트업 CFO",
    "VC 심사역",

    # ── HR 심화 ──
    "테크 리크루터",
    "HRBP",
    "교육 L&D 담당자",

    # ── 디자인 심화 ──
    "모션 그래픽 디자이너",
    "브랜드 디자이너",
    "UI 디자이너",

    # ── 산업별 특화 ──
    "핀테크 컴플라이언스",
    "헬스케어 PM",
    "이커머스 운영",
    "물류 SCM 담당자",
]

def main():
    print(f"Headhunter QA Testing v8.5 with {len(QUERIES)} queries...")
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
    print("📊 [QA Report]")
    
    print("\n🚨 [Zero Hit Queries]")
    if not zero_hits:
        print("None! All queries returned hits.")
    else:
        for z in zero_hits:
            print(f"- {z}")
            
    print("\n🏆 [Top 5 Queries by Hits]")
    sorted_res = sorted(results.items(), key=lambda x: x[1], reverse=True)[:5]
    for q, cnt in sorted_res:
        print(f"- {q}: {cnt}명")
    
    with open("headhunter_qa_report_deep.md", "w", encoding="utf-8") as f:
        f.write("# Headhunter Deep QA Report\n\n")
        f.write("## Zero Hits\n")
        for z in zero_hits: f.write(f"- {z}\n")
        f.write("\n## Top 5 Hits\n")
        for q, cnt in sorted_res: f.write(f"- {q}: {cnt}명\n")
        f.write("\n## All Results\n")
        for q, cnt in results.items(): f.write(f"- {q}: {cnt}명\n")
        
    print("\n✅ Testing completed! Saved to headhunter_qa_report_deep.md")

if __name__ == "__main__":
    main()
