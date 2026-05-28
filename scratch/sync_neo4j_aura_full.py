import sqlite3
import sys
import json
import time
from neo4j import GraphDatabase

def sync_full_neo4j():
    sys.stdout.reconfigure(encoding='utf-8')
    
    # 1. Read SQLite candidates
    print("Reading master candidates from candidates.db...")
    conn = sqlite3.connect('candidates.db')
    cur = conn.cursor()
    cur.execute('''SELECT id, name_kr, email, phone, birth_year, total_years, 
                          sector, profile_summary, current_company, google_drive_url, source_file
                   FROM candidates 
                   WHERE is_duplicate=0''')
    rows = cur.fetchall()
    conn.close()
    
    total_candidates = len(rows)
    print(f"Total Master Candidates to sync: {total_candidates}")
    
    # 2. Connect to Neo4j Aura
    print("Connecting to Neo4j Aura...")
    with open('secrets.json', 'r', encoding='utf-8') as f:
        secrets = json.load(f)
        
    driver = GraphDatabase.driver(
        secrets['NEO4J_URI'],
        auth=(secrets['NEO4J_USERNAME'], secrets['NEO4J_PASSWORD'])
    )
    
    # Prepare batch sync
    batch_size = 100
    batch = []
    synced_count = 0
    start_time = time.time()
    
    query = """
    UNWIND $batch AS row
    MERGE (c:Candidate {id: row.id})
    SET c.name = row.name_kr,
        c.name_kr = row.name_kr,
        c.email = row.email,
        c.phone = row.phone,
        c.birth_year = row.birth_year,
        c.total_years = row.total_years,
        c.sector = row.sector,
        c.summary = row.profile_summary,
        c.profile_summary = row.profile_summary,
        c.current_company = row.current_company,
        c.google_drive_url = row.google_drive_url,
        c.source_file = row.source_file,
        c.last_synced_at = datetime()
    """
    
    with driver.session() as session:
        for r in rows:
            # Map Row to dict, handling None values gracefully
            batch.append({
                'id': r[0],
                'name_kr': r[1] or "",
                'email': r[2] or "",
                'phone': r[3] or "",
                'birth_year': int(r[4]) if r[4] is not None and str(r[4]).isdigit() else None,
                'total_years': float(r[5]) if r[5] is not None else None,
                'sector': r[6] or "미분류",
                'profile_summary': r[7] or "정보 없음",
                'current_company': r[8] or "",
                'google_drive_url': r[9] or "",
                'source_file': r[10] or ""
            })
            
            if len(batch) >= batch_size:
                session.run(query, batch=batch)
                synced_count += len(batch)
                print(f"  Synced {synced_count}/{total_candidates} candidates...")
                batch = []
                
        # Sync remaining
        if batch:
            session.run(query, batch=batch)
            synced_count += len(batch)
            print(f"  Synced {synced_count}/{total_candidates} candidates...")
            
    driver.close()
    elapsed = time.time() - start_time
    print(f"\nSuccessfully synchronized {synced_count} candidates to Neo4j Aura in {elapsed:.2f} seconds!")

if __name__ == "__main__":
    sync_full_neo4j()
