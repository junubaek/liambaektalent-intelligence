from neo4j import GraphDatabase
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open("secrets.json", "r", encoding="utf-8") as f:
    secrets = json.load(f)

uri = secrets["NEO4J_URI"]
username = secrets["NEO4J_USERNAME"]
password = secrets["NEO4J_PASSWORD"]

driver = GraphDatabase.driver(uri, auth=(username, password))

cypher = """
MATCH (c:Candidate)
SET c.has_career_embeddings = false
RETURN count(c) as cnt
"""

try:
    with driver.session() as session:
        print("Running schema update query in Neo4j Aura (for all Candidates)...")
        res = session.run(cypher)
        cnt = res.single()["cnt"]
        print(f"Schema update complete! Marked {cnt} candidates with has_career_embeddings = false.")
except Exception as e:
    print(f"Error updating Neo4j schema: {e}")
finally:
    driver.close()
