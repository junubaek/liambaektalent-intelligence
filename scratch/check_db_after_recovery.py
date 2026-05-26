import sqlite3, sys
sys.stdout.reconfigure(encoding='utf-8')
conn = sqlite3.connect('candidates.db')
cur = conn.cursor()

cur.execute('SELECT COUNT(*) FROM candidates')
print(f'전체: {cur.fetchone()[0]}명')

cur.execute('SELECT COUNT(*) FROM candidates WHERE is_duplicate=0')
print(f'마스터: {cur.fetchone()[0]}명')

cur.execute('SELECT COUNT(*) FROM candidates WHERE is_duplicate=0 AND raw_text IS NOT NULL AND length(raw_text) > 100')
print(f'이력서 있는 마스터: {cur.fetchone()[0]}명')

cur.execute('SELECT COUNT(*) FROM candidates WHERE is_duplicate=0 AND (raw_text IS NULL OR length(raw_text) < 100)')
print(f'이력서 없는 마스터(복구된 것): {cur.fetchone()[0]}명')

conn.close()
