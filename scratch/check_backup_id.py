import sqlite3

conn = sqlite3.connect('candidates_backup_20260526_1514.db')
cur = conn.cursor()

names = ['김국현', '이원철', '한상현']
for name in names:
    cur.execute("SELECT id, name_kr FROM candidates WHERE name_kr=?", (name,))
    for row in cur.fetchall():
        print(f"Backup [{name}]: ID={row[0]}")
        
conn.close()
