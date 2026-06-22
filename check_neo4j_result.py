import json
s = json.load(open('secrets.json', encoding='utf-8'))
from neo4j import GraphDatabase
driver = GraphDatabase.driver(s['NEO4J_URI'], auth=(s['NEO4J_USERNAME'], s['NEO4J_PASSWORD']))
with driver.session() as sess:
    cnt_c = sess.run('MATCH (c:Candidate) RETURN count(c) as cnt').single()['cnt']
    cnt_s = sess.run('MATCH (s:Skill) RETURN count(s) as cnt').single()['cnt']
    cnt_e = sess.run('MATCH ()-[e]->(:Skill) RETURN count(e) as cnt').single()['cnt']
    cnt_space = sess.run("MATCH (s:Skill) WHERE s.name CONTAINS ' ' RETURN count(s) as cnt").single()['cnt']
    print('Candidates:', cnt_c)
    print('Skill nodes:', cnt_s)
    print('Skill edges:', cnt_e)
    print('Non-canonical nodes:', cnt_space)
    pct = cnt_space/cnt_s*100 if cnt_s else 0
    print(f'Non-canonical ratio: {pct:.1f}%')
driver.close()
