import json
import os
import sys
from neo4j import GraphDatabase

with open("secrets.json", "r", encoding="utf-8") as f:
    secrets = json.load(f)

uri = secrets.get("NEO4J_URI")
user = secrets.get("NEO4J_USERNAME")
password = secrets.get("NEO4J_PASSWORD")

driver = GraphDatabase.driver(uri, auth=(user, password))
test_nodes = ["Legal_Core", "Legal_Practice", "Litigation", "Contract_Review"]

with driver.session() as session:
    res = session.run("MATCH (n:Skill) WHERE n.name IN $names RETURN n.name as name", names=test_nodes).data()
    print("Found nodes:", [r["name"] for r in res])
    
    # Check edges for Legal_Core
    res_edges = session.run("MATCH (n:Skill {name: 'Legal_Core'})-[r]->(m) RETURN m.name as target, type(r) as rel").data()
    print("Legal_Core edges:", res_edges)

driver.close()
