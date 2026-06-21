import json
from neo4j import GraphDatabase

s = json.load(open('secrets.json'))
driver = GraphDatabase.driver(s['NEO4J_URI'], auth=(s['NEO4J_USERNAME'], s['NEO4J_PASSWORD']))
with driver.session() as session:
    c = session.run('MATCH (c:Candidate) RETURN COUNT(c) as n').single()['n']
    sk = session.run('MATCH (s:Skill) RETURN COUNT(s) as n').single()['n']
    e = session.run('MATCH ()-[r]->(:Skill) RETURN COUNT(r) as n').single()['n']
    print('Candidate:', c)
    print('Skill:', sk)
    print('Edge:', e)
driver.close()
