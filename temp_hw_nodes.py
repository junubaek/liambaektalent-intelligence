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

query = """
MATCH (s:Skill)
WHERE s.name =~ '.*[가-힣].*'
WITH s, count{(s)<-[]-(:Candidate)} as cnt
WHERE cnt >= 1
AND (
  s.name =~ '.*RTL.*'
  OR s.name =~ '.*DFT.*'
  OR s.name =~ '.*SoC.*'
  OR s.name =~ '.*반도체.*'
  OR s.name =~ '.*설계.*'
  OR s.name =~ '.*회로.*'
  OR s.name =~ '.*임베디드.*'
  OR s.name =~ '.*펌웨어.*'
  OR s.name =~ '.*FPGA.*'
  OR s.name =~ '.*칩.*'
  OR s.name =~ '.*공정.*'
  OR s.name =~ '.*패키징.*'
  OR s.name =~ '.*웨이퍼.*'
  OR s.name =~ '.*검증.*'
  OR s.name =~ '.*테스트.*'
)
RETURN s.name as name, cnt
ORDER BY cnt DESC;
"""

with driver.session() as session:
    result = session.run(query)
    records = [record for record in result]
    
print(f"총 {len(records)}개의 노드가 발견되었습니다.\n")
print("노드명 | 후보자수")
print("-" * 30)
for i, r in enumerate(records, 1):
    print(f"{i}. {r['name']} | {r['cnt']}")

driver.close()
