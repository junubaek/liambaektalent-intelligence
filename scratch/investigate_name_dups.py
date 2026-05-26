import sqlite3, sys
sys.stdout.reconfigure(encoding='utf-8')
conn = sqlite3.connect('candidates.db')
cur = conn.cursor()

# 같은 이름으로 마스터가 1명인데 다른 직군 레코드가 중복 처리된 경우
# → 이름별로 그룹핑해서 sector가 다른 중복 레코드 찾기
cur.execute('''
    SELECT name_kr, COUNT(*) as total,
           COUNT(CASE WHEN is_duplicate=0 THEN 1 END) as masters,
           COUNT(CASE WHEN is_duplicate=1 THEN 1 END) as dups
    FROM candidates
    WHERE name_kr IS NOT NULL AND name_kr != ""
    GROUP BY name_kr
    HAVING masters = 1 AND dups >= 2
    ORDER BY total DESC
    LIMIT 30
''')
rows = cur.fetchall()
print(f'마스터 1명인데 중복 2개 이상인 이름: {len(rows)}개')
print()
for name, total, masters, dups in rows:
    # 각 레코드의 sector 확인
    cur.execute('''SELECT current_company, sector, is_duplicate, length(raw_text)
                   FROM candidates WHERE name_kr = ?
                   ORDER BY is_duplicate, length(raw_text) DESC''', (name,))
    records = cur.fetchall()
    sectors = set(r[1] for r in records if r[1])
    print(f'[{name}] 총{total}개 | 섹터: {sectors}')
    for r in records:
        print(f'  dup:{r[2]} | {r[0]} | {r[1]} | {r[3]}자')
    print()

conn.close()
