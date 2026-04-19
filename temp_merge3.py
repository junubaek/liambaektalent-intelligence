import sys
import os

ROOT_DIR = r"c:\Users\cazam\Downloads\이력서자동분석검색시스템"
sys.path.append(ROOT_DIR)

from neo4j import GraphDatabase

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

driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "toss1234"))

def merge_skills(target_map):
    with driver.session() as session:
        for old_name, new_name in target_map.items():
            print(f"Merging '{old_name}' -> '{new_name}'")
            
            # Step 1: Create new node if not exists
            session.run("MERGE (new:Skill {name: $new_name})", new_name=new_name)
            
            # Step 2: Move edges explicitly
            for rel_type in ["USED", "LED", "MANAGED", "KNOWN", "EXPERIENCED", "DEVELOPED", "MAINTAINED"]:
                q = f"""
                MATCH (old:Skill {{name: $old_name}})
                MATCH (c:Candidate)-[r:{rel_type}]->(old)
                MERGE (new:Skill {{name: $new_name}})
                MERGE (c)-[r2:{rel_type}]->(new)
                ON CREATE SET r2 = properties(r)
                """
                session.run(q, old_name=old_name, new_name=new_name)
            
            # Step 3: Delete old node & its edges
            del_q = """
            MATCH (old:Skill {name: $old_name})
            DETACH DELETE old
            """
            session.run(del_q, old_name=old_name)

merge_skills(maps)

with driver.session() as session:
    res = session.run("MATCH (s:Skill) WHERE s.name =~ '.*[가-힣].*' WITH s, count{(s)<-[]-(:Candidate)} as cnt WHERE cnt >= 5 RETURN count(s) as c")
    print(f"Remaining Korean Nodes >=5 candidates: {res.single()['c']}")

driver.close()
