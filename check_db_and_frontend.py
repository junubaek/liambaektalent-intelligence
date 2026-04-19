import sqlite3
import json
from neo4j import GraphDatabase
from jd_compiler import parse_jd_to_json

with open("secrets.json", "r", encoding="utf-8") as f:
    secrets = json.load(f)
driver = GraphDatabase.driver("neo4j://127.0.0.1:7687", auth=("neo4j", "toss1234"))

print("=== 1. 프론트엔드 엣지 직접 확인 ===")
with driver.session() as session:
    res = session.run("""
        MATCH (c:Candidate)-[r]->(s:Skill)
        WHERE s.name = 'Frontend_Development'
        RETURN c.name_kr, c.name, type(r)
        LIMIT 10
    """)
    records = res.fetch_action() if hasattr(res, 'fetch_action') else res.data()
    for rec in records:
        print(f"Name_Kr: {rec['c.name_kr']} / Name: {rec['c.name']} / Action: {rec['type(r)']}")

print("\n=== 2. 프론트엔드 검색 시 매핑 진단 ===")
q = "프론트엔드 개발자 React"
result = parse_jd_to_json(q)
conds = result.get('conditions', [])
mandatories = [c for c in conds if c.get('is_mandatory')]
print(f"'{q}' -> 총 {len(conds)}개 조건 중 Mandatory {len(mandatories)}개")
for idx, c in enumerate(conds):
    print(f" - {idx+1}. {c['skill']} (Mandatory: {c['is_mandatory']})")

print("\n=== 3. 0건 쿼리 키워드 기반 SQLite 모수 확인 ===")
conn = sqlite3.connect("candidates.db")
cursor = conn.cursor()

sqls = [
    ("그로스", """
        SELECT count(*) FROM candidates
        WHERE lower(raw_text) LIKE '%그로스%'
           OR lower(raw_text) LIKE '%growth hacking%'
    """),
    ("해외 영업", """
        SELECT count(*) FROM candidates  
        WHERE lower(raw_text) LIKE '%해외영업%'
           OR lower(raw_text) LIKE '%글로벌 영업%'
           OR lower(raw_text) LIKE '%수출%'
    """),
    ("조직문화", """
        SELECT count(*) FROM candidates
        WHERE lower(raw_text) LIKE '%조직문화%'
           OR lower(raw_text) LIKE '%culture%'
    """),
    ("풀스택", """
        SELECT count(*) FROM candidates
        WHERE lower(raw_text) LIKE '%풀스택%'
           OR lower(raw_text) LIKE '%fullstack%'
           OR lower(raw_text) LIKE '%full stack%'
    """)
]

for label, sql in sqls:
    cursor.execute(sql)
    cnt = cursor.fetchone()[0]
    print(f"[{label}] 통과 인원: {cnt}명")

conn.close()
