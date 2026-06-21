import json
import sys
from neo4j import GraphDatabase

sys.stdout.reconfigure(encoding='utf-8')
secrets_path = r"C:\Users\cazam\Downloads\이력서자동분석검색시스템\secrets.json"

with open(secrets_path, "r", encoding="utf-8") as f:
    secrets = json.load(f)

n_uri = secrets.get("NEO4J_URI", "neo4j://127.0.0.1:7687")
n_user = secrets.get("NEO4J_USERNAME", "neo4j")
n_pw = secrets.get("NEO4J_PASSWORD", "toss1234")
driver = GraphDatabase.driver(n_uri, auth=(n_user, n_pw))

def run_queries():
    # Query 1
    q1 = """
    MATCH (c:Candidate)-[r]->(s:Skill)
    WHERE c.name IN ['전형준', 'Hyeongjun Jeon', '박지민', '이석현', '전예찬']
       OR c.name_kr IN ['전형준', '박지민', '이석현', '전예찬']
    RETURN coalesce(c.name, c.name_kr) AS name, type(r) AS rel_type, s.name AS skill, 
           coalesce(r.weight, r.confidence) AS score, r.evidence_span AS evidence
    ORDER BY name, score DESC
    """
    
    # Query 2
    q2 = """
    MATCH (c:Candidate)-[r]->(s:Skill)
    WHERE c.name = '이정수' OR c.name_kr = '이정수'
    RETURN type(r) AS rel_type, s.name AS skill, coalesce(r.weight, r.confidence) AS score, r.evidence_span AS evidence
    ORDER BY score DESC
    """
    
    with driver.session() as session:
        print("=== [1] Neo4j Edges for 전형준, 박지민, 이석현, 전예찬 ===")
        res1 = session.run(q1)
        records1 = list(res1)
        if not records1:
            print("No edges found for the requested candidates.")
        else:
            for rec in records1:
                print(f"후보자: {rec['name']} | 관계: {rec['rel_type']} | 스킬: {rec['skill']} | 점수(weight/conf): {rec['score']}")
                if rec['evidence']:
                    print(f"  근거: {rec['evidence']}")
        
        print("\n=== [2] Neo4j Edges for 이정수 ===")
        res2 = session.run(q2)
        records2 = list(res2)
        if not records2:
            print("No edges found for 이정수.")
        else:
            for rec in records2:
                print(f"관계: {rec['rel_type']} | 스킬: {rec['skill']} | 점수(weight/conf): {rec['score']}")
                if rec['evidence']:
                    print(f"  근거: {rec['evidence']}")

if __name__ == "__main__":
    run_queries()
    driver.close()
