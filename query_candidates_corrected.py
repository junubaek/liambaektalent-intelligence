import sqlite3

# DB 경로
DB_PATH = r'C:\\Users\\cazam\\Downloads\\이력서자동분석검색시스템\\candidates.db'

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

check = [
    ('신동주',), ('손태희',), ('김동민',), ('이상헌',), ('장수빈',), ('이영도',)
]

for (name,) in check:
    cur.execute('''
        SELECT id, name_kr, current_title, sector
        FROM candidates WHERE name_kr = ? AND is_duplicate = 0
    ''', (name,))
    for r in cur.fetchall():
        # sector is a string; no companies column in this schema
        print(f"{r[1]} | {r[0]} | {r[2]} | {r[3]}")

conn.close()
