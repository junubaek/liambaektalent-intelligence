import sqlite3
import json

conn = sqlite3.connect('candidates.db')
cur = conn.cursor()
cur.execute('SELECT name_kr, careers_json FROM candidates WHERE id = ?', ("55726c4a-4601-4ee9-87dc-581d15eda75e",))
row = cur.fetchone()
if row:
    print(f"Name: {row[0]}")
    data = json.loads(row[1]) if row[1] else []
    print(json.dumps(data, indent=2, ensure_ascii=False))
conn.close()
