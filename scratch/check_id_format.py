import sqlite3

conn = sqlite3.connect('candidates.db')
cur = conn.cursor()

names = ['김국현', '임서환', '이승용', '우형일', '황의영']
for name in names:
    cur.execute("SELECT id, name_kr, is_duplicate FROM candidates WHERE name_kr=? AND is_duplicate=0", (name,))
    row = cur.fetchone()
    if row:
        print(f"{row[1]}: ID={row[0]}")
    else:
        print(f"{name}: Not found in DB")
        
conn.close()
