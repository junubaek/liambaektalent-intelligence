import json
from neo4j import GraphDatabase

secrets = json.load(open('secrets.json', encoding='utf-8'))
driver = GraphDatabase.driver(secrets['NEO4J_URI'], auth=(secrets['NEO4J_USERNAME'], secrets['NEO4J_PASSWORD']))
session = driver.session()

# 전체 관계 수
cnt = session.run('MATCH ()-[r]->() RETURN count(r)').single()[0]
print(f'전체 엣지: {cnt}개')

# 김국현 엣지 확인
edges = session.run('''
    MATCH (c:Candidate {name_kr: "김국현"})-[r]->(s:Skill)
    RETURN type(r) as type, s.name as skill_name
''').data()
print(f'김국현 엣지: {len(edges)}개')
for e in edges[:10]:
    print(f"  {e.get('type')} -> {e.get('skill_name')}")

driver.close()
