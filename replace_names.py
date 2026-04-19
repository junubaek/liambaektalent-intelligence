import re

# Dictionary matching the exact strings to replace
MIGRATION_MAP = {
    '"기술영업_PreSales"': '"Technical_Sales"',
    "'기술영업_PreSales'": "'Technical_Sales'",
    '"물류_Logistics"': '"Logistics_and_Supply_Chain"',
    "'물류_Logistics'": "'Logistics_and_Supply_Chain'",
    '"조직개발_OD"': '"Organizational_Development"',
    "'조직개발_OD'": "'Organizational_Development'",
    '"투자_M&A"': '"Mergers_and_Acquisitions"',
    "'투자_M&A'": "'Mergers_and_Acquisitions'",
    '"언론홍보_PR"': '"Public_Relations"',
    "'언론홍보_PR'": "'Public_Relations'",
    '"채용_리크루팅"': '"Talent_Acquisition"',
    "'채용_리크루팅'": "'Talent_Acquisition'",
    '"그로스마케팅"': '"Growth_Marketing"',
    "'그로스마케팅'": "'Growth_Marketing'",
    '"퍼포먼스마케팅"': '"Performance_Marketing"',
    "'퍼포먼스마케팅'": "'Performance_Marketing'",
    '"브랜드마케팅"': '"Brand_Management"',
    "'브랜드마케팅'": "'Brand_Management'",
    '"콘텐츠마케팅"': '"Content_Marketing"',
    "'콘텐츠마케팅'": "'Content_Marketing'",
    '"보안_Security"': '"Information_Security"',
    "'보안_Security'": "'Information_Security'",
    '"정보보안"': '"Information_Security"',
    "'정보보안'": "'Information_Security'",
    '"법무_Legal"': '"Legal_Practice"',
    "'법무_Legal'": "'Legal_Practice'",
    '"세무_Tax"': '"Tax_Accounting"',
    "'세무_Tax'": "'Tax_Accounting'",
    '"재무회계"': '"Financial_Accounting"',
    "'재무회계'": "'Financial_Accounting'",
    '"특허_IP"': '"Patent_Management"',
    "'특허_IP'": "'Patent_Management'",
    '"사업개발_BD"': '"Business_Development"',
    "'사업개발_BD'": "'Business_Development'"
}

with open('ontology_graph.py', 'r', encoding='utf-8') as f:
    text = f.read()
    
# Replace exact occurrences
for old, new in MIGRATION_MAP.items():
    text = text.replace(old, new)
    
with open('ontology_graph.py', 'w', encoding='utf-8') as f:
    f.write(text)
    
print("Replaced all occurrences in ontology_graph.py")
