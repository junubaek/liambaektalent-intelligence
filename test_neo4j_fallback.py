import os, sys
from neo4j import GraphDatabase
sys.stdout.reconfigure(encoding='utf-8')
uri = os.getenv('NEO4J_URI')
user = os.getenv('NEO4J_USERNAME')
pwd = os.getenv('NEO4J_PASSWORD')
if not uri:
    print('NEO4J_URI missing')
    sys.exit(1)
# Try with encryption disabled if +s present
if uri.startswith('neo4j+s://'):
    uri = uri.replace('neo4j+s://', 'neo4j://')
    encrypted = False
else:
    encrypted = True

driver = GraphDatabase.driver(uri, auth=(user, pwd), encrypted=encrypted)
with driver.session() as session:
    result = session.run('RETURN 1 AS n').single()
    print('Neo4j 연결 성공:', result['n'])

driver.close()
