import sqlite3
import json
import sys
from incremental_ingest_v10 import build_embedding_text, secrets, openai_client, pinecone_client, chunk_text

# 1. Fetch 박천혁 details from SQLite
conn = sqlite3.connect('candidates.db')
cur = conn.cursor()
cur.execute('''
    SELECT name_kr, sector, current_company, profile_summary, raw_text 
    FROM candidates 
    WHERE id='3d322d13-0699-4453-b70e-5a4c2aac38f9'
''')
row = cur.fetchone()
conn.close()

if not row:
    print("Error: Candidate 박천혁 not found in SQLite.")
    sys.exit(1)

name_kr, sector, current_company, profile_summary, raw_text = row
print(f"Candidate found: {name_kr} @ {current_company}")

# 2. Build embedding text and upload to Pinecone
try:
    cand_dict = {
        "name_kr": name_kr,
        "sector": sector,
        "current_company": current_company,
        "profile_summary": profile_summary,
        "raw_text": raw_text
    }
    emb_text = build_embedding_text(cand_dict)
    chunks = chunk_text(emb_text)
    
    if chunks:
        print(f"Generating embeddings for {len(chunks)} chunks...")
        response = openai_client.embeddings.create(model="text-embedding-3-small", input=chunks)
        vectors = []
        c_id = '3d322d13-0699-4453-b70e-5a4c2aac38f9'
        for i, emb in enumerate(response.data):
            vectors.append({
                "id": f"{c_id}_chunk_{i}",
                "values": emb.embedding,
                "metadata": {"candidate_id": c_id, "chunk_index": i}
            })
        print(f"Upserting to Pinecone namespace resume_vectors...")
        pinecone_client.upsert(vectors, namespace="resume_vectors")
        print("박천혁 Pinecone 재업서트: True")
    else:
        print("Error: No chunks generated.")
except Exception as e:
    print(f"Error upserting to Pinecone: {e}")
