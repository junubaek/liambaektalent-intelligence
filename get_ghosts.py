from neo4j import GraphDatabase
import os

from ontology_graph import CANONICAL_MAP
valid_nodes = set(CANONICAL_MAP.values())

driver = GraphDatabase.driver('neo4j://127.0.0.1:7687', auth=('neo4j', 'toss1234'))

ghosts = []
with driver.session() as session:
    res = session.run("MATCH (s:Skill) RETURN s.name AS name")
    for rec in res:
        name = rec["name"]
        if name not in valid_nodes and not '_' in name and not name.isupper():
            ghosts.append(name)

ghosts.sort()
print("GHOSTS_LIST:")
for g in ghosts:
    print(f"- {g}")
