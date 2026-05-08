import json
import os
import sys
from neo4j import GraphDatabase
import sys
sys.path.append(os.getcwd())
import ontology_graph
from collections import defaultdict

# Load secrets
with open("secrets.json", "r", encoding="utf-8") as f:
    secrets = json.load(f)

uri = secrets.get("NEO4J_URI")
user = secrets.get("NEO4J_USERNAME")
password = secrets.get("NEO4J_PASSWORD")

print(f"Syncing ontology to Neo4j Aura: {uri}")

def sync_nodes():
    driver = GraphDatabase.driver(uri, auth=(user, password))
    nodes = set(ontology_graph.CANONICAL_MAP.values())
    
    with driver.session() as session:
        print(f"1. Syncing {len(nodes)} Master Nodes...")
        batch_size = 500
        nodes_list = list(nodes)
        for i in range(0, len(nodes_list), batch_size):
            batch = nodes_list[i:i+batch_size]
            session.run("""
            UNWIND $names AS name
            MERGE (s:Skill {name: name})
            """, names=batch)
            
        print("2. Syncing Edges...")
        edges = ontology_graph.EDGES
        # Group edges by relation type
        by_rel = defaultdict(list)
        for s, d, r, w in edges:
            by_rel[r.upper()].append({"src": s, "dst": d, "weight": float(w)})
            
        for rel_type, rel_edges in by_rel.items():
            print(f"   Processing {rel_type}: {len(rel_edges)} edges...")
            for i in range(0, len(rel_edges), batch_size):
                batch = rel_edges[i:i+batch_size]
                query = f"""
                UNWIND $rows AS row
                MATCH (s1:Skill {{name: row.src}}), (s2:Skill {{name: row.dst}})
                MERGE (s1)-[r:{rel_type}]->(s2)
                SET r.weight = row.weight, r.distance = round(1.0/row.weight, 4)
                """
                session.run(query, rows=batch)
                
        print(f"✅ Sync complete. {len(nodes)} nodes and {len(edges)} edges processed.")
        
    driver.close()

if __name__ == "__main__":
    sync_nodes()
