from neo4j import GraphDatabase
import json

secrets = json.load(open('secrets.json', encoding='utf-8'))
driver = GraphDatabase.driver(secrets['NEO4J_URI'], auth=(secrets['NEO4J_USERNAME'], secrets['NEO4J_PASSWORD']))

target_id = 'ba99c86f-562d-4193-8380-0e414bd19093' # 배성호

with driver.session() as session:
    res = session.run("""
        MATCH (c:Candidate {id: $id})-[r]->(s:Skill)
        RETURN s.name AS skill, type(r) AS action
    """, id=target_id)
    print("배성호's Skills in Neo4j:")
    for r in res:
        print(f"  {r['skill']} ({r['action']})")

driver.close()
