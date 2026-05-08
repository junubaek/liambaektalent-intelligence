import json
import os
import sys
import time
from openai import OpenAI
from neo4j import GraphDatabase

# Ensure project root is in path
sys.path.insert(0, os.getcwd())
from jd_compiler import _get_secret

# Ensure UTF-8 output
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

def refresh_embeddings():
    # 1. Setup
    secrets_path = 'secrets.json'
    with open(secrets_path, 'r', encoding='utf-8') as f:
        secrets = json.load(f)

    client = OpenAI(api_key=secrets.get("OPENAI_API_KEY"))
    driver = GraphDatabase.driver(secrets['NEO4J_URI'], auth=(secrets['NEO4J_USERNAME'], secrets['NEO4J_PASSWORD']))

    # 2. Get Candidates
    print("Fetching candidates from Neo4j...")
    with driver.session() as session:
        # Sort so that Choi (c3d4ee55-...) comes early or just fetch him specifically
        candidates = session.run("""
            MATCH (c:Candidate) 
            WHERE c.raw_text IS NOT NULL
            RETURN c.id as id, c.raw_text as text, c.name_kr as name
            ORDER BY CASE WHEN c.id = 'c3d4ee55-266a-44f6-8e66-fb7486be38a8' THEN 0 ELSE 1 END
        """).data()
    
    total = len(candidates)
    print(f"Total candidates to re-embed: {total}")

    # 3. Process ONE BY ONE for better debugging
    success_count = 0
    for i, c in enumerate(candidates):
        text = (c['text'] or "").strip()
        if not text:
            text = "Empty Resume"
        
        # Safe limit for tokens
        text = text[:10000]
        
        try:
            # Generate Embedding
            res = client.embeddings.create(input=[text], model="text-embedding-3-small")
            emb = res.data[0].embedding
            
            # Update Neo4j
            with driver.session() as session:
                session.run("MATCH (cand:Candidate {id: $id}) SET cand.embedding = $emb", id=c['id'], emb=emb)
            
            success_count += 1
            if i % 10 == 0 or c['id'] == 'c3d4ee55-266a-44f6-8e66-fb7486be38a8':
                print(f"[{i+1}/{total}] Success: {c['name']} ({c['id']})")
            
            # Respect rate limits for small Tier accounts
            time.sleep(0.02)
            
        except Exception as e:
            print(f"[{i+1}/{total}] Error for {c['name']} ({c['id']}): {e}")
            if "400" in str(e):
                # If it's a 400, maybe try an even shorter snippet
                try:
                    res = client.embeddings.create(input=[text[:1000]], model="text-embedding-3-small")
                    emb = res.data[0].embedding
                    with driver.session() as session:
                        session.run("MATCH (cand:Candidate {id: $id}) SET cand.embedding = $emb", id=c['id'], emb=emb)
                    print(f"  -> Fixed with shorter snippet (1000 chars)")
                except:
                    print(f"  -> Still failing even with 1000 chars.")
            time.sleep(0.5)

    driver.close()
    print("--- Neo4j Embedding Refresh Complete ---")

if __name__ == "__main__":
    refresh_embeddings()
