import json, sys
from neo4j import GraphDatabase

def check():
    with open('secrets.json', 'r', encoding='utf-8') as f:
        secrets = json.load(f)
    driver = GraphDatabase.driver(secrets.get('NEO4J_URI'), auth=(secrets.get('NEO4J_USERNAME'), secrets.get('NEO4J_PASSWORD')))
    with driver.session() as s:
        res = s.run('MATCH (c:Candidate) RETURN c.id as id LIMIT 10').data()
        for r in res:
            cid = r['id']
            print(f'ID: {cid} | Type: {type(cid)}')
            
        # Also check the count of STARTS WITH "32" or similar dummy patterns
        res2 = s.run('MATCH (c:Candidate) WHERE toString(c.id) STARTS WITH "32" OR toString(c.id) STARTS WITH "33" RETURN count(c) as cnt').single()
        print(f'Count with STARTS WITH 32/33: {res2["cnt"]}')
        
        # Check samples
        res3 = s.run('MATCH (c:Candidate) WHERE toString(c.id) STARTS WITH "32" OR toString(c.id) STARTS WITH "33" RETURN c.id as id, c.name_kr as name LIMIT 5').data()
        for r in res3:
            print(f'Sample: {r["id"]} | {r["name"]}')
            
    driver.close()

if __name__ == "__main__":
    check()
