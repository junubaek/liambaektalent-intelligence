import os
import json
from neo4j import GraphDatabase

ROOT_DIR = r"c:\Users\cazam\Downloads\이력서자동분석검색시스템"
SECRETS_FILE = os.path.join(ROOT_DIR, "secrets.json")
ARTIFACT_PATH = r"C:\Users\cazam\.gemini\antigravity\brain\40516708-d2c8-4e50-a5f8-ff10183de737\artifacts\korean_nodes_report.md"

os.makedirs(os.path.dirname(ARTIFACT_PATH), exist_ok=True)

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

with driver.session() as session:
    res = session.run(query)
    results = [record for record in res]

driver.close()

with open(ARTIFACT_PATH, "w", encoding="utf-8") as f:
    f.write(f"# Neo4j 한글 노드 (Skill) 전수 조사 결과\n\n")
    f.write(f"총 발견된 한글 포함 스킬 노드 개수: **{len(results)}개**\n\n")
    f.write("> 영어 표준화(Canonical Map) 원칙이 무시되고 그대로 Ingest된 노드들의 전체 목록입니다.\n\n")
    f.write("| 스킬 노드명 (Skill Name) | 연결된 후보자 수 (Candidate Count) |\n")
    f.write("|:---|:---|\n")
    for r in results:
        f.write(f"| {r['node_name']} | {r['candidate_count']} |\n")

print(f"Wrote to artifact: {ARTIFACT_PATH}")
print(f"Total: {len(results)}")
print("Top 10:")
for r in results[:10]:
    print(r['node_name'], "->", r['candidate_count'])
