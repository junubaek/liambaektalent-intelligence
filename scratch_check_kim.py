import sqlite3, json
conn = sqlite3.connect('candidates.db')
conn.row_factory = sqlite3.Row
cur = conn.cursor()
cur.execute('''SELECT * FROM candidates WHERE name_kr LIKE '%김효민%' AND current_company LIKE '%당근마켓%' ''')
r = cur.fetchone()
if r:
    with open('scratch_kim.txt', 'w', encoding='utf-8') as f:
        for k, v in dict(r).items():
            f.write(f'{k}: {v}\n')
