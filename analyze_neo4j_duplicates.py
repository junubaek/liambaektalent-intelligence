import json
from neo4j import GraphDatabase

def run_analysis():
    with open('secrets.json', 'r', encoding='utf-8') as f:
        secrets = json.load(f)

    driver = GraphDatabase.driver(
        secrets.get('NEO4J_URI'),
        auth=(secrets.get('NEO4J_USERNAME'), secrets.get('NEO4J_PASSWORD'))
    )

    with driver.session() as s:
        # 1. 중복 name_kr 현황
        print('=== 1. 중복 name_kr 현황 (Top 20) ===')
        q1 = '''
        MATCH (c:Candidate)
        WITH c.name_kr as name, collect(c.id) as ids, count(c) as cnt
        WHERE cnt > 1
        RETURN name, cnt, ids
        ORDER BY cnt DESC
        LIMIT 20
        '''
        res1 = s.run(q1).data()
        for r in res1:
            name = r['name']
            cnt = r['cnt']
            ids = [i[:8] for i in r['ids']]
            print(f'{name}: {cnt}명 | IDs: {ids}')
        
        # 2. 전체 중복 규모
        print('\n=== 2. 전체 중복 규모 ===')
        q2 = '''
        MATCH (c:Candidate)
        WITH c.name_kr as name, count(c) as cnt
        WHERE cnt > 1
        RETURN count(*) as duplicate_names, sum(cnt) as affected_candidates
        '''
        res2 = s.run(q2).single()
        print(f'중복 이름 수: {res2["duplicate_names"]}')
        print(f'영향 받는 후보자 수: {res2["affected_candidates"]}')
        
        # 3. 샘플 1건 상세 조회
        target_name = next((r['name'] for r in res1 if r['name'] is not None), None)
        if target_name:
            print(f'\n=== 3. 샘플 상세 조회 (이름: {target_name}) ===')
            q3 = '''
            MATCH (c:Candidate {name_kr: $name})
            RETURN c.id as id, c.name_kr as name, c.phone as phone, c.email as email, c.current_company as company, c.seniority as seniority
            '''
            res3 = s.run(q3, name=target_name).data()
            for r in res3:
                print(f'ID: {r["id"][:8]} | 이름: {r["name"]} | 연락처: {r["phone"]} | 이메일: {r["email"]} | 현직: {r["company"]} | 연차: {r["seniority"]}')

    driver.close()

if __name__ == "__main__":
    run_analysis()
