import sqlite3
import json
import re
import sys
from neo4j import GraphDatabase

# UTF-8 출력 보장
sys.stdout.reconfigure(encoding='utf-8')

# [1] SQLite 중복 및 동일 한글명 검사
print("=== [1] 중복 레코드 현황 ===")
conn = sqlite3.connect('candidates.db')
conn.row_factory = sqlite3.Row
cur = conn.cursor()

row = cur.execute("""
    SELECT COUNT(*) as total,
           SUM(CASE WHEN is_duplicate=1 THEN 1 ELSE 0 END) as dupes,
           SUM(CASE WHEN is_duplicate=0 THEN 1 ELSE 0 END) as active
    FROM candidates
""").fetchone()

print(f"Total Records: {row['total']}")
print(f"Duplicate Records (is_duplicate=1): {row['dupes']}")
print(f"Active Records (is_duplicate=0): {row['active']}")
print()

print("--- 동일 name_kr이 2개 이상이면서 active=0인 케이스 (Top 20) ---")
cur.execute("""
    SELECT name_kr, COUNT(*) as cnt
    FROM candidates
    WHERE is_duplicate = 0 AND name_kr IS NOT NULL AND name_kr != ''
    GROUP BY name_kr
    HAVING cnt > 1
    ORDER BY cnt DESC
    LIMIT 20
""")
duplicates = cur.fetchall()
if duplicates:
    for idx, r in enumerate(duplicates, 1):
        print(f"  {idx}. {r['name_kr']}: {r['cnt']}명")
else:
    print("  동일 한글명을 가진 활성 후보자가 없습니다.")
print()


# [2] Neo4j 엣지 없는 활성 후보자 수
print("=== [2] Neo4j 엣지 없는 활성 후보자 수 ===")
try:
    secrets = json.load(open('secrets.json', encoding='utf-8'))
    driver = GraphDatabase.driver(secrets['NEO4J_URI'],
        auth=(secrets['NEO4J_USERNAME'], secrets['NEO4J_PASSWORD']))

    with driver.session() as s:
        r = s.run("""
            MATCH (c:Candidate)
            WHERE NOT (c)-[]->(:Skill)
            RETURN count(c) as no_edge_count
        """)
        no_edge = r.single()['no_edge_count']
        
        r2 = s.run("MATCH (c:Candidate) RETURN count(c) as total")
        total_neo = r2.single()['total']
        
        print(f"엣지 없는 Neo4j 후보자 수: {no_edge}명")
        print(f"Neo4j 전체 후보자 수: {total_neo}명")
    driver.close()
except Exception as e:
    print("Neo4j 연결 및 조회 실패:", str(e))
print()


# [3] 영문 이력서 후보자 수 (한글 이름 없는 케이스)
# SQLite REGEXP 우회 처리를 위해 파이썬 레벨에서 정규식 사용
print("=== [3] 영문 이력서 후보자 수 (한글 이름 없는 케이스) ===")
cur.execute("""
    SELECT id, name_kr
    FROM candidates
    WHERE is_duplicate = 0
""")
candidates = cur.fetchall()

eng_resume_count = 0
for cand in candidates:
    name_kr = cand['name_kr']
    
    # name_kr이 Null이거나 한글 글자가 없으면 영문 이력서로 판단
    if not name_kr:
        eng_resume_count += 1
    elif not re.search('[가-힣]', name_kr):
        eng_resume_count += 1

print(f"영문 이력서 후보자 수 (활성 후보군 중): {eng_resume_count}명")
print()


# [4] profile_summary가 수동 enrichment된 케이스 확인
print("=== [4] profile_summary 수동 enrichment 케이스 (길이 < 100자) ===")
row_summary = cur.execute("""
    SELECT COUNT(*) as cnt FROM candidates
    WHERE is_duplicate = 0
    AND length(profile_summary) < 100
    AND profile_summary IS NOT NULL
""").fetchone()

print(f"Enriched Profile Summary 개수 (< 100자): {row_summary['cnt']}개")

conn.close()
