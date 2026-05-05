from neo4j import GraphDatabase

driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "toss1234"))

with driver.session() as session:
    print("--- Vector Indexes ---")
    res = session.run("SHOW INDEXES YIELD name, type, labelsOrTypes, properties WHERE type = 'VECTOR'")
    for r in res:
        print(r)
        
    print("\n--- Check Kim Eun Hyung Embedding ---")
    # Check if she has an embedding property
    res = session.run("MATCH (n:Candidate {id: 'f5875fc2-99aa-4605-9742-5ec93f4cd51a'}) RETURN n.name_kr, keys(n) as props, n.embedding IS NOT NULL as has_embedding")
    for r in res:
        print(f"Name: {r['n.name_kr']}")
        print(f"Props: {r['props']}")
        print(f"Has Embedding: {r['has_embedding']}")

driver.close()
