from neo4j import GraphDatabase

LOCAL_URI = "bolt://127.0.0.1:7687"
LOCAL_AUTH = ("neo4j", "toss1234")
AURA_URI = "neo4j+ssc://72de4959.databases.neo4j.io"
AURA_AUTH = ("72de4959", "oicDGhFqhTz-5NhnnW0uGEKOIrSUs0GZBdKtzRhyvns")

local = GraphDatabase.driver(LOCAL_URI, auth=LOCAL_AUTH)
aura = GraphDatabase.driver(AURA_URI, auth=AURA_AUTH)

# 현재 AuraDB 엣지 수 확인
with aura.session() as s:
    existing = s.run("MATCH ()-[r]->() RETURN count(r) as n").single()['n']
    print(f"기존 엣지: {existing}개")

# 로컬에서 전체 엣지 읽기
print("로컬에서 엣지 읽는 중...")
with local.session() as s:
    edges = s.run("""
        MATCH (c:Candidate)-[r]->(sk:Skill)
        RETURN c.id as cid, type(r) as rel, sk.name as skill
        ORDER BY c.id
    """).data()
print(f"총 {len(edges)}개 엣지")

# 관계 타입별로 분류
from collections import defaultdict
by_rel = defaultdict(list)
for e in edges:
    by_rel[e['rel']].append({'cid': e['cid'], 'skill': e['skill']})

# 관계 타입별 배치 UNWIND (500개씩)
BATCH = 500
total_done = 0

for rel_type, rel_edges in by_rel.items():
    print(f"\n{rel_type}: {len(rel_edges)}개 처리 중...")
    for i in range(0, len(rel_edges), BATCH):
        batch = rel_edges[i:i+BATCH]
        with aura.session() as s:
            s.run(f"""
                UNWIND $rows AS row
                MATCH (c:Candidate {{id: row.cid}})
                MATCH (sk:Skill {{name: row.skill}})
                MERGE (c)-[:{rel_type}]->(sk)
            """, rows=batch)
        total_done += len(batch)
        if total_done % 5000 == 0:
            print(f"  진행: {total_done}/{len(edges)}")

# 최종 확인
with aura.session() as s:
    nc = s.run("MATCH (c:Candidate) RETURN count(c) as n").single()['n']
    nsk = s.run("MATCH (s:Skill) RETURN count(s) as n").single()['n']
    ne = s.run("MATCH ()-[r]->() RETURN count(r) as n").single()['n']
    print(f"\n✅ 완료: Candidates={nc}, Skills={nsk}, Edges={ne}")

local.close()
aura.close()
