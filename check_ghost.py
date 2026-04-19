from neo4j import GraphDatabase
import json

NEO4J_URI = "neo4j://127.0.0.1:7687"
NEO4J_AUTH = ("neo4j", "toss1234")

# Load valid nodes
valid_nodes = set()
try:
    from ontology_graph import CANONICAL_MAP
    valid_nodes = set(CANONICAL_MAP.values())
except Exception as e:
    print(f"Error parsing CANONICAL_MAP: {e}")

try:
    driver = GraphDatabase.driver(NEO4J_URI, auth=NEO4J_AUTH)
    with driver.session() as session:
        result = session.run("MATCH (s:Skill) RETURN s.name AS skill_name")
        neo4j_nodes = set([record["skill_name"] for record in result])
        
    ghost_nodes = neo4j_nodes - valid_nodes
    ghost_nodes = {n for n in ghost_nodes if not '_' in n and not n.isupper()}
    
    print(f"Ghost Nodes: {ghost_nodes}")
    if len(ghost_nodes) > 0:
        with driver.session() as session:
            for g in ghost_nodes:
                session.run(f"MATCH (s:Skill {{name: '{g}'}}) DETACH DELETE s")
                print(f"Deleted ghost node: {g}")
except Exception as e:
    print(f"Neo4j Error: {e}")
