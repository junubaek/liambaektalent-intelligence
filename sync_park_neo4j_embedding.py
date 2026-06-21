import sqlite3
import json
from neo4j import GraphDatabase
from openai import OpenAI
from incremental_ingest_v10 import build_embedding_text

# Load secrets
with open("secrets.json", "r", encoding="utf-8") as f:
    secrets = json.load(f)

api_key = secrets.get("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

n_uri = secrets.get("NEO4J_URI", "neo4j://127.0.0.1:7687")
n_user = secrets.get("NEO4J_USERNAME", "neo4j")
n_pw = secrets.get("NEO4J_PASSWORD", "toss1234")

# 1. Fetch details from SQLite
conn = sqlite3.connect('candidates.db')
cur = conn.cursor()
cur.execute('''
    SELECT name_kr, sector, current_company, profile_summary, raw_text 
    FROM candidates 
    WHERE id='3d322d13-0699-4453-b70e-5a4c2aac38f9'
''')
row = cur.fetchone()
conn.close()

name_kr, sector, current_company, profile_summary, raw_text = row

# 2. Build embedding text
cand_dict = {
    "name_kr": name_kr,
    "sector": sector,
    "current_company": current_company,
    "profile_summary": profile_summary,
    "raw_text": raw_text
}
emb_text = build_embedding_text(cand_dict)

# Truncate text just like embed_candidates.py did
text_to_embed = emb_text[:3500]

# 3. Create embedding
print("Creating embedding via OpenAI...")
res = client.embeddings.create(input=[text_to_embed], model="text-embedding-3-small")
embedding = res.data[0].embedding

# 4. Set embedding in Neo4j
print("Updating c.embedding in Neo4j...")
driver = GraphDatabase.driver(n_uri, auth=(n_user, n_pw))
with driver.session() as session:
    session.run("""
        MATCH (c:Candidate {id: $id})
        SET c.embedding = $emb
    """, id='3d322d13-0699-4453-b70e-5a4c2aac38f9', emb=embedding)
driver.close()

print("Neo4j embedding updated successfully!")
