import sys
sys.stdout.reconfigure(encoding='utf-8')
from neo4j import GraphDatabase

# 로컬 DB 접속 정보 복구 (toss1234)
local = GraphDatabase.driver('bolt://localhost:7687', auth=('neo4j', 'toss1234'))
# 새 Aura 접속 정보
aura = GraphDatabase.driver('neo4j+ssc://deb21ee0.databases.neo4j.io', auth=('deb21ee0', 'pdaL-7EcG4TAejKf9HuSMkgiA0uPWP6Yl5Bw-XywhrQ'))

ls = local.session()
as_ = aura.session()

# 관계 타입 목록
rel_types = ['MANAGED','BUILT','DESIGNED','ANALYZED','LED','LAUNCHED','GREW','NEGOTIATED','SUPPORTED']

for rel_type in rel_types:
    # 해당 타입 엣지 전체 가져오기
    edges = ls.run(f'''
        MATCH (c:Candidate)-[r:{rel_type}]->(s:Skill)
        RETURN c.id as cid, s.name as skill_name
    ''').data()
    
    if not edges:
        print(f'{rel_type}: 0개 스킵')
        continue
    
    # 배치로 Aura에 삽입
    for i in range(0, len(edges), 500):
        batch = edges[i:i+500]
        as_.run(f'''
            UNWIND $batch as row
            MATCH (c:Candidate {{id: row.cid}})
            MATCH (s:Skill {{name: row.skill_name}})
            MERGE (c)-[:{rel_type}]->(s)
        ''', batch=batch)
    
    print(f'{rel_type}: {len(edges)}개 이전 완료')

# 임베딩은 별도 (용량 큼)
emb_cnt = ls.run('MATCH (c:Candidate) WHERE c.embedding IS NOT NULL RETURN count(c)').single()[0]
print(f'임베딩 있는 노드: {emb_cnt}개 (별도 처리 필요)')

ls.close()
as_.close()
local.close()
aura.close()
print('엣지 마이그레이션 완료')
