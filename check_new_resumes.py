import sqlite3, sys, codecs
sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer)
conn = sqlite3.connect('candidates.db')
cur = conn.cursor()

names = ['한경환','김지은','신동주','김대식','이호석','김예지','김일수',
         '오수영','김율','장성해','고대웅','권효상','홍전일','김용석','김진호','이겨례']

for name in names:
    cur.execute("""
        SELECT id, name_kr, current_title, current_company, sector
        FROM candidates WHERE name_kr=? AND is_duplicate=0
    """, (name,))
    rows = cur.fetchall()
    if rows:
        for r in rows:
            print(f"✅ {r[1]} | {r[0][:8]} | {r[2]} | {r[3]} | {r[4]}")
    else:
        print(f"❌ NOT FOUND: {name}")
conn.close()
