import os
import sys
import json
from neo4j import GraphDatabase

sys.stdout.reconfigure(encoding='utf-8')
ROOT_DIR = r"c:\Users\cazam\Downloads\이력서자동분석검색시스템"

SECRETS_FILE = os.path.join(ROOT_DIR, "secrets.json")

with open(SECRETS_FILE, "r", encoding="utf-8") as f:
    secrets = json.load(f)
neo4j_pwd = secrets.get('NEO4J_PASSWORD', 'toss1234')

driver = GraphDatabase.driver('bolt://localhost:7687', auth=('neo4j', neo4j_pwd))

print("━━━━━━━━━━━━━━━━━━━━\nMERGE 결과 이상치 교차 검증\n━━━━━━━━━━━━━━━━━━━━")

with driver.session() as session:
    res1 = session.run("""
    MATCH (c:Candidate)-[r]->(s:Skill {name: 'Data_Analysis'})
    RETURN count(DISTINCT c) as unique_candidates, count(r) as total_edges
    """)
    for record in res1:
        print(f"Data_Analysis -> Unique Candidates: {record['unique_candidates']}, Total Edges: {record['total_edges']}")

    res2 = session.run("""
    MATCH (c:Candidate)-[r]->(s:Skill {name: 'B2B_Sales'})
    RETURN count(DISTINCT c) as unique_candidates, count(r) as total_edges
    """)
    for record in res2:
        print(f"B2B_Sales     -> Unique Candidates: {record['unique_candidates']}, Total Edges: {record['total_edges']}")

driver.close()
