import sqlite3
conn = sqlite3.connect('candidates.db')
cur = conn.cursor()
cur.execute('PRAGMA table_info(candidates)')
cols = [r[1] for r in cur.fetchall()]
print('Columns:', cols)
conn.close()
