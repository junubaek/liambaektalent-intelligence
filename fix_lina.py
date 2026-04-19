import sqlite3
import json
from neo4j import GraphDatabase
import os

target_id = "33522567-1b6f-81d1-84b4-d80fff34b631"
real_name = "김보람"

print("1. Updating SQLite candidates.db")
conn = sqlite3.connect('candidates.db')
c = conn.cursor()
c.execute("UPDATE candidates SET name_kr = ? WHERE id = ?", (real_name, target_id))
conn.commit()
conn.close()

print("2. Updating candidates_cache_jd.json")
try:
    with open('candidates_cache_jd.json', 'r', encoding='utf-8') as f:
        cache = json.load(f)
        
    for cand in cache:
        if cand.get('id') == target_id:
            cand['name_kr'] = real_name
            cand['name'] = real_name
                
    with open('candidates_cache_jd.json', 'w', encoding='utf-8') as f:
        json.dump(cache, f, ensure_ascii=False, indent=2)
except Exception as e:
    print("Cache update failed:", e)

print("3. Updating Neo4j Graph")
try:
    driver = GraphDatabase.driver(
        "bolt://127.0.0.1:7687", 
        auth=("neo4j", "toss1234")
    )
    with driver.session() as session:
        q = "MATCH (c:Candidate {id: $id}) SET c.name = $name"
        session.run(q, id=target_id, name=real_name)
    driver.close()
    print("Neo4j Update Complete.")
except Exception as e:
    print("Neo4j update failed:", e)

print(f"\n✨ Fixed ID {target_id} to {real_name}")
