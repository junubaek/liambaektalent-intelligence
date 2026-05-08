import json
from neo4j import GraphDatabase

secrets = json.load(open('secrets.json'))
driver = GraphDatabase.driver(secrets['NEO4J_URI'], auth=(secrets['NEO4J_USERNAME'], secrets['NEO4J_PASSWORD']))
with driver.session() as session:
    query = 'MATCH (c:Candidate) WITH c.id as cid, count(c) as cnt WHERE cnt > 1 RETURN cid, cnt'
    results = session.run(query)
    print("[Remaining ID Duplicates in Neo4j]")
    found = False
    for r in results:
        found = True
        print(f" - ID: {r['cid']} | Count: {r['cnt']}")
    if not found:
        print("No duplicate IDs found. Integrity restored.")
driver.close()
