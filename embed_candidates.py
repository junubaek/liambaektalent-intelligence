import sqlite3
import json
import os
import sys
import time
from tqdm import tqdm
from neo4j import GraphDatabase
from openai import OpenAI

def setup_index():
    driver = GraphDatabase.driver("bolt://127.0.0.1:7687", auth=("neo4j", "toss1234"))
    with driver.session() as session:
        session.run("""
        CREATE VECTOR INDEX candidate_embedding IF NOT EXISTS
        FOR (c:Candidate) ON (c.embedding)
        OPTIONS {indexConfig: {
          `vector.dimensions`: 1536,
          `vector.similarity_function`: 'cosine'
        }}
        """)
    driver.close()

def main():
    if "--setup" in sys.argv:
        setup_index()
        print("Neo4j Vector Index Verified/Created.")
        return

    is_test = "--test" in sys.argv

    # Load API Key
    with open("secrets.json", "r", encoding="utf-8") as f:
        secrets = json.load(f)
    api_key = secrets.get("OPENAI_API_KEY")
    if not api_key:
        api_key = secrets.get("openai_api_key")
        
    client = OpenAI(api_key=api_key)
    
    # Load raw text
    conn = sqlite3.connect('candidates.db')
    c = conn.cursor()
    c.execute("SELECT name_kr, raw_text FROM candidates WHERE raw_text IS NOT NULL AND length(raw_text) > 10")
    rows = c.fetchall()
    conn.close()
    
    raw_text_map = {r[0]: r[1] for r in rows}
    
    driver = GraphDatabase.driver("bolt://127.0.0.1:7687", auth=("neo4j", "toss1234"))
    
    # Target candidates existing in Neo4j
    with driver.session() as session:
        # Skip those who already have embeddings
        res = session.run("MATCH (c:Candidate) WHERE c.embedding IS NULL RETURN c.name_kr AS name, c.id AS target_id")
        targets = []
        for r in res:
            name = r['name']
            if name in raw_text_map:
                targets.append((name, r['target_id']))
                
    if is_test:
        targets = targets[:10]
        print(f"Running TEST mode with 10 candidates.")
    else:
        print(f"Running FULL mode with {len(targets)} candidates.")
        
    batch_size = 100
    
    for i in tqdm(range(0, len(targets), batch_size)):
        batch = targets[i:i+batch_size]
        
        # We can pass an array of inputs to OpenAI
        texts_to_embed = []
        for name, _id in batch:
            text = raw_text_map[name]
            # Truncate to avoid max token errors (limit is 8192 tokens, roughly 12000 KR chars = safe)
            texts_to_embed.append(text[:3500])
            
        try:
            res = client.embeddings.create(input=texts_to_embed, model="text-embedding-3-small")
            embeddings = [data.embedding for data in res.data]
            
            with driver.session() as session:
                for (name, tid), emb in zip(batch, embeddings):
                    session.run("""
                        MATCH (c:Candidate {id: $id})
                        SET c.embedding = $emb
                    """, id=tid, emb=emb)
        except Exception as e:
            tqdm.write(f"Error on batch {i}: {e}")
            time.sleep(5)
            
    driver.close()
    print("Embedding done.")
    
if __name__ == '__main__':
    main()
