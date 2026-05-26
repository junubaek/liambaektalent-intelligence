import json, sys
sys.stdout.reconfigure(encoding='utf-8')
from neo4j import GraphDatabase

# 로컬 (toss1234로 복구)
local = GraphDatabase.driver('bolt://localhost:7687', auth=('neo4j', 'toss1234'))
# 새 Aura (접속 정보 유지)
aura = GraphDatabase.driver('neo4j+ssc://deb21ee0.databases.neo4j.io', auth=('deb21ee0', 'pdaL-7EcG4TAejKf9HuSMkgiA0uPWP6Yl5Bw-XywhrQ'))

ls = local.session()
as_ = aura.session()

# Candidate 노드 전체 이전
total = ls.run('MATCH (c:Candidate) RETURN count(c)').single()[0]
print(f'이전 대상: {total}명')

batch_size = 200
offset = 0
migrated = 0

while offset < total:
    rows = ls.run('''
        MATCH (c:Candidate)
        RETURN properties(c) as props
        SKIP $skip LIMIT $limit
    ''', skip=offset, limit=batch_size).data()
    
    if not rows:
        break
    
    as_.run('''
        UNWIND $rows as row
        MERGE (c:Candidate {id: row.props.id})
        SET c = row.props
    ''', rows=rows)
    
    migrated += len(rows)
    offset += batch_size
    print(f'  {migrated}/{total} 완료')

print(f'Candidate 이전 완료: {migrated}명')

# Skill 노드 이전
skills = ls.run('MATCH (s:Skill) RETURN properties(s) as props').data()
print(f'Skill 노드: {len(skills)}개')
for i in range(0, len(skills), 500):
    batch = skills[i:i+500]
    as_.run('UNWIND $batch as b MERGE (s:Skill {name: b.props.name}) SET s = b.props', batch=batch)
print('Skill 이전 완료')

# Ontology Node / Edge 전체 이전 (추가적으로 있으면 안전하게 마이그레이션 - 혹시 몰라서 확인용)
# 간단하게 기존 스크립트에 포함된 Candidate와 Skill만 이전하도록 둡니다.

ls.close()
as_.close()
local.close()
aura.close()
print('마이그레이션 완료')
