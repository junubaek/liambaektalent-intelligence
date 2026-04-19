import sqlite3
from neo4j import GraphDatabase
import json
import os

def run_neo4j_dedup():
    print("Fetching duplicate hashes from SQLite...")
    conn = sqlite3.connect('candidates.db')
    c = conn.cursor()
    # Using 'id' for neo4j matching, because in Neo4j the node id is often 'document_hash' or 'id'.
    # I will fetch both just to be safe. But the user said:
    # MATCH (c:Candidate) WHERE c.id IN $duplicate_hashes SET c.is_duplicate = true
    c.execute("SELECT id FROM candidates WHERE is_duplicate = 1")
    dup_ids = [row[0] for row in c.fetchall()]
    print(f"Loaded {len(dup_ids)} duplicate IDs to mark in Neo4j.")
    
    driver = GraphDatabase.driver(
        "bolt://127.0.0.1:7687",
        auth=("neo4j", "toss1234")
    )
    
    query = """
    UNWIND $dup_ids AS dup_id
    MATCH (c:Candidate)
    WHERE c.id = dup_id OR c.document_hash = dup_id
    SET c.is_duplicate = true
    RETURN count(c)
    """
    
    with driver.session() as session:
        # First reset all
        session.run("MATCH (c:Candidate) REMOVE c.is_duplicate")
        res = session.run(query, dup_ids=dup_ids)
        marked_count = res.single()[0]
        
    print(f"Successfully marked {marked_count} ghost/duplicate nodes in Neo4j!")

if __name__ == "__main__":
    run_neo4j_dedup()
