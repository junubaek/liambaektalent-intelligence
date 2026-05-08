import json
from neo4j import GraphDatabase

secrets = json.load(open('secrets.json'))
driver = GraphDatabase.driver(secrets['NEO4J_URI'], auth=(secrets['NEO4J_USERNAME'], secrets['NEO4J_PASSWORD']))
with driver.session() as session:
    query = 'MATCH (s:Skill {name: "Global_Sales_and_Marketing"}) RETURN s.name as name, s.keywords as keywords'
    res = session.run(query).single()
    if res:
        print(f"Skill Name: {res['name']}")
        print(f"Keywords: {res['keywords']}")
    else:
        print("Skill node 'Global_Sales_and_Marketing' not found.")
        
    # Also check ANY Skill node that Kang Ki-tae is connected to
    print("\n--- Kang Ki-tae Skills Investigation ---")
    query_kang = 'MATCH (c:Candidate {name_kr: "강기태"})-[r]->(s:Skill) RETURN s.name as name, s.keywords as keywords, type(r) as rel'
    results = session.run(query_kang)
    for r in results:
        print(f"Rel: {r['rel']} -> Skill: {r['name']} | Keywords: {r['keywords']}")
driver.close()
