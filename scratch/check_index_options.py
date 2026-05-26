import json
from neo4j import GraphDatabase

secrets = json.load(open('secrets.json'))
driver = GraphDatabase.driver(secrets['NEO4J_URI'], auth=(secrets['NEO4J_USERNAME'], secrets['NEO4J_PASSWORD']))

with driver.session() as session:
    res = session.run('SHOW INDEXES YIELD name, options WHERE name = "candidate_embedding"').single()
    print(res['options'] if res else 'Not found')

driver.close()
