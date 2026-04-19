from neo4j import GraphDatabase
driver = GraphDatabase.driver('bolt://127.0.0.1:7687', auth=('neo4j', 'toss1234'))
res=driver.execute_query("MATCH (c:Candidate)-[r:BUILT|DESIGNED|MANAGED|ANALYZED|SUPPORTED|NEGOTIATED|GREW|LAUNCHED|LED|OPTIMIZED|PLANNED|EXECUTED]->(s:Skill) WHERE s.name = 'Treasury_Management' RETURN c.name_kr, count(s) AS cnt ORDER BY cnt DESC LIMIT 10")[0]
print([(r['c.name_kr'], r['cnt']) for r in res])
