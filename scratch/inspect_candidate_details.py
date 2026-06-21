import sqlite3

conn = sqlite3.connect('candidates.db')
cur = conn.cursor()
cur.execute("SELECT name_kr, current_company, sector, profile_summary, raw_text FROM candidates WHERE id = 'ba99c86f-562d-4193-8380-0e414bd19093'")
row = cur.fetchone()
if row:
    print("이름:", row[0])
    print("회사:", row[1])
    print("세터:", row[2])
    print("요약:", row[3])
    print("이력서 본문 일부:")
    print(row[4][:600] if row[4] else "없음")
conn.close()
