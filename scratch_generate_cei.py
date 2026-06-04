import json, sqlite3, time
from cei_generator import generate_cei
from datetime import datetime

conn = sqlite3.connect('candidates.db')
cur = conn.cursor()

# node_idf 로드
node_idf = json.load(open('node_idf.json', encoding='utf-8'))

# Specific candidates of interest: 이강원, 김은형, 전형준, 정혜연
target_names = ['이강원', '김은형', '전형준', '정혜연']
specific_candidates = []
for name in target_names:
    cur.execute("""
        SELECT id, name_kr, current_company,
               sector, raw_text, careers_json, profile_summary
        FROM candidates
        WHERE name_kr = ?
    """, (name,))
    rows = cur.fetchall()
    cols = ['id','name_kr','current_company',
            'sector','raw_text','careers_json','profile_summary']
    for r in rows:
        specific_candidates.append(dict(zip(cols, r)))

# Also find one candidate with a short raw_text/profile_summary to satisfy "미흡한 이력서 후보자 1명"
cur.execute("""
    SELECT id, name_kr, current_company,
           sector, raw_text, careers_json, profile_summary
    FROM candidates
    WHERE is_duplicate = 0
    AND (raw_text IS NOT NULL AND length(raw_text) > 0 AND length(raw_text) < 150)
    LIMIT 1
""")
row = cur.fetchone()
if row:
    cols = ['id','name_kr','current_company',
            'sector','raw_text','careers_json','profile_summary']
    specific_candidates.append(dict(zip(cols, row)))

# Get the general batch candidates (up to 500)
cur.execute("""
    SELECT id, name_kr, current_company,
           sector, raw_text, careers_json, profile_summary
    FROM candidates
    WHERE is_duplicate = 0
    AND cei_json IS NULL
    AND (
        (profile_summary IS NOT NULL AND length(profile_summary) > 100)
        OR (raw_text IS NOT NULL AND length(raw_text) > 300)
    )
    ORDER BY
        CASE
            WHEN careers_json IS NOT NULL
             AND length(careers_json) > 50 THEN 0
            ELSE 1
        END
    LIMIT 500
""")
rows = cur.fetchall()
cols = ['id','name_kr','current_company',
        'sector','raw_text','careers_json','profile_summary']
batch_candidates = [dict(zip(cols, r)) for r in rows]

# Combine lists and deduplicate by id
seen_ids = set()
candidates = []
for c in specific_candidates + batch_candidates:
    if c['id'] not in seen_ids:
        seen_ids.add(c['id'])
        candidates.append(c)

print(f'처리 대상: {len(candidates)}명')

success, failed = 0, 0
for i, cand in enumerate(candidates):
    try:
        cei = generate_cei(cand, conn, node_idf)

        cur.execute("""
            UPDATE candidates
            SET cei_json = ?,
                cei_confidence = ?,
                cei_updated_at = ?
            WHERE id = ?
        """, (
            json.dumps(cei, ensure_ascii=False),
            cei['confidence'],
            datetime.now().isoformat(),
            cand['id']
        ))
        conn.commit()
        success += 1

        if success % 50 == 0 or cand['name_kr'] in target_names:
            print(f'완료: {success}명 / 실패: {failed}명 (최근 처리: {cand.get("name_kr")})')

        time.sleep(0.3)  # Gemini rate limit

    except Exception as e:
        failed += 1
        print(f'오류 발생 ({cand.get("name_kr")}): {e}')
        continue

conn.close()
print(f'최종: 성공 {success}명, 실패 {failed}명')
