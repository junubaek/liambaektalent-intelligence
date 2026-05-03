
from neo4j import GraphDatabase
import json
import os

SECRETS_PATH = "secrets.json"
with open(SECRETS_PATH, "r", encoding="utf-8") as f:
    secrets = json.load(f)

driver = GraphDatabase.driver(
    secrets['NEO4J_URI'], 
    auth=(secrets['NEO4J_USERNAME'], secrets['NEO4J_PASSWORD'])
)

print("--- Neo4j Candidate Sample (Top 50) ---")
with driver.session() as session:
    res = session.run("MATCH (c:Candidate) RETURN c.id AS id, c.name_kr AS name, c.name AS name_en LIMIT 50")
    for r in res:
        print(f"ID: {r['id']} | Name: {r['name']} / {r['name_en']}")

driver.close()
