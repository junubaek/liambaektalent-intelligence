import os
import sys
import json
from neo4j import GraphDatabase

sys.stdout.reconfigure(encoding='utf-8')

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(ROOT_DIR)

# Load constraints & mapping
try:
    from ontology_graph import CANONICAL_MAP
except ImportError:
    CANONICAL_MAP = {}

print("━━━━━━━━━━━━━━━━━━━━\n2. Canonical Map에서 총무 관련 매핑 확인\n━━━━━━━━━━━━━━━━━━━━")
search_keywords = ['총무', 'general affairs', 'ga', 'general_affairs']
found_mappings = {}

for k, v in CANONICAL_MAP.items():
    lower_k = k.lower()
    lower_v = v.lower()
    
    # if key or value matches our search keywords
    matched = False
    for sk in search_keywords:
        if sk in lower_k or sk in lower_v:
            matched = True
            break
            
    if matched:
        found_mappings[k] = v

if found_mappings:
    for k, v in found_mappings.items():
        print(f"'{k}' -> '{v}'")
else:
    print("관련 매핑 항목 없음")


# Load Secrets
SECRETS_FILE = os.path.join(ROOT_DIR, "secrets.json")
with open(SECRETS_FILE, "r", encoding="utf-8") as f:
    secrets = json.load(f)
neo4j_pwd = secrets.get('NEO4J_PASSWORD', 'toss1234')

# Connect Neo4j
driver = GraphDatabase.driver('bolt://localhost:7687', auth=('neo4j', neo4j_pwd))

print("\n━━━━━━━━━━━━━━━━━━━━\n1. Neo4j General_Affairs 노드 엣지 현황\n━━━━━━━━━━━━━━━━━━━━")

query1 = """
MATCH (c:Candidate)-[r]->(s:Skill)
WHERE s.name IN [
  'General_Affairs',
  '총무',
  'General Affairs',
  'GA',
  '총무관리',
  '인사총무'
]
RETURN s.name as node_name,
       count(DISTINCT c) as candidate_count,
       count(r) as edge_count
ORDER BY candidate_count DESC
"""
with driver.session() as session:
    res1 = session.run(query1)
    
    print(f"{'node_name':<20} | {'candidate_count':<15} | {'edge_count'}")
    print("-" * 50)
    for record in res1:
        print(f"{record['node_name']:<20} | {record['candidate_count']:<15} | {record['edge_count']}")


print("\n━━━━━━━━━━━━━━━━━━━━\n3. 총무 경력자 실제 Neo4j 연결 상태 확인\n━━━━━━━━━━━━━━━━━━━━")

query3 = """
MATCH (c:Candidate)-[r]->(s:Skill)
WHERE c.name_kr IN ['정해법', '박상국', '이상헌']
RETURN c.name_kr,
       s.name as skill,
       type(r) as verb,
       count(r) as cnt
ORDER BY c.name_kr, cnt DESC
"""

with driver.session() as session:
    res3 = session.run(query3)
    # group by candidate
    data = {}
    for record in res3:
        name = record['c.name_kr']
        skill = record['skill']
        verb = record['verb']
        cnt = record['cnt']
        
        if name not in data:
            data[name] = []
        data[name].append(f"{skill} ({verb}: {cnt})")
        
    for name, skills in data.items():
        print(f"\n[{name}]")
        for s in skills:
            print(f"  - {s}")

driver.close()
