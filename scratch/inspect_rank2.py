import json
from neo4j import GraphDatabase

secrets = json.load(open('secrets.json'))
driver = GraphDatabase.driver(secrets['NEO4J_URI'], auth=(secrets['NEO4J_USERNAME'], secrets['NEO4J_PASSWORD']))

target_id = '32022567-1b6f-8140-9d49-f3f038b20c5f'

with driver.session() as session:
    res = session.run("MATCH (c:Candidate {id: $id}) RETURN c", id=target_id).single()
    print(f"Node: {res['c'] if res else 'None'}")
    
    res_s = session.run("MATCH (c:Candidate {id: $id})-[r]->(s:Skill) RETURN s.name, type(r)", id=target_id)
    print("Skills:")
    for r in res_s:
        print(f"  {r['s.name']} ({r['type(r)']})")

driver.close()
