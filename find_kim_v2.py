import sqlite3
import json
import sys

# Set encoding to utf-8
sys.stdout.reconfigure(encoding='utf-8')

conn = sqlite3.connect('candidates.db')
cur = conn.cursor()
# Note: Column names are based on PRAGMA table_info output
cur.execute("SELECT id, name_kr, is_duplicate, is_pinecone_synced, is_neo4j_synced, current_company, total_years FROM candidates WHERE name_kr LIKE '%김은형%'")
rows = cur.fetchall()

for row in rows:
    print(f"ID: {row[0]}, Name: {row[1]}, Duplicate: {row[2]}, Pinecone: {row[3]}, Neo4j: {row[4]}, Company: {row[5]}, Total Years: {row[6]}")
conn.close()
