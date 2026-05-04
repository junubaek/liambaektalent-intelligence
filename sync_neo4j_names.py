
import json
import sqlite3
import sys
from neo4j import GraphDatabase

# Set output encoding to utf-8
sys.stdout.reconfigure(encoding='utf-8')

def sync_neo4j_names():
    # 1. Load Secrets
    with open('secrets.json', 'r', encoding='utf-8') as f:
        secrets = json.load(f)
    
    driver = GraphDatabase.driver(
        secrets['NEO4J_URI'],
        auth=(secrets['NEO4J_USERNAME'], secrets['NEO4J_PASSWORD'])
    )
    
    # 2. Get Data from SQLite
    db_path = r'c:\Users\cazam\Downloads\이력서자동분석검색시스템\candidates.db'
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    
    cur.execute('SELECT id, name_kr, current_company, total_years FROM candidates')
    sqlite_candidates = cur.fetchall()
    print(f"SQLite candidates count: {len(sqlite_candidates)}")
    
    # 3. Sync to Neo4j
    with driver.session() as session:
        print("Syncing candidates to Neo4j...")
        
        # Unwind batch for speed
        batch_params = []
        sqlite_ids = set()
        for row in sqlite_candidates:
            batch_params.append({
                'id': row['id'],
                'name_kr': row['name_kr'],
                'current_company': row['current_company'],
                'total_years': row['total_years']
            })
            sqlite_ids.add(row['id'])
            
        # Batch MERGE
        BATCH_SIZE = 500
        for i in range(0, len(batch_params), BATCH_SIZE):
            batch = batch_params[i:i+BATCH_SIZE]
            session.run('''
                UNWIND $batch as item
                MERGE (c:Candidate {id: item.id})
                SET c.name_kr = item.name_kr,
                    c.name = item.name_kr,
                    c.current_company = item.current_company,
                    c.total_years = item.total_years
            ''', batch=batch)
            print(f"  Progress: {min(i+BATCH_SIZE, len(batch_params))}/{len(batch_params)}")
            
        # 4. Cleanup deleted candidates from Neo4j
        print("Cleaning up deleted candidates from Neo4j...")
        # Get all Neo4j candidate IDs
        res = session.run("MATCH (c:Candidate) RETURN c.id as id")
        neo4j_ids = [r['id'] for r in res]
        
        to_delete = [nid for nid in neo4j_ids if nid not in sqlite_ids]
        if to_delete:
            print(f"  Deleting {len(to_delete)} candidates from Neo4j...")
            session.run('''
                MATCH (c:Candidate)
                WHERE c.id IN $ids
                DETACH DELETE c
            ''', ids=to_delete)
        else:
            print("  No candidates to delete from Neo4j.")
            
    conn.close()
    driver.close()
    print("Neo4j Name & Structure Sync Complete.")

if __name__ == "__main__":
    sync_neo4j_names()
