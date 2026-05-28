import sqlite3
import json
from neo4j import GraphDatabase

def purge_orphans():
    # 1. Get all valid SQLite master IDs
    conn = sqlite3.connect('candidates.db')
    cur = conn.cursor()
    cur.execute("SELECT id FROM candidates WHERE is_duplicate=0")
    valid_ids = {str(row[0]) for row in cur.fetchall()}
    conn.close()
    
    print(f"Total valid master candidate IDs in SQLite: {len(valid_ids)}")
    
    # 2. Connect to Neo4j
    with open('secrets.json', 'r', encoding='utf-8') as f:
        secrets = json.load(f)
        
    driver = GraphDatabase.driver(
        secrets['NEO4J_URI'],
        auth=(secrets['NEO4J_USERNAME'], secrets['NEO4J_PASSWORD'])
    )
    
    # Query all Candidate IDs in Neo4j Aura
    with driver.session() as session:
        print("Querying all candidates in Neo4j Aura...")
        res = session.run("MATCH (c:Candidate) RETURN c.id, c.name")
        neo_candidates = [(str(r[0]), r[1]) for r in res]
        
        print(f"Total candidates found in Neo4j Aura: {len(neo_candidates)}")
        
        orphans = []
        for cid, name in neo_candidates:
            if cid not in valid_ids:
                orphans.append((cid, name))
                
        print(f"Found {len(orphans)} orphaned Candidate nodes in Neo4j Aura that are not in SQLite valid master list!")
        
        if not orphans:
            print("No orphaned nodes to delete.")
            driver.close()
            return
            
        # Let's show some samples
        print("Some orphaned samples (first 10):")
        for o in orphans[:10]:
            print(f"  ID: {o[0]} | name: {o[1]}")
            
        # Purge orphans in batches
        print("\nDeleting orphaned nodes and their relationships from Neo4j Aura...")
        batch_size = 100
        for i in range(0, len(orphans), batch_size):
            batch_ids = [o[0] for o in orphans[i:i+batch_size]]
            session.run("""
                MATCH (c:Candidate)
                WHERE c.id IN $ids
                DETACH DELETE c
            """, ids=batch_ids)
            print(f"  Deleted {i + len(batch_ids)}/{len(orphans)} orphans...")
            
    driver.close()
    print("Purge completed successfully! All orphaned Neo4j Aura Candidate nodes have been deleted!")

if __name__ == "__main__":
    purge_orphans()
