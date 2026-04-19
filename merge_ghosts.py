from neo4j import GraphDatabase
from ontology_graph import CANONICAL_MAP

# 1. Gather true valid nodes so we don't accidentally merge to a new ghost
valid_nodes = set(CANONICAL_MAP.values())

# 2. Heuristic mapper for the 38 ghosts
mapping = {
    "Android": "Android_Development",
    "Architecture Design": "Backend_Architecture",
    "Blockchain": "Blockchain_Ecosystem",
    "Embedded Systems": "3D_Simulation_and_Viewer_Development", # Or omit if unsure
    "Firmware": "Firmware", 
    "Hadoop": "Big_Data_Processing",
    "Litigation": "Litigation",
    "MySQL": "DBA",
    "Risk Management": "Credit_Risk_Management",
    "Security": "보안_Security",
    "software testing": "QA_and_Testing", # Example valid node
    "개인정보보호": "Data_Privacy_Protection",
    "경영자문": "Corporate_Strategic_Planning",
    "광고기획": "Digital_Campaign_Planning",
    "광고디자인": "Brand_and_Visual_Design",
    "국제조세": "Corporate_Accounting",
    "그래픽디자인": "Brand_and_Visual_Design",
    "기업분석": "Corporate_Strategic_Planning",
    "미디어": "Corporate_Public_Relations",
    "보안정책/감사": "Data_Privacy_and_Compliance",
    "브랜드디자인": "Brand_Design",
    "브랜딩": "Brand_Management",
    "빅데이터": "Big_Data_Processing",
    "사물인터넷(IoT)": "Hardware_Embedded",
    "세무자문": "Corporate_Accounting",
    "세무조사": "Corporate_Accounting",
    "시각디자인": "Brand_and_Visual_Design",
    "언론홍보": "Corporate_Public_Relations",
    "영업관리": "B2B영업",
    "이전가격": "Corporate_Accounting",
    "임베디드": "Hardware_Embedded",
    "정보보호": "Data_Privacy_Protection",
    "컨텐츠마케팅": "Content_Marketing",
    "투자전략": "Corporate_Strategic_Planning",
    "퍼포포먼스마케팅": "Performance_Marketing",
    "프라이버시/정보보호": "Data_Privacy_Protection",
    "회계감사": "Financial_Accounting"
}

# Fix missing node mappings cleanly using CANONICAL_MAP if possible
for key in list(mapping.keys()):
    if key in CANONICAL_MAP:
        mapping[key] = CANONICAL_MAP[key]
    elif mapping[key] not in valid_nodes:
        # Try to find a fallback
        mapping[key] = "Strategic_Planning" # Default fallback for any unmapped

driver = GraphDatabase.driver('neo4j://127.0.0.1:7687', auth=('neo4j', 'toss1234'))

with driver.session() as session:
    # Delete 'None' skill
    session.run("MATCH (n:Skill {name: 'None'}) DETACH DELETE n")

    for old, new in mapping.items():
        if old == new: continue
        
        # Merge edges
        res = session.run("""
            MATCH (c:Candidate)-[r]->(old:Skill {name: $old})
            RETURN c.id AS cid, type(r) AS rtype, properties(r) AS props
        """, old=old)
        
        count = 0
        for row in res:
            cid = row["cid"]
            rtype = row["rtype"]
            props = row["props"]
            session.run(f"""
                MATCH (c:Candidate {{id: $cid}})
                MERGE (new:Skill {{name: $new}})
                MERGE (c)-[r:{rtype}]->(new)
                SET r += $props
            """, cid=cid, new=new, props=props)
            count += 1
            
        # Delete old node
        session.run("MATCH (old:Skill {name: $old}) DETACH DELETE old", old=old)
        print(f"Merged {old} -> {new} ({count} edges)")
