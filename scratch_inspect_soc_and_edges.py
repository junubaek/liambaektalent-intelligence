import sys
import json
from neo4j import GraphDatabase

sys.stdout.reconfigure(encoding='utf-8')
sys.path.append(r'C:\Users\cazam\Downloads\이력서자동분석검색시스템')

from jd_compiler import api_search_v9

def main():
    # [작업 1] SoC 쿼리 확인
    print("=== [작업 1] SoC Architect Query check ===")
    query = "SoC 아키텍트 찾아줘"
    try:
        res = api_search_v9(query)
        matched = res.get('matched', [])
        
        targets = ['강종훈', '서보옥']
        found = {t: "30위 권외" for t in targets}
        
        print("\n=== Top 30 Search Results for SoC ===")
        for i, c in enumerate(matched[:30]):
            name = c.get('name_kr') or c.get('name')
            score = c.get('final_score') or 0.0
            company = c.get('current_company') or '미상'
            print(f"Rank {i+1}: {name} | Score: {score:.4f} | 회사: {company}")
            
            if name in found:
                found[name] = f"{i+1}위 (Score: {score:.4f})"
                
        print("\n=== SoC TARGET CANDIDATES RANKS ===")
        for name, rank in found.items():
            print(f"- {name}: {rank}")
            
    except Exception as e:
        print(f"Error running SoC query: {e}")
        
    # [작업 3] 황승현, 홍용기, 최성우, 전예찬 Neo4j 엣지 확인
    print("\n=== [작업 3] Neo4j edges for 황승현, 홍용기, 최성우, 전예찬 ===")
    with open("secrets.json", encoding="utf-8") as f:
        secrets = json.load(f)
        
    driver = GraphDatabase.driver(secrets["NEO4J_URI"], auth=(secrets["NEO4J_USERNAME"], secrets["NEO4J_PASSWORD"]))
    
    q_edges = """
    MATCH (c:Candidate)-[r]->(s:Skill)
    WHERE c.name_kr IN ['황승현', '홍용기', '최성우', '전예찬']
    RETURN c.name_kr AS name, collect(s.name) AS skills
    ORDER BY name
    """
    
    with driver.session() as session:
        result = session.run(q_edges)
        for r in result:
            skills_str = ", ".join(r['skills'])
            print(f"- {r['name']}: {skills_str}")
            
    driver.close()

if __name__ == "__main__":
    main()
