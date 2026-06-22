import sqlite3
conn = sqlite3.connect('candidates.db')
cur = conn.cursor()
cur.execute('SELECT raw_text FROM candidates WHERE id="028449d0-5ae4-46cf-b403-20f23e1e5fab"')
row = cur.fetchone()
print('raw_text exists:', row is not None and row[0] is not None)
if row and row[0]:
    print('raw_text length:', len(row[0]))
    print('raw_text preview:', row[0][:200])
conn.close()
