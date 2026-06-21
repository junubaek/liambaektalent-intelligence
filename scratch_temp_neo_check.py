import json
import sys
import sqlite3
from neo4j import GraphDatabase

sys.stdout.reconfigure(encoding='utf-8')

with open('secrets.json', 'r', encoding='utf-8') as f:
    secrets = json.load(f)

uri = secrets['NEO4J_URI']
username = secrets['NEO4J_USERNAME']
password = secrets['NEO4J_PASSWORD']

driver = GraphDatabase.driver(uri, auth=(username, password))

targets = [
    ('1aaad2d3-348d-48f7-8501-38d7c1f7df03', '한경환'),
    ('fbc27466-7587-45e6-b459-c2920b5d71fe', '김태경'),
    ('e88ea471-e1eb-4c40-b5e1-7648e340fac4', '김일곤'),
    ('31f22567-1b6f-81fd-ae6f-f34e3f501ca7', '이형덕'),
    ('ff33752e-5e9c-4b2d-9698-f4022f2a8a57', '신기욱'),
    ('7fd23c15-b296-4bd2-a59c-eb09db05d0ef', '박민규'),
    ('31f22567-1b6f-8152-93ca-ca5ab3080016', '유정한'),
    ('4b4c3372-401b-4897-a9b3-d36a3ba3de37', '김형수'),
    ('32e22567-1b6f-8181-9992-d986271e941f', '오수영'),
    ('2808b157-0e3a-4454-971e-ad10b8136df6', '강희성'),
    ('07f2a68d-49b7-41e9-9c8f-e54a0e5a5482', '박상수'),
    ('fafa2636-cf0b-42c1-8c18-598d089e9c61', '배정현'),
    ('fcf70649-6ba3-4c6e-935b-a67eeff81094', '이광욱'),
    ('ba4abc09-302e-4fd4-ae93-b8af52aed567', '하현재'),
    ('9a65646e-062e-4460-b402-bfa280d0d7b2', '강동욱'),
    ('32022567-1b6f-819f-b62e-fa5ecb02e3de', '김진영'),
    ('1c3e3279-b0c5-4661-9dcf-7fa929dd47bb', '김진호'),
    ('3d322d13-0699-4453-b70e-5a4c2aac38f9', '박천혁'),
]

# 1. Query Neo4j for mapped skills
print("=== Neo4j Skill Mappings ===")
query = """
MATCH (c:Candidate {id: $cid})-[r]->(s)
RETURN s.name as name, labels(s) as labels, type(r) as rel_type
"""

with driver.session() as session:
    for cid, name in targets:
        result = session.run(query, cid=cid)
        records = list(result)
        if records:
            nodes_info = []
            for r in records:
                s_name = r.get('name') or ''
                lbl = r['labels'][0] if r['labels'] else 'NoLabel'
                nodes_info.append(f"{s_name}({lbl})")
            print(f"[{name}] 연결 노드 {len(records)}개: {nodes_info[:8]}")
        else:
            print(f"[{name}] 연결 노드 없음 ({cid})")

driver.close()

# 2. Query CANONICAL_MAP hit rates from candidates.db raw_text
print("\n=== CANONICAL_MAP Hit Rates from Raw Text ===")
from jd_compiler import CANONICAL_MAP

conn = sqlite3.connect('candidates.db')
cur = conn.cursor()

for cid, name in targets:
    cur.execute('SELECT raw_text FROM candidates WHERE id=?', (cid,))
    row = cur.fetchone()
    if not row or not row[0]:
        print(f"[{name}] raw_text 없음")
        continue
    text = row[0].lower()
    hits = []
    # Count occurrences of keys in raw_text
    for key, canonical in CANONICAL_MAP.items():
        if key.lower() in text:
            hits.append((key, canonical))
    
    # Print hit count and sample hits
    print(f"[{name}] Hit count: {len(hits)}")
    unique_canonicals = sorted(list(set(c for k, c in hits)))
    print(f"  고유 Canonical 매핑 ({len(unique_canonicals)}개): {unique_canonicals[:8]}")

conn.close()
