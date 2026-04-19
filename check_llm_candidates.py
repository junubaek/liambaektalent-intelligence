import sys
sys.stdout.reconfigure(encoding='utf-8')
from neo4j import GraphDatabase

driver = GraphDatabase.driver('bolt://127.0.0.1:7687', auth=('neo4j', 'toss1234'))

with driver.session() as s:
    print('--- 이보미 ---')
    res = s.run("MATCH (c:Candidate {name_kr: '이보미'})-[r]->(sk:Skill) RETURN sk.name as skill")
    print([r['skill'] for r in res])
    
    print('--- 박용재 ---')
    res2 = s.run("MATCH (c:Candidate {name_kr: '박용재'})-[r]->(sk:Skill) RETURN sk.name as skill")
    print([r['skill'] for r in res2])

driver.close()
