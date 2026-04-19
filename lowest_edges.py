import json
import sqlite3
import sys

sys.stdout.reconfigure(encoding='utf-8')

f = open('processed_step6.json', 'r', encoding='utf-8')
d = json.load(f)

edges_info = [(k, v.get('edge_count', 0)) for k, v in d.items()]
edges_info.sort(key=lambda x: x[1])

db = sqlite3.connect('candidates.db')
c = db.cursor()

names = []
for uid, cnt in edges_info:
    c.execute('SELECT name_kr FROM candidates WHERE id=?', (uid,))
    row = c.fetchone()
    name = row[0] if row else uid
    names.append((name, cnt))

zero_count = sum(1 for _, cnt in names if cnt == 0)
print(f"Zero edge candidates: {zero_count}")
print("Lowest 5 (including zeros):")
for n in names[:5]:
    print(n)

print("\nLowest 5 (with at least 1 edge):")
from neo4j import GraphDatabase
driver = GraphDatabase.driver("bolt://127.0.0.1:7687", auth=("neo4j", "toss1234"))

with driver.session() as s:
    count = 0
    for name, cnt in names:
        if cnt > 0:
            res = s.run("MATCH (c:Candidate {name_kr: $name})-[]->(sk:Skill) RETURN sk.name as skill", name=name)
            skills = [r['skill'] for r in res]
            print(f"- {name} ({cnt} edges): {skills}")
            count += 1
            if count == 5:
                break
