content = '''
# --- Korean Job Keyword Mappings ---
CANONICAL_MAP.update({
    # 영업/세일즈
    "해외영업": "Global_Sales_and_Marketing",
    "글로벌영업": "Global_Sales_and_Marketing",
    "수출영업": "Global_Sales_and_Marketing",
    "영업관리": "B2B_Sales",
    "기업영업": "B2B_Sales",
    "법인영업": "B2B_Sales",
    "채널영업": "B2B_Sales",
    "대리점 영업": "B2B_Sales",
    "파트너 영업": "Technical_Sales",
    "Pre-sales": "Technical_Sales",
    "프리세일즈": "Technical_Sales",

    # 마케팅
    "디지털마케팅": "Digital_Marketing",
    "퍼포먼스마케팅": "Performance_Marketing",
    "그로스해킹": "Growth_Marketing",
    "CRM": "CRM_Marketing",
    "이메일마케팅": "CRM_Marketing",
    "앱마케팅": "Performance_Marketing",
    "바이럴마케팅": "Content_Marketing",
    "콘텐츠마케팅": "Content_Marketing",
    "인플루언서": "Influencer_and_Sponsorship_Marketing",
    "SNS마케팅": "Content_Marketing",

    # HR
    "인사총무": "HR_Strategic_Planning",
    "인사기획": "HR_Strategic_Planning",
    "채용담당": "Talent_Acquisition",
    "헤드헌팅": "Talent_Acquisition",
    "서치펌": "Talent_Acquisition",
    "급여담당": "Payroll_Management",
    "노무사": "Labor_Law_Compliance",
    "노무관리": "Employee_Relations",
    "조직문화": "Corporate_Culture_Branding",
    "HRD": "Learning_and_Development",
    "HRM": "HR_Strategic_Planning",

    # 재무/회계
    "재무회계": "Financial_Accounting",
    "관리회계": "Management_Accounting",
    "세무회계": "Tax_Accounting",
    "원가회계": "Management_Accounting",
    "결산": "Financial_Accounting",
    "재무제표": "Financial_Accounting",
    "자금관리": "Treasury_Management",
    "자금조달": "Corporate_Funding",
    "IR담당": "IR_Management",
    "투자유치": "IR_Management",
    "FP&A": "Financial_Planning_and_Analysis",
    "예산관리": "Financial_Planning_and_Analysis",

    # 개발
    "백엔드개발": "Backend_Engineering",
    "서버개발": "Backend_Engineering",
    "프론트개발": "Frontend_Development",
    "프론트엔드개발": "Frontend_Development",
    "풀스택": "Backend_Engineering",
    "앱개발": "Mobile_Application_Development",
    "iOS개발": "Mobile_Application_Development",
    "안드로이드": "Android_Development",
    "데이터분석": "Data_Analysis",
    "데이터엔지니어": "Data_Engineering",
    "ML엔지니어": "Machine_Learning",
    "AI엔지니어": "AI_Engineering",
    "인프라엔지니어": "Infrastructure_and_Cloud",
    "클라우드엔지니어": "Infrastructure_and_Cloud",
    "보안엔지니어": "Information_Security",
})

# B2B_Sales Gravity Field 추가
UNIFIED_GRAVITY_FIELD["B2B_Sales"] = {
    "core_attracts": {
        "Global_Sales_and_Marketing": 0.8,
        "Technical_Sales": 0.7,
        "영업기획": 0.7,
        "CRM_Marketing": 0.5,
    },
    "repels": {
        "Financial_Accounting": -0.3,
        "Tax_Accounting": -0.4,
        "Backend_Engineering": -0.2,
        "HR_Strategic_Planning": -0.3,
    }
}

# Technical_Sales 기존 한글 노드 참조 수정
if "Technical_Sales" in UNIFIED_GRAVITY_FIELD:
    UNIFIED_GRAVITY_FIELD["Technical_Sales"]["core_attracts"] = {
        "Infrastructure_and_Cloud": 0.8,
        "Backend_Engineering": 0.7,
        "B2B_Sales": 0.8,
        "Global_Sales_and_Marketing": 0.6,
    }
'''
with open("ontology_graph.py", "a", encoding="utf-8") as f:
    f.write("\n" + content + "\n")
print("추가 완료")
