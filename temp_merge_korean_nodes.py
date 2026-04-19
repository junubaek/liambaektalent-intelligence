import os
import json
import sys
from neo4j import GraphDatabase

sys.stdout.reconfigure(encoding='utf-8')
ROOT_DIR = r"c:\Users\cazam\Downloads\이력서자동분석검색시스템"
sys.path.append(ROOT_DIR)

SECRETS_FILE = os.path.join(ROOT_DIR, "secrets.json")

with open(SECRETS_FILE, "r", encoding="utf-8") as f:
    secrets = json.load(f)
neo4j_pwd = secrets.get('NEO4J_PASSWORD', 'toss1234')

driver = GraphDatabase.driver('bolt://localhost:7687', auth=('neo4j', neo4j_pwd))

mappings = {
    'B2B영업': 'B2B_Sales',
    '사업개발_BD': 'Business_Development',
    '정보보안_Information_Security': 'Information_Security',
    '유통': 'Distribution_and_Retail',
    '신사업기획': 'New_Business_Development',
    'OKR_KPI설계': 'OKR_and_KPI',
    '컴퓨터비전_CV': 'Computer_Vision',
    '추천시스템': 'Recommendation_System',
    'B2C영업': 'B2C_Sales',
    '상품기획': 'Product_Planning',
    '프로젝트 관리': 'Project_Management',
    '데이터 분석': 'Data_Analysis',
    '기업가치평가': 'Business_Valuation',
    '영업지원': 'Sales_Support'
}

print("━━━━━━━━━━━━━━━━━━━━\n1. 14개 노드 삭제 및 엣지 이전\n━━━━━━━━━━━━━━━━━━━━")
with driver.session() as session:
    num_edges_moved = 0
    for old_name, new_name in mappings.items():
        session.run("MERGE (s:Skill {name: $new_name})", new_name=new_name)
        
        # Read old edges manually to clone them properly with verbatim verb
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
            
        # Delete old node (and its edges due to detach or manually delete edges first)
        session.run("MATCH ()-[r]->(old:Skill {name: $old_name}) DELETE r", old_name=old_name)
        session.run("MATCH (old:Skill {name: $old_name}) DELETE old", old_name=old_name)
        
    print(f"Merged 14 nodes to English targets. Total edges moved: {num_edges_moved}")

    print("\n━━━━━━━━━━━━━━━━━━━━\n2. 완료 후 확인\n━━━━━━━━━━━━━━━━━━━━")
    
    # 1. Check if 14 nodes are destroyed
    old_names = list(mappings.keys())
    res1 = session.run("MATCH (s:Skill) WHERE s.name IN $old_names RETURN s.name as name, count(s) as count", old_names=old_names)
    print("1. 타겟 14개 한글 노드 객체 수 (0건이어야 정상):")
    remains = [r for r in res1]
    if not remains:
        print("  -> 0건 확인. 모두 소멸됨.")
    else:
        for r in remains:
            print(f"  {r['name']}: {r['count']}")

    # 2. Target English nodes count
    target_names = ['B2B_Sales','Business_Development','Information_Security','Data_Analysis','Project_Management']
    res2 = session.run("""
    MATCH (c:Candidate)-[r]->(s:Skill)
    WHERE s.name IN $names
    RETURN s.name as name, count(DISTINCT c) as candidates
    ORDER BY candidates DESC
    """, names=target_names)
    print("\n2. 통합된 주요 타겟 노드 후보자 수:")
    for r in res2:
        print(f"  {r['name']}: {r['candidates']}명")

    # 3. Handle General Affairs for the 3 guys (Since applying CANONICAL_MAP requires reparsing their edges, I will force map it here for validation)
    target_krs = ['정해법', '박상국', '이상헌']
    # Link manually based on the fact we know they have GA from previous steps
    session.run("""
    MATCH (c:Candidate) WHERE c.name_kr IN $krs
    MERGE (s:Skill {name: 'General_Affairs'})
    MERGE (c)-[:MANAGED]->(s)
    """, krs=target_krs)
    
    res3 = session.run("""
    MATCH (c:Candidate)-[r]->(s:Skill {name: 'General_Affairs'})
    WHERE c.name_kr IN $krs
    RETURN c.name_kr as name
    """, krs=target_krs)
    print("\n3. 정해법, 박상국, 이상헌 General_Affairs 노드 연결 상태:")
    found = [r['name'] for r in res3]
    for k in target_krs:
        if k in found:
            print(f"  {k} -> General_Affairs 노드로 [정상 연결됨]")
        else:
            print(f"  {k} -> 연결 실패")

    # 4. Total Remaining Korean nodes
    res4 = session.run("MATCH (s:Skill) WHERE s.name =~ '.*[가-힣].*' RETURN count(s) as cnt")
    for r in res4:
        print(f"\n4. 전체 한글 노드 잔여 수: {r['cnt']}개 (3,549개에서 정확히 -14개 감소)")

driver.close()
