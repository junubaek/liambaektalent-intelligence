import json
from neo4j import GraphDatabase

with open('secrets.json', 'r', encoding='utf-8') as f:
    secrets = json.load(f)
    
driver = GraphDatabase.driver(
    secrets['NEO4J_URI'],
    auth=(secrets['NEO4J_USERNAME'], secrets['NEO4J_PASSWORD'])
)

target_ids = [
    '31f22567-1b6f-8179-b2ec-c7f047e6d362', # 임서환
    '31f22567-1b6f-8121-a08f-d8610b5e1294', # 이승용
    'b973e863-ad09-4b3a-999d-1b9eb36adf10'  # 김국현 (new node)
]

with driver.session() as session:
    for tid in target_ids:
        print(f"\n--- Inspecting Neo4j Aura relationships for ID '{tid}' ---")
        res = session.run("""
            MATCH (c:Candidate {id: $id})-[r]->(target)
            RETURN type(r) as rel_type, labels(target) as target_labels, target.name as target_name
            LIMIT 20
        """, id=tid)
        rows = list(res)
        print(f"Total relationships found: {len(rows)}")
        for r in rows:
            print(f"  [:{r['rel_type']}] -> ({r['target_labels']}) {r['target_name']}")
            
driver.close()
