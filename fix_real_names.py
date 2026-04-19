import sqlite3
import json
from neo4j import GraphDatabase
import os

updates = [
    ("33522567-1b6f-81d1-84b4-d80fff34b631", "리나"),
    ("69832170-515b-40b6-95f4-65de96656665", "어울림"),
    ("2d65303e-0fff-4868-924c-11f699a577c1", "이상열"),
    ("2c6aba15-67ed-4c11-a251-e3d7c59d1247", "정한아"),
    ("8147a5d5-85b3-409e-b120-ea5ac64a5e14", "최종요"),
    ("fc659206-ef0e-4cbe-bac3-17bd665f4df1", "최종호"),
    ("25dd9a02-b5ac-4838-92a3-0fa886853099", "홍승언"),
    ("3f64bc68-eda8-4ca7-894c-3a16d58a7ba8", "강한")
]

print("1. Updating SQLite candidates.db")
conn = sqlite3.connect('candidates.db')
c = conn.cursor()
for cid, real_name in updates:
    c.execute("UPDATE candidates SET name_kr = ? WHERE id = ?", (real_name, cid))
conn.commit()
conn.close()

print("2. Updating candidates_cache_jd.json")
try:
    with open('candidates_cache_jd.json', 'r', encoding='utf-8') as f:
        cache = json.load(f)
        
    for cand in cache:
        for cid, real_name in updates:
            if cand.get('id') == cid:
                cand['name_kr'] = real_name
                cand['name'] = real_name # also update english name fallback
                
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
        for cid, real_name in updates:
            q = "MATCH (c:Candidate {id: $id}) SET c.name = $name"
            session.run(q, id=cid, name=real_name)
    driver.close()
    print("Neo4j Update Complete.")
except Exception as e:
    print("Neo4j update failed:", e)

print("\n✨ All repairs complete.")
