import os
import sys
import json
import sqlite3
from neo4j import GraphDatabase

sys.stdout.reconfigure(encoding='utf-8')

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(ROOT_DIR, "candidates.db")
CACHE_FILE = os.path.join(ROOT_DIR, "candidates_cache_jd.json")
SECRETS_FILE = os.path.join(ROOT_DIR, "secrets.json")

target_fixes = {
    '33522567-1b6f-819b-bea5-fea6d36a9b7b': '남예영',
    '33522567-1b6f-8105-b67d-ff8da7c3a1d5': '박강민',
    '33522567-1b6f-8175-9813-d8481429bc99': 'ddaiee',
    '33522567-1b6f-81ad-b948-e46907a062cc': '장수아',
    '33522567-1b6f-810f-b44e-c4887fc8f61d': '김보라',
    '33522567-1b6f-811e-9d91-ecece5e9547e': '이민영',
    '33522567-1b6f-8100-8418-d4f9402ecc53': '권재훈(Jeahoon Kwon)',
    '33522567-1b6f-81dc-b909-d9bbb81be114': '김동은',
    '33522567-1b6f-8150-ad07-d60eca78b805': '김한얼',
    '33522567-1b6f-81c1-9b1e-fc9cdbce6786': '정영아',
    '33522567-1b6f-8199-ac64-ff40615e6410': '임세호',
    '33522567-1b6f-8182-9c23-d49d39bc9444': '원창희',
    '33522567-1b6f-8132-85e2-cb3141647e04': '엄상빈'
}

print("1. Updating SQLite")
conn = sqlite3.connect(DB_PATH)
c = conn.cursor()
for cid, real_name in target_fixes.items():
    c.execute("UPDATE candidates SET name_kr = ? WHERE id = ?", (real_name, cid))
conn.commit()
conn.close()

print("2. Updating JSON Cache & Shim Mi-kyung's company")
with open(CACHE_FILE, "r", encoding="utf-8") as f:
    cands = json.load(f)

for cand in cands:
    cid = cand.get('id')
    
    if cid in target_fixes:
        real_name = target_fixes[cid]
        cand['name_kr'] = real_name
        if 'name' in cand:
            cand['name'] = real_name
            
    if '심미경' in cand.get('name_kr', ''):
        careers = cand.get('parsed_career_json')
        if isinstance(careers, str):
            try: careers = json.loads(careers)
            except: careers = []
        if careers:
            for career in careers:
                if career.get('company') == '재직중':
                    career['company'] = '어플라이드머티어리얼즈'
            cand['parsed_career_json'] = careers

with open(CACHE_FILE, "w", encoding="utf-8") as f:
    json.dump(cands, f, ensure_ascii=False, indent=2)

print("3. Updating Neo4j")
with open(SECRETS_FILE, "r", encoding="utf-8") as f:
    secrets = json.load(f)
neo4j_pwd = secrets.get('NEO4J_PASSWORD', 'toss1234')
driver = GraphDatabase.driver('bolt://localhost:7687', auth=('neo4j', neo4j_pwd))

with driver.session() as session:
    for cid, real_name in target_fixes.items():
        session.run("MATCH (c:Candidate {id: $id}) SET c.name_kr = $name", id=cid, name=real_name)
        session.run("MATCH (c:Candidate {id: $id}) WHERE c.name IS NOT NULL SET c.name = $name", id=cid, name=real_name)

    shim_cands = [c for c in cands if '심미경' in c.get('name_kr', '')]
    if shim_cands:
        shim_cid = shim_cands[0].get('id')
        updated_careers_str = json.dumps(shim_cands[0].get('parsed_career_json'), ensure_ascii=False)
        session.run("MATCH (c:Candidate {id: $id}) SET c.parsed_career_json = $data", id=shim_cid, data=updated_careers_str)

driver.close()
print("All done!")
