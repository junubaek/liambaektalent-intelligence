import json, sys
from neo4j import GraphDatabase

def final_check():
    with open('secrets.json', 'r', encoding='utf-8') as f:
        secrets = json.load(f)
    driver = GraphDatabase.driver(secrets.get('NEO4J_URI'), auth=(secrets.get('NEO4J_USERNAME'), secrets.get('NEO4J_PASSWORD')))
    
    with driver.session() as s:
        # 1. 유효 데이터 보유 현황
        print('=== 1. 유효 데이터 보유 현황 ===')
        q1 = '''
        MATCH (c:Candidate)
        WHERE c.id STARTS WITH '32' OR c.id STARTS WITH '33'
        RETURN 
          count(c) as total,
          count(c.name_kr) as has_name,
          count(c.phone) as has_phone,
          count(c.email) as has_email,
          count(c.profile_summary) as has_summary
        '''
        res1 = s.run(q1).single()
        print(f'전체 대상: {res1["total"]}명')
        print(f'이름 보유: {res1["has_name"]}명')
        print(f'전화번호 보유: {res1["has_phone"]}명')
        print(f'이메일 보유: {res1["has_email"]}명')
        print(f'요약 보유: {res1["has_summary"]}명')
        
        # 2. 임베딩 보유 현황
        print('\n=== 2. 임베딩 보유 현황 ===')
        q2 = '''
        MATCH (c:Candidate)
        WHERE c.id STARTS WITH '32' OR c.id STARTS WITH '33'
        RETURN
          count(CASE WHEN c.embedding IS NOT NULL THEN 1 END) as has_emb,
          count(CASE WHEN c.embedding IS NULL THEN 1 END) as no_emb
        '''
        res2 = s.run(q2).single()
        print(f'임베딩 있음: {res2["has_emb"]}명')
        print(f'임베딩 없음: {res2["no_emb"]}명')
        
        # 3. 엣지 현황
        print('\n=== 3. 엣지(스킬) 보유 현황 ===')
        q3 = '''
        MATCH (c:Candidate)-[r]->(s:Skill)
        WHERE c.id STARTS WITH '32' OR c.id STARTS WITH '33'
        RETURN count(r) as edge_count
        '''
        res3 = s.run(q3).single()
        print(f'총 스킬 연결(엣지) 수: {res3["edge_count"]}')
        
    driver.close()

if __name__ == "__main__":
    final_check()
