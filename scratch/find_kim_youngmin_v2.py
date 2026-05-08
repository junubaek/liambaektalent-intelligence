import sqlite3, sys
sys.stdout.reconfigure(encoding='utf-8')
conn = sqlite3.connect('candidates.db')
cur = conn.cursor()
cur.execute('SELECT id, name_kr, current_company, program_position, profile_summary, raw_text FROM candidates WHERE name_kr = "김영민" AND is_duplicate = 0')
row = cur.fetchone()
if row:
    print(f'ID: {row[0]}')
    print(f'이름: {row[1]}')
    print(f'현직: {row[2]} / {row[3]}')
    print(f'요약: {row[4]}')
    print(f'본문(앞 500자): {row[5][:500] if row[5] else "없음"}')
else:
    cur.execute('SELECT id, name_kr, current_company FROM candidates WHERE name_kr = "김영민"')
    rows = cur.fetchall()
    if rows:
        print('Found following records for 김영민:')
        for r in rows:
            print(f'  ID:{r[0]} | Company: {r[1]}')
    else:
        print("Candidate 김영민 not found.")
conn.close()
