import os
import sqlite3
import json
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from neo4j import GraphDatabase
from connectors.openai_api import OpenAIClient

def load_secrets():
    with open("secrets.json", "r", encoding="utf-8") as f:
        return json.load(f)

def fetch_candidates_from_sqlite():
    conn = sqlite3.connect("candidates.db")
    c = conn.cursor()
    # Fetch id/hash, name, and raw_text
    # Neo4j Candidate nodes use exactly what logic for ID matching? 
    # Usually they use `name_kr` or the hash as ID, wait... 
    # Let me check how dynamic_parser_v2.py maps them. 
    # Actually, dynamic_parser_v2.py uses `document_hash` as ID, but the SQLite might use name.
    # Let's fetch all. We can match Neo4j by `name` or `name_kr` to be safe if ID differs.
    c.execute("SELECT name_kr, document_hash, raw_text FROM candidates WHERE raw_text IS NOT NULL AND LENGTH(TRIM(raw_text)) > 50")
    rows = c.fetchall()
    conn.close()
    return [{"name_kr": r[0], "hash": r[1], "text": r[2]} for r in rows]

def run_migration():
    secrets = load_secrets()
    openai_client = OpenAIClient(secrets["OPENAI_API_KEY"])
    driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "toss1234"))
    
    candidates = fetch_candidates_from_sqlite()
    print(f"Loaded {len(candidates)} valid candidates from SQLite.")
    
    # Check how many are in Neo4j
    with driver.session() as session:
        res = session.run("MATCH (c:Candidate) RETURN c.name_kr AS name_kr")
        neo4j_names = {r["name_kr"] for r in res}
        
    print(f"Neo4j contains {len(neo4j_names)} Candidate nodes.")
    
    # Filter candidates to those existing in Neo4j
    valid_cands = [c for c in candidates if c["name_kr"] in neo4j_names]
    print(f"Will migrate embeddings for {len(valid_cands)} overlapping candidates.")
    
    def process_candidate(cand):
        text = cand["text"]
        if len(text) > 20000: text = text[:20000] # Safe limit
        vec = openai_client.embed_content(text)
        if vec:
            with driver.session() as session:
                session.run("MATCH (c:Candidate {name_kr: $name}) SET c.embedding = $vec", 
                            name=cand["name_kr"], vec=vec)
            return True
        return False

    success = 0
    start_t = time.time()
    
    # Using ThreadPool to accelerate API requests
    with ThreadPoolExecutor(max_workers=20) as executor:
        futures = {executor.submit(process_candidate, c): c for c in valid_cands}
        for i, future in enumerate(as_completed(futures)):
            if future.result():
                success += 1
            if (i + 1) % 100 == 0:
                print(f"Progress: {i+1}/{len(valid_cands)} (Success: {success})")
                
    driver.close()
    print(f"Migration completed in {time.time() - start_t:.1f}s. Indexed {success}/{len(valid_cands)}.")

if __name__ == "__main__":
    run_migration()
