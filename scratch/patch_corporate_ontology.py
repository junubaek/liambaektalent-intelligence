import re
import sys
import os

# Set encoding for output
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

target_file = 'ontology_graph.py'

if not os.path.exists(target_file):
    print(f"Error: {target_file} not found.")
    sys.exit(1)

with open(target_file, 'r', encoding='utf-8') as f:
    content = f.read()

edge_pattern = re.findall(r'\(\"([^\"]+)\",\s*\"([^\"]+)\",\s*\"([^\"]+)\",\s*([\d.]+)\)', content)
EXISTING = set()
for s, d, r, w in edge_pattern:
    EXISTING.add((s, d))
    EXISTING.add((d, s))

print(f'기존 엣지 수: {len(edge_pattern)}')

new_edges = []
added = set()

def add(src, dst, rel, weight):
    if (src, dst) not in EXISTING and (dst, src) not in EXISTING and (src, dst) not in added:
        new_edges.append((src, dst, rel, weight))
        added.add((src, dst))

# ── Sales_Core (신규 허브) ──────────────────────────────
add("Sales_Core",            "B2B_Sales",                   "part_of",    2.0)
add("Sales_Core",            "B2C_Sales",                   "part_of",    2.0)
add("Sales_Core",            "Enterprise_Sales",            "part_of",    2.0)
add("Sales_Core",            "Channel_Management",          "part_of",    1.8)
add("Sales_Core",            "Account_Management",          "part_of",    1.8)
add("Sales_Core",            "Global_Sales",                "part_of",    1.8)
add("Sales_Core",            "Sales_Leadership",            "part_of",    1.8)
add("Sales_Core",            "Sales_Management",            "part_of",    1.8)
add("Sales_Core",            "Sales_Analytics",             "part_of",    1.5)
add("Sales_Core",            "Chief_Revenue_Officer",       "part_of",    1.5)

# Sales_Leadership 고립 해제
add("Sales_Leadership",      "Sales_Core",                  "part_of",    1.8)
add("Sales_Leadership",      "B2B_Sales",                   "depends_on", 1.8)
add("Sales_Leadership",      "Enterprise_Sales",            "depends_on", 1.8)
add("Sales_Leadership",      "Business_Development",        "related_to", 1.3)

# Enterprise_Sales 고립 해제
add("Enterprise_Sales",      "B2B_Sales",                   "similar_to", 0.7)
add("Enterprise_Sales",      "Account_Management",          "depends_on", 1.8)
add("Enterprise_Sales",      "Sales_Core",                  "part_of",    1.8)
add("Enterprise_Sales",      "Channel_Management",          "related_to", 0.5)

# Channel_Management 고립 해제
add("Channel_Management",    "B2B_Sales",                   "related_to", 0.6)
add("Channel_Management",    "Distribution_and_Retail",     "related_to", 0.6)
add("Channel_Management",    "Sales_Core",                  "part_of",    1.8)
add("Channel_Management",    "Strategic_Partnership",       "related_to", 0.5)

# Account_Management 고립 해제
add("Account_Management",    "B2B_Sales",                   "depends_on", 1.8)
add("Account_Management",    "Enterprise_Sales",            "similar_to", 0.6)
add("Account_Management",    "Sales_Core",                  "part_of",    1.8)
add("Account_Management",    "CRM_Strategy",                "related_to", 0.5)

# Sales_Management 고립 해제
add("Sales_Management",      "Sales_Core",                  "part_of",    1.8)
add("Sales_Management",      "Sales_Analytics",             "depends_on", 1.5)
add("Sales_Management",      "B2B_Sales",                   "related_to", 0.6)

# Sales_Analytics 고립 해제
add("Sales_Analytics",       "Sales_Core",                  "part_of",    1.5)
add("Sales_Analytics",       "Data_Driven_Decision",        "depends_on", 1.5)
add("Sales_Analytics",       "Sales_Management",            "related_to", 0.5)

# Global_Sales 고립 해제
add("Global_Sales",          "Sales_Core",                  "part_of",    1.8)
add("Global_Sales",          "B2B_Sales",                   "related_to", 0.6)
add("Global_Sales",          "Global_Business_Development", "related_to", 0.6)

# Chief_Revenue_Officer 고립 해제
add("Chief_Revenue_Officer", "Sales_Leadership",            "part_of",    1.8)
add("Chief_Revenue_Officer", "Sales_Core",                  "part_of",    1.5)
add("Chief_Revenue_Officer", "Business_Development",        "related_to", 0.5)

# Distribution_and_Retail 고립 해제
add("Distribution_and_Retail","B2C_Sales",                  "related_to", 0.6)
add("Distribution_and_Retail","Channel_Management",         "related_to", 0.6)
add("Distribution_and_Retail","Sales_Core",                 "part_of",    1.5)
add("Distribution_and_Retail","Commerce_MD",                "related_to", 0.5)

# Commerce_MD 고립 해제
add("Commerce_MD",           "Distribution_and_Retail",     "related_to", 0.6)
add("Commerce_MD",           "B2C_Sales",                   "related_to", 0.5)
add("Commerce_MD",           "Sales_Core",                  "part_of",    1.5)
add("Commerce_MD",           "E_Commerce_Operations",       "similar_to", 0.6)

# E_Commerce_Operations 고립 해제
add("E_Commerce_Operations", "Commerce_MD",                 "similar_to", 0.6)
add("E_Commerce_Operations", "B2C_Sales",                   "related_to", 0.5)
add("E_Commerce_Operations", "Sales_Core",                  "part_of",    1.5)

# ── HR_Core (신규 허브) ─────────────────────────────────
add("HR_Core",               "Talent_Acquisition",          "part_of",    2.0)
add("HR_Core",               "Learning_and_Development",    "part_of",    2.0)
add("HR_Core",               "Compensation_and_Benefits",   "part_of",    2.0)
add("HR_Core",               "HR_Operations",               "part_of",    2.0)
add("HR_Core",               "HR_Strategic_Planning",       "part_of",    1.8)
add("HR_Core",               "Performance_and_Compensation","part_of",    1.8)
add("HR_Core",               "Global_HR",                   "part_of",    1.8)
add("HR_Core",               "HR_Leadership",               "part_of",    1.8)
add("HR_Core",               "HR_and_Admin_Management",     "part_of",    1.5)
add("HR_Core",               "HR_Strategy_and_Operations",  "part_of",    1.5)
add("HR_Core",               "Recruiting_and_Talent_Acquisition","part_of",1.8)
add("HR_Core",               "Labor_Law_Compliance",        "related_to", 0.5)

# HR_Leadership 고립 해제
add("HR_Leadership",         "HR_Core",                     "part_of",    1.8)
add("HR_Leadership",         "HR_Strategic_Planning",       "depends_on", 1.8)
add("HR_Leadership",         "Talent_Acquisition",          "depends_on", 1.5)

# Performance_and_Compensation 고립 해제
add("Performance_and_Compensation","HR_Core",               "part_of",    1.8)
add("Performance_and_Compensation","Compensation_and_Benefits","similar_to",0.7)
add("Performance_and_Compensation","HR_Strategic_Planning", "related_to", 0.5)

# Global_HR 고립 해제
add("Global_HR",             "HR_Core",                     "part_of",    1.8)
add("Global_HR",             "Talent_Acquisition",          "related_to", 0.5)
add("Global_HR",             "HR_Strategic_Planning",       "related_to", 0.5)

# Recruiting_and_Talent_Acquisition 고립 해제
add("Recruiting_and_Talent_Acquisition","Talent_Acquisition","similar_to",0.9)
add("Recruiting_and_Talent_Acquisition","HR_Core",          "part_of",    1.8)

# HR_Operations 보강
add("HR_Operations",         "HR_Core",                     "part_of",    1.8)
add("HR_Operations",         "Labor_Law_Compliance",        "depends_on", 1.5)
add("HR_Operations",         "Compensation_and_Benefits",   "related_to", 0.5)

# Learning_and_Development 보강
add("Learning_and_Development","HR_Core",                   "part_of",    1.8)
add("Learning_and_Development","HR_Strategic_Planning",     "related_to", 0.5)
add("Learning_and_Development","Talent_Acquisition",        "related_to", 0.3)

# 형제 척력
add("Talent_Acquisition",    "Compensation_and_Benefits",   "related_to", 0.3)
add("Talent_Acquisition",    "Learning_and_Development",    "related_to", 0.3)
add("Compensation_and_Benefits","Learning_and_Development", "related_to", 0.3)

# ── Marketing_Strategy / Marketing_Core 고립 해제 ───────────────

# Marketing_Planning 고립 해제
add("Marketing_Planning",    "Marketing_Strategy",          "part_of",    1.8)
add("Marketing_Planning",    "Marketing_Core",              "part_of",    1.5)
add("Marketing_Planning",    "Digital_Marketing",           "related_to", 0.4)

# BTL_Marketing 고립 해제
add("BTL_Marketing",         "Marketing_Strategy",          "part_of",    1.5)
add("BTL_Marketing",         "Brand_Management",            "related_to", 0.5)
add("BTL_Marketing",         "IMC_Strategy",                "related_to", 0.5)
add("BTL_Marketing",         "Digital_Marketing",           "related_to", 0.2)  # 척력

# Promotion_Planning 고립 해제
add("Promotion_Planning",    "Marketing_Strategy",          "part_of",    1.5)
add("Promotion_Planning",    "BTL_Marketing",               "similar_to", 0.6)
add("Promotion_Planning",    "Brand_Management",            "related_to", 0.4)

# App_Marketing 고립 해제
add("App_Marketing",         "Digital_Marketing",           "part_of",    1.8)
add("App_Marketing",         "Performance_Marketing",       "similar_to", 0.6)
add("App_Marketing",         "Growth_Marketing",            "similar_to", 0.5)
add("App_Marketing",         "Brand_Management",            "related_to", 0.2)  # 척력

# Performance_Analytics 고립 해제
add("Performance_Analytics", "Digital_Marketing",           "part_of",    1.5)
add("Performance_Analytics", "Performance_Marketing",       "depends_on", 1.8)
add("Performance_Analytics", "Data_Driven_Decision",        "depends_on", 1.5)

# Proposal_Writing 고립 해제
add("Proposal_Writing",      "B2B_Marketing_Strategy",      "related_to", 0.6)
add("Proposal_Writing",      "Marketing_Core",              "related_to", 0.4)

# ── Finance_Core (신규 허브) ──────────────────────────────
add("Finance_Core",          "Corporate_Finance",           "part_of",    2.0)
add("Finance_Core",          "Financial_Accounting",        "part_of",    2.0)
add("Finance_Core",          "FP_and_A",                    "part_of",    2.0)
add("Finance_Core",          "Tax_Advisory_and_Compliance", "part_of",    1.8)
add("Finance_Core",          "Treasury_Management",         "part_of",    1.8)
add("Finance_Core",          "Consolidated_Accounting",     "part_of",    1.8)
add("Finance_Core",          "Finance_Leadership",          "part_of",    1.8)
add("Finance_Core",          "Corporate_Accounting",        "part_of",    1.8)
add("Finance_Core",          "Financial_Systems_Management","part_of",    1.5)
add("Finance_Core",          "Financial_Regulation",        "part_of",    1.5)
add("Finance_Core",          "Financial_Certificate_KR",    "part_of",    1.3)
add("Finance_Core",          "Forensic_Accounting",         "part_of",    1.3)

# FP_and_A 고립 해제 (핵심)
add("FP_and_A",              "Finance_Core",                "part_of",    1.8)
add("FP_and_A",              "Financial_Planning_and_Analysis","similar_to",0.9)
add("FP_and_A",              "Corporate_Finance",           "part_of",    1.8)
add("FP_and_A",              "Data_Driven_Decision",        "depends_on", 1.5)
add("FP_and_A",              "Corporate_Strategic_Planning","related_to", 0.5)
add("FP_and_A",              "Treasury_Management",         "related_to", 0.3)  # 척력

# Financial_Planning_and_Analysis 고립 해제
add("Financial_Planning_and_Analysis","FP_and_A",           "similar_to", 0.9)
add("Financial_Planning_and_Analysis","Finance_Core",       "part_of",    1.8)
add("Financial_Planning_and_Analysis","Corporate_Finance",  "part_of",    1.8)

# Consolidated_Accounting 고립 해제
add("Consolidated_Accounting","Finance_Core",               "part_of",    1.8)
add("Consolidated_Accounting","Financial_Accounting",       "similar_to", 0.7)
add("Consolidated_Accounting","Corporate_Accounting",       "similar_to", 0.6)
add("Consolidated_Accounting","Mergers_and_Acquisitions",   "related_to", 0.5)

# Financial_Systems_Management 고립 해제
add("Financial_Systems_Management","Finance_Core",          "part_of",    1.5)
add("Financial_Systems_Management","Financial_Accounting",  "depends_on", 1.5)
add("Financial_Systems_Management","Corporate_Accounting",  "related_to", 0.5)

# Financial_Regulation 고립 해제
add("Financial_Regulation",  "Finance_Core",                "part_of",    1.5)
add("Financial_Regulation",  "Financial_Compliance",        "similar_to", 0.7)
add("Financial_Regulation",  "Tax_Advisory_and_Compliance", "related_to", 0.4)

# Forensic_Accounting 고립 해제
add("Forensic_Accounting",   "Finance_Core",                "part_of",    1.3)
add("Forensic_Accounting",   "Financial_Accounting",        "related_to", 0.4)
add("Forensic_Accounting",   "Mergers_and_Acquisitions",    "related_to", 0.5)

# Financial_Certificate_KR 고립 해제
add("Financial_Certificate_KR","Finance_Core",              "part_of",    1.3)
add("Financial_Certificate_KR","Financial_Accounting",      "related_to", 0.4)

# Finance_Leadership 보강
add("Finance_Leadership",    "Finance_Core",                "part_of",    1.8)
add("Finance_Leadership",    "FP_and_A",                    "depends_on", 1.5)
add("Finance_Leadership",    "Treasury_Management",         "depends_on", 1.5)

# 재무 형제 척력
add("Treasury_Management",   "Financial_Accounting",        "related_to", 0.2)
add("Tax_Advisory_and_Compliance","Financial_Accounting",   "related_to", 0.3)
add("Consolidated_Accounting","Treasury_Management",        "related_to", 0.2)

NEW_ALIASES = {
    # 영업
    "Sales_Core": [
        "영업", "세일즈", "영업팀", "sales",
        "영업 전문가", "영업 담당",
    ],
    "Sales_Leadership": [
        "영업 리더십", "영업 총괄", "영업 임원",
        "영업본부장", "영업팀장", "세일즈 리더",
        "CSO", "Chief Sales Officer",
    ],
    "Enterprise_Sales": [
        "엔터프라이즈 영업", "대기업 영업",
        "enterprise sales", "대형 고객 영업",
        "전략 고객 영업", "KAM", "Key Account Manager",
    ],
    "Channel_Management": [
        "채널 관리", "파트너 채널", "대리점 관리",
        "channel management", "채널 영업",
        "딜러 관리", "총판 관리", "리셀러",
    ],
    "Account_Management": [
        "어카운트 매니지먼트", "고객 관리",
        "account management", "거래처 관리",
        "고객사 관리", "AM", "account manager",
    ],
    "Global_Sales": [
        "해외 영업", "글로벌 영업", "수출 영업",
        "global sales", "해외 세일즈",
        "해외 시장 개척", "export sales",
    ],
    "Sales_Management": [
        "영업 관리", "sales management",
        "영업 운영", "세일즈 오퍼레이션",
        "sales ops", "영업 프로세스",
    ],
    "Sales_Analytics": [
        "영업 분석", "sales analytics",
        "매출 분석", "파이프라인 분석",
        "세일즈 데이터", "영업 KPI",
    ],
    "Chief_Revenue_Officer": [
        "CRO", "최고매출책임자", "Chief Revenue Officer",
        "수익 총괄", "매출 총괄",
    ],
    "Commerce_MD": [
        "MD", "상품기획", "머천다이징",
        "merchandising", "바이어", "buyer",
        "상품 MD", "카테고리 매니저",
    ],
    # HR
    "HR_Core": [
        "인사", "HR", "인사팀", "인력관리",
        "human resources", "사람관리",
    ],
    "HR_Leadership": [
        "HR 리더십", "인사 총괄", "CHRO",
        "Chief Human Resources Officer", "인사본부장",
        "HR 임원", "인사 임원",
    ],
    "Performance_and_Compensation": [
        "성과관리", "보상 관리", "평가제도",
        "performance management", "KPI 관리",
        "인센티브", "성과급", "연봉 관리",
    ],
    "Global_HR": [
        "글로벌 HR", "global HR", "해외 인사",
        "글로벌 인사", "expat 관리", "주재원 관리",
        "cross-border HR",
    ],
    "Recruiting_and_Talent_Acquisition": [
        "채용", "리크루팅", "recruiting",
        "인재 채용", "헤드헌팅", "sourcing",
        "채용 담당", "채용 전략",
    ],
    # 마케팅
    "Marketing_Planning": [
        "마케팅 기획", "마케팅플래닝",
        "marketing planning", "마케팅 전략 기획",
        "마케팅 계획", "연간 마케팅 계획",
    ],
    "BTL_Marketing": [
        "BTL", "BTL 마케팅", "오프라인 마케팅",
        "이벤트 마케팅", "체험 마케팅",
        "프로모션", "현장 마케팅",
    ],
    "Promotion_Planning": [
        "프로모션 기획", "판촉 기획",
        "promotion planning", "캠페인 기획",
        "판촉 활동",
    ],
    "App_Marketing": [
        "앱 마케팅", "app marketing", "모바일 마케팅",
        "ASO", "앱스토어 최적화", "UA",
        "user acquisition", "앱 광고",
    ],
    "Performance_Analytics": [
        "퍼포먼스 분석", "마케팅 분석",
        "performance analytics", "ROI 분석",
        "마케팅 데이터 분석", "캠페인 분석",
    ],
    # 재무
    "Finance_Core": [
        "재무", "금융", "재무팀", "finance",
        "재경", "재무/회계", "회계/재무",
    ],
    "FP_and_A": [
        "FP&A", "재무 기획", "재무 분석",
        "financial planning", "재무 계획",
        "예산 관리", "budgeting", "forecasting",
        "재무 모델링", "financial modeling",
    ],
    "Financial_Planning_and_Analysis": [
        "FP&A", "재무계획 및 분석",
        "Financial Planning and Analysis",
        "재무 기획 및 분석",
    ],
    "Consolidated_Accounting": [
        "연결 회계", "연결재무제표", "연결결산",
        "consolidated accounting", "그룹 연결",
        "지배구조 연결", "종속회사 연결",
    ],
    "Financial_Systems_Management": [
        "재무시스템 관리", "ERP 재무",
        "SAP FI", "재무 IT", "회계 시스템",
        "재무 인프라", "Financial Systems",
    ],
    "Financial_Regulation": [
        "금융 규제", "financial regulation",
        "금융법규", "규제 대응", "금융감독",
        "FSS", "금융감독원 대응",
    ],
    "Forensic_Accounting": [
        "법정 회계", "forensic accounting",
        "부정 조사", "회계 감사", "fraud 조사",
        "내부 감사", "회계 감리",
    ],
    "Financial_Certificate_KR": [
        "공인회계사", "CPA", "KICPA",
        "세무사", "공인세무사", "회계사",
        "AICPA", "금융자격증",
    ],
}

# Injected edges
edge_lines = [
    '\n    # ══════════════════════════════════════════════',
    '    # 영업/HR/마케팅/재무 온톨로지 보강 (2026-05-07)',
    '    # Sales_Core, HR_Core, Finance_Core 허브 신설',
    '    # ══════════════════════════════════════════════',
]
for s, d, r, w in new_edges:
    w_str = str(int(w)) if w == int(w) else str(w)
    edge_lines.append(f'    ("{s}", "{d}", "{r}", {w_str}),')

edge_patch = '\n'.join(edge_lines)
last_edge = list(re.finditer(r'\("[^"]+",\s*"[^"]+",\s*"[^"]+",\s*[\d.]+\),', content))
if last_edge:
    pos = last_edge[-1].end()
    content = content[:pos] + '\n' + edge_patch + content[pos:]

# Injected aliases
alias_lines = [
    '',
    '    # ══ 영업/HR/마케팅/재무 aliases (2026-05-07) ══',
]
for node, aliases in NEW_ALIASES.items():
    alias_lines.append(f'    "{node}": [')
    for i, alias in enumerate(aliases):
        comma = ',' if i < len(aliases) - 1 else ''
        escaped = alias.replace('"', '\\"')
        alias_lines.append(f'        "{escaped}"{comma}')
    alias_lines.append('    ],')

if 'NODE_ALIASES' in content:
    na_start = content.find('NODE_ALIASES')
    na_end = content.find('\n}', na_start)
    content = content[:na_end] + '\n' + '\n'.join(alias_lines) + content[na_end:]
else:
    map_end = content.find('\n}', content.find('CANONICAL_MAP')) + 2
    content = content[:map_end] + '\n' + '\n'.join(alias_lines) + content[map_end:]

with open(target_file, 'w', encoding='utf-8') as f:
    f.write(content)

print(f'✅ 패치 완료')
print(f'   추가 엣지: {len(new_edges)}개')
