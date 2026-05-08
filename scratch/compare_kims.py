import sqlite3, sys
sys.stdout.reconfigure(encoding='utf-8')
conn = sqlite3.connect('candidates.db')
cur = conn.cursor()
ids = ["32122567-1b6f-81be-9203-ee72cb56df2f", "8a8f2be2-8a1a-4acc-8a59-e006f3907697"]
cur.execute('SELECT id, name_kr, raw_text FROM candidates WHERE id IN (?, ?)', ids)
rows = cur.fetchall()
for r in rows:
    print(f'ID: {r[0]} | Name: {r[1]}')
    print(f'Content Sample: {r[2][:300]}...')
    print('-' * 80)
conn.close()
