import os, sys
from neo4j import GraphDatabase
sys.stdout.reconfigure(encoding='utf-8')
uri = os.getenv('NEO4J_URI')
user = os.getenv('NEO4J_USERNAME')
pwd = os.getenv('NEO4J_PASSWORD')
if not uri or not user or not pwd:
    print('환경 변수 중 하나가 누락되었습니다')
    sys.exit(1)
driver = GraphDatabase.driver(uri, auth=(user, pwd))
with driver.session() as session:
    result = session.run('RETURN 1 AS n').single()
    print('Neo4j 연결 성공:', result['n'])
driver.close()
