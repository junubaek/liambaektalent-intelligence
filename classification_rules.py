ALLOWED_ROLES = [
    "영업", "마케팅", "HR", "총무", "Finance", "STRATEGY", "디자인", "법무", "물류/유통",
    "MD", "PRODUCT", "DATA", "SW", "HW", "반도체", "AI", "보안", "기타"
]

ROLE_CLUSTERS = {
    "영업": ["해외영업", "B2B영업", "기술영업", "Pre-sales", "영업지원", "영업기획", "Sales", "Business Development"],
    "마케팅": ["퍼포먼스", "그로스", "브랜드", "콘텐츠", "인플루언서 협업", "PR", "마케팅기획", "Marketing", "Growth"],
    "HR": ["채용", "TA", "평가보상", "C&B", "급여", "Payroll", "노무", "ER", "인사기획", "교육", "L&D", "Human Resources", "Recruiting"],
    "총무": ["복리후생 운영", "자산관리", "IT 비품 관리", "General Affairs"],
    "Finance": ["재무회계", "자금", "세무", "IR", "M&A", "내부통제_감사", "FP&A", "회계사", "Accounting"],
    "STRATEGY": ["전략_경영기획", "Business Operation", "신사업 발굴", "Strategy"],
    "디자인": ["UIUX", "브랜드", "제품", "웹", "디자인 기획", "디자인 시스템", "Design"],
    "법무": ["일반법무", "컴플라이언스", "지적재산권", "IP", "변호사", "Legal"],
    "물류/유통": ["구매", "SCM", "유통망 관리", "물류기획", "Logistics", "Purchasing"],
    "MD": ["상품기획", "소싱MD", "영업MD", "Merchandising"],
    "PRODUCT": ["Product Owner", "PO", "Project Manager", "PM", "서비스기획", "TPM"],
    "DATA": ["데이터분석가", "데이터엔지니어", "데이터사이언티스트", "DBA", "Data Analyst", "Data Engineer", "Data Scientist"],
    "SW": ["BE", "서버", "FE", "웹", "DevOps", "SRE", "인프라", "Cloud", "Mobile", "iOS", "Android", "Software Engineer"],
    "HW": ["회로설계", "PCB", "기구설계", "로보틱스", "자동화", "PLC", "임베디드", "FAE", "CE", "Hardware Engineer"],
    "반도체": ["SoC", "RTL", "하단 드라이버", "FW", "공정", "Semiconductor"],
    "AI": ["엔지니어", "Serving", "MLOps", "리서쳐", "모델링", "기획", "AI Governance", "DT", "AT", "AX", "Artificial Intelligence", "Machine Learning"],
    "보안": ["정보보안", "개인정보보호", "CPO", "Security"],
    "기타": ["Unclassified"]
}

def get_role_cluster(role):
    # Backward compatibility for direct role matching
    for cluster, roles in ROLE_CLUSTERS.items():
        if role == cluster or role in roles:
            return cluster
    return "기타"

def validate_role(role, fallback="기타"):
    if role in ALLOWED_ROLES:
        return role
    return fallback


# validate_domains removed as it used legacy ALLOWED_DOMAINS and is no longer part of v8.0 spec.
