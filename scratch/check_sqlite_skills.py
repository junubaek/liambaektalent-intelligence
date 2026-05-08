import sqlite3
import json

conn = sqlite3.connect('candidates.db')
cur = conn.cursor()
names = ["이신형", "이상헌", "배유정", "김대중", "최우성"]

for name in names:
    cur.execute('SELECT id, name_kr, skills FROM candidates WHERE name_kr = ?', (name,))
    rows = cur.fetchall()
    print(f"Name: {name}")
    for r in rows:
        print(f"  - ID: {r[0]} | Skills: {r[2][:100]}...")

conn.close()
