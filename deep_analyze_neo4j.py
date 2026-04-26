import json, sys
sys.stdout.reconfigure(encoding='utf-8')
from neo4j import GraphDatabase

def run_deep_analysis():
    with open('secrets.json', 'r', encoding='utf-8') as f:
        secrets = json.load(f)

    driver = GraphDatabase.driver(
        secrets.get('NEO4J_URI'),
        auth=(secrets.get('NEO4J_USERNAME'), secrets.get('NEO4J_PASSWORD'))
    )

    with driver.session() as s:
        # 1. 의심 더미 노드 확인
        print('=== 1. 의심 더미 노드 확인 (Pattern: *22567) ===')
        q1_count = 'MATCH (c:Candidate) WHERE c.id ENDS WITH "22567" RETURN count(c) as cnt'
        count_res = s.run(q1_count).single()
        count = count_res['cnt'] if count_res else 0
        print(f'패턴 매칭 노드 수: {count}')
        
        q1_samples = 'MATCH (c:Candidate) WHERE c.id ENDS WITH "22567" RETURN c.id as id, c.name_kr as name, c.phone as phone, c.email as email, c.profile_summary as summary LIMIT 5'
        samples = s.run(q1_samples).data()
        for r in samples:
            print(f'  ID: {r["id"][:8]} | 이름: {r["name"]} | 연락처: {r["phone"]} | 이메일: {r["email"]} | 요약: {str(r["summary"])[:50]}...')

        # 2. 동명이인 분류
        print('\n=== 2. 동명이인 분류 (진짜 vs 중복등록) ===')
        # Use APOC if possible, or fallback logic. 
        # Actually, let's just do it in Python to be safe and clear.
        q2_data = '''
        MATCH (c:Candidate)
        WHERE c.name_kr IS NOT NULL
        WITH c.name_kr as name, 
             collect({phone: c.phone, email: c.email}) as contacts,
             count(c) as cnt
        WHERE cnt > 1
        RETURN name, cnt, contacts
        ORDER BY cnt DESC
        LIMIT 20
        '''
        res2 = s.run(q2_data).data()
        for r in res2:
            name = r['name']
            cnt = r['cnt']
            contacts = r['contacts']
            
            # Filter None
            phones = [c['phone'] for c in contacts if c['phone']]
            emails = [c['email'] for c in contacts if c['email']]
            
            unique_phones = len(set(phones))
            unique_emails = len(set(emails))
            
            # Classification
            if (len(phones) > 0 and unique_phones < len(phones)) or (len(emails) > 0 and unique_emails < len(emails)):
                ctype = '중복등록의심'
            else:
                ctype = '진짜동명이인'
                
            print(f'{name}({cnt}): {ctype} | phones: {phones} | emails: {emails}')

    driver.close()

if __name__ == "__main__":
    run_deep_analysis()
