import sqlite3
import os
import sys

# 프로젝트 루트 경로 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import jd_compiler

from neo4j import GraphDatabase

def repair_kim_daejung():
    # 1. 김대중 정보 가져오기
    conn = sqlite3.connect('candidates.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id, name_kr, document_hash FROM candidates WHERE name_kr LIKE '%김대중%' LIMIT 1")
    kim_info = cursor.fetchone()
    conn.close()
    
    if not kim_info:
        print("❌ 김대중님을 DB에서 찾을 수 없습니다.")
        return
        
    c_id, name, doc_hash = kim_info
    print(f"🎯 딥 리페어 타겟: {name} (Hash: {doc_hash})")

    # 2. Neo4j 연결 및 엣지 주입
    uri = "bolt://127.0.0.1:7687"
    driver = GraphDatabase.driver(uri, auth=("neo4j", "toss1234"))
    
    with driver.session() as session:
        # 기존 엣지 수 확인
        result = session.run("MATCH (c:Candidate {name_kr: '김대중'})-[r]->(s:Skill) RETURN count(r) as cnt")
        before_cnt = result.single()["cnt"]
        print(f"📊 기존 엣지 수: {before_cnt}개")
        
        # 엣지 딥 리페어 쿼리 (사용자가 명시한 핵심 스킬을 강한 동사로 추가)
        repair_query = """
        MATCH (c:Candidate {name_kr: '김대중'})
        
        // Cash Pooling, 해외법인 자금관리
        MERGE (s1:Skill {name: 'Treasury_Management'})
        MERGE (c)-[r1:BUILT]->(s1)
        MERGE (c)-[r2:MANAGED]->(s1)
        
        // 외국환 신고 
        MERGE (s2:Skill {name: 'FX_Dealing'})
        MERGE (c)-[r3:MANAGED]->(s2)
        
        // AR Factoring, 무역금융, 뱅킹 네트워크
        MERGE (s3:Skill {name: 'Corporate_Funding'})
        MERGE (c)-[r4:BUILT]->(s3)
        MERGE (c)-[r5:MANAGED]->(s3)
        MERGE (c)-[r6:NEGOTIATED]->(s3)
        
        // 추가로 자금결제(신디케이션론 등)
        MERGE (s4:Skill {name: 'Financial_Accounting'})
        MERGE (c)-[r7:MANAGED]->(s4)
        
        RETURN count(*)
        """
        session.run(repair_query)
        
        # Delete query removed to fix syntax error

        # 수정 후 엣지 수 확인
        result = session.run("MATCH (c:Candidate {name_kr: '김대중'})-[r]->(s:Skill) RETURN count(r) as cnt")
        after_cnt = result.single()["cnt"]
        print(f"🚀 리페어 후 엣지 수: {after_cnt}개 (+{after_cnt - before_cnt} 증가)")
        
    driver.close()

    print("\n===============================")
    print("🔍 랭킹 테스트: '6년차 이상 자금 담당자'")
    print("===============================")
    
    res = jd_compiler.api_search_v8("6년차 이상 자금 담당자")
    candidates = res.get("matched", res.get("candidates", []))
    
    found_rank = -1
    for idx, c in enumerate(candidates[:100]):
        rank = idx + 1
        c_name = c.get('이름', '')
        score = c.get('total_score', c.get('_score'))
        if rank <= 5 or "김대중" in c_name:
            print(f"[{rank}위] {c_name} | Score: {score}")
            if "김대중" in c_name:
                found_rank = rank
                
    if found_rank == -1:
        print("\n👉 아직 100위 안에 진입하지 못했습니다.")
    else:
        print(f"\n🎉 김대중님이 {found_rank}위로 랭크업했습니다!")

if __name__ == "__main__":
    repair_kim_daejung()
