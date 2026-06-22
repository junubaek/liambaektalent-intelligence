import json, sys, codecs
sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer)
from neo4j import GraphDatabase
s = json.load(open('secrets.json', encoding='utf-8'))
driver = GraphDatabase.driver(s['NEO4J_URI'], auth=(s['NEO4J_USERNAME'], s['NEO4J_PASSWORD']))
with driver.session() as sess:
    # 배유정 스킬 확인
    r = sess.run("""
        MATCH (c:Candidate {id: '028449d0-5ae4-46cf-b403-20f23e1e5fab'})-[e]->(s:Skill)
        RETURN type(e) as rel, s.name as skill
    """)
    rows = list(r)
    print('배유정 skills:', len(rows))
    for row in rows:
        print(' ', row['rel'], row['skill'])
    
    # PR 관련 스킬 노드 존재 확인
    r2 = sess.run("MATCH (s:Skill) WHERE s.name IN ['Public_Relations','Corporate_PR','PR_Campaign_Planning'] RETURN s.name")
    print('PR canonical nodes:', [r['s.name'] for r in r2])
    
    # Team Leadership 매핑 확인
    r3 = sess.run("MATCH (s:Skill) WHERE s.name = 'Team Leadership' RETURN count(s) as cnt")
    print('Team Leadership still exists:', r3.single()['cnt'])
    
    r4 = sess.run("MATCH (s:Skill) WHERE s.name = 'Team_Leadership' RETURN count(s) as cnt")  
    print('Team_Leadership (canonical) exists:', r4.single()['cnt'])

driver.close()
