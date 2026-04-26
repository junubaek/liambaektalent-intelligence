import json, sys
sys.stdout.reconfigure(encoding='utf-8')
from neo4j import GraphDatabase

with open('secrets.json', 'r', encoding='utf-8') as f:
    secrets = json.load(f)

driver = GraphDatabase.driver(secrets.get('NEO4J_URI'), auth=(secrets.get('NEO4J_USERNAME'), secrets.get('NEO4J_PASSWORD')))
with driver.session() as s:
    res = s.run('MATCH (c:Candidate) WHERE c.id ENDS WITH "22567" RETURN c.id as id, c.name_kr as name, c.phone as phone, c.email as email LIMIT 5').data()
    print(f'Count: {len(res)}')
    for r in res:
        print(f'ID: {r["id"]} | Name: {r["name"]} | Phone: {r["phone"]} | Email: {r["email"]}')
driver.close()
