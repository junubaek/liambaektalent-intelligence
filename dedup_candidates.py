
import sys
import sqlite3
import os

# Set output encoding to utf-8
sys.stdout.reconfigure(encoding='utf-8')

db_path = r'c:\Users\cazam\Downloads\이력서자동분석검색시스템\candidates.db'

if not os.path.exists(db_path):
    print(f"Database not found: {db_path}")
    sys.exit(1)

conn = sqlite3.connect(db_path)
cur = conn.cursor()

# 1. 중복 그룹 찾기 (이름+회사 기준)
# 이름이 있고, 특정한 더미 데이터가 아니며, 회사 정보가 있는 경우
print("중복 후보자 분석 중...")
cur.execute('''
    SELECT name_kr, current_company, COUNT(*) as cnt, GROUP_CONCAT(id) as ids
    FROM candidates
    WHERE name_kr IS NOT NULL 
    AND name_kr != ''
    AND name_kr NOT IN ('미상', '개인정보', '보안컨설')
    AND current_company IS NOT NULL
    AND current_company != ''
    GROUP BY name_kr, current_company
    HAVING COUNT(*) > 1
''')
groups = cur.fetchall()
print(f"발견된 중복 그룹: {len(groups)}개")

delete_ids = []
for name, company, cnt, ids_str in groups:
    ids = ids_str.split(',')
    
    # 각 ID의 raw_text 길이 확인 (가장 긴 것을 유지하기 위함)
    placeholders = ",".join("?" * len(ids))
    cur.execute(f'''
        SELECT id, LENGTH(COALESCE(raw_text, "")) as txt_len
        FROM candidates WHERE id IN ({placeholders})
        ORDER BY txt_len DESC
    ''', ids)
    ranked = cur.fetchall()
    
    if not ranked:
        continue
        
    # 가장 긴 것(첫 번째) 유지, 나머지 삭제 목록에 추가
    keep_id = ranked[0][0]
    for rid, _ in ranked[1:]:
        delete_ids.append(rid)

print(f"삭제 대상 후보자: {len(delete_ids)}명")

# 2. 실제 삭제 작업
if delete_ids:
    # SQLite 파라미터 개수 제한(보통 999개)을 피하기 위해 배치 처리
    batch_size = 500
    for i in range(0, len(delete_ids), batch_size):
        batch = delete_ids[i:i+batch_size]
        placeholders = ','.join('?' * len(batch))
        cur.execute(f'DELETE FROM candidates WHERE id IN ({placeholders})', batch)
    
    conn.commit()
    print(f"삭제 완료: {len(delete_ids)}명")
else:
    print("삭제할 중복 레코드가 없습니다.")

# 3. 최종 확인
cur.execute('SELECT COUNT(*) FROM candidates')
total_remaining = cur.fetchone()[0]
print(f"정리 후 총 후보자 수: {total_remaining}명")

conn.close()
