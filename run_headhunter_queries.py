import sys
import os
import json
import time

from jd_compiler import api_search_v8

QUERIES = [
    # ── 개발 (원티드 1위 직군) ──
    "백엔드 개발자 5년차",
    "프론트엔드 개발자 React",
    "풀스택 개발자 스타트업",
    "데이터 엔지니어 Spark Kafka",
    "머신러닝 엔지니어",
    "DevOps 엔지니어 AWS Kubernetes",
    "iOS 개발자",
    "안드로이드 개발자",

    # ── 마케팅 ──
    "퍼포먼스 마케터 3년차",
    "그로스 마케터",
    "브랜드 마케터",
    "CRM 마케터",
    "콘텐츠 마케터 SNS",
    "B2B 마케터",

    # ── 기획·PM ──
    "서비스 기획자 핀테크",
    "프로덕트 매니저 커머스",
    "사업 기획자",
    "전략 기획 5년차",

    # ── 디자인 ──
    "UX 디자이너",
    "프로덕트 디자이너",
    "브랜드 디자이너",

    # ── 영업·BD ──
    "B2B 영업 SaaS",
    "사업개발 BD 파트너십",
    "해외 영업",

    # ── HR ──
    "채용 담당자 IT 스타트업",
    "HR 기획 보상 담당",
    "조직문화 담당자",

    # ── 금융·재무 ──
    "자금 담당자 핀테크",
    "재무 회계 담당자",
    "IR 담당자",

    # ── 데이터 ──
    "데이터 분석가 SQL",
    "데이터 사이언티스트",

    # ── 정보보안 ──
    "보안 엔지니어"
]

def main():
    print(f"Testing {len(QUERIES)} Headhunter Queries via V8 Engine...")
    
    report_lines = []
    report_lines.append("# 🎯 Headhunter Real-World Query V8 Evaluation Report\n")
    report_lines.append("> 이 문서는 헤드헌터들의 실제 질의어를 대상으로 V8 엔진의 검색 정확성(Precision)을 검증하기 위한 리포트입니다.\n")
    
    zero_hits = []
    
    for q in QUERIES:
        print(f"Querying [{q}]...")
        start = time.time()
        
        try:
            res = api_search_v8(prompt=q)
            matched = res.get('matched', [])
            
            elapsed = time.time() - start
            report_lines.append(f"\n## 🔍 Q: `{q}`")
            report_lines.append(f"- **소요 시간:** {elapsed:.2f}s")
            report_lines.append(f"- **검색 결과:** 총 {len(matched)}건\n")
            
            if not matched:
                report_lines.append("> ❌ 적합한 후보자가 없습니다.\n")
                zero_hits.append(q)
            else:
                for i, c in enumerate(matched[:5]):
                    name = c.get('이름', 'Unknown')
                    score = c.get('_score', 0)
                    mechanics = str(c.get('_mechanics', '')).replace('<br>', ' | ').replace('<b>', '').replace('</b>', '')
                    summary = c.get('Experience Summary', '')[:100] + '...'
                    report_lines.append(f"**{i+1}. {name} (Score: {score})**")
                    report_lines.append(f"  - **역학:** {mechanics}")
                    report_lines.append(f"  - **요약:** {summary}\n")
                    
        except Exception as e:
            report_lines.append(f"❌ Error executing query: {e}\n")
            print(f"Error on {q}: {e}")
            
    with open("headhunter_qa_report.md", "w", encoding="utf-8") as f:
        f.write("\n".join(report_lines))
        
    print("\n[Zero Hit Queries]")
    for z in zero_hits:
        print(f"- {z}")
        
    print("✅ Testing completed! Saved to headhunter_qa_report.md")

if __name__ == "__main__":
    main()
