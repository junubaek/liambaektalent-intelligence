import json
from neo4j import GraphDatabase
from ontology_graph import CANONICAL_MAP

NEO4J_URI = "neo4j://127.0.0.1:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "toss1234"

driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

def run_migration():
    canonical_keys_lower = {k.lower(): (k, v) for k, v in CANONICAL_MAP.items()}
    
    with driver.session() as session:
        # Pre-count
        edge_res = session.run("MATCH (c:Candidate)-[r]->(s:Skill) RETURN count(r) as total_edges")
        pre_count = edge_res.single()['total_edges']
        print(f"치환 전 총 후보자 엣지 수: {pre_count}")
        
        # Get nodes to migrate
        query = """
        MATCH (s:Skill)<-[r]-(:Candidate)
        RETURN s.name as name
        """
        all_skills = [record['name'] for record in session.run(query)]
        all_skills = list(set(all_skills))
        
        to_migrate = []
        for name in all_skills:
            if name.lower() in canonical_keys_lower:
                _, mapped_val = canonical_keys_lower[name.lower()]
                if name != mapped_val:
                    to_migrate.append((name, mapped_val))
                    
        print(f"치환 대상 노드 종류 수: {len(to_migrate)}")
        
        # Migrate edges natively through python iteration to avoid APOC dependency
        migrated_nodes_count = 0
        for old_name, new_name in to_migrate:
            rels = session.run("MATCH (c:Candidate)-[r]->(old:Skill {name: $old_name}) RETURN c.id as cid, type(r) as rtype, properties(r) as props", old_name=old_name).data()
            
            if not rels:
                continue
                
            session.run("MERGE (new:Skill {name: $new_name})", new_name=new_name)
            
            for record in rels:
                cid = record['cid']
                rtype = record['rtype']
                props = record['props']
                
                # Merge connection to new node
                session.run(f"""
                MATCH (c:Candidate {{id: $cid}})
                MATCH (new:Skill {{name: $new_name}})
                MERGE (c)-[r:{rtype}]->(new)
                SET r += $props
                """, cid=cid, new_name=new_name, props=props)
                
            # Delete old edges and old node
            session.run("MATCH (old:Skill {name: $old_name}) DETACH DELETE old", old_name=old_name)
            migrated_nodes_count += 1
            
        print(f"실제 치환 완료된 노드 종류 수: {migrated_nodes_count}")
            
        # Post-count
        post_edge_res = session.run("MATCH (c:Candidate)-[r]->(s:Skill) RETURN count(r) as total_edges")
        post_count = post_edge_res.single()['total_edges']
        print(f"치환 후 총 후보자 엣지 수: {post_count}")
        
        # Sample candidates
        print("\n=== 샘플 후보자 3명 엣지 출력 ===")
        sample_query = """
        MATCH (c:Candidate)-[r]->(s:Skill)
        WITH c, collect({rel: type(r), skill: s.name}) as edges
        WHERE size(edges) > 5
        LIMIT 3
        RETURN c.name_kr as name, c.id as id, edges
        """
        result = session.run(sample_query)
        for record in result:
            print(f"\nCandidate: {record['name']} ({record['id'][:8]}...)")
            for edge in record['edges'][:10]: # Print up to 10 edges to avoid massive logs
                print(f"  - [:{edge['rel']}]-> {edge['skill']}")
            if len(record['edges']) > 10:
                print(f"  ... (and {len(record['edges']) - 10} more)")


if __name__ == "__main__":
    run_migration()
