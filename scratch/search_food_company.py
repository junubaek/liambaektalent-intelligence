import sqlite3
conn = sqlite3.connect('candidates.db')
cur = conn.cursor()
query = "SELECT id, name_kr, current_company FROM candidates WHERE current_company LIKE '%중독푸드%' OR raw_text LIKE '%중독푸드%'"
cur.execute(query)
rows = cur.fetchall()
print("[Candidates related to 중독푸드 in SQLite]")
for r in rows:
    print(f" - ID: {r[0]} | Name: {r[1]} | Company: {r[2]}")
conn.close()
