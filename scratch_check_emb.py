import json
from neo4j import GraphDatabase

with open('secrets.json', encoding='utf-8') as f:
    secrets = json.load(f)

driver = GraphDatabase.driver(secrets['NEO4J_URI'], auth=(secrets['NEO4J_USERNAME'], secrets['NEO4J_PASSWORD']))
with driver.session() as session:
    res = session.run('MATCH (c:Candidate {id: $cid}) RETURN keys(c) as k, c.embedding IS NOT NULL as has_emb', cid='3d322d13-0699-4453-b70e-5a4c2aac38f9')
    r = res.single()
    print(r)
driver.close()
