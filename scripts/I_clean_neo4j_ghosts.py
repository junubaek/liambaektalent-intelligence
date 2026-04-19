from neo4j import GraphDatabase
import json

def clean_ghost_nodes():
    print("Purging Neo4j Ghost Nodes...")
    
    with open('candidates_cache_jd.json', 'r', encoding='utf-8') as f:
        cache = json.load(f)
        
    valid_ids = {str(c['id']) for c in cache}
    
    driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "toss1234"))
    
    deleted_count = 0
    with driver.session() as session:
        # Fetch all candidate IDs from Neo4j
        res = session.run("MATCH (c:Candidate) RETURN c.id AS cid").data()
        neo4j_ids = [r['cid'] for r in res if r['cid']]
        
        ghost_ids = [nid for nid in neo4j_ids if nid not in valid_ids]
        
        if ghost_ids:
            print(f"Found {len(ghost_ids)} ghost Candidate nodes. Deleting...")
            # Delete in chunks
            chunk_size = 500
            for i in range(0, len(ghost_ids), chunk_size):
                chunk = ghost_ids[i:i+chunk_size]
                session.run("MATCH (c:Candidate) WHERE c.id IN $gids DETACH DELETE c", gids=chunk)
                deleted_count += len(chunk)
                
    print(f"Successfully deleted {deleted_count} ghost nodes from Neo4j.")

if __name__ == "__main__":
    clean_ghost_nodes()
