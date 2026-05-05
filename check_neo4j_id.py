from neo4j import GraphDatabase

driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "toss1234"))

with driver.session() as session:
    res = session.run("MATCH (n:Candidate) WHERE n.name_kr CONTAINS '은형' RETURN n.id as id, n.name_kr as name")
    for r in res:
        print(f"ID: '{r['id']}' (Length: {len(r['id'])})")
        print(f"Name: '{r['name']}'")
        print(f"ID Hex: {r['id'].encode('utf-8').hex()}")

driver.close()
