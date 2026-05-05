import sqlite3
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

conn = sqlite3.connect('candidates.db')
cur = conn.cursor()

# 스키마 확인 먼저
cur.execute("PRAGMA table_info(candidates)")
columns = [row[1] for row in cur.fetchall()]
print(f"[스키마 확인] 컬럼 목록:")
print(columns)
print()

# DB 실제 컬럼명 (is_pinecone_synced, is_neo4j_synced) 반영
has_pinecone = 'is_pinecone_synced' in columns
has_neo4j = 'is_neo4j_synced' in columns

print(f"is_pinecone_synced 컬럼: {'있음' if has_pinecone else '없음'}")
print(f"is_neo4j_synced 컬럼: {'있음' if has_neo4j else '없음'}")
print()

# 마스터 후보자 전체 조회
query = "SELECT id, name_kr, current_company"
if has_pinecone:
    query += ", is_pinecone_synced"
if has_neo4j:
    query += ", is_neo4j_synced"
query += " FROM candidates WHERE is_duplicate = 0"

cur.execute(query)
masters = cur.fetchall()

print(f"전체 마스터 후보자: {len(masters)}명")
print()

if not has_pinecone and not has_neo4j:
    print("⚠️  동기화 상태 컬럼이 없습니다.")
    conn.close()
    sys.exit()

# 동기화 안 된 마스터 필터
need_sync = []
for row in masters:
    idx = 3
    pinecone_ok = True
    neo4j_ok = True

    if has_pinecone:
        pinecone_ok = bool(row[idx])
        idx += 1
    if has_neo4j:
        neo4j_ok = bool(row[idx])

    if not pinecone_ok or not neo4j_ok:
        need_sync.append({
            'id': row[0],
            'name_kr': row[1],
            'current_company': row[2],
            'pinecone': pinecone_ok if has_pinecone else 'N/A',
            'neo4j': neo4j_ok if has_neo4j else 'N/A',
        })

print(f"=== 재색인 필요 현황 ===")
print(f"동기화 완료: {len(masters) - len(need_sync)}명")
print(f"재색인 필요: {len(need_sync)}명")
print()

if need_sync:
    print("=== 재색인 필요 후보자 (상위 30명) ===")
    for r in need_sync[:30]:
        print(f"  {r['name_kr']} | {r['current_company']} | "
              f"pinecone: {r['pinecone']} | neo4j: {r['neo4j']} | ID: {r['id'][:8]}...")

    # ID 목록 파일로 저장
    ids = [r['id'] for r in need_sync]
    with open('resync_targets.json', 'w', encoding='utf-8') as f:
        json.dump(ids, f, ensure_ascii=False, indent=2)
    print(f"\n전체 {len(need_sync)}명 ID → resync_targets.json 저장 완료")

conn.close()
