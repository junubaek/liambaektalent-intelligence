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

query = """
MATCH (s:Skill)
WHERE s.name =~ '.*[가-힣].*'
WITH s, count{(s)<-[]-(:Candidate)} as cnt
WHERE cnt >= 10
RETURN s.name as node_name, cnt
ORDER BY cnt DESC
"""

with driver.session() as session:
    res = session.run(query)
    results = [record for record in res]

driver.close()

print(f"총 {len(results)}개\n")
for i, r in enumerate(results, 1):
    print(f"{i}. {r['node_name']} | {r['cnt']}")
