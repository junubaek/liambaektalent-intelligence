import json
import sqlite3
import sys
import math
from neo4j import GraphDatabase
import openai

sys.stdout.reconfigure(encoding='utf-8')

with open('secrets.json', encoding='utf-8') as f:
    secrets = json.load(f)

openai_client = openai.OpenAI(api_key=secrets['OPENAI_API_KEY'])
driver = GraphDatabase.driver(secrets['NEO4J_URI'], auth=(secrets['NEO4J_USERNAME'], secrets['NEO4J_PASSWORD']))

query = 'healthcare AI computer vision deep learning medical imaging'
target_id = '32022567-1b6f-819f-b62e-fa5ecb02e3de'
seniority = 'MIDDLE'

# Let's run a modified execution to see where target_id is
# We copy-paste the exact scoring loop of api_search_v9

# Get Vector IDs
res_emb = openai_client.embeddings.create(model='text-embedding-3-small', input=[query])
queryVector = res_emb.data[0].embedding

with driver.session() as session:
    res = session.run('''
        CALL db.index.vector.queryNodes('candidate_embedding', 200, $queryVector)
        YIELD node AS c, score
        RETURN c.id AS id, score
    ''', queryVector=queryVector)
    vector_results = {rec['id']: rec['score'] for rec in res}

# Load from SQLite
conn = sqlite3.connect('candidates.db')
cur = conn.cursor()
cur.execute("SELECT id, name_kr, total_years, sector FROM candidates WHERE is_duplicate=0")
sqlite_candidates = {r[0]: {'name_kr': r[1], 'total_years': r[2], 'sector': r[3]} for r in cur.fetchall()}

# Match IDs present in both SQLite and Vector Results
combined_ids = set(vector_results.keys()) & set(sqlite_candidates.keys())
print(f"Total combined IDs: {len(combined_ids)}")
print(f"Is target in combined_ids? {target_id in combined_ids}")

# Let's simulate the rest of api_search_v9 logic for target_id
if target_id in combined_ids:
    print("Target is in the combined candidate pool.")
else:
    print("Target is NOT in the combined candidate pool!")
    # Check why they don't intersect
    print(f"Target in vector_results? {target_id in vector_results}")
    print(f"Target in sqlite_candidates? {target_id in sqlite_candidates}")

conn.close()
driver.close()
