with open('ontology_graph.py', 'r', encoding='utf-8', errors='surrogateescape') as f:
    content = f.read()

replacements = {
    "'보상설계'": "'Compensation_and_Benefits'",
    "\"보상설계\"": "\"Compensation_and_Benefits\"",
    "'기구설계'": "'Mechanical_Engineering'",
    "\"기구설계\"": "\"Mechanical_Engineering\"",
    "'반도체_Semiconductor'": "'Semiconductor_Engineering'",
    "\"반도체_Semiconductor\"": "\"Semiconductor_Engineering\"",
    "'컴플라이언스'": "'Compliance_Management'",
    "\"컴플라이언스\"": "\"Compliance_Management\"",
    "'해외영업'": "'Global_Sales_and_Marketing'",
    "\"해외영업\"": "\"Global_Sales_and_Marketing\"",
    "'영업지원'": "'Sales_Support'",
    "\"영업지원\"": "\"Sales_Support\"",
    "'상품기획'": "'Product_Planning'",
    "\"상품기획\"": "\"Product_Planning\"",
    "'물류기획'": "'Logistics_Planning'",
    "\"물류기획\"": "\"Logistics_Planning\"",
    "'공정_Yield'": "'Yield_Engineering'",
    "\"공정_Yield\"": "\"Yield_Engineering\"",
    "'유통'": "'Retail_Distribution'",
    "\"유통\"": "\"Retail_Distribution\"",
    "'컴퓨터비전_CV'": "'Computer_Vision'",
    "\"컴퓨터비전_CV\"": "\"Computer_Vision\"",
    "'영업MD'": "'Merchandising'",
    "\"영업MD\"": "\"Merchandising\"",
    "'기업가치평가'": "'Corporate_Valuation'",
    "\"기업가치평가\"": "\"Corporate_Valuation\"",
    "'FW_컨트롤러'": "'Firmware_Engineering'",
    "\"FW_컨트롤러\"": "\"Firmware_Engineering\"",
    "'모의해킹'": "'Penetration_Testing'",
    "\"모의해킹\"": "\"Penetration_Testing\"",
    "'서비스기획'": "'Service_Planning'",
    "\"서비스기획\"": "\"Service_Planning\"",
    "'추천시스템'": "'Recommendation_System'",
    "\"추천시스템\"": "\"Recommendation_System\"",
    "'B2C영업'": "'B2C_Sales'",
    "\"B2C영업\"": "\"B2C_Sales\"",
    "'OKR_KPI설계'": "'Performance_Management'",
    "\"OKR_KPI설계\"": "\"Performance_Management\"",
    "'마케팅기획'": "'Marketing_Strategy'",
    "\"마케팅기획\"": "\"Marketing_Strategy\"",
    "'회로설계_PCB'": "'Circuit_Design'",
    "\"회로설계_PCB\"": "\"Circuit_Design\"",
    "'신사업기획'": "'New_Business_Development'",
    "\"신사업기획\"": "\"New_Business_Development\"",
    "'교육_L&D'": "'Learning_and_Development'",
    "\"교육_L&D\"": "\"Learning_and_Development\"",
}

for old, new in replacements.items():
    content = content.replace(old, new)

with open('ontology_graph.py', 'w', encoding='utf-8', errors='surrogateescape') as f:
    f.write(content)
print('나머지 교체 완료')
