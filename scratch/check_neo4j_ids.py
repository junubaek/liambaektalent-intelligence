import json
from neo4j import GraphDatabase

with open("secrets.json", "r", encoding="utf-8") as f:
    secrets = json.load(f)

driver = GraphDatabase.driver(secrets["NEO4J_URI"], auth=(secrets["NEO4J_USERNAME"], secrets["NEO4J_PASSWORD"]))
names = ["이신형", "이상헌", "배유정", "김대중", "최우성"]

with driver.session() as session:
    for name in names:
        res = session.run("MATCH (c:Candidate {name_kr: $name}) RETURN c.id as id", name=name).data()
        print(f"Name: {name} | Neo4j IDs: {[r['id'] for r in res]}")

driver.close()
