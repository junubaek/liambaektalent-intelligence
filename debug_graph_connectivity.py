from neo4j import GraphDatabase

def debug_graph_search():
    uri = "neo4j+ssc://72de4959.databases.neo4j.io"
    user = "72de4959"
    password = "oicDGhFqhTz-5NhnnW0uGEKOIrSUs0GZBdKtzRhyvns"
    driver = GraphDatabase.driver(uri, auth=(user, password))
    
    test_skill = "Kubernetes"
    
    query = """
    MATCH (s {name: $name})<-[r]-(c:Candidate)
    RETURN c.name as candidate_name, type(r) as rel_type, s.name as skill_name
    LIMIT 10
    """
    
    print(f"Searching for connections to '{test_skill}'...")
    with driver.session() as session:
        result = session.run(query, name=test_skill)
        records = list(result)
        if not records:
            print(f"No connections found for '{test_skill}' via incoming edge (s<-c)")
            # Try outgoing edge (c->s)
            query_rev = """
            MATCH (c:Candidate)-[r]->(s {name: $name})
            RETURN c.name as candidate_name, type(r) as rel_type, s.name as skill_name
            LIMIT 10
            """
            print(f"Trying outgoing edge (c->s)...")
            result_rev = session.run(query_rev, name=test_skill)
            records = list(result_rev)
            
        for r in records:
            print(f"Found: {r['candidate_name']} ---[{r['rel_type']}]---> {r['skill_name']}")
            
        if not records:
            print("Still no connections found. Let's check candidate nodes.")
            res_c = session.run("MATCH (c:Candidate) RETURN c.name LIMIT 5")
            print("Sample candidates:", [r["c.name"] for r in res_c])
            
    driver.close()

if __name__ == "__main__":
    debug_graph_search()
