import sys
import json
import os
from neo4j import GraphDatabase

# Ensure UTF-8 output
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

dataset_path = 'golden_dataset_v8.json'
if not os.path.exists(dataset_path):
    print(f"Error: {dataset_path} not found.")
    sys.exit(1)

with open(dataset_path, 'r', encoding='utf-8') as f:
    golden = json.load(f)

secrets_path = 'secrets.json'
if not os.path.exists(secrets_path):
    print("Error: secrets.json not found.")
    sys.exit(1)
with open(secrets_path, 'r', encoding='utf-8') as f:
    secrets = json.load(f)

driver = GraphDatabase.driver(secrets['NEO4J_URI'], auth=(secrets['NEO4J_USERNAME'], secrets['NEO4J_PASSWORD']))

print(f"=== Detailed Analysis of Golden Dataset Targets ({len(golden)} queries) ===")
print("-" * 60)

with driver.session() as session:
    for q_data in golden:
        query = q_data.get('query', '')
        rel_ids = q_data.get('relevant_ids', [])
        rel_names = q_data.get('relevant_names', [])
        
        if not rel_ids:
            continue
            
        print(f"Query: '{query}'")
        
        for i, cid in enumerate(rel_ids):
            name = rel_names[i] if i < len(rel_names) else "Unknown"
            
            # Fetch skills from Neo4j
            res = session.run(
                'MATCH (c:Candidate {id: $cid})-[r]->(s:Skill) RETURN s.name as skill_name, type(r) as rel',
                cid=cid
            ).data()
            
            skills = [f"{r['skill_name']}({r['rel']})" for r in res]
            
            print(f"  Target: {name} ({cid[:8]}...)")
            print(f"  Skills ({len(skills)}): {', '.join(skills[:15])}{' ...' if len(skills) > 15 else ''}")
            
            # Check if any skill matches the query (simple keyword check)
            query_keywords = query.lower().split()
            matches = [s for s in skills if any(k in s.lower() for k in query_keywords)]
            if matches:
                print(f"  [OK] Potential matches found in skills: {matches}")
            else:
                print(f"  [WARN] No direct skill match found for query keywords!")
        print("-" * 60)

driver.close()
