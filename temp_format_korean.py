import os
import json
import sys
import re
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
WITH s.name as node_name, count{(s)<-[]-(:Candidate)} as candidate_count
WHERE candidate_count >= 50
RETURN node_name, candidate_count
ORDER BY candidate_count DESC
"""

def determine_type(name):
    # 알파벳이나 숫자가 포함되면 혼합/병기, 아니면 순한글
    if re.search(r'[A-Za-z]', name):
        return "혼합/병기"
    return "순한글"

with driver.session() as session:
    res = session.run(query)
    print("노드명 | 후보자수 | 유형(순한글/혼합/병기)")
    print("-" * 50)
    for record in res:
        name = record['node_name']
        count = record['candidate_count']
        t = determine_type(name)
        print(f"{name} | {count} | {t}")

driver.close()
