with open('ontology_graph.py', 'r', encoding='utf-8') as f:
    text = f.read()

new_mappings = '''    # --- Phase 2 Aliases Additions ---
    '단기자금': 'Treasury_Management',
    '어음관리': 'Treasury_Management',
    'Cash Pooling': 'Treasury_Management',
    'FX Dealing': 'Treasury_Management',
    
    'CB/BW 발행': 'Corporate_Funding',
    'Project Financing': 'Corporate_Funding',
    'PF': 'Corporate_Funding',
    
    'K-IFRS': 'Financial_Accounting',
    'US-GAAP': 'Financial_Accounting',
    '연결결산': 'Financial_Accounting',
    '별도결산': 'Financial_Accounting',
    '지분법': 'Financial_Accounting',
    
    'NDR': 'Investor_Relations',
    '기관투자자 미팅': 'Investor_Relations',
    'Earnings Release': 'Investor_Relations',
    
    'ROAS': 'Performance_Marketing',
    'CPA/CAC': 'Performance_Marketing',
    'Meta Ads': 'Performance_Marketing',
    'Google Ads': 'Performance_Marketing',
    '앱스플라이어': 'Performance_Marketing',
    'MMP': 'Performance_Marketing',
    
    'IMC 캠페인': 'Brand_Management',
    'Brand Identity': 'Brand_Management',
    '브랜드 포지셔닝': 'Brand_Management',
    
    '핵심인재 관리': 'HR_Strategic_Planning',
    '인건비 예산': 'HR_Strategic_Planning',
    '조직 설계': 'HR_Strategic_Planning',

    # --- Phase 2 New Nodes Additions ---
    'Management_Accounting': 'Management_Accounting',
    '관리회계': 'Management_Accounting',
    '원가회계': 'Management_Accounting',
    'Costing': 'Management_Accounting',
    '손익 분석': 'Management_Accounting',
    '원가 절감': 'Management_Accounting',
    'BEP 분석': 'Management_Accounting',
    '표준원가': 'Management_Accounting',

    'CRM_Marketing': 'CRM_Marketing',
    'CRM': 'CRM_Marketing',
    '고객관계관리': 'CRM_Marketing',
    '리텐션 마케팅': 'CRM_Marketing',
    'VIP 마케팅': 'CRM_Marketing',
    'Braze': 'CRM_Marketing',
    '마케팅 자동화': 'CRM_Marketing',

    'Content_Marketing': 'Content_Marketing',
    '콘텐츠 마케팅': 'Content_Marketing',
    'SNS 채널 운영': 'Content_Marketing',
    '인플루언서 협업': 'Content_Marketing',
    '유튜브 기획': 'Content_Marketing',

    'Talent_Acquisition': 'Talent_Acquisition',
    '채용': 'Talent_Acquisition',
    '리크루팅': 'Talent_Acquisition',
    'TA': 'Talent_Acquisition',
    '다이렉트 소싱': 'Talent_Acquisition',
    '채용 브랜딩': 'Talent_Acquisition',
    '온보딩': 'Talent_Acquisition',

    'Compensation_and_Benefits': 'Compensation_and_Benefits',
    'C&B': 'Compensation_and_Benefits',
    'Comp&Ben': 'Compensation_and_Benefits',
    'Payroll': 'Compensation_and_Benefits',
    '4대보험': 'Compensation_and_Benefits',
    '연말정산': 'Compensation_and_Benefits',
    '인센티브 제도': 'Compensation_and_Benefits',

    'Employee_Relations': 'Employee_Relations',
    '노무': 'Employee_Relations',
    'ER': 'Employee_Relations',
    '노사 관계': 'Employee_Relations',
    '근로기준법': 'Employee_Relations',
    '취업규칙 개정': 'Employee_Relations',
    '노동청 대응': 'Employee_Relations',
'''

text = text.replace('CANONICAL_MAP: dict[str, str] = {', 'CANONICAL_MAP: dict[str, str] = {\n' + new_mappings)

with open('ontology_graph.py', 'w', encoding='utf-8') as f:
    f.write(text)
print('Done updating ontology_graph!')
