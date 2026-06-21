import json
import sqlite3
import numpy as np
import pickle
import re
from openai import OpenAI
from neo4j import GraphDatabase

with open('secrets.json', 'r', encoding='utf-8') as f:
    secrets = json.load(f)

# Connect to Neo4j
driver = GraphDatabase.driver(
    secrets['NEO4J_URI'],
    auth=(secrets['NEO4J_USERNAME'], secrets['NEO4J_PASSWORD'])
)

def tokenize(text):
    tokens = re.findall(r'[가-힣]{2,}|[a-zA-Z]{2,}|\d+', text or '')
    return [t.lower() for t in tokens]

with open('bm25_index.pkl', 'rb') as f:
    bm25_data = pickle.load(f)
    bm25_index = bm25_data['bm25']
    ids = bm25_data['ids']

oai = OpenAI(api_key=secrets['OPENAI_API_KEY'])
resp = oai.embeddings.create(model='text-embedding-3-small', input=['Technical Program Manager'])
q_vec = np.array(resp.data[0].embedding)

with driver.session() as s:
    res = s.run("MATCH (c:Candidate) WHERE c.embedding IS NOT NULL RETURN c.id as id, c.name_kr as name, c.embedding as embedding").data()

q_tokens = tokenize('Technical Program Manager')

all_scores = []
for r in res:
    cid = r['id']
    cname = r['name']
    c_emb = r['embedding']
    
    v_score = np.dot(q_vec, np.array(c_emb)) if c_emb else 0.0
    
    bm_score = 0.0
    if cid in ids:
        bm_score = bm25_index.get_scores(q_tokens)[ids.index(cid)]
        
    combined = (v_score * 0.6) + (bm_score * 0.03)
    all_scores.append({
        'id': cid,
        'name': cname,
        'vector': v_score,
        'bm25': bm_score,
        'combined': combined
    })

all_scores.sort(key=lambda x: -x['combined'])

print("=== Top 30 for TPM ===")
for rank, item in enumerate(all_scores[:30]):
    marker = " [TARGET]" if item['name'] == '안유리' else ""
    print(f"{rank+1}. {item['name']} ({item['id'][:8]}) - Vector: {item['vector']:.4f} | BM25: {item['bm25']:.4f} | Combined: {item['combined']:.4f}{marker}")

# Find Yura's rank
yura_rank = -1
for rank, item in enumerate(all_scores):
    if item['name'] == '안유리':
        yura_rank = rank + 1
        print(f"\n안유리 Rank: {yura_rank} | Vector: {item['vector']:.4f} | BM25: {item['bm25']:.4f} | Combined: {item['combined']:.4f}")
        break

driver.close()
