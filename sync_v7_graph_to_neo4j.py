import sys
sys.path.append('c:/Users/cazam/Downloads/이력서자동분석검색시스템')

from neo4j import GraphDatabase
import ontology_graph

uri = "neo4j+ssc://2c78ff2f.databases.neo4j.io"
user = "neo4j"
password = "sUdocj6IJEdIWCPNE6qzJq7kCdynS6EjSuBeKJtcye4"

def sync_graph():
    driver = GraphDatabase.driver(uri, auth=(user, password))
    
    # Extract unique master nodes from CANONICAL_MAP values
    nodes = set(ontology_graph.CANONICAL_MAP.values())
    
    with driver.session() as session:
        print("Syncing Nodes...")
        # 1. Create nodes
        for node in nodes:
            session.run("MERGE (s:Skill {name: $name})", name=node)
            
        print(f"Synced {len(nodes)} master nodes.")
        
        # 2. Create edges
        print("Syncing Edges...")
        edges_count = 0
        for src, dst, rel, weight in ontology_graph.EDGES:
            query = f"""
            MATCH (s1:Skill {{name: $src}}), (s2:Skill {{name: $dst}})
            MERGE (s1)-[r:{rel.upper()}]->(s2)
            SET r.distance = $weight
            """
            session.run(query, src=src, dst=dst, weight=weight)
            edges_count += 1
            
        print(f"Synced {edges_count} edges.")
    
    driver.close()

if __name__ == "__main__":
    sync_graph()
