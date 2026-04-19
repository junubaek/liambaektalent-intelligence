import sqlite3
import re

conn = sqlite3.connect('candidates.db')
cursor = conn.cursor()
cursor.execute("SELECT id, name_kr, document_hash, substr(raw_text, 1, 50) FROM candidates LIMIT 10")
for row in cursor.fetchall():
    print(row)
conn.close()
