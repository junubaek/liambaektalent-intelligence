import sqlite3
conn = sqlite3.connect('candidates.db')
cur = conn.cursor()
name_query = '%김은형%'
cur.execute("SELECT id, name_kr, current_company, is_duplicate FROM candidates WHERE name_kr LIKE ?", (name_query,))
rows = cur.fetchall()
print("ID | Name | Company | Duplicate")
for row in rows:
    print(f"{row[0]} | {row[1]} | {row[2]} | {row[3]}")
conn.close()
