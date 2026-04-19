import json
from neo4j import GraphDatabase
from ontology_graph import CANONICAL_MAP

NEO4J_URI = "neo4j://127.0.0.1:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "toss1234"

driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

def prepare():
    with driver.session() as session:
        # 1. Delete V9 Chunks
        res = session.run("MATCH (e:Experience_Chunk) DETACH DELETE e RETURN count(e) as deleted")
        deleted_count = res.single()['deleted']
        
        # Check remaining edges
        edge_res = session.run("MATCH ()-[r]->() RETURN count(r) as total_edges")
        total = edge_res.single()['total_edges']
        
        cand_edge_res = session.run("MATCH (c:Candidate)-[r]->(s:Skill) RETURN count(c) as cand_count, count(r) as edge_count")
        cand_edges = cand_edge_res.single()

        # 2. Find nodes to be migrated
        canonical_keys_lower = {k.lower(): (k, v) for k, v in CANONICAL_MAP.items()}
        
        query = """
        MATCH (s:Skill)<-[r]-(:Candidate)
        RETURN s.name as name, count(r) as degree
        ORDER BY degree DESC
        """
        all_skills = session.run(query)
        
        to_migrate = []
        for record in all_skills:
            name = record['name']
            degree = record['degree']
            
            lower_name = name.lower()
            if lower_name in canonical_keys_lower:
                original_key, mapped_val = canonical_keys_lower[lower_name]
                if name != mapped_val:
                    to_migrate.append((name, mapped_val, degree))
                    
        with open('prep_out.txt', 'w', encoding='utf-8') as f:
            f.write(f"=== 1. V9 청크(Experience_Chunk) 데이터 삭제 ===\n")
            f.write(f"삭제된 Experience_Chunk 노드 수: {deleted_count}\n")
            f.write(f"남은 후보자 엣지 연결 수: {cand_edges['edge_count']}개 (후보자 연관)\n")
            f.write(f"전체 DB 엣지 수: {total}개\n\n")
            
            f.write("=== 2. 치환 대상 구 노드 (Top 20) ===\n")
            count = 0
            for name, mapped_val, degree in to_migrate:
                f.write(f"[{degree:4d} edges] '{name}'  ==>  '{mapped_val}'\n")
                count += 1
                if count >= 20:
                    break
            f.write(f"\n총 치환 대상이 될 수 있는 노드 종류 수: {len(to_migrate)}\n")

if __name__ == "__main__":
    prepare()
