import json
import sqlite3
import sys
from neo4j import GraphDatabase
import openai

sys.stdout.reconfigure(encoding='utf-8')

with open('secrets.json', encoding='utf-8') as f:
    secrets = json.load(f)

openai_client = openai.OpenAI(api_key=secrets['OPENAI_API_KEY'])
driver = GraphDatabase.driver(secrets['NEO4J_URI'], auth=(secrets['NEO4J_USERNAME'], secrets['NEO4J_PASSWORD']))

tests = [
    ('SCM logistics operations cost management', 'MIDDLE', '31f22567-1b6f-8152-93ca-ca5ab3080016', '유정한'),
    ('on-device AI inference embedded AI semiconductor', 'SENIOR', 'ba4abc09-302e-4fd4-ae93-b8af52aed567', '하현재'),
    ('healthcare AI computer vision deep learning medical imaging', 'MIDDLE', '32022567-1b6f-819f-b62e-fa5ecb02e3de', '김진영'),
    ('IPO IR strategic planning fundraising finance', 'SENIOR', '1c3e3279-b0c5-4661-9dcf-7fa929dd47bb', '김진호'),
]

conn = sqlite3.connect('candidates.db')
cur = conn.cursor()

for query, seniority, target_id, name in tests:
    print(f"\n=== Diagnosing {name} ({target_id}) ===")
    
    # Check SQLite values
    cur.execute("SELECT name_kr, total_years, sector, current_company FROM candidates WHERE id=?", (target_id,))
    db_row = cur.fetchone()
    print(f"  SQLite: name={db_row[0]}, years={db_row[1]}, sector={db_row[2]}, company={db_row[3]}")
    
    # Check Neo4j node existence
    with driver.session() as session:
        res = session.run("MATCH (c:Candidate {id: $cid}) RETURN c.id as id, c.name as name, c.embedding IS NOT NULL as has_emb", cid=target_id)
        r = res.single()
        print(f"  Neo4j Node: {r.data() if r else 'NOT FOUND'}")
        
    # Check if present in Vector Search
    res_emb = openai_client.embeddings.create(model='text-embedding-3-small', input=[query])
    q_vec = res_emb.data[0].embedding
    with driver.session() as session:
        res = session.run('''
            CALL db.index.vector.queryNodes('candidate_embedding', 200, $queryVector)
            YIELD node AS c, score
            RETURN c.id AS id, c.name_kr AS name_kr, score
        ''', queryVector=q_vec)
        records = list(res)
        vector_rank = next((i+1 for i, rec in enumerate(records) if rec['id'] == target_id), None)
        print(f"  Vector Search Rank: {vector_rank} (total matches: {len(records)})")

conn.close()
driver.close()
