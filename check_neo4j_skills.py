import json
s = json.load(open('secrets.json', encoding='utf-8'))
from neo4j import GraphDatabase
driver = GraphDatabase.driver(s['NEO4J_URI'], auth=(s['NEO4J_USERNAME'], s['NEO4J_PASSWORD']))
with driver.session() as sess:
    cnt = sess.run('MATCH (s:Skill) RETURN count(s) as cnt').single()['cnt']
    print('Total Skill nodes:', cnt)
    cnt_space = sess.run("MATCH (s:Skill) WHERE s.name CONTAINS ' ' RETURN count(s) as cnt").single()['cnt']
    print('Skill nodes with spaces:', cnt_space)
    cnt_nospace = cnt - cnt_space
    print('Skill nodes without spaces:', cnt_nospace)
driver.close()
