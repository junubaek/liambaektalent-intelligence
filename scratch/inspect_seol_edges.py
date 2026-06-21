from neo4j import GraphDatabase
import json
import sys

def main():
    sys.stdout.reconfigure(encoding='utf-8')
    secrets = json.load(open('secrets.json', encoding='utf-8'))
    driver = GraphDatabase.driver(secrets['NEO4J_URI'], auth=(secrets['NEO4J_USERNAME'], secrets['NEO4J_PASSWORD']))

    with driver.session() as s:
        print("=== 설우식 후보자의 Neo4j 엣지 전체 상세 리스트 ===")
        
        # 1. Candidate -> Skill Direct Edges
        res = s.run("""
            MATCH (c:Candidate {name_kr: '홍기재'})-[r]->(s:Skill)
            RETURN type(r) as type, s.name as skill, properties(r) as props
        """)
        direct_edges = res.data()
        
        print("1. Candidate -> Skill (Direct Edges):")
        if direct_edges:
            for i, e in enumerate(direct_edges):
                props_str = json.dumps(e.get('props', {}), ensure_ascii=False)
                print(f"  [{i+1}] Skill: {e['skill']:<25} | Type: {e['type']:<10} | Properties: {props_str}")
        else:
            print("  (직접 연결된 Skill 엣지가 존재하지 않거나, 이력 청크를 통해 연결되어 있습니다.)")
            
        # 2. Experience_Chunk -> Skill Edges
        print("\n2. Experience_Chunk -> Skill (Experience Chunks Edges):")
        res_chunk = s.run("""
            MATCH (c:Candidate {name_kr: '홍기재'})-[:HAS_EXPERIENCE]->(e:Experience_Chunk)-[r]->(s:Skill)
            RETURN e.company_name as company, type(r) as type, s.name as skill, properties(r) as props
        """)
        chunk_edges = res_chunk.data()
        if chunk_edges:
            for i, e in enumerate(chunk_edges):
                props_str = json.dumps(e.get('props', {}), ensure_ascii=False)
                print(f"  [{i+1}] Company: {e['company']:<15} | Skill: {e['skill']:<25} | Type: {e['type']:<10} | Properties: {props_str}")
        else:
            print("  (이력 청크를 통한 Skill 엣지가 존재하지 않습니다.)")

    driver.close()

if __name__ == '__main__':
    main()
