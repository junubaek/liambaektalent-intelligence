import json
from neo4j import GraphDatabase

with open("secrets.json", "r", encoding="utf-8") as f:
    secrets = json.load(f)

driver = GraphDatabase.driver(secrets["NEO4J_URI"], auth=(secrets["NEO4J_USERNAME"], secrets["NEO4J_PASSWORD"]))

with driver.session() as session:
    res = session.run("MATCH (c:Candidate)-[r]->(s:Skill) RETURN count(r) as count").single()
    print(f"Total Candidate-Skill edges in Neo4j: {res['count']}")
    
    res2 = session.run("MATCH (c:Candidate) RETURN count(c) as count").single()
    print(f"Total Candidates in Neo4j: {res2['count']}")

driver.close()
