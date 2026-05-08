import sqlite3
import json

conn = sqlite3.connect('candidates.db')
cur = conn.cursor()
cur.execute('SELECT name_kr, careers_json FROM candidates WHERE name_kr = ?', ("최우성",))
row = cur.fetchone()
if row:
    print(f"Name: {row[0]}")
    data = json.loads(row[1]) if row[1] else []
    print(json.dumps(data[:3], indent=2, ensure_ascii=False))
conn.close()
