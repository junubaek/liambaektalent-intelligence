import sqlite3, sys
sys.stdout.reconfigure(encoding='utf-8')
conn = sqlite3.connect('candidates.db')
cur = conn.cursor()
cur.execute('''
    SELECT name_kr, current_title, current_company,
           sector, total_years, has_big_company, has_startup
    FROM candidates
    WHERE is_duplicate=0
    ORDER BY created_at DESC
    LIMIT 19
''')
for r in cur.fetchall():
    print(r)
conn.close()
