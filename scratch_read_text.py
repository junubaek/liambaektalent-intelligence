import sqlite3
conn = sqlite3.connect('candidates.db')
row = conn.execute('SELECT raw_text FROM candidates WHERE id = ?', ('33522567-1b6f-817e-a77b-ffc7e1b8d5d4',)).fetchone()
if row:
    print(row[0])
else:
    print("NOT FOUND")
conn.close()
