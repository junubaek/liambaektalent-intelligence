import sqlite3
import json
import os
import sys
from neo4j import GraphDatabase

# Ensure project root is in path
sys.path.insert(0, os.getcwd())
from jd_compiler import _get_secret

# Ensure UTF-8 output
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

def sync_metadata():
    # 1. Load Secrets
    secrets_path = 'secrets.json'
    with open(secrets_path, 'r', encoding='utf-8') as f:
        secrets = json.load(f)

    # 2. Connect
    conn = sqlite3.connect('candidates.db')
    cur = conn.cursor()
    driver = GraphDatabase.driver(secrets['NEO4J_URI'], auth=(secrets['NEO4J_USERNAME'], secrets['NEO4J_PASSWORD']))

    # 3. Fetch all from SQLite
    print("Fetching candidates from SQLite...")
    cur.execute("SELECT id, name_kr, current_company, program_position, raw_text FROM candidates WHERE is_duplicate = 0")
    candidates = cur.fetchall()
    total = len(candidates)
    print(f"Total candidates to sync: {total}")

    # 4. Sync in batches
    batch_size = 100
    for i in range(0, total, batch_size):
        batch = candidates[i:i+batch_size]
        
        with driver.session() as session:
            def tx_work(tx):
                for cid, name, company, position, raw_text in batch:
                    # Sync metadata including raw_text
                    tx.run("""
                        MERGE (c:Candidate {id: $id})
                        SET c.name_kr = $name,
                            c.company = $company,
                            c.position = $position,
                            c.raw_text = $raw_text
                    """, id=cid, name=name, company=company, position=position, raw_text=raw_text)
            
            try:
                session.execute_write(tx_work)
                print(f"Progress: {min(i + batch_size, total)}/{total} ({(min(i + batch_size, total))/total*100:.1f}%)")
            except Exception as e:
                print(f"Error in batch starting at {i}: {e}")

    conn.close()
    driver.close()
    print("--- Metadata Sync Complete ---")

if __name__ == "__main__":
    sync_metadata()
