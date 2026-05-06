
import re
import sys
import os

# Ensure UTF-8 output
sys.stdout.reconfigure(encoding='utf-8')

ONTOLOGY_FILE = 'ontology_graph.py'

if not os.path.exists(ONTOLOGY_FILE):
    print(f"Error: {ONTOLOGY_FILE} not found.")
    sys.exit(1)

# ══════════════════════════════════════════════════════════
# NODE_ALIASES 정의
# ══════════════════════════════════════════════════════════
NODE_ALIASES = {
    # 고객 대면 / Solutions Engineer 계열
    "Client_Communication": [
        "고객사 커뮤니케이션", "Client Communication",
        "고객 기술 지원", "기술 지원", "고객 지원", "고객지원",
        "기술 영업", "솔루션 엔지니어", "필드 엔지니어",
        "FAE", "Field Application Engineer", "Solutions Engineer",
        "Forward Deployed Engineer", "Pre-Sales", "프리세일즈",
        "기술 컨설팅", "고객사 기술 지원", "기술 데모",
        "고객 기술 문의", "customer support", "technical support",
        "customer-facing", "고객 대면",
    ],
    "CX_CS": [
        "CS", "CX", "고객경험", "고객만족",
        "고객서비스", "CS팀", "고객센터", "콜센터",
        "Customer Experience", "Customer Service",
        "고객 CS", "CS 운영",
    ],
    "Product_Owner": [
        "po", "PO", "프로덕트오너", "프로덕트 오너",
        "ProductOwner", "Product Owner", "Product_Owner",
        "Product Owner(PO)", "product owner",
    ],
    "Product_Manager": [
        "프로덕트 매니저", "PM", "pm", "프로덕트매니저",
        "ProductManager", "Product Manager", "Product_Manager",
        "product manager", "프로덕트 매니저(PM)",
    ],
    "Project_Manager": [
        "ProjectManager", "Project Manager(PM)",
        "프로젝트 매니저", "프로젝트매니저",
        "TPM", "Technical PM", "기술 PM",
        "Project Manager", "PM(Project)", "PjM",
        "프로젝트 관리자",
    ],
    "Service_Planning": [
        "서비스 기획", "기획(화면설계)", "서비스기획(화면설계)",
        "서비스 기획자", "서비스 플래너", "기획자",
        "서비스기획자", "IT 서비스 기획", "앱 서비스 기획",
        "플랫폼 기획", "서비스 플래닝",
    ],
    "Requirement_Definition": [
        "요구사항 정의", "요구사항 분석", "요구사항 관리",
        "requirements", "RD", "기능 정의",
        "요구사항 명세", "사용자 요구사항",
    ],
    "User_Research": [
        "사용자 리서치", "유저 리서치", "VOC 분석",
        "사용자 조사", "UX 리서치", "사용자 인터뷰",
        "user research", "UR", "고객 리서치",
        "사용자 경험 분석",
    ],
    "Data_Driven_Decision": [
        "데이터 기반 의사결정", "데이터 드리븐",
        "data-driven", "데이터 기반", "데이터 중심",
        "지표 기반", "KPI 분석", "데이터 의사결정",
    ],
    "Product_Service_Planning": [
        "로드맵", "백로그", "스프린트", "roadmap",
        "backlog", "sprint", "제품 로드맵",
        "서비스 로드맵", "릴리즈 계획",
    ],
    "Stakeholder_Management": [
        "이해관계자 관리", "스테이크홀더", "stakeholder",
        "크로스펑셔널", "cross-functional", "유관부서 협업",
        "사업-기술 협업", "고객 인게이지먼트",
        "customer engagement", "파트너 관리",
    ],
    "LLM_Inference": [
        "LLM추론", "모델경량화", "추론최적화",
        "AI 추론", "추론 최적화", "인공지능 추론",
        "모델 추론", "inference", "AI inference",
        "vLLM 추론", "LLM 추론", "추론 가속",
        "throughput 최적화", "latency 최적화",
    ],
    "LLM_Serving": [
        "모델서빙", "LLM Serving", "LLM 서빙",
        "AI 서빙", "vLLM", "TensorRT", "TensorRT-LLM",
        "serving", "model serving", "추론 서빙",
    ],
    "Model_Serving": [
        "모델 배포", "AI 모델 배포", "serving infrastructure",
        "추론 인프라", "AI 서빙 인프라", "서빙 인프라",
        "production serving", "프로덕션 서빙",
    ],
    "MLOps": [
        "ML운영", "엔지니어(Serving/MLOps)", "MLOps",
        "AI 인프라", "인공지능 인프라", "ML 인프라",
        "AI 플랫폼", "머신러닝 인프라", "AI 시스템",
        "ML Ops", "머신러닝 운영", "AI 운영",
        "프로덕션 ML", "production ML",
    ],
    "ML_Pipeline": [
        "AI 파이프라인", "머신러닝 파이프라인",
        "워크로드 스케줄링", "workload scheduling",
        "ML pipeline", "데이터 파이프라인(ML)",
        "학습 파이프라인",
    ],
    "Hardware_Acceleration": [
        "하드웨어 가속", "GPU 가속", "AI 가속",
        "모델 최적화", "quantization", "퀀타이제이션",
        "pipelining", "파이프라이닝", "에너지 효율",
        "성능 벤치마킹", "시스템 병목 분석",
        "hardware acceleration", "성능 최적화",
    ],
    "NPU": [
        "NPU", "AI가속기", "AI Chip", "Neural Processing Unit",
        "NPU 가속", "뉴럴 프로세싱", "신경망 처리장치",
    ],
    "AI_Accelerator": [
        "AI 칩", "AI chip", "edge AI", "엣지 AI",
        "AI 반도체 가속기", "accelerator", "AI accelerator",
    ],
    "Deep_Learning": [
        "딥러닝", "deep learning", "인공지능", "AI",
        "신경망", "neural network", "PyTorch", "파이토치",
        "TensorFlow", "텐서플로",
    ],
    "Machine_Learning": [
        "머신러닝", "machine learning", "ML",
        "기계학습", "예측 모델", "지도학습",
    ],
    "LLM_Engineering": [
        "LLM", "대형 언어 모델", "파운데이션 모델",
        "foundation model", "생성형 AI", "generative AI",
        "RAG", "파인튜닝", "fine-tuning",
        "LLM 엔지니어링", "프롬프트 엔지니어링",
    ],
    "Technical_Documentation": [
        "기술 문서", "기술 문서화", "기술 가이드",
        "통합 가이드", "best practice", "베스트 프랙티스",
        "화이트페이퍼", "whitepaper", "기술 블로그",
        "API 문서", "기술 명세", "테크니컬 라이팅",
    ],
    "Kubernetes": [
        "쿠버네티스", "k8s", "Kubernetes",
        "컨테이너 오케스트레이션", "container orchestration",
        "고가용성", "high availability", "failover",
        "k8s 운영", "쿠버네티스 운영",
    ],
    "Docker": [
        "도커", "Docker", "컨테이너", "container",
        "docker-compose", "컨테이너 빌드",
    ],
    "Treasury_Management": [
        "캐시풀링", "자금", "자금담당", "자금관리",
        "자금운용", "자금조달", "자금 운용", "금융상품 운용",
        "Treasury", "재무 운용", "기업 자금", "자금_Treasury",
        "자금총괄", "자금팀", "운전자금",
    ],
    "Mergers_and_Acquisitions": [
        "재무자문/M&A", "M&A", "PMI", "인수합병",
        "크로스보더 딜", "Mergers and Acquisitions",
        "Mergers_and_Acquisitions", "기업인수", "합병",
        "M&A 자문", "딜 실행",
    ],
    "IPO_Preparation_and_Execution": [
        "기업공개", "IPO 업무", "IPO 준비", "예비심사청구",
        "IPO 준비 및 실행", "IPO Preparation and Execution",
        "IPO_Preparation_and_Execution", "IPO", "상장 준비",
        "코스닥 상장", "코스피 상장", "상장심사",
    ],
    "Talent_Acquisition": [
        "Recruiting_and_Talent_Acquisition", "테크 리크루터",
        "IT 리크루터", "채용", "리크루팅", "인재 채용",
        "Talent Acquisition", "헤드헌팅", "sourcing",
        "채용 담당", "인사 채용", "채용 전략",
    ],
    "Distribution_and_Retail": [
        "Retail_Distribution", "유통", "리테일",
        "Distribution and Retail", "유통관리",
        "도소매", "유통 채널", "오프라인 유통",
    ],
    "Data_Analysis": [
        "데이터 분석", "데이터분석", "DA", "데이터분석가",
        "DataAnalysis", "data analysis", "데이터 애널리스트",
        "분석가", "비즈니스 분석",
    ],
    "Data_Visualization": [
        "데이터 시각화", "data visualization",
        "Tableau", "Power BI", "대시보드",
        "시각화", "Data Visualization and Dashboarding",
    ],
    "Information_Security": [
        "Encryption FDE/FBE", "정보보안_Information_Security",
        "Security_Incident_Analysis_and_Reporting",
        "Security_Monitoring_and_Operations",
        "정보보안 엔지니어", "Information_Security",
        "보안 엔지니어", "보안 컨설턴트", "정보보안",
        "보안", "사이버 보안", "cybersecurity",
        "Information Security", "보안 관제",
    ],
    "Performance_Marketing": [
        "퍼포먼스마케팅", "SEO", "SEO 마케터", "검색엔진최적화",
        "퍼포먼스 마케팅", "CPA 감소", "미디어 믹스",
        "전환 캠페인", "퍼포먼스 광고", "디지털 광고",
        "SEM", "그로스 마케팅", "Performance Marketing",
    ],
    "Corporate_Strategic_Planning": [
        "전략 수립", "전략", "사업전략", "경영 기획",
        "전략 기획", "경영계획 수립", "경영실적 보고",
        "사업계획 수립", "전략기획팀", "경영기획",
        "Corporate Planning", "전략경영", "기업전략",
    ],
    "Business_Development": [
        "사업개발_BD", "사업개발", "BD",
        "Business Development", "비즈니스 개발",
        "파트너십 개발", "사업 확장",
    ],
    "New_Business_Development": [
        "New_Business_Development", "신사업 개발", "신사업 제휴",
        "New Business Development", "신사업", "신규사업",
        "신사업 발굴 및 런칭", "신규 사업", "신사업 기획",
        "사업 다각화",
    ],
}

with open(ONTOLOGY_FILE, 'r', encoding='utf-8') as f:
    content = f.read()

# Remove existing NODE_ALIASES if any
if 'NODE_ALIASES' in content:
    # Look for NODE_ALIASES: dict[str, list[str]] = { ... }
    match = re.search(r'\n# ══════════════════════════════════════════════════════\n# NODE_ALIASES — .*?\n# ══════════════════════════════════════════════════════\nNODE_ALIASES: dict\[str, list\[str\]\] = \{.*?\}\n', content, re.DOTALL)
    if not match:
        # Fallback to a simpler match if comments are different
        match = re.search(r'\nNODE_ALIASES: dict\[str, list\[str\]\] = \{.*?\}\n', content, re.DOTALL)
    
    if match:
        content = content[:match.start()] + content[match.end():]
        print('기존 NODE_ALIASES 블록 제거 완료')
    else:
        # If it exists but we can't find it with regex, manual check might be needed.
        # Let's try to find based on first/last lines
        start_idx = content.find('\nNODE_ALIASES')
        if start_idx != -1:
            end_idx = content.find('\n}', start_idx)
            if end_idx != -1:
                content = content[:start_idx] + content[end_idx+2:]
                print('기존 NODE_ALIASES 블록(수동) 제거 완료')

# Find the end of CANONICAL_MAP
map_start = content.find('CANONICAL_MAP')
if map_start != -1:
    map_end = content.find('\n}', map_start) + 2
else:
    print("Error: CANONICAL_MAP not found.")
    sys.exit(1)

# Generate NODE_ALIASES block
lines = [
    '',
    '# ══════════════════════════════════════════════════════',
    '# NODE_ALIASES — 노드별 유사어/다국어/약어 통합 정의',
    '# 어떤 표현으로 검색해도 동일 노드로 수렴',
    '# 마지막 업데이트: 2026-05-07',
    '# ══════════════════════════════════════════════════════',
    'NODE_ALIASES: dict[str, list[str]] = {',
]

for node, aliases in NODE_ALIASES.items():
    lines.append(f'    "{node}": [')
    for i, alias in enumerate(aliases):
        comma = ',' if i < len(aliases) - 1 else ''
        escaped = alias.replace('"', '\\"')
        lines.append(f'        "{escaped}"{comma}')
    lines.append('    ],')

lines.append('}')
lines.append('')
lines.append('# NODE_ALIASES를 CANONICAL_MAP에 자동 병합')
lines.append('for _node, _aliases in NODE_ALIASES.items():')
lines.append('    for _alias in _aliases:')
lines.append('        if _alias not in CANONICAL_MAP:')
lines.append('            CANONICAL_MAP[_alias] = _node')
lines.append('')

patch = '\n'.join(lines)
new_content = content[:map_end] + '\n' + patch + content[map_end:]

with open(ONTOLOGY_FILE, 'w', encoding='utf-8') as f:
    f.write(new_content)

total_aliases = sum(len(v) for v in NODE_ALIASES.values())
print(f'✅ NODE_ALIASES 블록 삽입 완료')
print(f'   노드 수: {len(NODE_ALIASES)}개')
print(f'   총 alias 수: {total_aliases}개')
print(f'   CANONICAL_MAP 자동 병합 코드 추가')
