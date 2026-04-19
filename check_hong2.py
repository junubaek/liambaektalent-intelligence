from neo4j import GraphDatabase
driver = GraphDatabase.driver('bolt://127.0.0.1:7687', auth=('neo4j', 'toss1234'))
res = driver.session().run("MATCH (c:Candidate {name_kr: '홍기재'})-[r]->(s) RETURN s.name")
print('홍기재 edges:', [r['s.name'] for r in res])
driver.close()
