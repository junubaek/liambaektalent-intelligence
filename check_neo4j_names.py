from neo4j import GraphDatabase
import json

with open("secrets.json", "r", encoding="utf-8") as f:
    secrets = json.load(f)
driver = GraphDatabase.driver("neo4j://127.0.0.1:7687", auth=("neo4j", "toss1234"))

with driver.session() as session:
    res = session.run("MATCH (c:Candidate) RETURN c.name_kr LIMIT 10")
    for r in res:
        print(r['c.name_kr'])
