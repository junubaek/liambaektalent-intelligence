import re
from neo4j import GraphDatabase

def find_coo_candidates_and_inject():
    uri = "neo4j://127.0.0.1:7687"
    driver = GraphDatabase.driver(uri, auth=("neo4j", "toss1234"))
    
    with driver.session() as session:
        names = ["이범기"] # known candidate
        print("Injecting COO for:", names)
        
        inject_query = """
        MATCH (c:Candidate)
        WHERE c.name_kr IN $names
        MERGE (s:Skill {name: 'Chief_Operating_Officer'})
        MERGE (c)-[:MANAGED]->(s)
        MERGE (c)-[:BUILT]->(s)
        RETURN c.name_kr
        """
        res_inj = session.run(inject_query, names=names)
        injected = [r["c.name_kr"] for r in res_inj]
        print("Successfully injected MANAGED/BUILT:Chief_Operating_Officer for:", injected)

    driver.close()

if __name__ == "__main__":
    find_coo_candidates_and_inject()
