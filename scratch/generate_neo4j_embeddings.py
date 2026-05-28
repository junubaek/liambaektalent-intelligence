import sqlite3
import json
import time
import sys
from openai import OpenAI
from neo4j import GraphDatabase

def generate_embeddings():
    sys.stdout.reconfigure(encoding='utf-8')
    
    # 1. Connect to SQLite to read candidate details
    print("Reading candidates from SQLite candidates.db...")
    conn = sqlite3.connect('candidates.db')
    cur = conn.cursor()
    cur.execute('''
        SELECT id, name_kr, sector, profile_summary
        FROM candidates
        WHERE is_duplicate=0
    ''')
    rows = cur.fetchall()
    conn.close()
    print(f"Total candidates in SQLite: {len(rows)}")
    
    # 2. Connect to Neo4j Aura to check who is missing embeddings
    print("Connecting to Neo4j Aura...")
    with open('secrets.json', 'r', encoding='utf-8') as f:
        secrets = json.load(f)
        
    driver = GraphDatabase.driver(
        secrets['NEO4J_URI'],
        auth=(secrets['NEO4J_USERNAME'], secrets['NEO4J_PASSWORD'])
    )
    
    with driver.session() as session:
        res = session.run("MATCH (c:Candidate) WHERE c.embedding IS NOT NULL RETURN c.id")
        existing_embedding_ids = {str(r[0]) for r in res}
        
    print(f"Candidates with existing embeddings in Neo4j Aura: {len(existing_embedding_ids)}")
    
    # Filter candidates that need embeddings
    to_generate = []
    for r in rows:
        cid = str(r[0])
        if cid not in existing_embedding_ids:
            to_generate.append({
                'id': cid,
                'name_kr': r[1] or "",
                'sector': r[2] or "미분류",
                'profile_summary': r[3] or "정보 없음"
            })
            
    print(f"Candidates needing new embeddings: {len(to_generate)}")
    
    if not to_generate:
        print("All candidates already have embeddings in Neo4j Aura!")
        driver.close()
        return
        
    # Initialize OpenAI Client
    client = OpenAI(api_key=secrets["OPENAI_API_KEY"])
    
    # Generate and sync in batches of 50
    batch_size = 50
    synced_count = 0
    
    query = """
    UNWIND $batch AS row
    MATCH (c:Candidate {id: row.id})
    SET c.embedding = row.embedding
    """
    
    with driver.session() as session:
        for i in range(0, len(to_generate), batch_size):
            batch = to_generate[i:i+batch_size]
            
            # Prepare inputs for OpenAI API
            inputs = []
            for item in batch:
                text = f"Candidate: {item['name_kr']}\nSector: {item['sector']}\nSummary: {item['profile_summary']}"
                inputs.append(text)
                
            try:
                # Call OpenAI Embedding API (text-embedding-3-small)
                emb_res = client.embeddings.create(input=inputs, model="text-embedding-3-small")
                
                # Zip vectors with candidate IDs
                update_batch = []
                for idx, item in enumerate(batch):
                    update_batch.append({
                        'id': item['id'],
                        'embedding': emb_res.data[idx].embedding
                    })
                    
                # Sync to Neo4j Aura
                session.run(query, batch=update_batch)
                synced_count += len(batch)
                print(f"  Generated & Synced {synced_count}/{len(to_generate)} embeddings...")
                
                # Graceful delay to respect rate limits
                time.sleep(0.5)
                
            except Exception as e:
                print(f"  Error processing batch {i//batch_size + 1}: {e}")
                
    driver.close()
    print(f"\nSuccessfully generated and synchronized {synced_count} candidate embeddings to Neo4j Aura!")

if __name__ == "__main__":
    generate_embeddings()
