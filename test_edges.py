import json
import logging
from neo4j import GraphDatabase

try:
    with open("secrets.json", "r", encoding="utf-8") as f:
        secrets = json.load(f)
        NEO4J_URI = secrets.get("NEO4J_URI", "bolt://localhost:7687")
        NEO4J_USER = secrets.get("NEO4J_USER", "neo4j")
        NEO4J_PASSWORD = secrets.get("NEO4J_PASSWORD", "dlftjs!")
except Exception as e:
    print(f"Failed to load secrets: {e}")

driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "toss1234"))

with driver.session() as session:
    res = session.run("MATCH (c:Candidate {name: '[리벨리온] 이범기(Treasury Manager)부문'})-[r]->(t) RETURN labels(t) as lbls, t.name as name")
    for r in res:
        print(f"Target: {r['name']} / Labels: {r['lbls']}")

    res2 = session.run("MATCH (c:Candidate {name: '[리벨리온] 김대중(Treasury Manager)부문'}) RETURN properties(c) as props")
    for r in res2:
        print(f"김대중 props: {r['props']}")
