import json
import sqlite3
import sys
import math

sys.stdout.reconfigure(encoding='utf-8')

with open('secrets.json', encoding='utf-8') as f:
    secrets = json.load(f)

# Connect to SQLite
conn = sqlite3.connect('candidates.db')
cur = conn.cursor()

# We will trace the candidates directly by simulating the scoring logic of api_search_v9
tests = [
    ('SCM logistics operations cost management', 'MIDDLE', '31f22567-1b6f-8152-93ca-ca5ab3080016', '유정한'),
    ('on-device AI inference embedded AI semiconductor', 'SENIOR', 'ba4abc09-302e-4fd4-ae93-b8af52aed567', '하현재'),
    ('healthcare AI computer vision deep learning medical imaging', 'MIDDLE', '32022567-1b6f-819f-b62e-fa5ecb02e3de', '김진영'),
    ('IPO IR strategic planning fundraising finance', 'SENIOR', '1c3e3279-b0c5-4661-9dcf-7fa929dd47bb', '김진호'),
]

from jd_compiler import api_search_v9

for query, seniority, target_id, name in tests:
    print(f"\n--- Tracing {name} ({target_id}) for query: '{query}' ---")
    
    # Run the full search
    r = api_search_v9(query, seniority=seniority)
    matched = r.get('matched', [])
    
    # Let's see if the candidate exists in matched
    rank = next((i+1 for i, c in enumerate(matched) if c.get('id') == target_id), None)
    if rank:
        print(f"  Result: Found at Rank {rank}")
    else:
        print("  Result: Not found in top 50.")
        
        # Let's inspect the candidate metadata
        cur.execute("SELECT name_kr, total_years, sector, current_company FROM candidates WHERE id=?", (target_id,))
        c_info = cur.fetchone()
        
        # Check if the candidate's ID is in the database metadata map of the query
        # Let's run a search and check the return structure
        # Wait, does the API return candidates that were filtered? No, only matches.
        # Let's run a quick query on Neo4j to see why their Graph Score (G) or Vector Score (V) is low.
        from neo4j import GraphDatabase
        driver = GraphDatabase.driver(secrets['NEO4J_URI'], auth=(secrets['NEO4J_USERNAME'], secrets['NEO4J_PASSWORD']))
        
        with driver.session() as session:
            # Check if candidate has skill connections
            res_skills = session.run("MATCH (c:Candidate {id: $cid})-[r]->(s:Skill) RETURN s.name as name, type(r) as rel", cid=target_id)
            skills = [f"{r['name']}({r['rel']})" for r in res_skills]
            print(f"  Neo4j Skills: {skills}")
            
        driver.close()
        
conn.close()
