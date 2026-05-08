import json
from neo4j import GraphDatabase

secrets = json.load(open('secrets.json'))
driver = GraphDatabase.driver(secrets['NEO4J_URI'], auth=(secrets['NEO4J_USERNAME'], secrets['NEO4J_PASSWORD']))
with driver.session() as session:
    query = 'MATCH (c:Candidate {name_kr: "강기태"}) RETURN c.id as id, c.current_company as company, count((c)--()) as edge_count'
    results = session.run(query)
    print("[Candidates named Kang Ki-tae in Neo4j]")
    for r in results:
        print(f" - ID: {r['id']} | Company: {r['company']} | Edges: {r['edge_count']}")
driver.close()
