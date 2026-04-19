from neo4j import GraphDatabase
driver = GraphDatabase.driver("neo4j://127.0.0.1:7687", auth=("neo4j", "toss1234"))
with driver.session() as session:
    res = session.run("MATCH (n) DETACH DELETE n")
    res_count = session.run("MATCH (n) RETURN COUNT(n) as cnt")
    for r in res_count:
        print(f"Remaining nodes: {r['cnt']}")
