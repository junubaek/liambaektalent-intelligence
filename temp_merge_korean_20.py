import os
import json
import sys
from neo4j import GraphDatabase

sys.stdout.reconfigure(encoding='utf-8')
ROOT_DIR = r"c:\Users\cazam\Downloads\이력서자동분석검색시스템"

SECRETS_FILE = os.path.join(ROOT_DIR, "secrets.json")
with open(SECRETS_FILE, "r", encoding="utf-8") as f:
    secrets = json.load(f)
neo4j_pwd = secrets.get('NEO4J_PASSWORD', 'toss1234')

driver = GraphDatabase.driver('bolt://localhost:7687', auth=('neo4j', neo4j_pwd))

mappings = {
    '회로설계_PCB': 'PCB_Design',
    '컴플라이언스': 'Compliance',
    'FW_컨트롤러': 'Firmware_Development',
    '영업기획': 'Sales_Planning',
    '시장 조사': 'Market_Research',
    '보상설계': 'Compensation_and_Benefits',
    '반도체_Semiconductor': 'Semiconductor',
    '커뮤니케이션': 'Communication',
    '팀워크': 'Teamwork',
    '데이터분석': 'Data_Analysis',
    '프로모션 기획': 'Promotion_Planning',
    '보고서 작성': 'Report_Writing',
    '팀 관리': 'Team_Management',
    '디지털 마케팅': 'Digital_Marketing',
    '기구설계': 'Mechanical_Design',
    '마케팅기획': 'Marketing_Planning',
    '모의해킹': 'Penetration_Testing',
    '문서 작성': 'Documentation',
    '콘텐츠 제작': 'Content_Creation',
    '브랜딩': 'Brand_Management'
}

print("━━━━━━━━━━━━━━━━━━━━\n1. 20개 노드 삭제 및 엣지 이전\n━━━━━━━━━━━━━━━━━━━━")
with driver.session() as session:
    num_edges_moved = 0
    for old_name, new_name in mappings.items():
        session.run("MERGE (s:Skill {name: $new_name})", new_name=new_name)
        
        # Read old edges
        res = session.run("""
        MATCH (c:Candidate)-[r]->(old:Skill {name: $old_name})
        RETURN c.id as cid, type(r) as verb
        """, old_name=old_name)
        
        edges = [record for record in res]
        for e in edges:
            session.run(f"""
            MATCH (c:Candidate {{id: $cid}}), (new:Skill {{name: $new_name}})
            MERGE (c)-[:{e['verb']}]->(new)
            """, cid=e['cid'], new_name=new_name)
            num_edges_moved += 1
            
        # Delete old node constraints
        session.run("MATCH ()-[r]->(old:Skill {name: $old_name}) DELETE r", old_name=old_name)
        session.run("MATCH (old:Skill {name: $old_name}) DELETE old", old_name=old_name)
        
    print(f"Merged 20 nodes to English targets. Total edges moved: {num_edges_moved}")

    print("\n━━━━━━━━━━━━━━━━━━━━\n2. 완료 후 확인\n━━━━━━━━━━━━━━━━━━━━")
    
    # 1. Check if ANY Korean nodes >= 10 candidates remain
    res1 = session.run("""
    MATCH (s:Skill)
    WHERE s.name =~ '.*[가-힣].*'
    WITH s, count{(s)<-[]-(:Candidate)} as cnt
    WHERE cnt >= 10
    RETURN count(s) as remaining
    """)
    for r in res1:
        print(f"10명 이상 연결된 한글 노드 잔여 수: {r['remaining']}건 (0건이어야 정상)")

    # 2. Total Remaining Korean nodes
    res2 = session.run("MATCH (s:Skill) WHERE s.name =~ '.*[가-힣].*' RETURN count(s) as cnt")
    for r in res2:
        print(f"전체 한글 노드 잔여 수: {r['cnt']}개")

driver.close()
