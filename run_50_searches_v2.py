import json
import os
import sys

# Ensure UTF-8 output
sys.stdout.reconfigure(encoding='utf-8')

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT_DIR)

from jd_compiler import api_search_v9

queries = [
    "Neural Network Operations Parallel Programming C++",
    "OEM ExportCompliance MarketResearch",
    "LINUX AWS Architecture",
    "Spring Fintech MSSQL",
    "ASRS Smart Factory Semiconductor Logistics Automation",
    "Blockchain NFT",
    "CFO IPO IR 자금조달 세무 재무총괄",
    "AI Accelerators Generative AI Datacenter GPU cluster",
    "Kubernetes Terraform LangGraph DevOps pipeline",
    "Collective Communication RDMA RoCE InfiniBand",
    "ERP Excel Labor Law HR payroll",
    "Financial Modeling Valuation DCF LBO",
    "Chip Bring-up Driver Development embedded",
    "ARM SVE Neural Network Operations embedded",
    "React TypeScript Next.js frontend performance",
    "CMO 또는 마케팅본부장 브랜드 전략 디지털마케팅",
    "CTO 스타트업 기술총괄 아키텍처",
    "VP Engineering 엔지니어링 조직 빌딩",
    "Product Manager B2B SaaS 기획",
    "Head of Sales 엔터프라이즈 영업 총괄",
    "데이터 사이언티스트 ML 모델링 추천시스템",
    "보안 전문가 CISO 정보보안 컴플라이언스",
    "법무팀장 M&A 계약 검토 스타트업",
    "IR 담당자 투자자 관계 공시 자금조달",
    "구매팀장 SCM 글로벌 소싱 협상",
    "헬스케어 디지털 헬스 의료기기 규제",
    "게임 개발 Unity Unreal 모바일게임",
    "자율주행 모빌리티 센서퓨전 SLAM",
    "핀테크 결제 PG 금융 API",
    "이커머스 플랫폼 그로스 퍼포먼스마케팅",
    "엔터테인먼트 콘텐츠 IP 라이선싱",
    "바이오 제약 임상 규제 RA",
    "반도체 장비 공정 Etch CVD",
    "물류 SCM 풀필먼트 라스트마일",
    "에너지 ESG 탄소중립 신재생에너지",
    "외국계 기업 경험 글로벌 커뮤니케이션 영어",
    "스타트업 초기 멤버 0to1 제품 빌딩",
    "대기업 출신 신사업 사내벤처",
    "컨설팅 출신 전략 기획 사업개발",
    "VC 투자사 심사역 포트폴리오 관리",
    "해외 근무 경험 글로벌 사업 확장",
    "카카오 토스 네이버 출신 프로덕트",
    "삼성전자 SK하이닉스 반도체 출신",
    "시리즈B C 스타트업 재무 CFO 경험",
    "대기업에서 스타트업으로 이직 CX 고객경험",
    "해외 MBA 출신 전략 컨설팅 경험",
    "개발자 출신 PM 기술 이해 프로덕트",
    "마케팅 자동화 CRM Salesforce HubSpot",
    "리테일 이커머스 MD 바잉 상품기획",
    "HR Tech 채용 시스템 ATS 온보딩"
]

output_file = 'golden_search_results_v6_50.txt'

with open(output_file, 'w', encoding='utf-8') as f:
    for i, q in enumerate(queries, 1):
        print(f"[{i}/50] Searching for: {q}")
        res = api_search_v9(q)
        matched = res.get('matched', [])[:5]
        
        f.write(f"[Q{i}] {q}\n")
        
        for rank, cand in enumerate(matched, 1):
            cid = str(cand.get('id', ''))
            name = cand.get('name_kr', 'Unknown')
            company = cand.get('current_company', 'Unknown')
            sector = cand.get('sector', 'Unknown')
            f.write(f"{rank}. {name} | {company} | {sector} | {cid}\n")
        
        f.write("\n")
        f.flush()

print(f"\nDone! Results saved to {output_file}")
