from neo4j import GraphDatabase

uri = "neo4j://127.0.0.1:7687"
auth = ("neo4j", "toss1234")

try:
    from ontology_graph import CANONICAL_MAP
    valid_nodes = set(CANONICAL_MAP.values())
    
    driver = GraphDatabase.driver(uri, auth=auth)
    with driver.session() as session:
        result = session.run("MATCH (s:Skill) RETURN s.name AS skill_name")
        neo4j_nodes = set([record["skill_name"] for record in result])
        
    ghost_nodes = neo4j_nodes - valid_nodes
    ghost_nodes = {n for n in ghost_nodes if not "_" in n and not n.isupper()}
    
    print(f"Ghost Nodes ({len(ghost_nodes)}):")
    for g in sorted(list(ghost_nodes)):
        print(f" - {g}")
        
except Exception as e:
    print(f"Error: {e}")
finally:
    if 'driver' in locals():
        driver.close()
