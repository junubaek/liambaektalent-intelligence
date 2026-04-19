import sqlite3
import os

db_uri = f"file:candidates.db?mode=ro"
conn = sqlite3.connect(db_uri, uri=True)
cur = conn.cursor()
rows = cur.execute('SELECT count(*), is_parsed, is_neo4j_synced, is_pinecone_synced FROM candidates GROUP BY is_parsed, is_neo4j_synced, is_pinecone_synced').fetchall()
print("ROWS:")
for r in rows:
    print(r)
