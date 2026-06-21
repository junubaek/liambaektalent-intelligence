import json
import sqlite3
import sys
from neo4j import GraphDatabase

sys.stdout.reconfigure(encoding='utf-8')

# Part 1. 하현재
print("--- Part 1. 하현재 ---")
# 1.1 Delete existing Neo4j edges for 하현재
with open('secrets.json', encoding='utf-8') as f:
    s = json.load(f)

driver = GraphDatabase.driver(s['NEO4J_URI'], auth=(s['NEO4J_USERNAME'], s['NEO4J_PASSWORD']))
cid_ha = 'ba4abc09-302e-4fd4-ae93-b8af52aed567'
with driver.session() as session:
    session.run('MATCH (c:Candidate {id:$cid})-[r]->() DELETE r', cid=cid_ha)
    print('엣지 삭제 완료')

# 1.2 Fetch raw_text from SQLite
conn = sqlite3.connect('candidates.db')
cur = conn.cursor()
cur.execute('SELECT raw_text FROM candidates WHERE id=?', (cid_ha,))
r = cur.fetchone()
print("\n[하현재 raw_text (앞부분 800자)]")
print(r[0][:800] if r else 'None')
conn.close()

# Part 2. 유정한
print("\n--- Part 2. 유정한 ---")
# 2.1 Set weights for 유정한
cid_yu = '31f22567-1b6f-8152-93ca-ca5ab3080016'
with driver.session() as session:
    weight_map = {
        'MANAGED': 1.8, 'BUILT': 1.7, 'DESIGNED': 1.6,
        'ANALYZED': 1.4, 'GREW': 1.3, 'NEGOTIATED': 1.3
    }
    for rel, w in weight_map.items():
        session.run(
            'MATCH (c:Candidate {id:$cid})-[r:' + rel + ']->() SET r.weight=$w',
            cid=cid_yu, w=w
        )
    # Check updated edges
    res = list(session.run(
        'MATCH (c:Candidate {id:$cid})-[r]->(s:Skill) RETURN s.name as s_name, type(r) as r_type, r.weight as weight ORDER BY r.weight DESC',
        cid=cid_yu
    ))
    for item in res:
        print(f'{item["s_name"]} | {item["r_type"]} | w={item["weight"]}')

driver.close()
