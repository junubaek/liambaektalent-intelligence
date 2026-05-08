import json
from neo4j import GraphDatabase

with open('secrets.json', 'r', encoding='utf-8') as f:
    secrets = json.load(f)

driver = GraphDatabase.driver(secrets['NEO4J_URI'], auth=(secrets['NEO4J_USERNAME'], secrets['NEO4J_PASSWORD']))

with driver.session() as session:
    # 전체 후보자 수
    total = session.run('MATCH (c:Candidate) RETURN count(c) as n').single()['n']
    
    # 스킬 엣지가 있는 후보자 수
    with_skills = session.run('MATCH (c:Candidate)-[r]->(s:Skill) WITH c, count(r) as cnt WHERE cnt > 0 RETURN count(c) as n').single()['n']
    
    no_skills = total - with_skills
    
    print(f'전체 후보자: {total}명')
    if total > 0:
        print(f'스킬 있음: {with_skills}명 ({with_skills/total*100:.1f}%)')
        print(f'스킬 없음: {no_skills}명 ({no_skills/total*100:.1f}%)')
    else:
        print('후보자가 없습니다.')

    # 스킬 있는 후보자의 평균 스킬 수
    avg_res = session.run('MATCH (c:Candidate)-[r]->(s:Skill) WITH c, count(r) as cnt RETURN avg(cnt) as avg').single()
    avg = avg_res['avg'] if avg_res['avg'] else 0
    print(f'스킬 있는 후보자 평균 스킬 수: {avg:.1f}개')

driver.close()
