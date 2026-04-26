from neo4j import GraphDatabase
import os
import sys

# 로컬 (소스)
LOCAL_URI = "bolt://127.0.0.1:7687"
LOCAL_AUTH = ("neo4j", "toss1234")

# AuraDB (타겟)
AURA_URI = "neo4j+ssc://72de4959.databases.neo4j.io"
AURA_AUTH = ("72de4959", "oicDGhFqhTz-5NhnnW0uGEKOIrSUs0GZBdKtzRhyvns")

try:
    local = GraphDatabase.driver(LOCAL_URI, auth=LOCAL_AUTH)
    aura = GraphDatabase.driver(AURA_URI, auth=AURA_AUTH)
except Exception as e:
    print("드라이버 연결 실패:", e)
    sys.exit(1)

BATCH = 500

# 1. Candidate 노드 이전
print("Candidate 노드 이전 중...")
with local.session() as ls:
    candidates = ls.run("""
        MATCH (c:Candidate)
        RETURN c.id as id, c.name_kr as name_kr,
               c.seniority as seniority,
               c.sector as sector,
               c.current_company as current_company,
               c.total_years as total_years
    """).data()

print(f"총 {len(candidates)}명 읽음")

for i in range(0, len(candidates), BATCH):
    batch = candidates[i:i+BATCH]
    with aura.session() as as_:
        as_.run("""
            UNWIND $rows AS row
            MERGE (c:Candidate {id: row.id})
            SET c.name_kr = row.name_kr,
                c.seniority = row.seniority,
                c.sector = row.sector,
                c.current_company = row.current_company,
                c.total_years = row.total_years
        """, rows=batch)
    print(f"  Candidate {i+len(batch)}/{len(candidates)} 완료")

# 2. Skill 노드 이전
print("Skill 노드 이전 중...")
with local.session() as ls:
    skills = ls.run("MATCH (s:Skill) RETURN s.name as name").data()

for i in range(0, len(skills), BATCH):
    batch = skills[i:i+BATCH]
    with aura.session() as as_:
        as_.run("""
            UNWIND $rows AS row
            MERGE (s:Skill {name: row.name})
        """, rows=batch)
print(f"  Skill {len(skills)}개 완료")

# 3. 엣지 이전
print("엣지 이전 중...")
with local.session() as ls:
    edges = ls.run("""
        MATCH (c:Candidate)-[r]->(s:Skill)
        RETURN c.id as cid, type(r) as rel, s.name as skill
    """).data()

print(f"총 {len(edges)}개 엣지")

for i in range(0, len(edges), BATCH):
    batch = edges[i:i+BATCH]
    with aura.session() as as_:
        for edge in batch:
            rel = edge['rel']
            as_.run(f"""
                MATCH (c:Candidate {{id: $cid}})
                MATCH (s:Skill {{name: $skill}})
                MERGE (c)-[:{rel}]->(s)
            """, cid=edge['cid'], skill=edge['skill'])
    print(f"  엣지 {i+len(batch)}/{len(edges)} 완료")

# 4. 검증
with aura.session() as as_:
    nc = as_.run("MATCH (c:Candidate) RETURN count(c) as n").single()['n']
    ns = as_.run("MATCH (s:Skill) RETURN count(s) as n").single()['n']
    ne = as_.run("MATCH ()-[r]->() RETURN count(r) as n").single()['n']
    print(f"\n✅ AuraDB 최종: Candidates={nc}, Skills={ns}, Edges={ne}")

local.close()
aura.close()
