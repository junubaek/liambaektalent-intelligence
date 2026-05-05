import sqlite3
import json
import time
import sys
sys.stdout.reconfigure(encoding='utf-8')

from openai import OpenAI
from neo4j import GraphDatabase
from connectors.pinecone_api import PineconeClient

# Load secrets
with open("secrets.json", "r") as f:
    secrets = json.load(f)

openai_client = OpenAI(api_key=secrets.get("OPENAI_API_KEY", ""))
pc_host = secrets.get("PINECONE_HOST", "").rstrip("/")
if not pc_host.startswith("https://"):
    pc_host = f"https://{pc_host}"
pc = PineconeClient(secrets.get("PINECONE_API_KEY", ""), pc_host)

# Use REMOTE Neo4j from secrets
n_uri = secrets.get("NEO4J_URI")
n_user = secrets.get("NEO4J_USERNAME")
n_pw = secrets.get("NEO4J_PASSWORD")
driver = GraphDatabase.driver(n_uri, auth=(n_user, n_pw))

conn = sqlite3.connect("candidates.db")
cur = conn.cursor()

target_id = "f5875fc2-99aa-4605-9742-5ec93f4cd51a"
cur.execute("SELECT id, name_kr, raw_text, profile_summary, current_company, sector FROM candidates WHERE id = ?", (target_id,))
row = cur.fetchone()

if row:
    cid, name, raw_text, summary, current_company, sector = row
    print(f"Resyncing {name} ({cid}) to REMOTE Neo4j and Pinecone...")
    
    # Generate Embedding for Neo4j
    embed_text = raw_text if raw_text else summary
    main_emb = None
    if embed_text:
        res = openai_client.embeddings.create(input=[embed_text[:3500]], model="text-embedding-3-small")
        main_emb = res.data[0].embedding

    # 1. Neo4j (Remote)
    with driver.session() as session:
        # Update or Create candidate node
        session.run("""
            MERGE (c:Candidate {id: $cid})
            SET c.name_kr = $name,
                c.summary = $summary,
                c.current_company = $company,
                c.sector = $sector,
                c.embedding = $emb
        """, cid=str(cid), name=name, summary=summary or "", company=current_company or "", sector=sector or "미분류", emb=main_emb)
        
        # Also, we should ensure the skills are linked if they are missing on the remote side, 
        # but let's assume they exist for now or just focus on the vector search.
        
    print("Remote Neo4j updated (including embedding).")
    
    # 2. Pinecone
    try:
        pc.delete(filter_meta={"candidate_id": str(cid)}, namespace="resume_vectors")
    except:
        pass
    
    if embed_text:
        chunks = [embed_text[i:i+1000] for i in range(0, len(embed_text), 1000)]
        emb_res = openai_client.embeddings.create(model="text-embedding-3-small", input=chunks)
        vectors = []
        for idx, ed in enumerate(emb_res.data):
            vectors.append({
                "id": f"{cid}_chunk_{idx}",
                "values": ed.embedding,
                "metadata": {"candidate_id": str(cid), "chunk_index": idx}
            })
        pc.upsert(vectors, namespace="resume_vectors")
        print("Pinecone updated.")
    
    # 3. DB status
    cur.execute("UPDATE candidates SET is_pinecone_synced = 1, is_neo4j_synced = 1 WHERE id = ?", (cid,))
    conn.commit()
    print("Local DB status updated.")
else:
    print("Target ID not found in DB.")

conn.close()
driver.close()
