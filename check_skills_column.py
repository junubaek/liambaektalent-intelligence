import sqlite3, sys, codecs
sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer)
conn = sqlite3.connect('candidates.db')
cur = conn.cursor()

cur.execute('PRAGMA table_info(candidates)')
cols = [r[1] for r in cur.fetchall()]
print('Columns:', cols)

skill_cols = [c for c in cols if 'skill' in c.lower()]
print('Skill-related columns:', skill_cols)

if skill_cols:
    col = skill_cols[0]
    cur.execute(f'SELECT id, name_kr, {col} FROM candidates WHERE is_duplicate=0 AND {col} IS NOT NULL AND {col} != \"\" LIMIT 3')
    for r in cur.fetchall():
        print(r[0][:8], r[1], '|', str(r[2])[:200])

conn.close()
