import json, sys
from neo4j import GraphDatabase

secrets = json.load(open('secrets.json'))
driver = GraphDatabase.driver(secrets['NEO4J_URI'], auth=(secrets['NEO4J_USERNAME'], secrets['NEO4J_PASSWORD']))

with driver.session() as session:
    res = session.run('SHOW INDEXES YIELD name, type, labelsOrTypes, properties WHERE type = "VECTOR"')
    for r in res:
        print(f"Index: {r['name']}, Label: {r['labelsOrTypes']}, Property: {r['properties']}")
driver.close()
