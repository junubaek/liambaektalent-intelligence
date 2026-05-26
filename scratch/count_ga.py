import json
from neo4j import GraphDatabase

secrets = json.load(open('secrets.json'))
driver = GraphDatabase.driver(secrets['NEO4J_URI'], auth=(secrets['NEO4J_USERNAME'], secrets['NEO4J_PASSWORD']))

with driver.session() as session:
    res = session.run('MATCH (c:Candidate)-[:MANAGED|HAS_SKILL]->(s:Skill {name: "General_Affairs"}) RETURN count(c) as cnt').single()
    print(f"Count: {res['cnt']}")

driver.close()
