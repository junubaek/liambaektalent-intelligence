import sqlite3
import json

conn = sqlite3.connect('candidates.db')
cur = conn.cursor()
targets = ["백승민", "정윤오", "정호진", "이신형"]

for name in targets:
    cur.execute('SELECT id, name_kr, is_neo4j_synced FROM candidates WHERE name_kr = ?', (name,))
    row = cur.fetchone()
    if row:
        print(f"Name: {row[1]} | ID: {row[0]} | Synced: {row[2]}")
    else:
        print(f"Name: {name} | NOT FOUND in SQLite")
conn.close()
