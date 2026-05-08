import sqlite3
conn = sqlite3.connect('candidates.db')
cur = conn.cursor()

# 테이블 목록 확인
cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
print(f"Tables: {[t[0] for t in cur.fetchall()]}")

# candidates 컬럼 확인
cur.execute("PRAGMA table_info(candidates)")
print("\n[Candidates Columns]")
for col in cur.fetchall():
    print(f" - {col[1]} ({col[2]})")

# 강기태 데이터의 모든 컬럼 조회 (일부 텍스트는 잘라서)
print("\n--- Kang Ki-tae Row Data ---")
cur.execute("SELECT * FROM candidates WHERE name_kr = '강기태' AND is_duplicate = 0")
row = cur.fetchone()
if row:
    col_names = [description[0] for description in cur.description]
    for name, val in zip(col_names, row):
        display_val = str(val)[:100] + "..." if isinstance(val, str) and len(str(val)) > 100 else val
        print(f" {name}: {display_val}")
else:
    print("Kang Ki-tae not found.")

conn.close()
