import json
from neo4j import GraphDatabase

s = json.load(open('secrets.json', encoding='utf-8'))
driver = GraphDatabase.driver(s['NEO4J_URI'], auth=(s['NEO4J_USERNAME'], s['NEO4J_PASSWORD']))

# CANONICAL_MAP에서 표준 노드 목록 가져오기
import sys
sys.path.insert(0, '.')
from ontology_graph import CANONICAL_MAP

# 표준 노드명 셋 (언더스코어 형식)
canonical_nodes = set(CANONICAL_MAP.values())
print(f'CANONICAL_MAP standard nodes: {len(canonical_nodes)}')

# 공백 포함 스킬 → 언더스코어 변환 후 CANONICAL_MAP 매칭
def to_canonical(name):
    # 공백을 언더스코어로 변환
    candidate = name.replace(' ', '_')
    if candidate in canonical_nodes:
        return candidate
    # 대소문자 무시 매칭
    candidate_lower = candidate.lower()
    for node in canonical_nodes:
        if node.lower() == candidate_lower:
            return node
    return None

with driver.session() as sess:
    # 공백 포함 스킬 노드 전체 조회
    result = sess.run("MATCH (s:Skill) WHERE s.name CONTAINS ' ' RETURN s.name as name")
    space_skills = [r['name'] for r in result]
    print(f'Non-canonical skill nodes: {len(space_skills)}')
    
    mapped = 0
    unmapped = 0
    
    for skill_name in space_skills:
        canonical = to_canonical(skill_name)
        if canonical:
            # 표준 노드로 엣지 이전 후 비표준 노드 삭제
            sess.run("""
                MATCH (old:Skill {name: $old_name})
                MERGE (new:Skill {name: $new_name})
                WITH old, new
                MATCH (c:Candidate)-[r]->(old)
                MERGE (c)-[r2:BUILT]->(new)
                SET r2 = properties(r)
                DELETE r
                WITH old
                MATCH (old) WHERE NOT (old)--()
                DELETE old
            """, old_name=skill_name, new_name=canonical)
            mapped += 1
        else:
            unmapped += 1
    
    print(f'Mapped to canonical: {mapped}')
    print(f'Could not map: {unmapped}')
    
    # 결과 확인
    cnt = sess.run('MATCH (s:Skill) RETURN count(s) as cnt').single()['cnt']
    print(f'Remaining skill nodes: {cnt}')

driver.close()
print('Done.')
