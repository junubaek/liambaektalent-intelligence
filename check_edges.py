from neo4j import GraphDatabase

driver = GraphDatabase.driver("bolt://127.0.0.1:7687", auth=("neo4j", "toss1234"))
with driver.session() as session:
    res = session.run("MATCH ()-[r:USED]->() WHERE r.source='booster_scan' RETURN count(r)")
    print("Booster Edges Injected:", res.single()[0])
