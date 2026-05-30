import sqlite3
import sys

sys.stdout.reconfigure(encoding='utf-8')
DB_PATH = r"C:\Users\cazam\Downloads\이력서자동분석검색시스템\candidates.db"

conn = sqlite3.connect(DB_PATH)
c = conn.cursor()
names = ['황승현', '홍용기', '최현석', '최성우', '정태영', '전형준', '전예찬', '이석현', '송우석', '박지민', '김학주', '김정근', '김기덕']

print("--- Current Database State ---")
for name in names:
    c.execute("SELECT id, name_kr, sector, updated_at FROM candidates WHERE name_kr LIKE ?", (f"%{name}%",))
    rows = c.fetchall()
    for row in rows:
        print(f"{name} match: {row}")
conn.close()
