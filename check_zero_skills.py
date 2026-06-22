import json
s = json.load(open('secrets.json', encoding='utf-8'))
from neo4j import GraphDatabase
driver = GraphDatabase.driver(s['NEO4J_URI'], auth=(s['NEO4J_USERNAME'], s['NEO4J_PASSWORD']))
with driver.session() as sess:
    r = sess.run('''
        MATCH (c:Candidate)
        WHERE NOT (c)-[]->(:Skill)
        RETURN count(c) as cnt
    ''')
    print('Candidates with ZERO skills:', r.single()['cnt'])
    
    r2 = sess.run('''
        MATCH (c:Candidate)
        WHERE (c)-[]->(:Skill)
        RETURN count(c) as cnt
    ''')
    print('Candidates WITH skills:', r2.single()['cnt'])
driver.close()
