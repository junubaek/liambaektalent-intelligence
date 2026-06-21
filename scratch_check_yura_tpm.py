import json
import sqlite3
import numpy as np
from openai import OpenAI
from neo4j import GraphDatabase

with open('secrets.json', 'r', encoding='utf-8') as f:
    secrets = json.load(f)

# Connect to Neo4j
driver = GraphDatabase.driver(
    secrets['NEO4J_URI'],
    auth=(secrets['NEO4J_USERNAME'], secrets['NEO4J_PASSWORD'])
)

# Connect to SQLite
conn = sqlite3.connect('candidates.db')
conn.row_factory = sqlite3.Row
cur = conn.cursor()

# Get Yura details
cur.execute("SELECT id, name_kr, sector, profile_summary FROM candidates WHERE id = '79d1edd5-7001-4f71-bc2b-95de15b11101'")
yura_row = cur.fetchone()
print(f"Yura: {yura_row['name_kr']} ({yura_row['id'][:8]}) | Sector: {yura_row['sector']}")

# Calculate Vector similarity manually
oai = OpenAI(api_key=secrets['OPENAI_API_KEY'])
resp = oai.embeddings.create(model='text-embedding-3-small', input=['Technical Program Manager'])
q_vec = np.array(resp.data[0].embedding)

with driver.session() as s:
    yura_emb = s.run("MATCH (c:Candidate {id: $id}) RETURN c.embedding", id=yura_row['id']).single()[0]
    if yura_emb:
        sim = np.dot(q_vec, np.array(yura_emb))
        print("Vector similarity for Yura:", sim)
    else:
        print("Yura has no embedding in Neo4j!")

# Let's run a full search scoring and check where Yura ranks among ALL candidates
# mimicking search_pipeline.py or jd_compiler.py
import re
def tokenize(text):
    tokens = re.findall(r'[가-힣]{2,}|[a-zA-Z]{2,}|\d+', text or '')
    return [t.lower() for t in tokens]

import pickle
with open('bm25_index.pkl', 'rb') as f:
    bm25_data = pickle.load(f)
    bm25_index = bm25_data['bm25']

q_tokens = tokenize('Technical Program Manager')
print("Query tokens:", q_tokens)

# Fetch all candidates from Neo4j with embeddings
with driver.session() as s:
    res = s.run("MATCH (c:Candidate) WHERE c.embedding IS NOT NULL RETURN c.id as id, c.name_kr as name, c.embedding as embedding").data()

all_scores = []
for r in res:
    cid = r['id']
    cname = r['name']
    c_emb = r['embedding']
    
    # Sim
    v_score = np.dot(q_vec, np.array(c_emb)) if c_emb else 0.0
    bm_score = bm25_index.get_score(cid, q_tokens)
    
    # We combine them using typical weight: v_score * 0.6 + bm_score * 0.03 (approx)
    # Let's see the combined score
    combined = (v_score * 0.6) + (bm_score * 0.03)
    all_scores.append({
        'id': cid,
        'name': cname,
        'vector': v_score,
        'bm25': bm_score,
        'combined': combined
    })

# Sort
all_scores.sort(key=lambda x: -x['combined'])

print("\n=== Top 20 Candidates ===")
for rank, item in enumerate(all_scores[:20]):
    marker = " [TARGET]" if item['name'] == '안유리' else ""
    print(f"{rank+1}. {item['name']} ({item['id'][:8]}) - Vector: {item['vector']:.4f} | BM25: {item['bm25']:.4f} | Combined: {item['combined']:.4f}{marker}")

# Find Yura's rank
yura_rank = -1
for rank, item in enumerate(all_scores):
    if item['name'] == '안유리':
        yura_rank = rank + 1
        print(f"\n안유리 Rank: {yura_rank} | Vector: {item['vector']:.4f} | BM25: {item['bm25']:.4f} | Combined: {item['combined']:.4f}")
        break

conn.close()
driver.close()
