from neo4j import GraphDatabase
from jd_compiler import parse_jd_to_json
import json

def check_overlap():
    driver = GraphDatabase.driver('bolt://127.0.0.1:7687', auth=('neo4j', 'toss1234'))
    with driver.session() as session:
        q = """
        MATCH (c:Candidate)-[r:BUILT|DESIGNED|MANAGED|ANALYZED|SUPPORTED|NEGOTIATED|GREW|LAUNCHED|LED|OPTIMIZED|PLANNED|EXECUTED]->(s:Skill)
        WHERE c.name_kr = '홍기재'
        RETURN type(r) AS action, s.name AS skill
        """
        res = session.run(q)
        print("\n========================================")
        print("👤 홍기재 님의 Neo4j 엣지 7개 목록:")
        edges = []
        for r in res:
            edge = f"[{r['action']}] -> {r['skill']}"
            edges.append(edge)
            print(f"  - {edge}")
            
    driver.close()
    
    print("\n========================================")
    print("🤖 jd_compiler 파싱 결과 ('Framework Software Engineer'):")
    # This might take a few seconds since it uses Gemini
    jd_analysis = parse_jd_to_json('Framework Software Engineer')
    
    # We want to see what nodes are actually extracted as target nodes
    # Usually it's in jd_analysis['target_nodes'] or 'domain_nodes'
    if 'domain_nodes' in jd_analysis:
        print(f"  - 종속 노드 (Domain Nodes): {jd_analysis['domain_nodes']}")
    if 'fallback_nodes' in jd_analysis:
        print(f"  - 폴백 노드 (Fallback Nodes): {jd_analysis.get('fallback_nodes', [])}")
        
    print("\n💡 전체 JD 파싱 JSON 응답 원문:")
    print(json.dumps(jd_analysis, indent=2, ensure_ascii=False))

if __name__ == '__main__':
    check_overlap()
