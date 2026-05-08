import json, sqlite3, sys
from neo4j import GraphDatabase
sys.stdout.reconfigure(encoding='utf-8')

secrets = json.load(open('secrets.json'))
driver = GraphDatabase.driver(secrets['NEO4J_URI'], auth=(secrets['NEO4J_USERNAME'], secrets['NEO4J_PASSWORD']))
session = driver.session()

# 1. Check stats
stats = session.run('''
    MATCH (c:Candidate)
    RETURN
        count(c) as total,
        sum(CASE WHEN c.summary IS NULL OR c.summary = "" THEN 1 ELSE 0 END) as no_summary,
        sum(CASE WHEN c.summary IS NOT NULL AND c.summary <> "" THEN 1 ELSE 0 END) as has_summary
''').single()
print(f'Total Candidates in Neo4j: {stats["total"]}')
print(f'Has Summary: {stats["has_summary"]}')
print(f'No Summary: {stats["no_summary"]}')

if stats["no_summary"] > 0:
    print("\nStarting batch update from SQLite to Neo4j...")
    
    conn = sqlite3.connect('candidates.db')
    cur = conn.cursor()
    cur.execute('SELECT id, profile_summary FROM candidates WHERE is_duplicate = 0 AND profile_summary IS NOT NULL AND profile_summary != ""')
    rows = cur.fetchall()
    conn.close()
    
    print(f"Found {len(rows)} master candidates with summaries in SQLite.")
    
    # Batch update
    batch_size = 100
    for i in range(0, len(rows), batch_size):
        batch = rows[i:i+batch_size]
        session.run('''
            UNWIND $batch as row
            MATCH (c:Candidate {id: row[0]})
            SET c.summary = row[1]
        ''', batch=batch)
        print(f"  Updated {i + len(batch)} / {len(rows)}...")

    print("Batch update completed.")

driver.close()
