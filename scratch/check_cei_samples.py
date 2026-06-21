import sqlite3, json

conn = sqlite3.connect('candidates.db')
cur = conn.cursor()

target_names = ['이강원', '김은형', '전형준', '정혜연']
print("=== [6-1] CEI 생성 샘플 확인 ===")

for name in target_names:
    cur.execute("SELECT name_kr, current_company, cei_json FROM candidates WHERE name_kr=?", (name,))
    rows = cur.fetchall()
    for row in rows:
        print(f"\n후보자: {row[0]} ({row[1]})")
        if row[2]:
            cei = json.loads(row[2])
            print(json.dumps(cei, indent=2, ensure_ascii=False))
        else:
            print("  CEI 데이터 없음")

# 미흡한 이력서 후보자 1명 찾기
cur.execute("""
    SELECT name_kr, current_company, cei_json
    FROM candidates
    WHERE cei_json IS NOT NULL
    ORDER BY cei_confidence ASC
    LIMIT 1
""")
row = cur.fetchone()
if row:
    print(f"\n미흡한 이력서 후보자: {row[0]} ({row[1]})")
    cei = json.loads(row[2])
    print(json.dumps(cei, indent=2, ensure_ascii=False))
else:
    print("\n미흡한 이력서 후보자 찾을 수 없음")

conn.close()
