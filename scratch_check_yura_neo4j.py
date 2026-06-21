import json
from neo4j import GraphDatabase

with open('secrets.json', 'r', encoding='utf-8') as f:
    secrets = json.load(f)

driver = GraphDatabase.driver(
    secrets['NEO4J_URI'],
    auth=(secrets['NEO4J_USERNAME'], secrets['NEO4J_PASSWORD'])
)

with driver.session() as s:
    res = s.run("MATCH (c:Candidate) WHERE c.name_kr = '안유리' RETURN c.id as id, c.name_kr as name, c.current_company as company").data()
    print("=== Neo4j Candidates for 안유리 ===")
    for r in res:
        print(f"ID: {r['id']} | Name: {r['name']} | Company: {r['company']}")

driver.close()
