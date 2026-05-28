import json
from neo4j import GraphDatabase

with open('secrets.json', 'r', encoding='utf-8') as f:
    secrets = json.load(f)
    
driver = GraphDatabase.driver(
    secrets['NEO4J_URI'],
    auth=(secrets['NEO4J_USERNAME'], secrets['NEO4J_PASSWORD'])
)

with driver.session() as session:
    res = session.run("MATCH (c:Candidate {name_kr: '김국현'}) RETURN c.id, keys(c), c.embedding IS NOT NULL")
    for r in res:
        print(f"ID={r[0]} | Keys={r[1]} | HasEmbedding={r[2]}")
        
driver.close()
