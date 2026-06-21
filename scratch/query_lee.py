import sqlite3
import sys
sys.stdout.reconfigure(encoding='utf-8')

db_path = r"C:\Users\cazam\Downloads\이력서자동분석검색시스템\candidates.db"
conn = sqlite3.connect(db_path)
cur = conn.cursor()

cur.execute("""
    SELECT name_kr, sector, current_company, profile_summary 
    FROM candidates 
    WHERE name_kr = '이정수'
""")
rows = cur.fetchall()

print(f"Query Results (Count: {len(rows)}):")
for r in rows:
    print(f"이름: {r[0]}")
    print(f"분류: {r[1]}")
    print(f"현재 회사: {r[2]}")
    print(f"프로필 요약: {r[3]}")
    print("-" * 50)
conn.close()
