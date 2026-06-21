import json
import sys
import sqlite3
from neo4j import GraphDatabase

sys.stdout.reconfigure(encoding='utf-8')

# Part 1. Rebuild Neo4j edges for 하현재
print("--- Part 1. 하현재 Neo4j 엣지 재구성 ---")
with open('secrets.json', encoding='utf-8') as f:
    s = json.load(f)

driver = GraphDatabase.driver(s['NEO4J_URI'], auth=(s['NEO4J_USERNAME'], s['NEO4J_PASSWORD']))
cid = 'ba4abc09-302e-4fd4-ae93-b8af52aed567'

skills = [
    ('SoC', 'MANAGED', 1.8),
    ('Chiplet_Architecture', 'MANAGED', 1.8),
    ('ASIC', 'BUILT', 1.7),
    ('ARM_Architecture', 'BUILT', 1.7),
    ('Network_on_Chip', 'DESIGNED', 1.6),
    ('Semiconductor_Engineering', 'DESIGNED', 1.6),
    ('High_Performance_Computing', 'ANALYZED', 1.4),
    ('Embedded_AI', 'ANALYZED', 1.4),
]

with driver.session() as session:
    # Clear edges first (to ensure only these edges exist)
    session.run('MATCH (c:Candidate {id:$cid})-[r]->() DELETE r', cid=cid)
    
    for skill, rel, w in skills:
        session.run(f'''
            MATCH (c:Candidate {{id: $cid}})
            MERGE (s:Skill {{name: $skill}})
            MERGE (c)-[r:{rel}]->(s)
            SET r.weight = $w
        ''', cid=cid, skill=skill, w=w)
    
    # Verify
    res = list(session.run(
        'MATCH (c:Candidate {id:$cid})-[r]->(s:Skill) RETURN s.name as s_name, type(r) as r_type, r.weight as weight ORDER BY r.weight DESC',
        cid=cid
    ))
    print(f'하현재 엣지 {len(res)}개:')
    for r in res:
        print(f'  {r["s_name"]} | {r["r_type"]} | w={r["weight"]}')
driver.close()

# Part 2. Rank checks
print("\n--- Part 2. 랭크 재확인 ---")
from jd_compiler import api_search_v9

tests = [
    ('on-device AI inference embedded AI semiconductor', 'SENIOR', 'ba4abc09-302e-4fd4-ae93-b8af52aed567', '하현재'),
    ('SCM logistics operations cost management', 'MIDDLE', '31f22567-1b6f-8152-93ca-ca5ab3080016', '유정한'),
    ('healthcare AI computer vision deep learning medical imaging', 'MIDDLE', '32022567-1b6f-819f-b62e-fa5ecb02e3de', '김진영'),
    ('IPO IR strategic planning fundraising finance', 'SENIOR', '1c3e3279-b0c5-4661-9dcf-7fa929dd47bb', '김진호'),
]

for query, seniority, target_id, name in tests:
    r = api_search_v9(query, seniority=seniority)
    matched = r.get('matched', [])
    rank = next((i+1 for i,c in enumerate(matched) if c.get('id')==target_id), None)
    top1 = matched[0] if matched else {}
    print(f'[{name}] rank={rank} | 1위={top1.get("name_kr","?")}')
