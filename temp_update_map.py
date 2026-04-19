import sys
import os
import re

ROOT_DIR = r"c:\Users\cazam\Downloads\이력서자동분석검색시스템"
file_path = os.path.join(ROOT_DIR, "ontology_graph.py")

with open(file_path, "r", encoding="utf-8") as f:
    text = f.read()

maps = {
    "시장 분석": "Market_Analysis",
    "전략 기획": "Corporate_Strategic_Planning",
    "재고 관리": "Inventory_Management",
    "콘텐츠 기획": "Content_Strategy",
    "품질 관리": "Quality_Management",
    "SNS마케팅": "Social_Media_Marketing",
    "고객 관리": "Customer_Relationship_Management",
    "서비스 기획": "Service_Planning",
    "마케팅": "Marketing_Planning",
    "문제 해결": "Problem_Solving",
    "커뮤니케이션 능력": "Communication",
    "퍼포먼스 마케팅": "Performance_Marketing",
    "퍼포먼스마케팅": "Performance_Marketing",
    "C언어": "C_Programming",
    "ERP 시스템": "ERP",
    "전략 수립": "Corporate_Strategic_Planning",
    "제안서 작성": "Proposal_Writing",
    "트렌드 분석": "Market_Research",
    "더존 ERP": "ERP",
    "매출 관리": "Sales_Management",
    "매출 분석": "Sales_Analytics",
    "소통 능력": "Communication",
    "영어": "English_Communication",
    "데이터 시각화": "Data_Visualization",
    "리스크 관리": "Risk_Management",
    "상품 기획": "Product_Planning",
    "성과 분석": "Performance_Analytics",
    "소프트웨어 엔지니어링": "Software_Engineering",
    "이벤트 기획": "Event_Management",
    "협상": "Negotiation",
    "회계": "Financial_Accounting"
}

# Find CANONICAL_MAP
match = re.search(r'(CANONICAL_MAP\s*(?::\s*dict\[str,\s*str\])?\s*=\s*\{)', text)
if match:
    insert_pos = match.end()
    
    # Check what already exists to avoid duplicates
    existing_map = {}
    from ontology_graph import CANONICAL_MAP
    existing_map = CANONICAL_MAP
    
    insertions = []
    for k, v in maps.items():
        if k not in existing_map:
            insertions.append(f'    "{k}": "{v}",\n')
            
    if insertions:
        new_text = text[:insert_pos] + '\n' + ''.join(insertions) + text[insert_pos:]
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(new_text)        
        print(f"Added {len(insertions)} mappings to CANONICAL_MAP.")
    else:
        print("All mappings already exist in CANONICAL_MAP.")
else:
    print("Could not find CANONICAL_MAP definition.")
