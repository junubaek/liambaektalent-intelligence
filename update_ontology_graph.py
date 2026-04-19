import re
with open('ontology_graph.py', 'r', encoding='utf-8') as f: text = f.read()

# 1. 인사기획 -> HR_Strategic_Planning
text = re.sub(r'\"인사기획\":\s*\".*?\"', '\"인사기획\": \"HR_Strategic_Planning\"', text)
text = re.sub(r'\"인사 기획\":\s*\".*?\"', '\"인사 기획\": \"HR_Strategic_Planning\"', text)

# 2. 재무기획 -> Financial_Planning_and_Analysis
text = re.sub(r'\"재무기획\":\s*\".*?\"', '\"재무기획\": \"Financial_Planning_and_Analysis\"', text)
text = re.sub(r'\"재무 기획\":\s*\".*?\"', '\"재무 기획\": \"Financial_Planning_and_Analysis\"', text)
text = re.sub(r'\"FP_and_A\":\s*\".*?\"', '\"FP_and_A\": \"Financial_Planning_and_Analysis\"', text)
text = re.sub(r'\"FP&A\":\s*\".*?\"', '\"FP&A\": \"Financial_Planning_and_Analysis\"', text)

# 3. 브랜드 -> Brand_Management
text = re.sub(r'\"브랜드\":\s*\".*?\"', '\"브랜드\": \"Brand_Management\"', text)
text = re.sub(r'\"브랜드마케팅\":\s*\".*?\"', '\"브랜드마케팅\": \"Brand_Management\"', text)
text = re.sub(r'\"브랜딩\":\s*\".*?\"', '\"브랜딩\": \"Brand_Management\"', text)
text = re.sub(r'\"brand marketing\":\s*\".*?\"', '\"brand marketing\": \"Brand_Management\"', text)

# 4. 컴플라이언스 -> Compliance
text = re.sub(r'\"컴플라이언스\":\s*\".*?\"', '\"컴플라이언스\": \"Compliance\"', text)
text = re.sub(r'\"규제대응\":\s*\".*?\"', '\"규제대응\": \"Compliance\"', text)
text = re.sub(r'\"준법\":\s*\".*?\"', '\"준법\": \"Compliance\"', text)

# 5. 물류 -> SCM
text = re.sub(r'\"물류\":\s*\".*?\"', '\"물류\": \"SCM\"', text)
text = re.sub(r'\"로지스틱스\":\s*\".*?\"', '\"로지스틱스\": \"SCM\"', text)
text = re.sub(r'\"Logistics\":\s*\".*?\"', '\"Logistics\": \"SCM\"', text)
text = re.sub(r'\"물류_Logistics\":\s*\".*?\"', '\"물류_Logistics\": \"SCM\"', text)

with open('ontology_graph.py', 'w', encoding='utf-8') as f: f.write(text)
print('Done!')
