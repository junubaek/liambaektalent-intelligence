import sqlite3, json, sys, uuid
sys.stdout.reconfigure(encoding='utf-8')
from neo4j import GraphDatabase

conn = sqlite3.connect('candidates.db')
cur = conn.cursor()

# 현재 SQLite에 있는 전체 ID
cur.execute('SELECT id FROM candidates')
sqlite_ids = set(r[0] for r in cur.fetchall())

secrets = json.load(open('secrets.json', encoding='utf-8'))
driver = GraphDatabase.driver(secrets['NEO4J_URI'], auth=(secrets['NEO4J_USERNAME'], secrets['NEO4J_PASSWORD']))
session = driver.session()

# Neo4j에만 있는 ID 전체 추출
neo4j_ids = set(r['id'] for r in session.run('MATCH (c:Candidate) RETURN c.id as id').data())
only_neo4j = list(neo4j_ids - sqlite_ids)
print(f'복구 대상: {len(only_neo4j)}명')

# 배치로 Neo4j에서 상세 데이터 가져오기
inserted = 0
skipped = 0
batch_size = 100

for i in range(0, len(only_neo4j), batch_size):
    batch = only_neo4j[i:i+batch_size]
    result = session.run('''
        MATCH (c:Candidate)
        WHERE c.id IN $ids
        RETURN c.id as id, c.name_kr as name_kr,
               c.current_company as current_company,
               c.sector as sector,
               c.summary as summary,
               c.email as email,
               c.phone as phone,
               c.raw_text as raw_text
    ''', ids=batch).data()

    for r in result:
        cid = r['id']
        name = r['name_kr'] or ''
        # 유효성 검사 - 이름 없거나 이상한 것 제외
        if not name or len(name) < 2:
            skipped += 1
            continue
        if name in ['원본','재무회계','UX컨설팅','연구개발 차량설계','보안 솔루션 총판영업']:
            skipped += 1
            continue

        try:
            cur.execute('''
                INSERT INTO candidates
                (id, name_kr, current_company, sector, profile_summary,
                 email, phone, raw_text, document_hash, is_duplicate, is_neo4j_synced, is_pinecone_synced)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 0, 1, 0)
            ''', (
                cid,
                name,
                r.get('current_company') or '',
                r.get('sector') or '',
                r.get('summary') or '',
                r.get('email') or '',
                r.get('phone') or '',
                r.get('raw_text') or '',
                r.get('document_hash') or f'recovered_{cid}',
            ))
            inserted += 1
        except Exception as e:
            print(f"Error inserting {cid}: {e}")
            skipped += 1

    conn.commit()
    print(f'  {min(i+len(batch), len(only_neo4j))}/{len(only_neo4j)} 처리중... 삽입:{inserted} 스킵:{skipped}')

conn.close()
driver.close()
print(f'\n복구 완료: {inserted}명 삽입, {skipped}명 스킵')
