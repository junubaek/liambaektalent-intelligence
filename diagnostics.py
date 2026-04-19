import json
from neo4j import GraphDatabase

NEO4J_URI = "neo4j://127.0.0.1:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "toss1234"

driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

def run_diagnostics():
    with driver.session() as session:
        # 1. Select 3 random candidates who have V9 chunks
        print("=== 1. V9 파싱된 인원 3명 샘플 엣지 확인 ===")
        sample_query = """
        MATCH (c:Candidate)-[:HAS_EXPERIENCE]->(e:Experience_Chunk)-[r]->(s:Skill)
        WITH c, collect({chunk: e.company_name + ' | ' + e.role_name, rel: type(r), skill: s.name}) as edges
        LIMIT 3
        RETURN c.name_kr as name, c.id as id, edges
        """
        result = session.run(sample_query)
        for record in result:
            print(f"\nCandidate: {record['name']} ({record['id']})")
            for edge in record['edges']:
                print(f"  - [{edge['chunk']}] -[:{edge['rel']}]-> {edge['skill']}")
        
        # 3. V8 edges count vs V9 chunks count
        print("\n=== 3. V8 vs V9 엣지/노드 통계 ===")
        
        # Check candidates with V8 direct edges
        v8_query = """
        MATCH (c:Candidate)-[r]->(s:Skill)
        WHERE type(r) <> 'HAS_EXPERIENCE'
        RETURN count(DISTINCT c) as v8_candidate_count, count(r) as v8_edge_count
        """
        v8_res = session.run(v8_query).single()
        print(f"V8 방식(직접 연결)을 가진 Candidate 수: {v8_res['v8_candidate_count']}명")
        print(f"V8 방식(직접 연결) 엣지 총 개수: {v8_res['v8_edge_count']}개")
        
        # Check candidates with V9 chunk edges
        v9_query = """
        MATCH (c:Candidate)-[:HAS_EXPERIENCE]->(e:Experience_Chunk)
        RETURN count(DISTINCT c) as v9_candidate_count, count(e) as chunk_count
        """
        v9_res = session.run(v9_query).single()
        print(f"V9 방식(청크 연결)을 가진 Candidate 수: {v9_res['v9_candidate_count']}명")
        
        # Check chunk to skill edges
        v9_edge_query = """
        MATCH (e:Experience_Chunk)-[r]->(s:Skill)
        RETURN count(r) as v9_edge_count
        """
        v9_edge_res = session.run(v9_edge_query).single()
        print(f"V9 방식(청크->스킬) 엣지 총 개수: {v9_edge_res['v9_edge_count']}개")

        # Are V8 edges still present for the V9 candidates?
        v9_with_v8_query = """
        MATCH (c:Candidate)-[:HAS_EXPERIENCE]->(:Experience_Chunk)
        MATCH (c)-[r]->(s:Skill)
        WHERE type(r) <> 'HAS_EXPERIENCE'
        RETURN count(DISTINCT c) as overlapped_count
        """
        overlapped_res = session.run(v9_with_v8_query).single()
        print(f"V9 청크도 있고 V8 직접 엣지도 있는 Candidate 수: {overlapped_res['overlapped_count']}명")


if __name__ == "__main__":
    run_diagnostics()
