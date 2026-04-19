from neo4j import GraphDatabase
from jd_compiler import api_search_v8
import json

with open("secrets.json", "r", encoding="utf-8") as f:
    secrets = json.load(f)
driver = GraphDatabase.driver("neo4j://127.0.0.1:7687", auth=("neo4j", "toss1234"))

nodes = [
    "Frontend_Development", "Mobile_iOS", "Android_Development",
    "Data_Science_and_Analysis", "UX_UI_Design", "Growth_Marketing",
    "해외영업", "Organizational_Development", "Fullstack_Development"
]

print("=== Neo4j Edge Counts ===")
with driver.session() as session:
    res = session.run("""
        MATCH (c:Candidate)-[r]->(s:Skill)
        WHERE s.name IN $nodes
        RETURN s.name as skill, count(r) as cnt
        ORDER BY cnt DESC
    """, nodes=nodes)
    for rec in res:
        print(f"{rec['skill']}: {rec['cnt']}")

print("\n=== Re-testing 0-hit Queries ===")
test_queries = [
    "프론트엔드 개발자",
    "iOS 개발자",
    "안드로이드 개발자",
    "데이터 분석가",
    "UX 디자이너",
    "그로스 마케터",
    "해외 영업",
    "조직문화 담당자",
    "풀스택 개발자"
]

print("쿼리 | 검색 결과 (명)")
print("---|---")
for q in test_queries:
    try:
        res = api_search_v8(prompt=q)
        cnt = len(res.get('matched', []))
        print(f"{q} | {cnt}")
    except Exception as e:
        print(f"{q} | ERROR: {e}")
