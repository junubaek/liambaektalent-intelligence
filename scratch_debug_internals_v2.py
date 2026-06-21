import sys
import json
import sqlite3
import math
from neo4j import GraphDatabase
import openai

sys.stdout.reconfigure(encoding='utf-8')

# We copy the exact logic of api_search_v9 from jd_compiler.py but insert tracing for target candidate id.
target_id = '32022567-1b6f-819f-b62e-fa5ecb02e3de' # 김진영
query = 'healthcare AI computer vision deep learning medical imaging'
seniority = 'MIDDLE'

with open('secrets.json', encoding='utf-8') as f:
    secrets = json.load(f)

# Run embedding
openai_client = openai.OpenAI(api_key=secrets['OPENAI_API_KEY'])
res_emb = openai_client.embeddings.create(model='text-embedding-3-small', input=[query])
queryVector = res_emb.data[0].embedding

driver = GraphDatabase.driver(secrets['NEO4J_URI'], auth=(secrets['NEO4J_USERNAME'], secrets['NEO4J_PASSWORD']))

# 1. Vector Search
with driver.session() as session:
    res = session.run('''
        CALL db.index.vector.queryNodes('candidate_embedding', 200, $queryVector)
        YIELD node AS c, score
        RETURN c.id AS id, score
    ''', queryVector=queryVector)
    vector_results = {rec['id']: rec['score'] for rec in res}

print(f"[Trace] Target in vector_results? {target_id in vector_results} (Score: {vector_results.get(target_id)})")

# 2. Graph Match (Tower 2)
# Let's get the skills from the query (we skip LLM query parse and hardcode the target skills for simplicity or inspect what jd_compiler did)
# Since we know jd_compiler matched 345 IDs, let's query Neo4j for the target_id skills directly
with driver.session() as session:
    # Get target skills of candidate
    res_skills = session.run("MATCH (c:Candidate {id: $cid})-[r]->(s:Skill) RETURN s.name as skill, type(r) as action", cid=target_id)
    cand_edges = [{'skill': r['skill'], 'action': r['action']} for r in res_skills]
    print(f"[Trace] Candidate edges: {cand_edges}")

# 3. Read metadata from SQLite
conn = sqlite3.connect('candidates.db')
cur = conn.cursor()
cur.execute("SELECT id, name_kr, sector, total_years, is_duplicate FROM candidates WHERE id=?", (target_id,))
print(f"[Trace] SQLite Row: {cur.fetchone()}")

# Let's check if is_duplicate = 0 filter in the main loading block matches our ID
cur.execute("SELECT id FROM candidates WHERE is_duplicate=0")
active_ids = [r[0] for r in cur.fetchall()]
print(f"[Trace] Target in active_ids (is_duplicate=0)? {target_id in active_ids}")

# Wait, why was he not returned?
# Let's run api_search_v9 and print where target_id is.
# Let's print candidate details if they are in the returned list
from jd_compiler import api_search_v9
r = api_search_v9(query, seniority=seniority)
matched = r.get('matched', [])
print(f"[Trace] api_search_v9 matched count: {len(matched)}")
for i, c in enumerate(matched):
    if c.get('id') == target_id:
        print(f"  Found at rank {i+1}!")
        break
else:
    print("  Target NOT found in matched list.")

conn.close()
driver.close()
