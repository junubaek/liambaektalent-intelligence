import sqlite3, sys, shutil, datetime
sys.stdout.reconfigure(encoding='utf-8')

# 1. 백업
backup_name = f'candidates_backup_{datetime.datetime.now().strftime("%Y%m%d_%H%M")}.db'
shutil.copy('candidates.db', backup_name)
print(f'백업 완료: {backup_name}')

conn = sqlite3.connect('candidates.db')
cur = conn.cursor()

# 깡통 마스터 삭제 + 진짜 데이터 승격
# 각 이름별로 raw_text 가장 긴 것을 마스터로
cur.execute('''
    SELECT m.id, m.name_kr
    FROM candidates m
    WHERE m.is_duplicate=0 AND (m.raw_text IS NULL OR length(m.raw_text) < 10)
    AND EXISTS (
        SELECT 1 FROM candidates d
        WHERE d.name_kr = m.name_kr
        AND d.is_duplicate=1 AND length(d.raw_text) > 500
    )
''')
targets = cur.fetchall()
print(f'처리 대상: {len(targets)}명')

fixed = 0
for cid, name in targets:
    # 진짜 데이터 중 가장 긴 것 찾기
    cur.execute('''SELECT id FROM candidates
                   WHERE name_kr=? AND is_duplicate=1
                   ORDER BY length(raw_text) DESC LIMIT 1''', (name,))
    best = cur.fetchone()
    if not best:
        continue
    
    # 깡통 마스터 삭제
    cur.execute('DELETE FROM candidates WHERE id=?', (cid,))
    # 진짜 데이터 승격
    cur.execute('UPDATE candidates SET is_duplicate=0, is_neo4j_synced=0, is_pinecone_synced=0 WHERE id=?', (best[0],))
    fixed += 1

conn.commit()

# 파편 마스터 (500자 미만) 처리
cur.execute('''SELECT m.id, m.name_kr FROM candidates m
               WHERE m.is_duplicate=0 AND length(m.raw_text) BETWEEN 10 AND 500
               AND EXISTS (
                   SELECT 1 FROM candidates d
                   WHERE d.name_kr=m.name_kr AND d.is_duplicate=1
                   AND length(d.raw_text) > 500
               )''')
frags = cur.fetchall()
print(f'파편 마스터 처리 대상: {len(frags)}명')

for cid, name in frags:
    cur.execute('''SELECT id FROM candidates
                   WHERE name_kr=? AND is_duplicate=1
                   ORDER BY length(raw_text) DESC LIMIT 1''', (name,))
    best = cur.fetchone()
    if not best:
        continue
    cur.execute('DELETE FROM candidates WHERE id=?', (cid,))
    cur.execute('UPDATE candidates SET is_duplicate=0, is_neo4j_synced=0, is_pinecone_synced=0 WHERE id=?', (best[0],))
    fixed += 1

conn.commit()
conn.close()
print(f'총 {fixed}명 복구 완료')
