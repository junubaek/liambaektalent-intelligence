import sqlite3
import json

conn = sqlite3.connect('candidates.db')
cur = conn.cursor()
cur.execute("SELECT id, name_kr, is_duplicate, is_pinecone_synced, is_neo4j_synced, current_company, 연차등급 FROM candidates WHERE name_kr LIKE '%김은형%'")
rows = cur.fetchall()

for row in rows:
    print(f"ID: {row[0]}, Name: {row[1]}, Duplicate: {row[2]}, Pinecone: {row[3]}, Neo4j: {row[4]}, Company: {row[5]}, Seniority: {row[6]}")
conn.close()
