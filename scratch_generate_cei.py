import json, sqlite3, time
from cei_generator import generate_cei
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

# Fetch target records
conn = sqlite3.connect('candidates.db')
cur = conn.cursor()

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

conn.close()

# Combine lists and deduplicate by id
seen_ids = set()
candidates = []
for c in specific_candidates + batch_candidates:
    if c['id'] not in seen_ids:
        seen_ids.add(c['id'])
        candidates.append(c)

print(f'처리 대상: {len(candidates)}명')

# node_idf 로드
node_idf = json.load(open('node_idf.json', encoding='utf-8'))

def process_candidate(cand):
    # Process single candidate using a dedicated connection to avoid locks
    db_conn = sqlite3.connect('candidates.db', timeout=60.0)
    try:
        # Prevent parallel write issues on the same db file by doing read-only or small delays inside if needed
        cei = generate_cei(cand, db_conn, node_idf)
        
        db_cur = db_conn.cursor()
        db_cur.execute("""
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
        db_conn.commit()
        return True, cand.get("name_kr")
    except Exception as e:
        return False, f'{cand.get("name_kr")}: {e}'
    finally:
        db_conn.close()

success, failed = 0, 0
# Use 15 threads for concurrent calling
with ThreadPoolExecutor(max_workers=15) as executor:
    futures = [executor.submit(process_candidate, c) for c in candidates]
    for idx, fut in enumerate(futures):
        ok, res = fut.result()
        if ok:
            success += 1
        else:
            failed += 1
            print(f"오류: {res}")
            
        if (idx + 1) % 50 == 0 or idx + 1 == len(candidates):
            print(f'진행률: {idx + 1}/{len(candidates)} 완료 | 성공: {success}명, 실패: {failed}명')
        time.sleep(0.02)

print(f'최종: 성공 {success}명, 실패 {failed}명')
