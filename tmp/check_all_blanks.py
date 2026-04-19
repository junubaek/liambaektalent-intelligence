import sqlite3

conn = sqlite3.connect('candidates.db')
cursor = conn.cursor()

cursor.execute("PRAGMA table_info(candidates)")
columns = [col[1] for col in cursor.fetchall()]

print("==== 각 컬럼별 텅 빈 데이터 점검 ====")
for col in columns:
    cursor.execute(f"SELECT count(*) FROM candidates WHERE `{col}` IS NULL OR `{col}` = '' OR `{col}` = '미상' OR `{col}` = 'Unknown'")
    cnt = cursor.fetchone()[0]
    print(f"- {col}: {cnt}명 비어있음")

conn.close()
