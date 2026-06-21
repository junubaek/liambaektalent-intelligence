import json, sys
from neo4j import GraphDatabase
sys.stdout.reconfigure(encoding='utf-8')

s = json.load(open('secrets.json'))
uri = s['NEO4J_URI']
username = s['NEO4J_USERNAME']
password = s['NEO4J_PASSWORD']

driver = GraphDatabase.driver(uri, auth=(username, password))
with driver.session() as session:
    result = session.run('RETURN 1 AS n').single()
    print('Neo4j 연결 성공:', result['n'])

driver.close()
