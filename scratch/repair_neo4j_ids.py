import sqlite3
import json
from neo4j import GraphDatabase
import sys

# Ensure UTF-8 output
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

with open('secrets.json', 'r', encoding='utf-8') as f:
    secrets = json.load(f)

driver = GraphDatabase.driver(secrets['NEO4J_URI'], auth=(secrets['NEO4J_USERNAME'], secrets['NEO4J_PASSWORD']))

conn = sqlite3.connect('candidates.db')
cur = conn.cursor()
cur.execute("SELECT id, name_kr FROM candidates")
rows = cur.fetchall()
conn.close()

print(f"Repairing {len(rows)} candidates in Neo4j...")

with driver.session() as session:
    # Batch update for speed
    batch_size = 100
    for i in range(0, len(rows), batch_size):
        batch = rows[i:i+batch_size]
        session.run("""
            UNWIND $batch AS item
            MERGE (c:Candidate {name_kr: item[1]})
            SET c.id = item[0]
        """, batch=batch)
        print(f"Progress: {i+len(batch)}/{len(rows)}")

print("Neo4j ID Repair Complete!")
driver.close()
