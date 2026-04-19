import sqlite3
import json
import urllib.request
from neo4j import GraphDatabase

def check_all_dbs():
    print("=== SQLITE DATABASE STATUS ===")
    conn = sqlite3.connect("candidates.db", timeout=10)
    c = conn.cursor()
    
    total = c.execute("SELECT COUNT(*) FROM candidates").fetchone()[0]
    active = c.execute("SELECT COUNT(*) FROM candidates WHERE is_duplicate=0").fetchone()[0]
    ghosts = c.execute("SELECT COUNT(*) FROM candidates WHERE is_duplicate=1").fetchone()[0]
    
    pine_sync_active = c.execute("SELECT COUNT(*) FROM candidates WHERE is_duplicate=0 AND is_pinecone_synced=1").fetchone()[0]
    pine_limbo = c.execute("SELECT COUNT(*) FROM candidates WHERE is_duplicate=0 AND is_pinecone_synced=0").fetchone()[0]
    
    neo_sync_active = c.execute("SELECT COUNT(*) FROM candidates WHERE is_duplicate=0 AND is_neo4j_synced=1").fetchone()[0]
    neo_limbo = c.execute("SELECT COUNT(*) FROM candidates WHERE is_duplicate=0 AND is_neo4j_synced=0").fetchone()[0]

    print(f"Total Candidates: {total}")
    print(f"Active (is_dup=0): {active}")
    print(f"Ghosts (is_dup=1): {ghosts}")
    print(f"Pinecone Synced (Active): {pine_sync_active}  |  Pinecone Limbo: {pine_limbo}")
    print(f"Neo4j Synced (Active): {neo_sync_active}  |  Neo4j Limbo: {neo_limbo}\n")
    
    print("=== PINECONE VECTOR STATUS ===")
    try:
        with open("secrets.json", "r") as f:
            secrets = json.load(f)
            
        host = secrets.get("PINECONE_HOST", "").rstrip("/")
        if not host.startswith("https://"):
            host = f"https://{host}"
            
        req = urllib.request.Request(f"{host}/describe_index_stats", headers={
            "Api-Key": secrets.get("PINECONE_API_KEY"),
            "Accept": "application/json"
        })
        
        with urllib.request.urlopen(req, timeout=5) as res:
            p_data = json.loads(res.read().decode('utf-8'))
            print(f"Total Vectors: {p_data.get('totalVectorCount')}")
            for ns, info in p_data.get('namespaces', {}).items():
                if ns == '': ns = '(default)'
                print(f"  - Namespace '{ns}': {info.get('vectorCount')} vectors")
    except Exception as e:
        print("Pinecone fetch failed:", str(e))
        
    print("\n=== NEO4J GRAPH STATUS ===")
    try:
        driver = GraphDatabase.driver("bolt://127.0.0.1:7687", auth=("neo4j", "toss1234"))
        with driver.session() as session:
            total_nodes = session.run("MATCH (c:Candidate) RETURN count(c)").single()[0]
            ghost_nodes = session.run("MATCH (c:Candidate {is_duplicate: true}) RETURN count(c)").single()[0]
            active_nodes = session.run("MATCH (c:Candidate) WHERE c.is_duplicate IS NULL OR c.is_duplicate=false RETURN count(c)").single()[0]
            total_edges = session.run("MATCH ()-[r]->() RETURN count(r)").single()[0]
            c_edges = session.run("MATCH (c:Candidate)-[r]->() RETURN count(r)").single()[0]
            
            print(f"Total Candidate Nodes: {total_nodes}")
            print(f"Active Candidate Nodes: {active_nodes}")
            print(f"Ghost Nodes (is_dup=true): {ghost_nodes}")
            print(f"Total Graph Edges: {total_edges} (From candidates: {c_edges})")
    except Exception as e:
        print("Neo4j fetch failed:", str(e))

if __name__ == "__main__":
    check_all_dbs()
