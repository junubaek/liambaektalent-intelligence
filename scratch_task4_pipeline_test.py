import sys
import json
import re

sys.stdout.reconfigure(encoding='utf-8')

# Import functions from jd_compiler
from jd_compiler import parse_jd_to_json

test_queries = [
    "NPU 드라이버 커널 엔지니어 찾아줘",
    "LLM 서빙 추론 최적화 엔지니어",
    "카카오 출신 백엔드 시니어 개발자",
    "삼성전자 경력 SoC 아키텍트",
    "스타트업 CFO 경험자",
    "10년차 이상 재무 담당자",
    "마케팅 그로스 해커 채용",
]

# Domain detection logic replicated from api_search_v9
SEMI_KEYWORDS = ['npu', 'soc', '반도체', 'rtl', 'fpga',
                 'asic', '팹리스', 'chip', '칩', 'verilog',
                 'tape-out', 'tape out', 'ppa']
AI_KEYWORDS   = ['llm', 'ai ', '인공지능', 'ml ', '머신러닝',
                 '딥러닝', 'deep learning', 'gpu', 'inference',
                 '추론', '서빙', 'transformer', 'pytorch', 'mlops']
SW_KEYWORDS   = ['백엔드', 'backend', '프론트', 'frontend',
                 'devops', '인프라', 'infra', 'kubernetes',
                 'docker', 'msa', '마이크로서비스']
EMBEDDED_KEYWORDS = ['드라이버', '커널', 'kernel', 'firmware',
                     '펌웨어', 'bsp', 'rtos', 'embedded',
                     '임베디드']
MARKETING_KEYWORDS = ['마케팅', 'marketing', '광고', '브랜드', 
                      '퍼포먼스', 'CRM', '그로스', 'growth']
PO_KEYWORDS = ['product owner', 'po ', 'p.o.', 
               '프로덕트 오너', '프로덕트 매니저', 'pm ',
               'product manager']
HR_KEYWORDS  = ['hr', '채용', '인사', '총무', 'general affairs', '시설관리', '구매관리', '복리후생', '노무']
DESIGN_KEYWORDS = ['uiux', 'ui/ux', 'ux 디자이너', 'ui 디자이너', 
                   '디자이너', 'product design', 'figma']
CTO_KEYWORDS = ['cto', 'chief technology', '기술 임원', '기술총괄']
CFO_KEYWORDS = ['cfo', 'chief financial', '재무총괄', '최고재무']
KAFKA_KEYWORDS = ['kafka', '카프카', 'message queue', '메시지큐', 'event streaming']

def detect_domain(query: str) -> str:
    query_lower = query.lower()
    if any(k in query_lower for k in SEMI_KEYWORDS):
        return 'semiconductor'
    elif any(k in query_lower for k in EMBEDDED_KEYWORDS):
        return 'embedded'
    elif any(k in query_lower for k in AI_KEYWORDS):
        return 'ai'
    elif any(k in query_lower for k in MARKETING_KEYWORDS):
        return 'marketing'
    elif any(k in query_lower for k in PO_KEYWORDS):
        return 'product'
    elif any(k in query_lower for k in SW_KEYWORDS):
        return 'sw'
    elif any(k in query_lower for k in HR_KEYWORDS):
        return 'hr'
    elif any(k in query_lower for k in DESIGN_KEYWORDS):
        return 'design'
    elif any(k in query_lower for k in CTO_KEYWORDS):
        return 'cto'
    elif any(k in query_lower for k in CFO_KEYWORDS) or any(k in query_lower for k in ['finance', '재무', 'fp&a', 'treasury', '회계', 'accounting']):
        return 'finance'
    elif any(k in query_lower for k in KAFKA_KEYWORDS):
        return 'data_infra'
    else:
        return 'general'

print("=== [Pipeline Test Results] ===")
for q in test_queries:
    parsed = parse_jd_to_json(q)
    domain = detect_domain(q)
    
    # Extract conditions
    conditions = parsed.get("conditions", [])
    skills = [c.get("skill") for c in conditions]
    min_years = parsed.get("min_years", 0)
    
    print(f"\nQuery: '{q}'")
    print(f"  - Detected Domain: {domain}")
    print(f"  - Extracted Target Skills: {skills}")
    if min_years > 0:
        print(f"  - Experience Condition: {min_years} years or more")
    else:
        print(f"  - Experience Condition: None (All)")
print("-" * 50)
