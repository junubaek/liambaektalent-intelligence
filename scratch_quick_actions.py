import sqlite3
import json
import sys
from neo4j import GraphDatabase

sys.stdout.reconfigure(encoding='utf-8')

# 1. Update 김진영 sector in SQLite
conn = sqlite3.connect('candidates.db')
conn.execute("UPDATE candidates SET sector='Eng_AI' WHERE id='32022567-1b6f-819f-b62e-fa5ecb02e3de'")
conn.commit()
conn.close()
print("1. 김진영 sector 업데이트 완료 (Healthcare -> Eng_AI)")

# 2. Query Neo4j edges for 유정한, 하현재
with open('secrets.json', encoding='utf-8') as f:
    s = json.load(f)

driver = GraphDatabase.driver(s['NEO4J_URI'], auth=(s['NEO4J_USERNAME'], s['NEO4J_PASSWORD']))
with driver.session() as session:
    for cid, name in [
        ('31f22567-1b6f-8152-93ca-ca5ab3080016', '유정한'),
        ('ba4abc09-302e-4fd4-ae93-b8af52aed567', '하현재'),
    ]:
        res = list(session.run(
            'MATCH (c:Candidate {id:$cid})-[r]->(s:Skill) RETURN s.name as name, type(r) as rel, r.weight as w ORDER BY r.weight DESC',
            cid=cid
        ))
        print(f'\n[{name}] {len(res)}개 엣지')
        for r in res[:8]:
            print(f'  {r["name"]} ({r["rel"]}, w={r["w"]})')
driver.close()
