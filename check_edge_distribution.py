import sqlite3
import json
from neo4j import GraphDatabase

with open("secrets.json", "r", encoding="utf-8") as f:
    secrets = json.load(f)
driver = GraphDatabase.driver("neo4j://127.0.0.1:7687", auth=("neo4j", "toss1234"))

print("=== 1. 엣지 분포 확인 ===")
with driver.session() as session:
    res = session.run("""
        MATCH (c:Candidate)-[r]->(s:Skill)
        WITH c, count(r) as edge_cnt
        RETURN 
          min(edge_cnt) as 최솟값,
          max(edge_cnt) as 최댓값,
          avg(edge_cnt) as 평균값,
          percentileCont(edge_cnt, 0.5) as 중앙값,
          percentileCont(edge_cnt, 0.9) as 상위10퍼
    """)
    record = res.single()
    print(f"최소: {record['최솟값']}개")
    print(f"최대: {record['최댓값']}개")
    print(f"평균: {record['평균값']:.1f}개")
    print(f"중앙값: {record['중앙값']}개")
    print(f"상위 10%: {record['상위10퍼']}개")

print("\n=== 2. 엣지 많은 상위 10명 ===")
with driver.session() as session:
    res = session.run("""
        MATCH (c:Candidate)-[r]->(s:Skill)
        WITH c, count(r) as edge_cnt
        ORDER BY edge_cnt DESC
        LIMIT 10
        RETURN c.name_kr as name_kr, c.name as name, edge_cnt
    """)
    for i, r in enumerate(res, 1):
        # Handle cases where name_kr or name might be None
        name_kr = r['name_kr'] or ""
        name = r['name'] or ""
        print(f"{i}. {name_kr} ({name}) - {r['edge_cnt']}개")

print("\n=== 3. DLQ 2건 내용 확인 ===")
try:
    conn = sqlite3.connect("candidates.db")
    cursor = conn.cursor()
    cursor.execute("""
        SELECT skill_name, candidate_name, detected_at
        FROM unknown_skills
        ORDER BY detected_at DESC
        LIMIT 5
    """)
    dlq_rows = cursor.fetchall()
    
    if not dlq_rows:
        print("unknown_skills 테이블이 비어 있습니다.")
    else:
        for row in dlq_rows:
            print(f"Skill: {row[0]}, Candidate: {row[1]}, Date: {row[2]}")
            
    conn.close()
except Exception as e:
    print(f"DLQ 조회 중 에러: {e}")
