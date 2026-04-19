import sqlite3
import json
from neo4j import GraphDatabase
from ontology_graph import CANONICAL_MAP

with open("secrets.json", "r", encoding="utf-8") as f:
    secrets = json.load(f)
driver = GraphDatabase.driver("neo4j://127.0.0.1:7687", auth=("neo4j", "toss1234"))

def sync_neo4j():
    print("=== 1. Neo4j 프로퍼티 동기화 시작 ===")
    conn = sqlite3.connect("candidates.db")
    cursor = conn.cursor()
    cursor.execute("SELECT document_hash, name_kr, phone, email FROM candidates")
    rows = cursor.fetchall()
    conn.close()

    with driver.session() as session:
        count = 0
        for row in rows:
            doc_hash, name_kr, phone, email = row
            session.run("""
                MATCH (c:Candidate {id: $doc_hash})
                SET c.name_kr = $name_kr,
                    c.name = $name_kr,
                    c.phone = $phone,
                    c.email = $email
            """, doc_hash=doc_hash, name_kr=name_kr, phone=phone, email=email)
            count += 1
            if count % 500 == 0:
                print(f"{count}명 업데이트 완료...")
                
        print(f"총 {count}명 프로퍼티 업데이트 완료!\n")
        
        print("=== 동기화 후 중복 이름 점검 ===")
        res = session.run("""
            MATCH (c:Candidate)
            WITH c.name_kr as name, count(c) as cnt
            WHERE cnt > 3
            RETURN name, cnt
            ORDER BY cnt DESC
            LIMIT 10
        """)
        for r in res:
            print(f"{r['name']}: {r['cnt']}명")

def clean_dlq():
    print("\n=== 2. DLQ(unknown_skills) 찌꺼기 정리 ===")
    conn = sqlite3.connect("candidates.db")
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT skill_name FROM unknown_skills")
    skills = [r[0] for r in cursor.fetchall()]
    
    deleted = 0
    with driver.session() as session:
        for skill in skills:
            res = session.run("MATCH ()-[]->(s:Skill {name: $skill}) RETURN count(s) as cnt", skill=skill)
            edge_exists = res.single()['cnt'] > 0
            
            is_mapped = skill in CANONICAL_MAP or skill in CANONICAL_MAP.values()
            
            if edge_exists or is_mapped:
                cursor.execute("DELETE FROM unknown_skills WHERE skill_name = ?", (skill,))
                deleted += cursor.rowcount
                print(f"삭제됨(유효 노드 판정): {skill}")
            else:
                print(f"유지됨(미식별 노드): {skill}")
                
    conn.commit()
    cursor.execute("SELECT count(*) FROM unknown_skills")
    remains = cursor.fetchone()[0]
    conn.close()
    print(f"\n총 {deleted}건의 DLQ 레코드를 삭제했습니다. 남은 DLQ: {remains}건")

if __name__ == "__main__":
    sync_neo4j()
    clean_dlq()
