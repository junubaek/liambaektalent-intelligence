import json
from neo4j import GraphDatabase
with open(r"C:\Users\cazam\Downloads\이력서자동분석검색시스템\secrets.json", "r", encoding="utf-8") as f:
    s = json.load(f)
driver = GraphDatabase.driver(s['NEO4J_URI'], auth=(s['NEO4J_USERNAME'], s['NEO4J_PASSWORD']))
with driver.session() as session:
    r = session.run('MATCH (c:Candidate) RETURN COUNT(c) as cnt')
    print(f'Neo4j 전체: {r.single()["cnt"]}명')
driver.close()
