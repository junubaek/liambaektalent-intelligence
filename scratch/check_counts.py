import json
from neo4j import GraphDatabase

with open("secrets.json", "r", encoding="utf-8") as f:
    secrets = json.load(f)

driver = GraphDatabase.driver(secrets["NEO4J_URI"], auth=(secrets["NEO4J_USERNAME"], secrets["NEO4J_PASSWORD"]))
skills = ["Treasury_Management", "Enterprise_Sales", "Legal_Practice", "Litigation"]

with driver.session() as session:
    for skill in skills:
        res = session.run("MATCH (c:Candidate)-[]->(s:Skill {name: $name}) RETURN count(c) as count", name=skill).single()
        print(f"{skill}: {res['count']} candidates")

driver.close()
