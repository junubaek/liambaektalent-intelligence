import json
import sqlite3
import sys
import openai
from neo4j import GraphDatabase

sys.stdout.reconfigure(encoding='utf-8')

with open('secrets.json', encoding='utf-8') as f:
    secrets = json.load(f)

openai_client = openai.OpenAI(api_key=secrets['OPENAI_API_KEY'])
driver = GraphDatabase.driver(secrets['NEO4J_URI'], auth=(secrets['NEO4J_USERNAME'], secrets['NEO4J_PASSWORD']))

conn = sqlite3.connect('candidates.db')
cur = conn.cursor()

# We trace 김진영 for 'healthcare AI computer vision deep learning medical imaging'
query = 'healthcare AI computer vision deep learning medical imaging'
target_id = '32022567-1b6f-819f-b62e-fa5ecb02e3de'
seniority = 'MIDDLE'

print(f"--- Tracing Drop Reason for {target_id} (김진영) ---")

# Step 1: LLM Parsing Simulation
# Let's see what api_search_v9 extracts for this query
from jd_compiler import api_search_v9
r = api_search_v9(query, seniority=seniority)
# We won't run full api_search_v9, we will just print its behavior by analyzing step-by-step:

# Let's get Vector IDs
res_emb = openai_client.embeddings.create(model='text-embedding-3-small', input=[query])
q_vec = res_emb.data[0].embedding

with driver.session() as session:
    res = session.run('''
        CALL db.index.vector.queryNodes('candidate_embedding', 200, $queryVector)
        YIELD node AS c, score
        RETURN c.id AS id, score
    ''', queryVector=q_vec)
    vector_ids = [rec['id'] for rec in res]
    
print(f"1. Is in Vector Search Top 200? {target_id in vector_ids} (Rank: {vector_ids.index(target_id)+1 if target_id in vector_ids else 'None'})")

# Let's get Graph IDs
# We check which skills are extracted by LLM for this query. Let's see what jd_compiler.py extracts.
# Actually, let's just query Neo4j for candidates matching any target skills.
# But wait, does target candidate have is_duplicate = 0? Yes.
# Let's check if target_id exists in the candidates.db database with the correct columns.
cur.execute("SELECT id, name_kr, is_duplicate, total_years, sector FROM candidates WHERE id=?", (target_id,))
row = cur.fetchone()
print(f"2. SQLite Candidates Row: {row}")

# Let's trace how many candidates are loaded from SQLite in api_search_v9
# In api_search_v9:
# cursor.execute("SELECT id, name_kr, ... FROM candidates WHERE is_duplicate=0")
# Let's see if target_id is retrieved!
cur.execute("SELECT COUNT(*) FROM candidates WHERE id=? AND is_duplicate=0", (target_id,))
print(f"3. Active Candidate in SQLite (is_duplicate=0)? {cur.fetchone()[0] > 0}")

# Wait, let's print ALL candidates in api_search_v9 matched result list.
# Let's see if target_id is present in final_candidates before slicing!
# Wait! Let's write a python code that reads jd_compiler.py's api_search_v9 variables directly by executing a patched version that saves the local variables to a json file!
# That is a brilliant way to inspect the internal state!
# Let's edit jd_compiler.py temporarily to save variables right before returning, run the search, and read the json file!

driver.close()
conn.close()
