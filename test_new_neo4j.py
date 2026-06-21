import json, sys
from neo4j import GraphDatabase
sys.stdout.reconfigure(encoding='utf-8')

s = json.load(open('secrets.json'))
driver = GraphDatabase.driver(s['NEO4J_URI'], auth=(s['NEO4J_USERNAME'], s['NEO4J_PASSWORD']))
with driver.session() as session:
    r = session.run('RETURN 1 AS n').single()
    print('Neo4j 연결 성공:', r['n'])

driver.close()
