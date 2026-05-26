import json
from neo4j import GraphDatabase

secrets = json.load(open('secrets.json'))
driver = GraphDatabase.driver(secrets['NEO4J_URI'], auth=(secrets['NEO4J_USERNAME'], secrets['NEO4J_PASSWORD']))

target_skills = ["General_Affairs"]
target_id = 'db752f0f-0f1a-437c-a09d-43c20442ab7b'

with driver.session() as session:
    res = session.run("""
        MATCH (c:Candidate)-[r]->(s:Skill)
        WHERE s.name IN $target_skills AND type(r) <> 'USED_AS_TEMP' 
        RETURN DISTINCT coalesce(c.id, c.name_kr) AS id
    """, target_skills=target_skills)
    
    ids = [str(r['id']) for r in res]
    print(f"Total graph matches: {len(ids)}")
    if target_id in ids:
        idx = ids.index(target_id)
        print(f"Lee Sang-heon found at index {idx} in graph matches.")
    else:
        print("Lee Sang-heon NOT in graph matches.")

driver.close()
