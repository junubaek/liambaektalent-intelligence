import sqlite3, sys
sys.stdout.reconfigure(encoding='utf-8')
conn = sqlite3.connect('candidates.db')
cur = conn.cursor()
cur.execute('''SELECT id, name_kr, current_company, profile_summary, 
               is_duplicate, length(raw_text)
               FROM candidates WHERE name_kr = '이상헌'
               ORDER BY length(raw_text) DESC''')
rows = cur.fetchall()
print(f'이상헌 전체 레코드: {len(rows)}개')
for r in rows:
    summary = r[3] if r[3] else "없음"
    print(f'  {r[0][:8]}... | {r[2]} | dup:{r[4]} | raw:{r[5]}자')
    print(f'  summary: {summary[:80]}')
    print()
conn.close()
