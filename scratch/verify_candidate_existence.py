import json
from neo4j import GraphDatabase

secrets = json.load(open('secrets.json', 'r', encoding='utf-8'))
driver = GraphDatabase.driver(secrets['NEO4J_URI'], auth=(secrets['NEO4J_USERNAME'], secrets['NEO4J_PASSWORD']))

with driver.session() as session:
    with open('resync_no_skills.json', 'r') as f:
        target_ids = json.load(f)
    
    sample_id = target_ids[0]
    print(f"Checking ID: {sample_id}")
    
    res = session.run('MATCH (c:Candidate {id: $cid}) RETURN c.name_kr as name', cid=sample_id).single()
    if res:
        print(f"Candidate found: {res['name']}")
    else:
        print(f"Candidate NOT found. Trying broad search...")
        res2 = session.run('MATCH (c:Candidate) WHERE c.id CONTAINS $cid RETURN c.id as id, c.name_kr as name', cid=sample_id[:8]).data()
        for r in res2:
            print(f"  Close Match: {r['name']} ({r['id']})")

driver.close()
