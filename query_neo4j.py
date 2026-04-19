from neo4j import GraphDatabase

uri = "neo4j://127.0.0.1:7687"
auth = ("neo4j", "toss1234")

try:
    driver = GraphDatabase.driver(uri, auth=auth)
    with driver.session() as session:
        query = "MATCH (c:Candidate)-[r]->(s:Skill) RETURN count(r) as total_edges, count(DISTINCT c) as total_cands"
        res = session.run(query).single()
        print(f"Total Edges: {res['total_edges']}")
        print(f"Total Candidates w/ Edges: {res['total_cands']}")
        
        # Test just relationships in general
        query2 = "MATCH ()-[r]->() RETURN count(r) as total_all_edges"
        res2 = session.run(query2).single()
        print(f"Total All Edges in DB: {res2['total_all_edges']}")
        
        # Test Nodes in general
        query3 = "MATCH (n) RETURN count(n) as total_nodes"
        res3 = session.run(query3).single()
        print(f"Total All Nodes in DB: {res3['total_nodes']}")
        
        # Test [r:HAS_SKILL] specifically
        query4 = "MATCH (c:Candidate)-[r:HAS_SKILL]->(s:Skill) RETURN count(r) as has_skill_edges"
        res4 = session.run(query4).single()
        print(f"Total HAS_SKILL Edges: {res4['has_skill_edges']}")
        
except Exception as e:
    print(f"Error: {e}")
finally:
    if 'driver' in locals():
        driver.close()
print("Done.")
