import json
from neo4j import GraphDatabase

with open('secrets.json', 'r', encoding='utf-8') as f:
    secrets = json.load(f)
    
driver = GraphDatabase.driver(
    secrets['NEO4J_URI'],
    auth=(secrets['NEO4J_USERNAME'], secrets['NEO4J_PASSWORD'])
)

names = ['김국현', '이원철', '한상현']
with driver.session() as session:
    for name in names:
        print(f"\n--- Checking Neo4j Aura nodes for '{name}' ---")
        res = session.run("MATCH (c:Candidate) WHERE c.name = $name OR c.name_kr = $name RETURN c.id, c.name, c.sector, c.current_company", name=name)
        for r in res:
            print(f"Node: ID={r[0]} | name={r[1]} | sector={r[2]} | company={r[3]}")
            
driver.close()
