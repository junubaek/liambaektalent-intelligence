import json
import os
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

print("━━━━━━━━━━━━━━━━━━━━\n실제 고스트 정의별 숫자 비교\n━━━━━━━━━━━━━━━━━━━━")

with driver.session() as session:
    res_a = session.run("MATCH (s:Skill) WHERE NOT (s)--() RETURN count(s) as c")
    print(f"A. 완전 고립 (엣지 0개): {res_a.single()['c']}개")
    
    res_b = session.run("MATCH (s:Skill) WHERE NOT (:Candidate)-[]->(s) RETURN count(s) as c")
    print(f"B. Candidate와 미연결 (후보자 엣지 없음): {res_b.single()['c']}개")
    
# C 로직 재현
try:
    from ontology_graph import CANONICAL_MAP
    valid_nodes = set(CANONICAL_MAP.values())
except Exception as e:
    valid_nodes = set()

with driver.session() as session:
    result = session.run("MATCH (s:Skill) RETURN s.name AS skill_name")
    neo4j_nodes = set([record["skill_name"] for record in result])
    
ghost_nodes = neo4j_nodes - valid_nodes
ghost_nodes = {n for n in ghost_nodes if not '_' in n and not n.isupper()}

print(f"C. CANONICAL_MAP 미등재 (현재 감사 로직): {len(ghost_nodes)}개")

driver.close()
