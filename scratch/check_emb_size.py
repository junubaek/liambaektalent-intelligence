import json
from neo4j import GraphDatabase

secrets = json.load(open('secrets.json'))
driver = GraphDatabase.driver(secrets['NEO4J_URI'], auth=(secrets['NEO4J_USERNAME'], secrets['NEO4J_PASSWORD']))

with driver.session() as session:
    res = session.run('MATCH (c:Candidate {id: $id}) RETURN size(c.embedding) as s', id='db752f0f-0f1a-437c-a09d-43c20442ab7b').single()
    print(f"Size: {res['s'] if res else 'None'}")

driver.close()
