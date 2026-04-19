import sqlite3

conn = sqlite3.connect('candidates.db')
c = conn.cursor()
row = c.execute('SELECT raw_text FROM candidates WHERE name_kr="최호진"').fetchone()
if row and row[0]:
    text = row[0]
    idx = text.lower().find('openstack')
    if idx != -1:
        start = max(0, idx - 100)
        end = min(len(text), idx + 200)
        print("=== Context for OpenStack ===")
        print(text[start:end])
else:
    print("Not found")
conn.close()
