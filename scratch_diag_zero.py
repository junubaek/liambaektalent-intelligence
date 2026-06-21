import json
import sys
import sqlite3
from neo4j import GraphDatabase

sys.stdout.reconfigure(encoding='utf-8')

with open('secrets.json', encoding='utf-8') as f:
    s = json.load(f)

driver = GraphDatabase.driver(s['NEO4J_URI'], auth=(s['NEO4J_USERNAME'], s['NEO4J_PASSWORD']))

# We need to map short IDs like 'c307e37b' to full UUIDs from sqlite candidates.db
conn = sqlite3.connect('candidates.db')
cur = conn.cursor()

def get_full_id(short_id):
    if len(short_id) == 36: # Already full UUID
        return short_id
    cur.execute("SELECT id FROM candidates WHERE id LIKE ?", (f"{short_id}%",))
    r = cur.fetchone()
    return r[0] if r else short_id

targets = [
    ('한경환', '1aaad2d3-348d-48f7-8501-38d7c1f7df03', 'c307e37b'),
    ('김태경', 'fbc27466-7587-45e6-b459-c2920b5d71fe', '33522567'),
    ('김일곤', 'e88ea471-e1eb-4c40-b5e1-7648e340fac4', 'c5394306'),
    ('유정한', '31f22567-1b6f-8152-93ca-ca5ab3080016', '746a76b6'),
    ('김형수', '4b4c3372-401b-4897-a9b3-d36a3ba3de37', 'c3d4ee55'),
    ('오수영', '32e22567-1b6f-8181-9992-d986271e941f', '341e6ee6'),
    ('배정현', 'fafa2636-cf0b-42c1-8c18-598d089e9c61', 'c307e37b'),
    ('하현재', 'ba4abc09-302e-4fd4-ae93-b8af52aed567', '33522567'),
    ('김진영', '32022567-1b6f-819f-b62e-fa5ecb02e3de', '33522567'),
    ('김진호', '1c3e3279-b0c5-4661-9dcf-7fa929dd47bb', '32122567'),
    ('박천혁', '3d322d13-0699-4453-b70e-5a4c2aac38f9', '31f22567'),
]

q = '''
MATCH (c:Candidate {id: $cid})-[r]->(s:Skill)
RETURN s.name as name, type(r) as rel
LIMIT 15
'''

with driver.session() as session:
    for name, answer_id, top1_short in targets:
        top1_id = get_full_id(top1_short)
        
        # Get candidate names
        cur.execute("SELECT name_kr, current_company FROM candidates WHERE id=?", (answer_id,))
        ans_row = cur.fetchone()
        ans_info = f"{ans_row[0]}({ans_row[1]})" if ans_row else name
        
        cur.execute("SELECT name_kr, current_company FROM candidates WHERE id=?", (top1_id,))
        top_row = cur.fetchone()
        top_info = f"{top_row[0]}({top_row[1]})" if top_row else top1_short
        
        print(f'\n[{name}] 정답자: {ans_info} ({answer_id})')
        res = list(session.run(q, cid=answer_id))
        print('  연결 노드: ' + ', '.join([f"{r['name']}({r['rel']})" for r in res]) if res else '  연결 노드: 없음')

        print(f'  1위 경쟁자: {top_info} ({top1_id[:8]})')
        res2 = list(session.run(q, cid=top1_id))
        print('  연결 노드: ' + ', '.join([f"{r['name']}({r['rel']})" for r in res2]) if res2 else '  연결 노드: 없음')

conn.close()
driver.close()
