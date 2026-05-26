import sqlite3, sys
sys.stdout.reconfigure(encoding='utf-8')
conn = sqlite3.connect('candidates.db')
cur = conn.cursor()

names = ['이범기','노장훈','이규원','하정근','이효성','김연아','김희원','권효상','김신애']
for name in names:
    cur.execute('''SELECT id, name_kr, current_company, sector, is_duplicate, length(raw_text) as rlen
                   FROM candidates WHERE name_kr = ?
                   ORDER BY is_duplicate, rlen DESC''', (name,))
    rows = cur.fetchall()
    print(f'[{name}] {len(rows)}개')
    for r in rows:
        print(f'  dup:{r[4]} | {r[2]} | {r[3]} | {r[5]}자 | {r[0][:8]}...')
    print()
conn.close()
