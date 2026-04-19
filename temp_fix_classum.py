import os
import json
import sqlite3
from neo4j import GraphDatabase

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
CACHE_FILE = os.path.join(ROOT_DIR, "candidates_cache_jd.json")
SECRETS_FILE = os.path.join(ROOT_DIR, "secrets.json")
DB_PATH = os.path.join(ROOT_DIR, "candidates.db")

target_id = '33522567-1b6f-816e-bc1a-da0cb6905e85'
real_name = '엄준용'

print("Fixing candidate:", target_id, "to", real_name)

# 1. Update SQLite
print("Updating SQLite...")
conn = sqlite3.connect(DB_PATH)
c = conn.cursor()
c.execute("UPDATE candidates SET name_kr = ? WHERE id = ?", (real_name, target_id))
conn.commit()
conn.close()
print("SQLite updated.")

# 2. Update JSON cache
print("Updating JSON cache...")
with open(CACHE_FILE, "r", encoding="utf-8") as f:
    cands = json.load(f)

for cand in cands:
    if cand.get('id') == target_id:
        cand['name_kr'] = real_name
        if 'name' in cand:
            cand['name'] = real_name

with open(CACHE_FILE, "w", encoding="utf-8") as f:
    json.dump(cands, f, ensure_ascii=False, indent=2)
print("JSON cache updated.")

# 3. Update Neo4j
print("Updating Neo4j...")
with open(SECRETS_FILE, "r", encoding="utf-8") as f:
    secrets = json.load(f)
neo4j_pwd = secrets.get('NEO4J_PASSWORD', 'toss1234')
driver = GraphDatabase.driver('bolt://localhost:7687', auth=('neo4j', neo4j_pwd))

with driver.session() as session:
    session.run("MATCH (c:Candidate {id: $id}) SET c.name_kr = $name", id=target_id, name=real_name)
    # also replace name property if it exists
    session.run("MATCH (c:Candidate {id: $id}) WHERE c.name IS NOT NULL SET c.name = $name", id=target_id, name=real_name)
    
driver.close()
print("Neo4j updated. Fix complete!")
