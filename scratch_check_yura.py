import sys
import os
import sqlite3
from neo4j import GraphDatabase

sys.stdout.reconfigure(encoding='utf-8')
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT_DIR)

from jd_compiler import api_search_v9

db_path = "candidates.db"
conn = sqlite3.connect(db_path)
cur = conn.cursor()

# Get Yura details
cur.execute("SELECT id, name_kr, sector, profile_summary, raw_text FROM candidates WHERE name_kr = '안유리'")
yura = cur.fetchone()
print("=== SQLite Yura ===")
print("ID:", yura[0])
print("Sector:", yura[1])
print("Summary:", yura[2])

# Check Neo4j nodes
with open('secrets.json', 'r', encoding='utf-8') as f:
    secrets = json.load(f) if 'json' in sys.modules else __import__('json').load(f)

driver = GraphDatabase.driver(secrets['NEO4J_URI'], auth=(secrets['NEO4J_USERNAME'], secrets['NEO4J_PASSWORD']))
with driver.session() as s:
    res = s.run("MATCH (c:Candidate {id: '79d1edd5-7001-4f71-bc2b-95de15b11101'}) RETURN c.name_kr as name, c.embedding IS NOT NULL as has_emb").single()
    print("\n=== Neo4j Yura ===")
    print("Name:", res['name'] if res else "NOT FOUND")
    print("Has Embedding:", res['has_emb'] if res else "N/A")

# Let's inspect BM25 and Vector scores for Yura manually inside search logic
# Or we can see all scores of Yura inside api_search_v9.
# Let's print candidate's detailed scores from matching logic.
# We can check by running a customized search loop just for Yura.
from jd_compiler import bm25_index, ontology_vectors, candidate_sector_map

print("\n=== Scoring Analysis ===")
# Vector similarity
import numpy as np
from openai import OpenAI
oai = OpenAI(api_key=secrets['OPENAI_API_KEY'])
resp = oai.embeddings.create(model='text-embedding-3-small', input=['Technical Program Manager'])
q_vec = np.array(resp.data[0].embedding)

with driver.session() as s:
    y_emb = s.run("MATCH (c:Candidate {id: '79d1edd5-7001-4f71-bc2b-95de15b11101'}) RETURN c.embedding").single()[0]
    if y_emb:
        sim = np.dot(q_vec, np.array(y_emb))
        print("Vector Cosine Similarity:", sim)

# BM25
from jd_compiler import clean_korean_text
q_tokens = clean_korean_text('Technical Program Manager').split()
print("Tokens:", q_tokens)
bm25_score = bm25_index.get_score('79d1edd5-7001-4f71-bc2b-95de15b11101', q_tokens)
print("BM25 Score:", bm25_score)

# Graph Tower Matched skills
print("Yura matched skills in Neo4j:")
with driver.session() as s:
    res = s.run("MATCH (c:Candidate {id: '79d1edd5-7001-4f71-bc2b-95de15b11101'})-[r]->(sk:Skill) RETURN sk.name, type(r)")
    for r in res:
        print(f"  Skill: {r['sk.name']} ({r['type(r)']})")

conn.close()
driver.close()
