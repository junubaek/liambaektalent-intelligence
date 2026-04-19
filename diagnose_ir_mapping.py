import sqlite3
from neo4j import GraphDatabase

def run_diagnostic():
    # 1. SQLite에서 IR 관련 후보자의 이름을 가져옵니다 (정확도를 위해 이름+전화번호 등 고유키가 좋으나, 
    # Neo4j 스키마 호환을 위해 일단 candidate.name 사용 또는 고유 contact 값 사용)
    # Neo4j Candidate 노드가 id: Name_Phone 형태라면 해당 규칙을 알아야 함
    # 우선 가장 쉬운건 Neo4j에서 raw_text/resume_text 속성이 있는지 확인하거나
    # 아니면 SQLite에서 name을 추출합니다.
    
    conn = sqlite3.connect('C:/Users/cazam/Downloads/이력서자동분석검색시스템/candidates.db')
    c = conn.cursor()
    c.execute("""
        SELECT name, phone FROM candidates
        WHERE raw_text LIKE '%IR%'
           OR raw_text LIKE '%투자자관계%'
           OR raw_text LIKE '%Investor Relations%'
    """)
    rows = c.fetchall()
    conn.close()
    
    if not rows:
        print("SQLite에서 IR 관련 후보자를 찾지 못했습니다.")
        return
        
    names = [r[0] for r in rows if r[0]]
    # 일부 동명이인이나 특수문자 등을 위해 중복 제거
    names = list(set(names))
    
    print(f"✅ SQLite에서 추출된 IR 포함 후보자 수 (고유 이름 기준): {len(names)}명")
    
    # 2. Neo4j 조회
    uri = 'neo4j://127.0.0.1:7687'
    auth = ('neo4j', 'toss1234')
    
    try:
        driver = GraphDatabase.driver(uri, auth=auth)
        with driver.session() as session:
            # 2-A: 이 그룹 전체가 가지고 있는 스킬 Top 20 조회
            # Neo4j query with UNWIND for efficient IN clause
            query_skills = """
                UNWIND $names AS candidate_name
                MATCH (c:Candidate)
                WHERE c.name = candidate_name // 혹은 id 규칙에 따라 다를 수 있음
                MATCH (c)-[r]->(s:Skill)
                RETURN s.name as skill_name, count(r) as cnt
                ORDER BY cnt DESC
                LIMIT 20
            """
            result_skills = session.run(query_skills, names=names)
            
            print("\n📊 [Top 20 매핑 노드 현황 (IR텍스트 보유자들 기준)]")
            total_edges = 0
            for record in result_skills:
                print(f" - {record['skill_name']}: {record['cnt']}개")
                total_edges += record['cnt']
                
            if total_edges == 0:
                 print(" - (매핑된 엣지가 전혀 없습니다.)")
                 
            # 2-B: 엣지가 하나도 없는 사람(Neo4j 누락자) 비율 조회
            query_missing = """
                UNWIND $names AS candidate_name
                MATCH (c:Candidate)
                WHERE c.name = candidate_name
                OPTIONAL MATCH (c)-[r]->(:Skill)
                WITH c, count(r) as edge_count
                WHERE edge_count = 0
                RETURN count(c) as zero_edge_count
            """
            res_missing = session.run(query_missing, names=names)
            zero_edge_in_neo4j = res_missing.single()['zero_edge_count']
            
            # Neo4j에 아예 등록 안된 사람(이름으로 매칭 안되는 사람) 계산
            query_exists = """
                UNWIND $names AS candidate_name
                MATCH (c:Candidate)
                WHERE c.name = candidate_name
                RETURN count(c) as exists_count
            """
            res_exists = session.run(query_exists, names=names)
            exists_in_neo4j = res_exists.single()['exists_count']
            
            print("\n📈 [엣지 및 노드 누락 현황]")
            print(f" - Neo4j에 노드(Candidate)로 존재하는 사람: {exists_in_neo4j} / {len(names)}")
            print(f" - 노드는 존재하나, 엣지(Skill)가 하나도 없는(0개) 사람: {zero_edge_in_neo4j}명")
            
    except Exception as e:
        print(f"Neo4j 쿼리 에러: {str(e)}")

run_diagnostic()
