import sqlite3

conn = sqlite3.connect('candidates.db')
cur = conn.cursor()

cur.execute("SELECT id, name_kr FROM candidates WHERE id LIKE '3%' LIMIT 10")
rows = cur.fetchall()
print("Candidate IDs starting with 3:", len(rows))
for r in rows:
    print(f"  {r[0]} : {r[1]}")
    
conn.close()
