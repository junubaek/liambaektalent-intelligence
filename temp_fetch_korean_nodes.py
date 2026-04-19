import os
import json
import sys
from neo4j import GraphDatabase

sys.stdout.reconfigure(encoding='utf-8')
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
SECRETS_FILE = os.path.join(ROOT_DIR, "secrets.json")

with open(SECRETS_FILE, "r", encoding="utf-8") as f:
    secrets = json.load(f)
neo4j_pwd = secrets.get('NEO4J_PASSWORD', 'toss1234')

driver = GraphDatabase.driver('bolt://localhost:7687', auth=('neo4j', neo4j_pwd))

query = """
MATCH (s:Skill)
WHERE s.name =~ '.*[가-힣].*'
RETURN s.name as node_name,
       count{(s)<-[]-(:Candidate)} as candidate_count
ORDER BY candidate_count DESC
"""

print("━━━━━━━━━━━━━━━━━━━━\n현재 Neo4j 한글 스킬 노드 전수 조사 결과\n━━━━━━━━━━━━━━━━━━━━")

with driver.session() as session:
    res = session.run(query)
    results = [record for record in res]
    
    print(f"Total Korean nodes found: {len(results)}\n")
    print(f"{'node_name':<35} | {'candidate_count'}")
    print("-" * 55)
    for record in results:
        print(f"{record['node_name']:<35} | {record['candidate_count']}")

driver.close()
