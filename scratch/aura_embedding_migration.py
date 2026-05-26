import sys
sys.stdout.reconfigure(encoding='utf-8')
from neo4j import GraphDatabase

local = GraphDatabase.driver('bolt://localhost:7687', auth=('neo4j', 'toss1234'))
aura = GraphDatabase.driver('neo4j+ssc://deb21ee0.databases.neo4j.io', auth=('deb21ee0', 'pdaL-7EcG4TAejKf9HuSMkgiA0uPWP6Yl5Bw-XywhrQ'))

ls = local.session()
as_ = aura.session()

# 임베딩 있는 노드 ID 목록
ids = [r['id'] for r in ls.run('MATCH (c:Candidate) WHERE c.embedding IS NOT NULL RETURN c.id as id').data()]
print(f'임베딩 이전 대상: {len(ids)}개')

migrated = 0
batch_size = 50  # 임베딩은 용량 크므로 작은 배치

for i in range(0, len(ids), batch_size):
    batch_ids = ids[i:i+batch_size]
    rows = ls.run('''
        MATCH (c:Candidate)
        WHERE c.id IN $ids AND c.embedding IS NOT NULL
        RETURN c.id as id, c.embedding as emb
    ''', ids=batch_ids).data()
    
    as_.run('''
        UNWIND $rows as row
        MATCH (c:Candidate {id: row.id})
        SET c.embedding = row.emb
    ''', rows=rows)
    
    migrated += len(rows)
    if migrated % 200 == 0:
        print(f'  {migrated}/{len(ids)} 완료')

print(f'임베딩 이전 완료: {migrated}개')

# Vector 인덱스 생성
try:
    as_.run('''
        CREATE VECTOR INDEX candidate_embedding IF NOT EXISTS
        FOR (c:Candidate) ON (c.embedding)
        OPTIONS {indexConfig: {
            `vector.dimensions`: 1536,
            `vector.similarity_function`: 'cosine'
        }}
    ''')
    print('Vector 인덱스 생성 완료')
except Exception as e:
    print(f'인덱스: {e}')

ls.close()
as_.close()
local.close()
aura.close()
print('전체 마이그레이션 완료')
