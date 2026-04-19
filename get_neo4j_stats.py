import shutil
import os
from neo4j import GraphDatabase

def main():
    # 1. Backup jd_compiler.py
    shutil.copy('jd_compiler.py', 'jd_compiler_v8_1_final.py')
    print("Backup created: jd_compiler_v8_1_final.py")
    
    # 2. Get Neo4j Stats
    driver = GraphDatabase.driver("bolt://127.0.0.1:7687", auth=("neo4j", "toss1234"))
    with driver.session() as session:
        # Total nodes
        res = session.run("MATCH (n) RETURN count(n)")
        total_nodes = res.single()[0]
        
        # Total edges
        res = session.run("MATCH ()-[r]->() RETURN count(r)")
        total_edges = res.single()[0]
        
        # Embedded candidates
        res = session.run("MATCH (c:Candidate) WHERE c.embedding IS NOT NULL RETURN count(c)")
        embedded_count = res.single()[0]
        
        # Total candidates for average
        res = session.run("MATCH (c:Candidate) RETURN count(c)")
        cand_count = res.single()[0]
        
        avg_edges = round(total_edges / cand_count, 2) if cand_count > 0 else 0
        
        print("\n=== Neo4j Status ===")
        print(f"Total Nodes: {total_nodes}")
        print(f"Total Edges: {total_edges}")
        print(f"Embedded Candidates: {embedded_count}")
        print(f"Average Edges per Candidate: {avg_edges}")
        
    driver.close()

if __name__ == "__main__":
    main()
