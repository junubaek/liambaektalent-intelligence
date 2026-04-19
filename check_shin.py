from neo4j import GraphDatabase

driver = GraphDatabase.driver('bolt://127.0.0.1:7687', auth=('neo4j', 'toss1234'))
res = driver.session().run("MATCH (c:Candidate {name_kr: '신정용'})-[r]->(s) RETURN type(r) AS rel_type, s.name AS skill")

print("Edges for 신정용:")
for r in res:
    print(f"- [{r['rel_type']}] -> {r['skill']}")
    
driver.close()
