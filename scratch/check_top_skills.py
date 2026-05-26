import json
from neo4j import GraphDatabase

secrets = json.load(open('secrets.json'))
driver = GraphDatabase.driver(secrets['NEO4J_URI'], auth=(secrets['NEO4J_USERNAME'], secrets['NEO4J_PASSWORD']))

with driver.session() as session:
    res = session.run('MATCH (c:Candidate {id: $id})-[:MANAGED|HAS_SKILL]->(s:Skill) RETURN s.name as name', id='edef1d71-14c5-415d-a13f-017d0393922d')
    skills = [r['name'] for r in res]
    print(f"Skills: {skills}")

driver.close()
