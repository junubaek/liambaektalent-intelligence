from neo4j import GraphDatabase
driver = GraphDatabase.driver('neo4j://127.0.0.1:7687', auth=('neo4j', 'toss1234'))
res = driver.session().run('MATCH (c:Candidate) RETURN c LIMIT 1').single()
if res:
    node = res[0]
    print(list(node.keys()))
driver.close()
