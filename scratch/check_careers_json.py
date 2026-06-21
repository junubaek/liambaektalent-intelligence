import sqlite3, json

conn = sqlite3.connect('candidates.db')
cur = conn.cursor()

# careers_json 있는 후보자 샘플 확인
cur.execute("""
    SELECT name_kr, careers_json
    FROM candidates
    WHERE is_duplicate=0
    AND careers_json IS NOT NULL
    AND length(careers_json) > 100
    LIMIT 3
""")
for name, cj in cur.fetchall():
    careers = json.loads(cj)
    print(name, '→ 경력 수:', len(careers))
    if careers:
        print('  첫번째:', json.dumps(careers[0], indent=2, ensure_ascii=False))

conn.close()
