import sqlite3
import json

conn = sqlite3.connect('candidates.db')
cursor = conn.cursor()

# Get the first 5 records with name 김대용
cursor.execute("SELECT id, name_kr, document_hash, phone FROM candidates WHERE name_kr IN ('김대용', '김용') LIMIT 5")
print("SQLite Top 5 Matches for 김대용/김용:")
for r in cursor.fetchall():
    print(r)

# See what other names are there
cursor.execute("SELECT name_kr, count(*) FROM candidates GROUP BY name_kr ORDER BY count(*) DESC LIMIT 5")
print("\nTop 5 Most Frequent Names in SQLite:")
for r in cursor.fetchall():
    print(r)

conn.close()
