import json
from neo4j import GraphDatabase

with open('secrets.json', 'r', encoding='utf-8') as f:
    secrets = json.load(f)
    
driver = GraphDatabase.driver(
    secrets['NEO4J_URI'],
    auth=(secrets['NEO4J_USERNAME'], secrets['NEO4J_PASSWORD'])
)

names = ['임서환', '이승용']
with driver.session() as session:
    for name in names:
        print(f"\n--- Inspecting Neo4j Aura relationships for '{name}' ---")
        # Find all relationships from Candidate c to any node
        res = session.run("""
            MATCH (c:Candidate)
            WHERE c.name = $name OR c.name_kr = $name
            MATCH (c)-[r]->(target)
            RETURN type(r) as rel_type, labels(target) as target_labels, target.name as target_name
            LIMIT 20
        """, name=name)
        for r in res:
            print(f"  [:{r['rel_type']}] -> ({r['target_labels']}) {r['target_name']}")
            
driver.close()
