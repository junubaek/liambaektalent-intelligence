import json
from neo4j import GraphDatabase

secrets = json.load(open('secrets.json'))
driver = GraphDatabase.driver(secrets['NEO4J_URI'], auth=(secrets['NEO4J_USERNAME'], secrets['NEO4J_PASSWORD']))

with driver.session() as session:
    res = session.run('MATCH (c:Candidate {id: $id})-[:MANAGED|HAS_SKILL]->(s:Skill) RETURN s.name as name', id='32022567-1b6f-8140-9d49-f3f038b20c5f')
    skills = [r['name'] for r in res]
    print(f"Skills: {skills}")

driver.close()
