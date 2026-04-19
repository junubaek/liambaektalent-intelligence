from neo4j import GraphDatabase

def run_checks():
    driver = GraphDatabase.driver("neo4j://127.0.0.1:7687", auth=("neo4j", "toss1234"))
    
    print("="*50)
    print("📋 [최종 검증 리포트]")
    print("="*50)
    
    with driver.session() as session:
        # 1. Total Count
        res = session.run("MATCH (c:Candidate) RETURN count(c) as cnt")
        total = res.single()['cnt']
        print(f"1. 총 후보자 수 (Neo4j): {total}명")
        
        # 2. 동명이인 처리 확인 (김현우)
        print("\n2. 동명이인 분리 확인 (상위 5건 그룹):")
        res2 = session.run("""
            MATCH (c:Candidate)
            WITH c.name_kr as kr, collect(c.name) as names, count(c) as cnt
            WHERE cnt > 1 AND kr IS NOT NULL
            RETURN kr, names, cnt ORDER BY cnt DESC LIMIT 5
        """)
        for r in res2:
            print(f"  - {r['kr']} ({r['cnt']}명): {r['names'][:3]} ...")
            
        # 3. 괴물 노드 사라졌는지
        print("\n3. 과거 괴물 노드 잔존 여부 ('마케터', '언론홍보', '경력기술' 등):")
        res3 = session.run("""
            MATCH (c:Candidate)
            WHERE c.name_kr IN ['마케터', '언론홍보', '경력기술', '자금', '임원', 'None']
            RETURN c.name_kr, count(c) as cnt
        """)
        monster_found = False
        for r in res3:
            monster_found = True
            print(f"  - [잔존] {r['c.name_kr']} 그룹명으로 보유: {r['cnt']}명")
        if not monster_found: print("  - ✅ 완벽히 사라짐 (발견 0건)")
        
        # 4. 딥 리페어 필요 대상 노드 확인
        print("\n4. 딥 리페어 모니터링 고위험 노드 엣지 상태:")
        deep_nodes = ['IR', 'BD', 'Brand', 'SCM', 'Treasury', 'Funding', 'Accounting', 'Marketing', 'HR', 'CRM', 'TA', 'C&B', 'ER']
        res4 = session.run("""
            MATCH (s:Skill)
            WHERE s.name IN $nodes
            OPTIONAL MATCH (c:Candidate)-[r]->(s)
            RETURN s.name as skill, count(r) as edge_count
            ORDER BY edge_count ASC
        """, nodes=deep_nodes)
        for r in res4:
            print(f"  - 노드 [{r['skill']}]: 연결 엣지 {r['edge_count']}건")
            
        # 5. 평균 엣지 수
        print("\n5. 전체 평균 엣지 수:")
        res5 = session.run("""
            MATCH (c:Candidate)-[r]->(s:Skill)
            RETURN count(r)*1.0 / count(DISTINCT c) AS avg_edges
        """)
        avg = res5.single()['avg_edges']
        avg = avg if avg else 0.0
        print(f"  - 후보자당 약 {avg:.2f}개")
        
    print("="*50)

if __name__ == '__main__':
    run_checks()
