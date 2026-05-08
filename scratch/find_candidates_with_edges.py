import json
from neo4j import GraphDatabase

with open("secrets.json", "r", encoding="utf-8") as f:
    secrets = json.load(f)

driver = GraphDatabase.driver(secrets["NEO4J_URI"], auth=(secrets["NEO4J_USERNAME"], secrets["NEO4J_PASSWORD"]))

with driver.session() as session:
    res = session.run("MATCH (c:Candidate)-[r]->(s:Skill) RETURN c.id as id, c.name_kr as name LIMIT 5").data()
    print("Candidates with edges:")
    for r in res:
        print(f"  - {r['name']} ({r['id']})")

driver.close()
