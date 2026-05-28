import sqlite3

conn = sqlite3.connect('candidates.db')
cur = conn.cursor()

target_ids = [
    '32e22567-1b6f-8153-b866-c9af67643875', # Rank 1 (이원철)
    '31f22567-1b6f-81fb-934d-e602e80cd1da', # Rank 2 (김국현)
    '31f22567-1b6f-8179-b2ec-c7f047e6d362', # Rank 3 (임서환)
    '31f22567-1b6f-8121-a08f-d8610b5e1294', # Rank 4 (이승용)
    '32e22567-1b6f-81a0-b913-ed0db4db2934'  # Rank 5 (한상현)
]

for tid in target_ids:
    cur.execute("SELECT id, name_kr, is_duplicate, duplicate_of, sector, current_company FROM candidates WHERE id=?", (tid,))
    row = cur.fetchone()
    if row:
        print(f"ID={row[0]} | name={row[1]} | dup={row[2]} | dup_of={row[3]} | sector={row[4]} | company={row[5]}")
    else:
        print(f"ID={tid} : NOT FOUND in SQLite db")
        
conn.close()
